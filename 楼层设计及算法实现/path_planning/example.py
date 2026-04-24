"""
使用示例脚本
演示如何使用船舶路径规划系统
"""

from path_planning.config import setup_logging, MAPS_FILE, DOORS_FILE, STAIRWAYS_FILE, GRAPH_EDGES_FILE, RFID_DEVICES_FILE
from path_planning.data_loader import DataLoader
from path_planning.graph_builder import GraphBuilder
from path_planning.path_planning_service import PathPlanningService
from path_planning.path_formatter import PathFormatter
from path_planning.api import PathPlanningAPI
from path_planning.models import Position

# 设置日志
setup_logging()


def main():
    print("="*80)
    print("船舶多层路径规划系统 - 使用示例")
    print("="*80)
    
    # 1. 加载数据
    print("\n1. 加载数据...")
    loader = DataLoader()
    maps = loader.load_maps(MAPS_FILE)
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    print(f"   - 加载了 {len(maps)} 个地图")
    print(f"   - 加载了 {len(doors)} 个门节点")
    print(f"   - 加载了 {len(stairways)} 个楼梯")
    print(f"   - 加载了 {len(edges)} 条边")
    print(f"   - 加载了 {len(rfid_devices)} 个 RFID 设备")
    
    # 2. 构建图
    print("\n2. 构建多层图...")
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    print(f"   - 图包含 {graph.get_node_count()} 个节点")
    print(f"   - 图包含 {graph.get_edge_count()} 条边")
    
    # 3. 验证连通性
    print("\n3. 验证图连通性...")
    report = builder.validate_connectivity()
    if report.is_connected:
        print("   ✓ 图连通性验证通过")
    else:
        print(f"   ✗ 图不连通，存在 {report.num_components} 个连通分量")
        for warning in report.warnings:
            print(f"     - {warning}")
    
    # 4. 创建服务和 API
    print("\n4. 创建路径规划服务...")
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    api = PathPlanningAPI(service, formatter)
    print("   ✓ 服务创建完成")
    
    # 5. 示例：同层路径规划
    print("\n5. 示例：同层路径规划（A甲板楼道 -> 甲板更衣室）")
    result = api.plan_path(
        start_x=21.3,
        start_y=8.9,
        start_map_id='floor1',
        end_x=22.4,
        end_y=4.0,
        end_map_id='floor1'
    )
    
    if result['success']:
        print(f"   ✓ 路径规划成功")
        print(f"   - 总距离：{result['distance']:.2f} 米")
        print(f"   - 经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"   - 路径步骤：{len(result['description']['steps'])} 步")
    else:
        print(f"   ✗ 路径规划失败：{result['error_message']}")
    
    # 6. 示例：跨层路径规划
    print("\n6. 示例：跨层路径规划（A甲板 -> 桥楼甲板）")
    result = api.plan_path(
        start_x=21.3,
        start_y=8.9,
        start_map_id='floor1',
        end_x=20.9,
        end_y=10.9,
        end_map_id='floor5'
    )
    
    if result['success']:
        print(f"   ✓ 路径规划成功")
        print(f"   - 总距离：{result['distance']:.2f} 米")
        print(f"   - 经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"   - 路径步骤：{len(result['description']['steps'])} 步")
    else:
        print(f"   ✗ 路径规划失败：{result['error_message']}")
    
    # 7. 示例：多点路径规划
    print("\n7. 示例：多点路径规划（A甲板 -> B甲板厨房 -> C甲板楼道）")
    result = api.plan_multi_waypoint_path(
        start_x=21.3,
        start_y=8.9,
        start_map_id='floor1',
        waypoints=[
            {'x': 20.3, 'y': 7.8, 'map_id': 'floor2'}
        ],
        end_x=22.9,
        end_y=8.9,
        end_map_id='floor3'
    )
    
    if result['success']:
        print(f"   ✓ 路径规划成功")
        print(f"   - 总距离：{result['distance']:.2f} 米")
        print(f"   - 经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"   - 路径步骤：{len(result['description']['steps'])} 步")
    else:
        print(f"   ✗ 路径规划失败：{result['error_message']}")
    
    # 8. 示例：RFID 定位路径规划
    print("\n8. 示例：RFID 定位路径规划（RFID R33 -> 桥楼甲板驾驶室）")
    end_pos = Position(x=20.9, y=10.9, map_id='floor5')
    result_obj = service.plan_path_from_rfid('R33', end_pos)
    
    if result_obj.success:
        description = formatter.format_path(result_obj.path)
        print(f"   ✓ 路径规划成功")
        print(f"   - 总距离：{result_obj.distance:.2f} 米")
        print(f"   - 经过楼层：{' -> '.join(description.floors)}")
        print(f"   - 路径步骤：{len(description.steps)} 步")
    else:
        print(f"   ✗ 路径规划失败：{result_obj.error_message}")
    
    print("\n" + "="*80)
    print("示例运行完成！")
    print("="*80)


if __name__ == "__main__":
    main()
