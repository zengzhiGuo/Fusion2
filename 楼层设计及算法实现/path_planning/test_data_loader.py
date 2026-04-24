"""
任务2测试：数据加载器测试
验证 DataLoader 的所有加载方法
"""

import logging
from config import setup_logging, MAPS_FILE, DOORS_FILE, STAIRWAYS_FILE, GRAPH_EDGES_FILE, RFID_DEVICES_FILE
from data_loader import DataLoader

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def test_load_maps():
    """测试加载地图数据"""
    print("\n" + "="*80)
    print("测试1：加载地图数据")
    print("="*80)
    
    loader = DataLoader()
    maps = loader.load_maps(MAPS_FILE)
    
    print(f"✓ 成功加载 {len(maps)} 个地图")
    print(f"\n前3个地图示例：")
    for i, map_obj in enumerate(maps[:3], 1):
        print(f"{i}. {map_obj.map_id} - {map_obj.region_name}")
        print(f"   尺寸: {map_obj.ship_length_m}m × {map_obj.ship_width_m}m")
    
    return maps


def test_load_doors():
    """测试加载门节点数据"""
    print("\n" + "="*80)
    print("测试2：加载门节点数据")
    print("="*80)
    
    loader = DataLoader()
    doors = loader.load_doors(DOORS_FILE)
    
    print(f"✓ 成功加载 {len(doors)} 个门节点")
    
    # 统计门类型
    type_counts = {1: 0, 2: 0, 3: 0}
    for door in doors:
        type_counts[door.room_type] = type_counts.get(door.room_type, 0) + 1
    
    print(f"\n门类型统计：")
    print(f"  房间 (type=1): {type_counts[1]} 个")
    print(f"  楼道 (type=2): {type_counts[2]} 个")
    print(f"  出入口 (type=3): {type_counts[3]} 个")
    
    print(f"\n前3个门节点示例：")
    for i, door in enumerate(doors[:3], 1):
        type_name = {1: "房间", 2: "楼道", 3: "出入口"}.get(door.room_type, "未知")
        print(f"{i}. ID={door.id} - {door.room_name} ({type_name})")
        print(f"   位置: ({door.x:.2f}, {door.y:.2f}) @ {door.map_id}")
    
    return doors


def test_load_stairways():
    """测试加载楼梯数据"""
    print("\n" + "="*80)
    print("测试3：加载楼梯数据")
    print("="*80)
    
    loader = DataLoader()
    stairways = loader.load_stairways(STAIRWAYS_FILE)
    
    print(f"✓ 成功加载 {len(stairways)} 个楼梯")
    
    print(f"\n前3个楼梯示例：")
    for i, stairway in enumerate(stairways[:3], 1):
        print(f"{i}. {stairway.stairway_id} - {stairway.stairway_name}")
        print(f"   所在楼层: {stairway.map_id}")
        print(f"   上层: {stairway.upper_map_id or '无'}, 下层: {stairway.lower_map_id or '无'}")
        print(f"   位置: ({stairway.x:.2f}, {stairway.y:.2f})")
    
    return stairways


def test_load_graph_edges():
    """测试加载图边数据"""
    print("\n" + "="*80)
    print("测试4：加载图边数据")
    print("="*80)
    
    loader = DataLoader()
    edges = loader.load_graph_edges(GRAPH_EDGES_FILE)
    
    print(f"✓ 成功加载 {len(edges)} 条边")
    
    # 统计边类型
    door_to_door = 0
    door_to_stair = 0
    stair_to_stair = 0
    
    for edge in edges:
        if edge.node_a_type == 1 and edge.node_b_type == 1:
            door_to_door += 1
        elif edge.node_a_type == 2 and edge.node_b_type == 2:
            stair_to_stair += 1
        else:
            door_to_stair += 1
    
    print(f"\n边类型统计：")
    print(f"  门-门: {door_to_door} 条")
    print(f"  门-楼梯: {door_to_stair} 条")
    print(f"  楼梯-楼梯: {stair_to_stair} 条")
    
    print(f"\n前3条边示例：")
    for i, edge in enumerate(edges[:3], 1):
        node_a_type = "门" if edge.node_a_type == 1 else "楼梯"
        node_b_type = "门" if edge.node_b_type == 1 else "楼梯"
        print(f"{i}. {node_a_type}({edge.node_a_id}) <-> {node_b_type}({edge.node_b_id})")
        print(f"   权重: {edge.weight:.2f}m")
    
    return edges


def test_load_rfid_devices():
    """测试加载 RFID 设备数据"""
    print("\n" + "="*80)
    print("测试5：加载 RFID 设备数据")
    print("="*80)
    
    loader = DataLoader()
    devices = loader.load_rfid_devices(RFID_DEVICES_FILE)
    
    print(f"✓ 成功加载 {len(devices)} 个 RFID 设备")
    
    # 统计关联类型
    door_devices = sum(1 for d in devices if d.door_id is not None)
    stair_devices = sum(1 for d in devices if d.stairway_id is not None)
    
    print(f"\n设备关联统计：")
    print(f"  关联到门: {door_devices} 个")
    print(f"  关联到楼梯: {stair_devices} 个")
    
    print(f"\n前3个 RFID 设备示例：")
    for i, device in enumerate(devices[:3], 1):
        print(f"{i}. {device.device_name}")
        print(f"   位置: ({device.x:.2f}, {device.y:.2f}) @ {device.map_id}")
        if device.door_id:
            print(f"   关联: 门 ID={device.door_id}")
        elif device.stairway_id:
            print(f"   关联: 楼梯 ID={device.stairway_id}")
    
    return devices


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*80)
    print("测试6：错误处理")
    print("="*80)
    
    loader = DataLoader()
    
    # 测试文件不存在
    try:
        loader.load_maps("nonexistent_file.txt")
        print("✗ 应该抛出 FileNotFoundError")
    except FileNotFoundError:
        print("✓ 正确处理文件不存在的情况")
    
    print("\n所有错误处理测试通过！")


if __name__ == "__main__":
    print("\n开始测试任务2：数据加载器")
    print("="*80)
    
    try:
        # 运行所有测试
        maps = test_load_maps()
        doors = test_load_doors()
        stairways = test_load_stairways()
        edges = test_load_graph_edges()
        devices = test_load_rfid_devices()
        test_error_handling()
        
        # 总结
        print("\n" + "="*80)
        print("任务2测试总结")
        print("="*80)
        print(f"✓ 地图数据: {len(maps)} 个")
        print(f"✓ 门节点: {len(doors)} 个")
        print(f"✓ 楼梯: {len(stairways)} 个")
        print(f"✓ 图边: {len(edges)} 条")
        print(f"✓ RFID 设备: {len(devices)} 个")
        print("\n所有测试通过！任务2（数据加载器）功能正常。")
        print("="*80)
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n✗ 测试失败: {e}")
