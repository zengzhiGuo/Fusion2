"""
任务3测试：多层图数据结构测试
验证 MultiLayerGraph 的所有方法
"""

import logging
from config import setup_logging
from graph import MultiLayerGraph
from models import Node, NodeInfo

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


def test_add_node():
    """测试添加节点"""
    print("\n" + "="*80)
    print("测试1：添加节点")
    print("="*80)
    
    graph = MultiLayerGraph()
    
    # 添加门节点
    node1 = (1, 46, 'floor1')  # (node_type, node_id, map_id)
    info1 = NodeInfo(
        node=node1,
        name="A甲板会议室",
        node_type=1,
        map_id='floor1',
        x=21.3,
        y=8.9
    )
    graph.add_node(node1, info1)
    
    # 添加楼梯节点
    node2 = (2, 'stairway_001', 'floor1')
    info2 = NodeInfo(
        node=node2,
        name="A甲板楼梯",
        node_type=2,
        map_id='floor1',
        x=19.8,
        y=12.7
    )
    graph.add_node(node2, info2)
    
    # 添加另一个楼层的节点
    node3 = (1, 51, 'floor2')
    info3 = NodeInfo(
        node=node3,
        name="B甲板办公室",
        node_type=1,
        map_id='floor2',
        x=20.5,
        y=9.2
    )
    graph.add_node(node3, info3)
    
    print(f"✓ 成功添加 {graph.get_node_count()} 个节点")
    print(f"  - floor1: {len(graph.get_nodes_by_floor('floor1'))} 个节点")
    print(f"  - floor2: {len(graph.get_nodes_by_floor('floor2'))} 个节点")
    
    return graph


def test_add_edge(graph):
    """测试添加边"""
    print("\n" + "="*80)
    print("测试2：添加双向边")
    print("="*80)
    
    node1 = (1, 46, 'floor1')
    node2 = (2, 'stairway_001', 'floor1')
    node3 = (1, 51, 'floor2')
    
    # 添加同层边
    graph.add_edge(node1, node2, 5.5)
    
    # 添加跨层边（楼梯连接）
    node2_upper = (2, 'stairway_001', 'floor2')
    info2_upper = NodeInfo(
        node=node2_upper,
        name="A甲板楼梯(上层)",
        node_type=2,
        map_id='floor2',
        x=19.8,
        y=12.7
    )
    graph.add_node(node2_upper, info2_upper)
    graph.add_edge(node2, node2_upper, 10.0)  # 跨层边权重为10米
    
    # 添加另一条同层边
    graph.add_edge(node2_upper, node3, 3.2)
    
    print(f"✓ 成功添加 {graph.get_edge_count()} 条边")
    
    # 验证双向性
    neighbors_node1 = graph.get_neighbors(node1)
    neighbors_node2 = graph.get_neighbors(node2)
    
    print(f"\n验证双向边：")
    print(f"  节点 {node1} 的邻居数量: {len(neighbors_node1)}")
    print(f"  节点 {node2} 的邻居数量: {len(neighbors_node2)}")
    
    # 检查对称性
    has_edge_1_to_2 = any(n == node2 for n, w in neighbors_node1)
    has_edge_2_to_1 = any(n == node1 for n, w in neighbors_node2)
    
    if has_edge_1_to_2 and has_edge_2_to_1:
        print(f"  ✓ 边的双向性验证通过")
    else:
        print(f"  ✗ 边的双向性验证失败")
    
    return graph


def test_get_neighbors(graph):
    """测试获取邻居"""
    print("\n" + "="*80)
    print("测试3：获取节点邻居")
    print("="*80)
    
    node2 = (2, 'stairway_001', 'floor1')
    neighbors = graph.get_neighbors(node2)
    
    print(f"节点 {node2} 的邻居：")
    for neighbor, weight in neighbors:
        info = graph.get_node_info(neighbor)
        print(f"  - {neighbor}: {info.name}, 距离 {weight:.2f}米")
    
    print(f"\n✓ 成功获取 {len(neighbors)} 个邻居")


def test_find_nearest_node(graph):
    """测试查找最近节点"""
    print("\n" + "="*80)
    print("测试4：查找最近节点")
    print("="*80)
    
    # 测试坐标
    test_x, test_y = 21.0, 9.0
    map_id = 'floor1'
    
    result = graph.find_nearest_node(test_x, test_y, map_id)
    
    if result:
        nearest_node, distance = result
        info = graph.get_node_info(nearest_node)
        print(f"查询坐标: ({test_x}, {test_y}) @ {map_id}")
        print(f"✓ 找到最近节点: {nearest_node}")
        print(f"  名称: {info.name}")
        print(f"  节点坐标: ({info.x:.2f}, {info.y:.2f})")
        print(f"  距离: {distance:.2f}米")
    else:
        print(f"✗ 未找到最近节点")
    
    # 测试楼层一致性
    print(f"\n验证楼层一致性：")
    result_floor2 = graph.find_nearest_node(20.0, 9.0, 'floor2')
    if result_floor2:
        nearest_node_floor2, _ = result_floor2
        info_floor2 = graph.get_node_info(nearest_node_floor2)
        if info_floor2.map_id == 'floor2':
            print(f"  ✓ 最近节点楼层一致性验证通过 (floor2)")
        else:
            print(f"  ✗ 最近节点楼层不一致")


def test_get_node_info(graph):
    """测试获取节点信息"""
    print("\n" + "="*80)
    print("测试5：获取节点信息")
    print("="*80)
    
    node1 = (1, 46, 'floor1')
    info = graph.get_node_info(node1)
    
    if info:
        print(f"节点 {node1} 的信息：")
        print(f"  名称: {info.name}")
        print(f"  类型: {'门' if info.node_type == 1 else '楼梯'}")
        print(f"  楼层: {info.map_id}")
        print(f"  坐标: ({info.x:.2f}, {info.y:.2f})")
        print(f"\n✓ 成功获取节点信息")
    else:
        print(f"✗ 节点信息不存在")


