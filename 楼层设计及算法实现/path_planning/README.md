# 船舶多层路径规划系统

船舶多层路径规划系统是一个基于图论的路径搜索系统，用于在船舶的多层结构中计算最优路径。

## 功能特性

- ✅ 同层路径规划
- ✅ 跨楼层路径规划
- ✅ 多点顺序路径规划
- ✅ RFID 设备定位
- ✅ 人类可读的路径描述
- ✅ 图连通性验证

## 系统架构

```
API Layer (接口层)
    ↓
Service Layer (服务层)
    ↓
Core Layer (核心层)
    ↓
Data Layer (数据层)
```

## 快速开始

### 1. 准备数据文件

确保以下数据文件存在于 `path_planning/database_export/` 目录：

- `maps_data.txt` - 地图数据
- `doors_data.txt` - 门节点数据
- `stairways_data.txt` - 楼梯数据
- `graph_edges_data.txt` - 图边数据
- `rfid_devices_data.txt` - RFID 设备数据

### 2. 基本使用示例

```python
from path_planning.config import setup_logging, MAPS_FILE, DOORS_FILE, STAIRWAYS_FILE, GRAPH_EDGES_FILE, RFID_DEVICES_FILE
from path_planning.data_loader import DataLoader
from path_planning.graph_builder import GraphBuilder
from path_planning.path_planning_service import PathPlanningService
from path_planning.path_formatter import PathFormatter
from path_planning.api import PathPlanningAPI

# 设置日志
setup_logging()

# 1. 加载数据
loader = DataLoader()
maps = loader.load_maps(MAPS_FILE)
doors = loader.load_doors(DOORS_FILE)
stairways = loader.load_stairways(STAIRWAYS_FILE)
edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)

# 2. 构建图
builder = GraphBuilder(doors, stairways, edges)
graph = builder.build_graph()

# 3. 验证连通性（可选）
report = builder.validate_connectivity()
print(f"图连通性：{'通过' if report.is_connected else '失败'}")

# 4. 创建服务和 API
service = PathPlanningService(graph, rfid_devices)
formatter = PathFormatter(graph)
api = PathPlanningAPI(service, formatter)

# 5. 规划路径
result = api.plan_path(
    start_x=21.3,
    start_y=8.9,
    start_map_id='floor1',
    end_x=22.4,
    end_y=4.0,
    end_map_id='floor1'
)

# 6. 输出结果
if result['success']:
    print(f"总距离：{result['distance']:.2f} 米")
    print(f"经过楼层：{' -> '.join(result['description']['floors'])}")
    for step in result['description']['steps']:
        print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']}")
else:
    print(f"路径规划失败：{result['error_message']}")
```

### 3. 多点路径规划

```python
result = api.plan_multi_waypoint_path(
    start_x=21.3,
    start_y=8.9,
    start_map_id='floor1',
    waypoints=[
        {'x': 20.3, 'y': 7.8, 'map_id': 'floor2'},
        {'x': 22.9, 'y': 8.9, 'map_id': 'floor3'}
    ],
    end_x=20.9,
    end_y=10.9,
    end_map_id='floor5'
)
```

### 4. RFID 定位路径规划

```python
from path_planning.models import Position

end_pos = Position(x=20.9, y=10.9, map_id='floor5')
result = service.plan_path_from_rfid('R33', end_pos)

if result.success:
    description = formatter.format_path(result.path)
    print(formatter.format_path_to_string(description))
```

## API 接口

### plan_path()

规划单点路径。

**参数：**
- `start_x` (float): 起点 X 坐标
- `start_y` (float): 起点 Y 坐标
- `start_map_id` (str): 起点楼层 ID
- `end_x` (float): 终点 X 坐标
- `end_y` (float): 终点 Y 坐标
- `end_map_id` (str): 终点楼层 ID

**返回：**
```python
{
    'success': bool,
    'path': List[List],  # 节点序列
    'distance': float,   # 总距离（米）
    'description': {
        'total_distance': float,
        'floors': List[str],
        'steps': List[Dict]
    },
    'error_code': str,      # 仅失败时
    'error_message': str    # 仅失败时
}
```

### plan_multi_waypoint_path()

规划多点顺序路径。

**参数：**
- `start_x`, `start_y`, `start_map_id`: 起点坐标
- `waypoints`: 途经点列表 `[{'x': float, 'y': float, 'map_id': str}, ...]`
- `end_x`, `end_y`, `end_map_id`: 终点坐标

**返回：** 同 `plan_path()`

### get_node_info()

获取节点信息。

**参数：**
- `node_type` (int): 节点类型（1=门，2=楼梯）
- `node_id` (int|str): 节点 ID
- `map_id` (str): 楼层 ID

**返回：**
```python
{
    'success': bool,
    'node_info': {
        'node': List,
        'name': str,
        'node_type': int,
        'map_id': str,
        'x': float,
        'y': float
    }
}
```

## 数据文件格式

### maps_data.txt

制表符分隔，包含以下字段：
```
map_id	region_name	image_path	ship_length_m	ship_width_m	image_width_px	image_height_px
```

### doors_data.txt

制表符分隔，包含以下字段：
```
id	room_name	room_type	map_id	x	y	description	is_active	create_time	update_time
```

- `room_type`: 1=房间, 2=楼道, 3=出入口

### stairways_data.txt

制表符分隔，包含以下字段：
```
id	stairway_id	stairway_name	map_id	upper_map_id	lower_map_id	x	y	description	is_active	create_time	update_time
```

- `upper_map_id`: 可以上到的楼层（NULL 表示无）
- `lower_map_id`: 可以下到的楼层（NULL 表示无）

### graph_edges_data.txt

制表符分隔，包含以下字段：
```
id	node_a_type	node_a_id	node_b_type	node_b_id	weight	create_time	update_time
```

- `node_a_type`, `node_b_type`: 1=门, 2=楼梯
- `weight`: 距离（米）

### rfid_devices_data.txt

制表符分隔，包含以下字段：
```
id	device_name	map_id	x	y	stairway_id	door_id	description	is_active	create_time	update_time
```

## 运行测试

```bash
python path_planning/test_integration.py
```

测试场景包括：
1. 同层路径（floor1 门46 -> 门3）
2. 跨一层路径（floor1 门46 -> floor2 门51）
3. 跨多层路径（floor1 门46 -> floor5 门45）
4. 多点路径（floor1 门46 -> floor2 门16 -> floor3 门53）
5. RFID 定位（RFID R33 -> 门45）

## 配置

配置文件：`path_planning/config.py`

主要配置项：
- `CROSS_FLOOR_WEIGHT = 10.0` - 跨楼层边的权重（米）
- `MAX_NEAREST_NODE_DISTANCE = 50.0` - 最近节点的最大距离（米）
- `PATH_CALCULATION_TIMEOUT = 5.0` - 路径计算超时时间（秒）

## 错误码

- `INVALID_PARAMETER` - 参数验证错误
- `PATH_NOT_FOUND` - 路径不可达
- `NODE_NOT_FOUND` - 节点不存在

## 许可证

MIT License
