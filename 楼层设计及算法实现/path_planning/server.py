"""
路径规划服务器
提供HTTP API接口，支持实时路径规划
"""

import logging
import math
import random
import json
from collections import deque
from urllib.error import URLError
from urllib.request import urlopen
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

# 尝试导入CORS，如果没有安装则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("警告: flask-cors 未安装，跨域请求将被禁用")
    print("安装方法: pip install flask-cors")

from data_loader import DataLoader
from graph_builder import GraphBuilder
from path_planning_service import PathPlanningService
from path_formatter import PathFormatter
from models import Position
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 如果CORS可用，则启用跨域支持
if CORS_AVAILABLE:
    CORS(app)
    print("✓ CORS跨域支持已启用")

# 全局变量：路径规划服务
path_service = None
path_formatter = None
GRID_SIZE_M = 1.0
GRID_SAMPLE_STEP_M = 0.25


def _build_path_nodes_with_coords(graph, path):
    path_nodes_with_coords = []
    for node in path:
        node_info = graph.get_node_info(node)
        path_nodes_with_coords.append({
            'node_type': node[0],
            'node_id': node[1],
            'map_id': node[2],
            'x': node_info.x if node_info else 0,
            'y': node_info.y if node_info else 0
        })
    return path_nodes_with_coords


def _sample_segment_points(start_point, end_point):
    dx = end_point['x'] - start_point['x']
    dy = end_point['y'] - start_point['y']
    distance = math.hypot(dx, dy)
    steps = max(1, int(math.ceil(distance / GRID_SAMPLE_STEP_M)))

    return [
        (
            start_point['x'] + dx * (index / steps),
            start_point['y'] + dy * (index / steps)
        )
        for index in range(steps + 1)
    ]


def _append_grid_center(grid_points, map_id, x, y):
    grid_x = int(math.floor(float(x) / GRID_SIZE_M))
    grid_y = int(math.floor(float(y) / GRID_SIZE_M))
    center_x = round((grid_x + 0.5) * GRID_SIZE_M, 2)
    center_y = round((grid_y + 0.5) * GRID_SIZE_M, 2)

    if grid_points:
        last_point = grid_points[-1]
        if (
            last_point['map_id'] == map_id and
            last_point['grid_x'] == grid_x and
            last_point['grid_y'] == grid_y
        ):
            return

    grid_points.append({
        'order': len(grid_points) + 1,
        'map_id': map_id,
        'grid_x': grid_x,
        'grid_y': grid_y,
        'center_x': center_x,
        'center_y': center_y
    })


def _build_path_grid_centers(path_nodes_with_coords):
    if not path_nodes_with_coords:
        return [], []

    path_grid_centers = []
    _append_grid_center(
        path_grid_centers,
        path_nodes_with_coords[0]['map_id'],
        path_nodes_with_coords[0]['x'],
        path_nodes_with_coords[0]['y']
    )

    for index in range(len(path_nodes_with_coords) - 1):
        current_point = path_nodes_with_coords[index]
        next_point = path_nodes_with_coords[index + 1]

        if current_point['map_id'] == next_point['map_id']:
            for sample_x, sample_y in _sample_segment_points(current_point, next_point):
                _append_grid_center(
                    path_grid_centers,
                    current_point['map_id'],
                    sample_x,
                    sample_y
                )
        else:
            _append_grid_center(
                path_grid_centers,
                next_point['map_id'],
                next_point['x'],
                next_point['y']
            )

    floor_grid_centers = []
    floor_lookup = {}
    for grid_point in path_grid_centers:
        floor_entry = floor_lookup.get(grid_point['map_id'])
        if floor_entry is None:
            floor_entry = {
                'map_id': grid_point['map_id'],
                'grid_centers': []
            }
            floor_lookup[grid_point['map_id']] = floor_entry
            floor_grid_centers.append(floor_entry)

        floor_entry['grid_centers'].append(grid_point)

    return path_grid_centers, floor_grid_centers


def _build_success_response(graph, result, description):
    path_nodes_with_coords = _build_path_nodes_with_coords(graph, result.path)
    path_grid_centers, floor_grid_centers = _build_path_grid_centers(path_nodes_with_coords)

    return {
        'success': True,
        'distance': result.distance,
        'total_distance': description.total_distance,
        'floors': description.floors,
        'steps': [
            {
                'step_number': step.step_number,
                'floor': step.floor,
                'action': step.action,
                'location': step.location,
                'distance': step.distance
            }
            for step in description.steps
        ],
        'path_nodes': path_nodes_with_coords,
        'path_grid_centers': path_grid_centers,
        'floor_grid_centers': floor_grid_centers
    }


def _calculate_polyline_distance(points):
    if len(points) < 2:
        return 0.0

    total = 0.0
    for index in range(len(points) - 1):
        current_point = points[index]
        next_point = points[index + 1]
        total += math.hypot(next_point['x'] - current_point['x'], next_point['y'] - current_point['y'])
    return round(total, 2)


def _extract_floors_from_points(points):
    floors = []
    seen = set()
    for point in points:
        map_id = point.get('map_id')
        if map_id and map_id not in seen:
            floors.append(map_id)
            seen.add(map_id)
    return floors


def _append_unique_point(points, point):
    if not point:
        return

    if points:
        last_point = points[-1]
        if (
            last_point.get('map_id') == point.get('map_id') and
            abs(float(last_point.get('x', 0)) - float(point.get('x', 0))) < 1e-6 and
            abs(float(last_point.get('y', 0)) - float(point.get('y', 0))) < 1e-6
        ):
            return

    points.append(point)


def _merge_point_sequences(*sequences):
    merged = []
    for sequence in sequences:
        for point in sequence or []:
            _append_unique_point(merged, point)
    return merged


