"""
集成测试和端到端测试
测试完整的路径规划流程
"""

import logging
from config import setup_logging, MAPS_FILE, DOORS_FILE, STAIRWAYS_FILE, GRAPH_EDGES_FILE, RFID_DEVICES_FILE
from data_loader import DataLoader
from graph_builder import GraphBuilder
from path_planning_service import PathPlanningService
from path_formatter import PathFormatter
from api import PathPlanningAPI
from models import Position

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def test_scenario_1_same_floor():
    """测试场景1：同层路径（floor1 门46 -> 门3）"""
    print("\n" + "="*80)
    print("测试场景1：同层路径（floor1 门46 -> 门3）")
    print("="*80)
    
    # 加载数据
    loader = DataLoader()
    maps = loader.load_maps(MAPS_FILE)
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    # 构建图
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    
    # 验证连通性
    report = builder.validate_connectivity()
    print(f"\n连通性验证：{'通过' if report.is_connected else '失败'}")
    
    # 创建服务和 API
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    api = PathPlanningAPI(service, formatter)
    
    # 查找门46和门3的坐标
    door_46 = next((d for d in doors if d.id == 46), None)
    door_3 = next((d for d in doors if d.id == 3), None)
    
    if not door_46 or not door_3:
        print("错误：找不到门46或门3")
        return
    
    # 规划路径
    result = api.plan_path(
        start_x=door_46.x,
        start_y=door_46.y,
        start_map_id=door_46.map_id,
        end_x=door_3.x,
        end_y=door_3.y,
        end_map_id=door_3.map_id
    )
    
    # 输出结果
    if result['success']:
        print(f"\n路径规划成功！")
        print(f"总距离：{result['distance']:.2f} 米")
        print(f"经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"\n详细路径：")
        for step in result['description']['steps']:
            if step['distance'] > 0:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']} ({step['distance']:.2f}米)")
            else:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']}")
    else:
        print(f"\n路径规划失败：{result['error_message']}")


def test_scenario_2_cross_one_floor():
    """测试场景2：跨一层路径（floor1 门46 -> floor2 门51）"""
    print("\n" + "="*80)
    print("测试场景2：跨一层路径（floor1 门46 -> floor2 门51）")
    print("="*80)
    
    # 加载数据
    loader = DataLoader()
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    # 构建图
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    
    # 创建服务和 API
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    api = PathPlanningAPI(service, formatter)
    
    # 查找门46和门51的坐标
    door_46 = next((d for d in doors if d.id == 46), None)
    door_51 = next((d for d in doors if d.id == 51), None)
    
    if not door_46 or not door_51:
        print("错误：找不到门46或门51")
        return
    
    # 规划路径
    result = api.plan_path(
        start_x=door_46.x,
        start_y=door_46.y,
        start_map_id=door_46.map_id,
        end_x=door_51.x,
        end_y=door_51.y,
        end_map_id=door_51.map_id
    )
    
    # 输出结果
    if result['success']:
        print(f"\n路径规划成功！")
        print(f"总距离：{result['distance']:.2f} 米")
        print(f"经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"\n详细路径：")
        for step in result['description']['steps']:
            if step['distance'] > 0:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']} ({step['distance']:.2f}米)")
            else:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']}")
    else:
        print(f"\n路径规划失败：{result['error_message']}")


def test_scenario_3_cross_multiple_floors():
    """测试场景3：跨多层路径（floor1 门46 -> floor5 门45）"""
    print("\n" + "="*80)
    print("测试场景3：跨多层路径（floor1 门46 -> floor5 门45）")
    print("="*80)
    
    # 加载数据
    loader = DataLoader()
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    # 构建图
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    
    # 创建服务和 API
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    api = PathPlanningAPI(service, formatter)
    
    # 查找门46和门45的坐标
    door_46 = next((d for d in doors if d.id == 46), None)
    door_45 = next((d for d in doors if d.id == 45), None)
    
    if not door_46 or not door_45:
        print("错误：找不到门46或门45")
        return
    
    # 规划路径
    result = api.plan_path(
        start_x=door_46.x,
        start_y=door_46.y,
        start_map_id=door_46.map_id,
        end_x=door_45.x,
        end_y=door_45.y,
        end_map_id=door_45.map_id
    )
    
    # 输出结果
    if result['success']:
        print(f"\n路径规划成功！")
        print(f"总距离：{result['distance']:.2f} 米")
        print(f"经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"\n详细路径：")
        for step in result['description']['steps']:
            if step['distance'] > 0:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']} ({step['distance']:.2f}米)")
            else:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']}")
    else:
        print(f"\n路径规划失败：{result['error_message']}")


def test_scenario_4_multi_waypoint():
    """测试场景4：多点路径（floor1 门46 -> floor2 门16 -> floor3 门53）"""
    print("\n" + "="*80)
    print("测试场景4：多点路径（floor1 门46 -> floor2 门16 -> floor3 门53）")
    print("="*80)
    
    # 加载数据
    loader = DataLoader()
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    # 构建图
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    
    # 创建服务和 API
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    api = PathPlanningAPI(service, formatter)
    
    # 查找门的坐标
    door_46 = next((d for d in doors if d.id == 46), None)
    door_16 = next((d for d in doors if d.id == 16), None)
    door_53 = next((d for d in doors if d.id == 53), None)
    
    if not door_46 or not door_16 or not door_53:
        print("错误：找不到指定的门")
        return
    
    # 规划路径
    result = api.plan_multi_waypoint_path(
        start_x=door_46.x,
        start_y=door_46.y,
        start_map_id=door_46.map_id,
        waypoints=[
            {'x': door_16.x, 'y': door_16.y, 'map_id': door_16.map_id}
        ],
        end_x=door_53.x,
        end_y=door_53.y,
        end_map_id=door_53.map_id
    )
    
    # 输出结果
    if result['success']:
        print(f"\n路径规划成功！")
        print(f"总距离：{result['distance']:.2f} 米")
        print(f"经过楼层：{' -> '.join(result['description']['floors'])}")
        print(f"\n详细路径：")
        for step in result['description']['steps']:
            if step['distance'] > 0:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']} ({step['distance']:.2f}米)")
            else:
                print(f"{step['step_number']}. [{step['floor']}] {step['action']} {step['location']}")
    else:
        print(f"\n路径规划失败：{result['error_message']}")


def test_scenario_5_rfid():
    """测试场景5：RFID 定位（RFID R33 -> 门45）"""
    print("\n" + "="*80)
    print("测试场景5：RFID 定位（RFID R33 -> 门45）")
    print("="*80)
    
    # 加载数据
    loader = DataLoader()
    doors = loader.load_doors(DOORS_FILE)
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    rfid_devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    # 构建图
    builder = GraphBuilder(doors, stairways, edges)
    graph = builder.build_graph()
    
    # 创建服务
    service = PathPlanningService(graph, rfid_devices)
    formatter = PathFormatter(graph)
    
    # 查找门45的坐标
    door_45 = next((d for d in doors if d.id == 45), None)
    
    if not door_45:
        print("错误：找不到门45")
        return
    
    # 规划路径
    end_pos = Position(x=door_45.x, y=door_45.y, map_id=door_45.map_id)
    result = service.plan_path_from_rfid('R33', end_pos)
    
    # 输出结果
    if result.success:
        description = formatter.format_path(result.path)
        print(f"\n路径规划成功！")
        print(f"总距离：{result.distance:.2f} 米")
        print(f"经过楼层：{' -> '.join(description.floors)}")
        print(f"\n详细路径：")
        for step in description.steps:
            if step.distance > 0:
                print(f"{step.step_number}. [{step.floor}] {step.action} {step.location} ({step.distance:.2f}米)")
            else:
                print(f"{step.step_number}. [{step.floor}] {step.action} {step.location}")
    else:
        print(f"\n路径规划失败：{result.error_message}")


if __name__ == "__main__":
    print("\n开始运行集成测试...")
    
    try:
        test_scenario_1_same_floor()
        test_scenario_2_cross_one_floor()
        test_scenario_3_cross_multiple_floors()
        test_scenario_4_multi_waypoint()
        test_scenario_5_rfid()
        
        print("\n" + "="*80)
        print("所有测试场景完成！")
        print("="*80)
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n测试失败: {e}")