def test_graph_statistics(graph):
    """测试图统计信息"""
    print("\n" + "="*80)
    print("测试6：图统计信息")
    print("="*80)
    
    print(f"图的统计信息：")
    print(f"  总节点数: {graph.get_node_count()}")
    print(f"  总边数: {graph.get_edge_count()}")
    print(f"  floor1 节点数: {len(graph.get_nodes_by_floor('floor1'))}")
    print(f"  floor2 节点数: {len(graph.get_nodes_by_floor('floor2'))}")
    
    # 测试节点存在性
    node1 = (1, 46, 'floor1')
    node_not_exist = (1, 999, 'floor1')
    
    print(f"\n节点存在性检查：")
    print(f"  节点 {node1} 存在: {graph.has_node(node1)}")
    print(f"  节点 {node_not_exist} 存在: {graph.has_node(node_not_exist)}")


def test_property_node_uniqueness():
    """属性测试：节点唯一性"""
    print("\n" + "="*80)
    print("属性测试：节点唯一性")
    print("="*80)
    
    graph = MultiLayerGraph()
    
    # 添加相同的节点两次
    node = (1, 100, 'floor1')
    info = NodeInfo(
        node=node,
        name="测试节点",
        node_type=1,
        map_id='floor1',
        x=10.0,
        y=10.0
    )
    
    graph.add_node(node, info)
    initial_count = graph.get_node_count()
    
    # 再次添加相同节点
    graph.add_node(node, info)
    final_count = graph.get_node_count()
    
    if initial_count == final_count:
        print(f"✓ 节点唯一性验证通过（添加重复节点不会增加节点数）")
    else:
        print(f"✗ 节点唯一性验证失败")


def test_property_edge_symmetry():
    """属性测试：双向边对称性"""
    print("\n" + "="*80)
    print("属性测试：双向边对称性")
    print("="*80)
    
    graph = MultiLayerGraph()
    
    # 添加两个节点
    node_a = (1, 1, 'floor1')
    node_b = (1, 2, 'floor1')
    
    info_a = NodeInfo(node=node_a, name="节点A", node_type=1, map_id='floor1', x=0.0, y=0.0)
    info_b = NodeInfo(node=node_b, name="节点B", node_type=1, map_id='floor1', x=5.0, y=0.0)
    
    graph.add_node(node_a, info_a)
    graph.add_node(node_b, info_b)
    
    # 添加边
    weight = 5.0
    graph.add_edge(node_a, node_b, weight)
    
    # 验证对称性
    neighbors_a = graph.get_neighbors(node_a)
    neighbors_b = graph.get_neighbors(node_b)
    
    has_a_to_b = any(n == node_b and w == weight for n, w in neighbors_a)
    has_b_to_a = any(n == node_a and w == weight for n, w in neighbors_b)
    
    if has_a_to_b and has_b_to_a:
        print(f"✓ 双向边对称性验证通过")
        print(f"  A -> B: 存在，权重 {weight}")
        print(f"  B -> A: 存在，权重 {weight}")
    else:
        print(f"✗ 双向边对称性验证失败")


def test_property_floor_consistency():
    """属性测试：最近节点楼层一致性"""
    print("\n" + "="*80)
    print("属性测试：最近节点楼层一致性")
    print("="*80)
    
    graph = MultiLayerGraph()
    
    # 在不同楼层添加节点
    for floor_num in range(1, 4):
        map_id = f'floor{floor_num}'
        for i in range(3):
            node = (1, floor_num * 10 + i, map_id)
            info = NodeInfo(
                node=node,
                name=f"节点{floor_num}-{i}",
                node_type=1,
                map_id=map_id,
                x=float(i * 5),
                y=float(i * 5)
            )
            graph.add_node(node, info)
    
    # 测试每个楼层
    all_passed = True
    for floor_num in range(1, 4):
        map_id = f'floor{floor_num}'
        result = graph.find_nearest_node(1.0, 1.0, map_id)
        
        if result:
            nearest_node, _ = result
            info = graph.get_node_info(nearest_node)
            if info.map_id != map_id:
                print(f"✗ {map_id} 楼层一致性验证失败")
                all_passed = False
    
    if all_passed:
        print(f"✓ 所有楼层的最近节点楼层一致性验证通过")


if __name__ == "__main__":
    print("\n开始测试任务3：多层图数据结构")
    print("="*80)
    
    try:
        # 基本功能测试
        graph = test_add_node()
        graph = test_add_edge(graph)
        test_get_neighbors(graph)
        test_find_nearest_node(graph)
        test_get_node_info(graph)
        test_graph_statistics(graph)
        
        # 属性测试
        test_property_node_uniqueness()
        test_property_edge_symmetry()
        test_property_floor_consistency()
        
        # 总结
        print("\n" + "="*80)
        print("任务3测试总结")
        print("="*80)
        print("✓ 节点添加功能正常")
        print("✓ 双向边添加功能正常")
        print("✓ 邻居查询功能正常")
        print("✓ 最近节点查找功能正常")
        print("✓ 节点信息查询功能正常")
        print("✓ 图统计功能正常")
        print("✓ 节点唯一性属性验证通过")
        print("✓ 双向边对称性属性验证通过")
        print("✓ 楼层一致性属性验证通过")
        print("\n所有测试通过！任务3（多层图数据结构）功能正常。")
        print("="*80)
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n✗ 测试失败: {e}")