def _make_point(x, y, map_id, **extra):
    point = {
        'x': round(float(x), 4),
        'y': round(float(y), 4),
        'map_id': map_id
    }
    point.update(extra)
    return point


def _build_custom_response(path_points, steps):
    path_grid_centers, floor_grid_centers = _build_path_grid_centers(path_points)
    total_distance = _calculate_polyline_distance(path_points)
    floors = _extract_floors_from_points(path_points)

    return {
        'success': True,
        'distance': total_distance,
        'total_distance': total_distance,
        'floors': floors,
        'steps': steps,
        'path_nodes': path_points,
        'path_grid_centers': path_grid_centers,
        'floor_grid_centers': floor_grid_centers
    }


def _parse_simulation_start_time(value):
    if not value:
        return datetime.now()
    try:
        normalized = value.replace('Z', '+00:00')
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError('start_time 必须是 ISO-8601 时间格式') from exc


def _get_simulation_nodes(graph):
    return [
        node for node in graph.get_all_nodes()
        if len(graph.get_neighbors(node)) > 0
    ]


def _choose_random_reachable_path(service, available_nodes, start_node, rng, max_attempts=20):
    if not available_nodes:
        raise ValueError('连通图中没有可用节点')

    candidates = [node for node in available_nodes if node != start_node]
    if not candidates:
        raise ValueError('连通图中没有可作为目标的其他节点')

    for _ in range(max_attempts):
        target_node = rng.choice(candidates)
        result = service.algorithm.find_shortest_path(start_node, target_node)
        if result.success and result.path:
            return result, target_node

    raise ValueError('随机选点后未找到可达路径，请检查连通图')


def _row_value(row, *keys):
    for key in keys:
        if key in row:
            return row.get(key)
    return None


def _normalize_region_grid_cell(row):
    return {
        'map_id': _row_value(row, 'map_id', 'mapId'),
        'grid_x': int(_row_value(row, 'grid_x', 'gridX')),
        'grid_y': int(_row_value(row, 'grid_y', 'gridY')),
        'center_x': float(_row_value(row, 'center_x', 'centerX')),
        'center_y': float(_row_value(row, 'center_y', 'centerY'))
    }


def _read_json_url(url, timeout=5):
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def _load_room_simulation_rows_from_api(base_url='http://localhost:8083'):
    doors_payload = _read_json_url(f'{base_url}/api/doors/list')
    doors = doors_payload.get('data', doors_payload) if isinstance(doors_payload, dict) else doors_payload
    if not isinstance(doors, list):
        return [], []

    bound_doors = [
        door for door in doors
        if _row_value(door, 'targetRegionId', 'target_region_id')
    ]
    region_ids = sorted({
        _row_value(door, 'targetRegionId', 'target_region_id')
        for door in bound_doors
    })

    grid_rows = []
    region_name_lookup = {
        _row_value(door, 'targetRegionId', 'target_region_id'): _row_value(door, 'targetRegionName', 'target_region_name')
        for door in bound_doors
    }
    for region_id in region_ids:
        region_cells = _read_json_url(f'{base_url}/api/regions/{region_id}/grid-cells')
        if isinstance(region_cells, list):
            grid_rows.extend(region_cells)

    door_bindings = []
    for door in bound_doors:
        door_bindings.append({
            'door_id': _row_value(door, 'id'),
            'door_map_id': _row_value(door, 'mapId', 'map_id'),
            'door_x': _row_value(door, 'x'),
            'door_y': _row_value(door, 'y'),
            'room_name': _row_value(door, 'roomName', 'room_name'),
            'region_id': _row_value(door, 'targetRegionId', 'target_region_id'),
            'region_name': _row_value(door, 'targetRegionName', 'target_region_name') or region_name_lookup.get(_row_value(door, 'targetRegionId', 'target_region_id'))
        })

    return door_bindings, grid_rows


def _load_room_simulation_context(server):
    try:
        door_bindings, grid_rows = _load_room_simulation_rows_from_api()
    except (URLError, TimeoutError, OSError, ValueError) as api_exc:
        logger.warning(f"Failed to load door-region grid data from Spring API: {api_exc}")
        try:
            from database import DatabaseManager

            with DatabaseManager(database='ship_floor') as db:
                door_bindings = db.execute_query("""
                    SELECT d.id AS door_id,
                           d.map_id AS door_map_id,
                           d.x AS door_x,
                           d.y AS door_y,
                           d.room_name,
                           d.target_region_id AS region_id,
                           r.region_name
                    FROM doors d
                    JOIN regions r ON d.target_region_id = r.region_id
                    WHERE d.is_active = 1
                      AND d.target_region_id IS NOT NULL
                      AND d.target_region_id <> ''
                """)
                grid_rows = db.execute_query("""
                    SELECT region_id, map_id, grid_x, grid_y, center_x, center_y
                    FROM region_grid_cells
                    ORDER BY region_id ASC, grid_y ASC, grid_x ASC
                """)
        except Exception as exc:
            logger.warning(f"Failed to load door-region grid data, fallback to graph simulation: {exc}")
            return {
                'available': False,
                'entries': [],
                'region_cells': {}
            }
    except Exception as exc:
        logger.warning(f"Failed to load door-region grid data, fallback to graph simulation: {exc}")
        return {
            'available': False,
            'entries': [],
            'region_cells': {}
        }

    region_cells = {}
    for row in grid_rows:
        region_id = _row_value(row, 'region_id', 'regionId')
        if not region_id:
            continue
        region_cells.setdefault(region_id, []).append(_normalize_region_grid_cell(row))

    graph_nodes = set(server.graph.get_all_nodes())
    entries = []
    entry_by_node = {}
    for binding in door_bindings:
        region_id = binding.get('region_id')
        door_id = binding.get('door_id')
        door_map_id = binding.get('door_map_id')
        if not region_id or door_id is None or not door_map_id:
            continue

        node = (1, int(door_id), door_map_id)
        cells = region_cells.get(region_id) or []
        if node not in graph_nodes or not cells:
            continue

        entry = {
            'node': node,
            'door_id': int(door_id),
            'door_name': binding.get('room_name') or f'Door-{door_id}',
            'door_map_id': door_map_id,
            'door_x': float(binding.get('door_x') or 0),
            'door_y': float(binding.get('door_y') or 0),
            'region_id': region_id,
            'region_name': binding.get('region_name') or region_id,
            'cells': cells
        }
        entries.append(entry)
        entry_by_node[node] = entry

    entries_by_region = {}
    for entry in entries:
        entries_by_region.setdefault(entry['region_id'], []).append(entry)

    cell_index = {}
    for region_id, cells in region_cells.items():
        for cell in cells:
            key = (cell['map_id'], cell['grid_x'], cell['grid_y'])
            cell_index.setdefault(key, []).append(region_id)

    return {
        'available': len(entries) > 0,
        'entries': entries,
        'entry_by_node': entry_by_node,
        'entries_by_region': entries_by_region,
        'cell_index': cell_index,
        'region_cells': region_cells
    }


def _choose_random_reachable_region_entry(service, entries, start_node, rng, max_attempts=40):
    if not entries:
        raise ValueError('No usable door-region bindings for room simulation')

    candidates = [entry for entry in entries if entry['node'] != start_node] or entries
    for _ in range(max_attempts):
        entry = rng.choice(candidates)
        result = service.algorithm.find_shortest_path(start_node, entry['node'])
        if result.success and result.path:
            return result, entry

    raise ValueError('No reachable bound room door found from the current graph node')


def _find_nearest_region_cell(cells, x, y):
    return min(
        cells,
        key=lambda cell: math.hypot(cell['center_x'] - x, cell['center_y'] - y)
    )


def _build_region_grid_walk(entry, point_count, rng):
    cells = entry.get('cells') or []
    if not cells or point_count <= 0:
        return []

    cell_lookup = {
        (cell['grid_x'], cell['grid_y']): cell
        for cell in cells
    }
    current_cell = _find_nearest_region_cell(cells, entry['door_x'], entry['door_y'])
    walk = []

    for _ in range(point_count):
        walk.append({
            **current_cell,
            'region_id': entry['region_id'],
            'region_name': entry['region_name'],
            'entry_door_id': entry['door_id'],
            'entry_door_name': entry['door_name']
        })
        grid_x = current_cell['grid_x']
        grid_y = current_cell['grid_y']
        neighbor_cells = [
            cell_lookup[key]
            for key in (
                (grid_x + 1, grid_y),
                (grid_x - 1, grid_y),
                (grid_x, grid_y + 1),
                (grid_x, grid_y - 1)
            )
            if key in cell_lookup
        ]

        current_cell = rng.choice(neighbor_cells) if neighbor_cells else rng.choice(cells)

    return walk


def _project_entry_to_region_cell(entry):
    nearest_cell = _find_nearest_region_cell(entry['cells'], entry['door_x'], entry['door_y'])
    return {
        **nearest_cell,
        'region_id': entry['region_id'],
        'region_name': entry['region_name'],
        'entry_door_id': entry['door_id'],
        'entry_door_name': entry['door_name']
    }


def _build_region_transition_points(route_path, room_context):
    points = []
    entry_by_node = room_context.get('entry_by_node') or {}

    for node in route_path:
        entry = entry_by_node.get(node)
        if not entry:
            continue

        projected_point = _project_entry_to_region_cell(entry)
        if points:
            last_point = points[-1]
            if (
                last_point['region_id'] == projected_point['region_id'] and
                last_point['grid_x'] == projected_point['grid_x'] and
                last_point['grid_y'] == projected_point['grid_y']
            ):
                continue

        points.append(projected_point)

    return points


def _get_position_grid(x, y):
    return int(math.floor(float(x) / GRID_SIZE_M)), int(math.floor(float(y) / GRID_SIZE_M))


def _resolve_region_for_position(room_context, position):
    grid_x, grid_y = _get_position_grid(position.x, position.y)
    candidate_region_ids = room_context.get('cell_index', {}).get((position.map_id, grid_x, grid_y), [])
    if not candidate_region_ids:
        return None

    if len(candidate_region_ids) == 1:
        return candidate_region_ids[0]

    nearest_region_id = None
    nearest_distance = float('inf')
    for region_id in candidate_region_ids:
        cells = room_context['region_cells'].get(region_id) or []
        if not cells:
            continue
        nearest_cell = _find_nearest_region_cell(cells, position.x, position.y)
        distance = math.hypot(nearest_cell['center_x'] - position.x, nearest_cell['center_y'] - position.y)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_region_id = region_id

    return nearest_region_id


def _find_region_cell_for_position(cells, position):
    grid_x, grid_y = _get_position_grid(position.x, position.y)
    exact_match = next(
        (
            cell for cell in cells
            if cell['grid_x'] == grid_x and cell['grid_y'] == grid_y and cell['map_id'] == position.map_id
        ),
        None
    )
    if exact_match:
        return exact_match
    return _find_nearest_region_cell(cells, position.x, position.y)


def _build_region_cell_path(cells, start_cell, end_cell):
    start_key = (start_cell['grid_x'], start_cell['grid_y'])
    end_key = (end_cell['grid_x'], end_cell['grid_y'])
    if start_key == end_key:
        return [start_cell]

    cell_lookup = {
        (cell['grid_x'], cell['grid_y']): cell
        for cell in cells
    }
    queue = deque([start_key])
    previous = {start_key: None}

    while queue:
        current_key = queue.popleft()
        if current_key == end_key:
            break

        current_x, current_y = current_key
        for neighbor_key in (
            (current_x + 1, current_y),
            (current_x - 1, current_y),
            (current_x, current_y + 1),
            (current_x, current_y - 1)
        ):
            if neighbor_key not in cell_lookup or neighbor_key in previous:
                continue
            previous[neighbor_key] = current_key
            queue.append(neighbor_key)

    if end_key not in previous:
        return [start_cell, end_cell]

    ordered_keys = []
    current_key = end_key
    while current_key is not None:
        ordered_keys.append(current_key)
        current_key = previous[current_key]
    ordered_keys.reverse()
    return [cell_lookup[key] for key in ordered_keys]


def _build_region_segment_points(region_id, region_name, cells, start_position, end_position, **extra):
    start_cell = _find_region_cell_for_position(cells, start_position)
    end_cell = _find_region_cell_for_position(cells, end_position)
    cell_path = _build_region_cell_path(cells, start_cell, end_cell)

    points = [_make_point(start_position.x, start_position.y, start_position.map_id, region_id=region_id, region_name=region_name, **extra)]
    for cell in cell_path:
        points.append(_make_point(
            cell['center_x'],
            cell['center_y'],
            cell['map_id'],
            grid_x=cell['grid_x'],
            grid_y=cell['grid_y'],
            region_id=region_id,
            region_name=region_name,
            **extra
        ))
    points.append(_make_point(end_position.x, end_position.y, end_position.map_id, region_id=region_id, region_name=region_name, **extra))
    return _merge_point_sequences(points)


def _build_graph_segment_points(graph, path):
    points = []
    for node in path:
        node_info = graph.get_node_info(node)
        if not node_info:
            continue
        points.append(_make_point(
            node_info.x,
            node_info.y,
            node_info.map_id,
            node_type=node[0],
            node_id=node[1]
        ))
    return points


def _build_augmented_graph_segment_points(graph, path, room_context, start_region_id=None, end_region_id=None):
    points = []
    entry_by_node = room_context.get('entry_by_node') or {}
    used_region_constraints = False

    for index, node in enumerate(path):
        node_info = graph.get_node_info(node)
        if not node_info:
            continue

        bound_entry = entry_by_node.get(node)
        is_start_node = index == 0
        is_end_node = index == len(path) - 1

        if (
            bound_entry and
            not is_start_node and
            not is_end_node and
            index > 0 and
            index < len(path) - 1
        ):
            prev_info = graph.get_node_info(path[index - 1])
            next_info = graph.get_node_info(path[index + 1])
            if prev_info and next_info and prev_info.map_id == node_info.map_id == next_info.map_id:
                region_points = _build_region_segment_points(
                    bound_entry['region_id'],
                    bound_entry['region_name'],
                    bound_entry['cells'],
                    Position(x=prev_info.x, y=prev_info.y, map_id=prev_info.map_id),
                    Position(x=next_info.x, y=next_info.y, map_id=next_info.map_id),
                    entry_door_id=bound_entry['door_id'],
                    entry_door_name=bound_entry['door_name']
                )
                points = _merge_point_sequences(points, region_points)
                used_region_constraints = True
                continue

        point = _make_point(
            node_info.x,
            node_info.y,
            node_info.map_id,
            node_type=node[0],
            node_id=node[1]
        )

        if bound_entry and ((is_start_node and bound_entry['region_id'] == start_region_id) or (is_end_node and bound_entry['region_id'] == end_region_id)):
            point['region_id'] = bound_entry['region_id']
            point['region_name'] = bound_entry['region_name']
            point['entry_door_id'] = bound_entry['door_id']
            point['entry_door_name'] = bound_entry['door_name']

        _append_unique_point(points, point)

    return points, used_region_constraints


def _build_steps_for_mixed_route(start_pos, end_pos, start_region_name, end_region_name, start_door_name=None, end_door_name=None, graph_distance=0.0, same_region=False):
    steps = []
    step_number = 1

    steps.append({
        'step_number': step_number,
        'floor': start_pos.map_id,
        'action': '出发',
        'location': f'{start_region_name}内起点' if start_region_name else '起点',
        'distance': 0.0
    })
    step_number += 1

    if same_region:
        steps.append({
            'step_number': step_number,
            'floor': end_pos.map_id,
            'action': '到达',
            'location': f'{end_region_name}内终点' if end_region_name else '终点',
            'distance': 0.0
        })
        return steps

    if start_region_name and start_door_name:
        steps.append({
            'step_number': step_number,
            'floor': start_pos.map_id,
            'action': '离开围栏',
            'location': f'{start_region_name} -> {start_door_name}',
            'distance': 0.0
        })
        step_number += 1

    if graph_distance > 0:
        steps.append({
            'step_number': step_number,
            'floor': start_pos.map_id,
            'action': '经过公共路径',
            'location': '门间连通图路径',
            'distance': round(graph_distance, 2)
        })
        step_number += 1

    if end_region_name and end_door_name:
        steps.append({
            'step_number': step_number,
            'floor': end_pos.map_id,
            'action': '进入围栏',
            'location': f'{end_door_name} -> {end_region_name}',
            'distance': 0.0
        })
        step_number += 1

    steps.append({
        'step_number': step_number,
        'floor': end_pos.map_id,
        'action': '到达',
        'location': f'{end_region_name}内终点' if end_region_name else '终点',
        'distance': 0.0
    })
    return steps


def _build_track_records(person_id, route_grid_centers, start_time, start_order):
    records = []
    for offset, grid_point in enumerate(route_grid_centers):
        records.append({
            'person_id': person_id,
            'order': start_order + offset,
            'x': grid_point['center_x'],
            'y': grid_point['center_y'],
            'map_id': grid_point['map_id'],
            'floor_id': grid_point['map_id'],
            'grid_x': grid_point['grid_x'],
            'grid_y': grid_point['grid_y'],
            'region_id': grid_point.get('region_id'),
            'region_name': grid_point.get('region_name'),
            'entry_door_id': grid_point.get('entry_door_id'),
            'entry_door_name': grid_point.get('entry_door_name'),
            'timestamp': (start_time + timedelta(seconds=offset)).isoformat()
        })
    return records


def _simulate_random_person_tracks(server, person_count, duration_seconds, start_time, seed=None, person_prefix='P'):
    if person_count <= 0:
        raise ValueError('person_count 必须大于 0')
    if duration_seconds <= 0:
        raise ValueError('duration_seconds 必须大于 0')

    rng = random.Random(seed)
    available_nodes = _get_simulation_nodes(server.graph)
    if not available_nodes:
        raise ValueError('连通图中没有可用节点')

    room_context = _load_room_simulation_context(server)
    use_room_constraints = room_context['available']
    people_tracks = []
    all_records = []

    for person_index in range(person_count):
        person_id = f'{person_prefix}{person_index + 1:03d}'
        current_node = rng.choice(room_context['entries'])['node'] if use_room_constraints else rng.choice(available_nodes)
        current_time = start_time
        current_order = 1
        person_records = []
        route_summaries = []

        while len(person_records) < duration_seconds:
            if use_room_constraints:
                route_result, entry = _choose_random_reachable_region_entry(
                    server.service,
                    room_context['entries'],
                    current_node,
                    rng
                )
                remaining_seconds = duration_seconds - len(person_records)
                route_grid_centers = _build_region_transition_points(route_result.path, room_context)

                if person_records and route_grid_centers:
                    last_record = person_records[-1]
                    first_grid = route_grid_centers[0]
                    if (
                        last_record.get('region_id') == first_grid.get('region_id') and
                        last_record['grid_x'] == first_grid['grid_x'] and
                        last_record['grid_y'] == first_grid['grid_y']
                    ):
                        route_grid_centers = route_grid_centers[1:]

                if not route_grid_centers:
                    current_node = entry['node']
                    continue

                route_grid_centers = route_grid_centers[:remaining_seconds]
                route_records = _build_track_records(
                    person_id,
                    route_grid_centers,
                    current_time,
                    current_order
                )
                person_records.extend(route_records)

                route_summaries.append({
                    'mode': 'region_door_transition',
                    'from_node': {
                        'node_type': current_node[0],
                        'node_id': current_node[1],
                        'map_id': current_node[2]
                    },
                    'entry_door': {
                        'door_id': entry['door_id'],
                        'door_name': entry['door_name'],
                        'map_id': entry['door_map_id']
                    },
                    'target_region': {
                        'region_id': entry['region_id'],
                        'region_name': entry['region_name']
                    },
                    'graph_nodes': len(route_result.path),
                    'graph_distance': route_result.distance,
                    'grid_points': len(route_grid_centers)
                })

                current_time = current_time + timedelta(seconds=len(route_grid_centers))
                current_order += len(route_grid_centers)
                current_node = entry['node']
                continue

            route_result, target_node = _choose_random_reachable_path(
                server.service,
                available_nodes,
                current_node,
                rng
            )
            path_nodes_with_coords = _build_path_nodes_with_coords(server.graph, route_result.path)
            route_grid_centers, _ = _build_path_grid_centers(path_nodes_with_coords)

            if person_records and route_grid_centers:
                last_record = person_records[-1]
                first_grid = route_grid_centers[0]
                if (
                    last_record['map_id'] == first_grid['map_id'] and
                    last_record['grid_x'] == first_grid['grid_x'] and
                    last_record['grid_y'] == first_grid['grid_y']
                ):
                    route_grid_centers = route_grid_centers[1:]

            if not route_grid_centers:
                current_node = target_node
                continue

            remaining_seconds = duration_seconds - len(person_records)
            route_slice = route_grid_centers[:remaining_seconds]
            route_records = _build_track_records(
                person_id,
                route_slice,
                current_time,
                current_order
            )
            person_records.extend(route_records)

            route_summaries.append({
                'from_node': {
                    'node_type': current_node[0],
                    'node_id': current_node[1],
                    'map_id': current_node[2]
                },
                'to_node': {
                    'node_type': target_node[0],
                    'node_id': target_node[1],
                    'map_id': target_node[2]
                },
                'grid_points': len(route_slice)
            })

            current_time = current_time + timedelta(seconds=len(route_slice))
            current_order += len(route_slice)
            current_node = target_node

        people_tracks.append({
            'person_id': person_id,
            'record_count': len(person_records),
            'records': person_records,
            'routes': route_summaries
        })
        all_records.extend(person_records)

    return {
        'success': True,
        'person_count': person_count,
        'duration_seconds': duration_seconds,
        'start_time': start_time.isoformat(),
        'grid_interval_seconds': 1,
        'constraint_mode': 'region_door_nearest_cells' if use_room_constraints else 'graph_grid_centers',
        'region_constraints_enabled': use_room_constraints,
        'records': all_records,
        'people': people_tracks
    }


def _plan_mixed_route(server, start_pos, end_pos):
    room_context = _load_room_simulation_context(server)
    if not room_context.get('available'):
        return None

    start_region_id = _resolve_region_for_position(room_context, start_pos)
    end_region_id = _resolve_region_for_position(room_context, end_pos)

    start_region_name = start_region_id
    end_region_name = end_region_id
    if start_region_id:
        region_entries = room_context.get('entries_by_region', {}).get(start_region_id) or []
        if region_entries:
            start_region_name = region_entries[0]['region_name']
    if end_region_id:
        region_entries = room_context.get('entries_by_region', {}).get(end_region_id) or []
        if region_entries:
            end_region_name = region_entries[0]['region_name']

    if start_region_id and end_region_id and start_region_id == end_region_id:
        region_cells = room_context['region_cells'].get(start_region_id) or []
        if not region_cells:
            return {
                'success': False,
                'error': '起点和终点位于同一围栏，但围栏网格数据不可用'
            }
        path_points = _build_region_segment_points(start_region_id, start_region_name, region_cells, start_pos, end_pos)
        steps = _build_steps_for_mixed_route(start_pos, end_pos, start_region_name, end_region_name, same_region=True)
        return _build_custom_response(path_points, steps)

    start_node = server.service._position_to_node(start_pos)
    end_node = server.service._position_to_node(end_pos)

    if start_region_id and not room_context.get('entries_by_region', {}).get(start_region_id):
        return {
            'success': False,
            'error': f'起点所在围栏 {start_region_name} 未绑定可用门口'
        }
    if end_region_id and not room_context.get('entries_by_region', {}).get(end_region_id):
        return {
            'success': False,
            'error': f'终点所在围栏 {end_region_name} 未绑定可用门口'
        }
    if not start_region_id and start_node is None:
        return {
            'success': False,
            'error': '起点附近未找到可用图节点'
        }
    if not end_region_id and end_node is None:
        return {
            'success': False,
            'error': '终点附近未找到可用图节点'
        }

    start_entries = room_context.get('entries_by_region', {}).get(start_region_id) if start_region_id else [None]
    end_entries = room_context.get('entries_by_region', {}).get(end_region_id) if end_region_id else [None]

    best_candidate = None
    for start_entry in start_entries:
        graph_start_node = start_entry['node'] if start_entry else start_node
        for end_entry in end_entries:
            graph_end_node = end_entry['node'] if end_entry else end_node
            if graph_start_node is None or graph_end_node is None:
                continue

            graph_result = server.service.algorithm.find_shortest_path(graph_start_node, graph_end_node)
            if not graph_result.success or not graph_result.path:
                continue

            segment_points = []
            if start_entry:
                region_cells = room_context['region_cells'][start_entry['region_id']]
                door_position = Position(x=start_entry['door_x'], y=start_entry['door_y'], map_id=start_entry['door_map_id'])
                segment_points = _merge_point_sequences(
                    segment_points,
                    _build_region_segment_points(
                        start_entry['region_id'],
                        start_entry['region_name'],
                        region_cells,
                        start_pos,
                        door_position,
                        entry_door_id=start_entry['door_id'],
                        entry_door_name=start_entry['door_name']
                    )
                )
            else:
                _append_unique_point(segment_points, _make_point(start_pos.x, start_pos.y, start_pos.map_id))

            graph_points, graph_uses_constraints = _build_augmented_graph_segment_points(
                server.graph,
                graph_result.path,
                room_context,
                start_region_id=start_region_id,
                end_region_id=end_region_id
            )

            if not (start_entry or end_entry or graph_uses_constraints):
                continue

            segment_points = _merge_point_sequences(segment_points, graph_points)

            if end_entry:
                region_cells = room_context['region_cells'][end_entry['region_id']]
                door_position = Position(x=end_entry['door_x'], y=end_entry['door_y'], map_id=end_entry['door_map_id'])
                segment_points = _merge_point_sequences(
                    segment_points,
                    _build_region_segment_points(
                        end_entry['region_id'],
                        end_entry['region_name'],
                        region_cells,
                        door_position,
                        end_pos,
                        entry_door_id=end_entry['door_id'],
                        entry_door_name=end_entry['door_name']
                    )
                )
            else:
                _append_unique_point(segment_points, _make_point(end_pos.x, end_pos.y, end_pos.map_id))

            total_distance = _calculate_polyline_distance(segment_points)
            if best_candidate is None or total_distance < best_candidate['total_distance']:
                best_candidate = {
                    'path_points': segment_points,
                    'total_distance': total_distance,
                    'graph_distance': graph_result.distance,
                    'start_entry': start_entry,
                    'end_entry': end_entry
                }

    if best_candidate is None:
        if not start_region_id and not end_region_id:
            return None
        return {
            'success': False,
            'error': '未找到满足围栏约束的可达路径'
        }

    steps = _build_steps_for_mixed_route(
        start_pos,
        end_pos,
        start_region_name,
        end_region_name,
        start_door_name=best_candidate['start_entry']['door_name'] if best_candidate['start_entry'] else None,
        end_door_name=best_candidate['end_entry']['door_name'] if best_candidate['end_entry'] else None,
        graph_distance=best_candidate['graph_distance']
    )
    return _build_custom_response(best_candidate['path_points'], steps)


class PathPlanningServer:
    """路径规划服务器类"""
    
    def __init__(self):
        """初始化服务器，加载数据并构建图"""
        logger.info("=" * 80)
        logger.info("初始化路径规划服务器...")
        logger.info("=" * 80)
        
        try:
            # 1. 加载数据
            logger.info("步骤1: 加载数据文件...")
            loader = DataLoader()
            
            self.maps = loader.load_maps('database_export/maps_data.txt')
            self.doors = loader.load_doors('database_export/doors_data.txt')
            self.stairways = loader.load_stairways('database_export/stairways_data.txt')
            self.edges = loader.load_graph_edges('database_export/graph_edges_data.txt')
            self.rfid_devices = loader.load_rfid_devices('database_export/rfid_devices_data.txt')
            
            logger.info(f"✓ 数据加载完成：{len(self.maps)}个地图，{len(self.doors)}个门，"
                       f"{len(self.stairways)}个楼梯，{len(self.edges)}条边，"
                       f"{len(self.rfid_devices)}个RFID设备")
            
            # 2. 构建图
            logger.info("步骤2: 构建多层图...")
            builder = GraphBuilder(self.doors, self.stairways, self.edges)
            self.graph = builder.build_graph()
            logger.info(f"✓ 图构建完成：{self.graph.get_node_count()}个节点，"
                       f"{self.graph.get_edge_count()}条边")
            
            # 3. 创建服务
            logger.info("步骤3: 初始化路径规划服务...")
            self.service = PathPlanningService(self.graph, self.rfid_devices)
            self.formatter = PathFormatter(self.graph)
            logger.info("✓ 服务初始化完成")
            
            logger.info("=" * 80)
            logger.info("路径规划服务器启动成功！")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"服务器初始化失败: {e}")
            traceback.print_exc()
            raise
    
    def reload_data(self):
        """重新加载数据（热加载，无需重启服务）"""
        logger.info("=" * 80)
        logger.info("开始重新加载数据...")
        logger.info("=" * 80)
        
        try:
            self.__init__()
            logger.info("数据重新加载成功！")
            return True
        except Exception as e:
            logger.error(f"数据重新加载失败: {e}")
            traceback.print_exc()
            return False
    
    def plan_path(self, start_x: float, start_y: float, start_map: str,
                  end_x: float, end_y: float, end_map: str):
        """
        规划路径
        
        Args:
            start_x: 起点X坐标
            start_y: 起点Y坐标
            start_map: 起点楼层ID
            end_x: 终点X坐标
            end_y: 终点Y坐标
            end_map: 终点楼层ID
            
        Returns:
            路径规划结果
        """
        try:
            # 创建位置对象
            start_pos = Position(x=start_x, y=start_y, map_id=start_map)
            end_pos = Position(x=end_x, y=end_y, map_id=end_map)
            
            # 执行路径规划
            mixed_result = _plan_mixed_route(self, start_pos, end_pos)
            if mixed_result is not None:
                return mixed_result

            result = self.service.plan_path(start_pos, end_pos)
            
            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message
                }
            
            # 格式化路径描述
            description = self.formatter.format_path(result.path)
            return _build_success_response(self.graph, result, description)
            
            # 构建返回结果，添加节点坐标信息
            path_nodes_with_coords = []
            for node in result.path:
                node_info = self.graph.get_node_info(node)
                path_nodes_with_coords.append({
                    'node_type': node[0],
                    'node_id': node[1],
                    'map_id': node[2],
                    'x': node_info.x if node_info else 0,
                    'y': node_info.y if node_info else 0
                })
            
            return {
                'success': True,
                'distance': result.distance,
                'total_distance': description.total_distance,
                'floors': description.floors,
                'steps': [
                    {
                        'step_number': step.step_number,
                        'floor': step.floor,
                        'action': step.action,
                        'location': step.location,
                        'distance': step.distance
                    }
                    for step in description.steps
                ],
                'path_nodes': path_nodes_with_coords
            }
            
        except Exception as e:
            logger.error(f"路径规划失败: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def plan_path_from_rfid(self, rfid_id: str, end_x: float, end_y: float, end_map: str):
        """
        从RFID设备位置规划路径
        
        Args:
            rfid_id: RFID设备ID
            end_x: 终点X坐标
            end_y: 终点Y坐标
            end_map: 终点楼层ID
            
        Returns:
            路径规划结果
        """
        try:
            # 创建终点位置对象
            end_pos = Position(x=end_x, y=end_y, map_id=end_map)
            
            # 执行路径规划
            result = self.service.plan_path_from_rfid(rfid_id, end_pos)
            
            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message
                }
            
            # 格式化路径描述
            description = self.formatter.format_path(result.path)
            return _build_success_response(self.graph, result, description)
            
            # 构建返回结果
            return {
                'success': True,
                'distance': result.distance,
                'total_distance': description.total_distance,
                'floors': description.floors,
                'steps': [
                    {
                        'step_number': step.step_number,
                        'floor': step.floor,
                        'action': step.action,
                        'location': step.location,
                        'distance': step.distance
                    }
                    for step in description.steps
                ]
            }
            
        except Exception as e:
            logger.error(f"路径规划失败: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }


# ==================== HTTP API 接口 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': 'path_planning',
        'nodes': path_service.graph.get_node_count() if path_service else 0,
        'edges': path_service.graph.get_edge_count() if path_service else 0
    })


@app.route('/api/plan_path', methods=['POST'])
def api_plan_path():
    """
    路径规划接口
    
    请求体示例:
    {
        "start": {
            "x": 22.4460,
            "y": 13.4433,
            "map_id": "floor1"
        },
        "end": {
            "x": 21.1138,
            "y": 12.9260,
            "map_id": "floor2"
        }
    }
    """
    try:
        data = request.get_json()
        
        # 验证参数
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：start 和 end'
            }), 400
        
        start = data['start']
        end = data['end']
        
        # 验证坐标
        required_fields = ['x', 'y', 'map_id']
        for field in required_fields:
            if field not in start or field not in end:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要字段：{field}'
                }), 400
        
        # 执行路径规划
        result = path_service.plan_path(
            start_x=float(start['x']),
            start_y=float(start['y']),
            start_map=start['map_id'],
            end_x=float(end['x']),
            end_y=float(end['y']),
            end_map=end['map_id']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plan_multi_waypoint_path', methods=['POST'])
def api_plan_multi_waypoint_path():
    """
    多点路径规划接口
    
    请求体示例:
    {
        "start": {
            "x": 22.4460,
            "y": 13.4433,
            "map_id": "floor1"
        },
        "waypoints": [
            {
                "x": 22.1582,
                "y": 6.4752,
                "map_id": "floor1"
            },
            {
                "x": 20.2682,
                "y": 7.7750,
                "map_id": "floor2"
            }
        ],
        "end": {
            "x": 21.1138,
            "y": 12.9260,
            "map_id": "floor2"
        }
    }
    """
    try:
        data = request.get_json()
        
        # 验证参数
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：start 和 end'
            }), 400
        
        start = data['start']
        end = data['end']
        waypoints_data = data.get('waypoints', [])
        
        # 验证坐标
        required_fields = ['x', 'y', 'map_id']
        for field in required_fields:
            if field not in start or field not in end:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要字段：{field}'
                }), 400
        
        # 验证途经点
        for i, wp in enumerate(waypoints_data):
            for field in required_fields:
                if field not in wp:
                    return jsonify({
                        'success': False,
                        'error': f'途经点{i+1}缺少必要字段：{field}'
                    }), 400
        
        # 创建位置对象
        from models import Position
        start_pos = Position(x=float(start['x']), y=float(start['y']), map_id=start['map_id'])
        end_pos = Position(x=float(end['x']), y=float(end['y']), map_id=end['map_id'])
        waypoints = [Position(x=float(wp['x']), y=float(wp['y']), map_id=wp['map_id']) 
                    for wp in waypoints_data]
        
        # 执行路径规划
        result = path_service.service.plan_multi_waypoint_path(start_pos, waypoints, end_pos)
        
        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error_message
            }), 400
        
        # 格式化路径描述
        description = path_formatter.format_path(result.path)
        return jsonify(_build_success_response(path_service.graph, result, description)), 200
        
        # 构建返回结果，添加节点坐标信息
        path_nodes_with_coords = []
        for node in result.path:
            node_info = path_service.graph.get_node_info(node)
            path_nodes_with_coords.append({
                'node_type': node[0],
                'node_id': node[1],
                'map_id': node[2],
                'x': node_info.x if node_info else 0,
                'y': node_info.y if node_info else 0
            })
        
        # 构建返回结果
        response_data = {
            'success': True,
            'distance': result.distance,
            'total_distance': description.total_distance,
            'floors': description.floors,
            'steps': [
                {
                    'step_number': step.step_number,
                    'floor': step.floor,
                    'action': step.action,
                    'location': step.location,
                    'distance': step.distance
                }
                for step in description.steps
            ],
            'path_nodes': path_nodes_with_coords
        }
        
        return jsonify(response_data), 200
            
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/plan_path_from_rfid', methods=['POST'])
def api_plan_path_from_rfid():
    """
    从RFID设备位置规划路径接口
    
    请求体示例:
    {
        "rfid_id": "RFID_001",
        "end": {
            "x": 21.1138,
            "y": 12.9260,
            "map_id": "floor2"
        }
    }
    """
    try:
        data = request.get_json()
        
        # 验证参数
        if not data or 'rfid_id' not in data or 'end' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：rfid_id 和 end'
            }), 400
        
        end = data['end']
        
        # 验证坐标
        required_fields = ['x', 'y', 'map_id']
        for field in required_fields:
            if field not in end:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要字段：{field}'
                }), 400
        
        # 执行路径规划
        result = path_service.plan_path_from_rfid(
            rfid_id=data['rfid_id'],
            end_x=float(end['x']),
            end_y=float(end['y']),
            end_map=end['map_id']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/simulate_person_tracks', methods=['POST'])
def api_simulate_person_tracks():
    """
    随机生成人员轨迹。

    请求体示例:
    {
        "person_count": 3,
        "duration_seconds": 120,
        "start_time": "2026-04-23T10:00:00",
        "seed": 42,
        "person_prefix": "PERSON_"
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        person_count = int(data.get('person_count', 1))
        duration_seconds = int(data.get('duration_seconds', 60))
        start_time = _parse_simulation_start_time(data.get('start_time'))
        seed = data.get('seed')
        person_prefix = str(data.get('person_prefix', 'P'))

        result = _simulate_random_person_tracks(
            path_service,
            person_count=person_count,
            duration_seconds=duration_seconds,
            start_time=start_time,
            seed=seed,
            person_prefix=person_prefix
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"人员轨迹仿真失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reload', methods=['POST'])
def api_reload_data():
    """
    重新加载数据接口（热加载）
    
    使用场景：数据库数据更新后，重新导出txt文件，然后调用此接口刷新内存数据
    """
    try:
        success = path_service.reload_data()
        
        if success:
            return jsonify({
                'success': True,
                'message': '数据重新加载成功',
                'nodes': path_service.graph.get_node_count(),
                'edges': path_service.graph.get_edge_count()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据重新加载失败'
            }), 500
            
    except Exception as e:
        logger.error(f"重新加载数据失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """获取服务统计信息"""
    try:
        return jsonify({
            'success': True,
            'stats': {
                'maps': len(path_service.maps),
                'doors': len(path_service.doors),
                'stairways': len(path_service.stairways),
                'edges': len(path_service.edges),
                'rfid_devices': len(path_service.rfid_devices),
                'graph_nodes': path_service.graph.get_node_count(),
                'graph_edges': path_service.graph.get_edge_count()
            }
        }), 200
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def main():
    """主函数"""
    global path_service, path_formatter
    
    # 初始化服务
    path_service = PathPlanningServer()
    path_formatter = path_service.formatter
    
    # 启动Flask服务器
    logger.info("\n启动HTTP服务器...")
    logger.info("监听地址: http://0.0.0.0:5000")
    logger.info("API文档:")
    logger.info("  - GET  /health                    健康检查")
    logger.info("  - POST /api/plan_path             路径规划")
    logger.info("  - POST /api/plan_path_from_rfid   从RFID规划路径")
    logger.info("  - POST /api/reload                重新加载数据")
    logger.info("  - GET  /api/stats                 获取统计信息")
    logger.info("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()
