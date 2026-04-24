"""
跨楼层路径规划测试
测试从楼层1到楼层2的路径规划功能
"""

import logging
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import DataLoader
from graph_builder import GraphBuilder
from path_planning_service import PathPlanningService
from path_formatter import PathFormatter
from models import Position

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_cross_floor_path():
    """测试跨楼层路径规划"""
    
    logger.info("=" * 80)
    logger.info("开始跨楼层路径规划测试")
    logger.info("=" * 80)
    
    # 1. 加载数据
    logger.info("\n步骤1: 加载数据文件...")
    loader = DataLoader()
    
    try:
        maps = loader.load_maps('database_export/maps_data.txt')
        doors = loader.load_doors('database_export/doors_data.txt')
        stairways = loader.load_stairways('database_export/stairways_data.txt')
        edges = loader.load_graph_edges('database_export/graph_edges_data.txt')
        rfid_devices = loader.load_rfid_devices('database_export/rfid_devices_data.txt')
        
        logger.info(f"✓ 加载完成：{len(maps)}个地图，{len(doors)}个门，{len(stairways)}个楼梯，{len(edges)}条边")
    except Exception as e:
        logger.error(f"✗ 数据加载失败: {e}")
        return False
    
    # 2. 构建图
    logger.info("\n步骤2: 构建多层图...")
    try:
        builder = GraphBuilder(doors, stairways, edges)
        graph = builder.build_graph()
        logger.info(f"✓ 图构建完成：{graph.get_node_count()}个节点，{graph.get_edge_count()}条边")
    except Exception as e:
        logger.error(f"✗ 图构建失败: {e}")
        return False
    
    # 3. 创建路径规划服务
    logger.info("\n步骤3: 初始化路径规划服务...")
    try:
        service = PathPlanningService(graph, rfid_devices)
        formatter = PathFormatter(graph)
        logger.info("✓ 服务初始化完成")
    except Exception as e:
        logger.error(f"✗ 服务初始化失败: {e}")
        return False
    
    # 4. 定义测试案例
    logger.info("\n步骤4: 执行跨楼层路径规划...")
    logger.info("-" * 80)
    logger.info("测试案例：")
    logger.info("  起点：楼层1 - A甲板会议室 (22.4460, 13.4433)")
    logger.info("  终点：楼层2 - 官员餐厅 (21.1138, 12.9260)")
    logger.info("-" * 80)
    
    # 起点：楼层1的A甲板会议室
    start_pos = Position(x=22.4460, y=13.4433, map_id='floor1')
    
    # 终点：楼层2的官员餐厅
    end_pos = Position(x=21.1138, y=12.9260, map_id='floor2')
    
    # 5. 执行路径规划
    try:
        result = service.plan_path(start_pos, end_pos)
        
        if not result.success:
            logger.error(f"✗ 路径规划失败: {result.error_message}")
            return False
        
        logger.info(f"✓ 路径规划成功！")
        logger.info(f"  总距离: {result.distance:.2f} 米")
        logger.info(f"  节点数量: {len(result.path)}")
        
        # 6. 格式化路径描述
        logger.info("\n步骤5: 生成路径描述...")
        description = formatter.format_path(result.path)
        
        logger.info("\n" + "=" * 80)
        logger.info("路径详情")
        logger.info("=" * 80)
        logger.info(f"总距离: {description.total_distance:.2f} 米")
        logger.info(f"经过楼层: {' -> '.join(description.floors)}")
        logger.info("\n详细步骤:")
        logger.info("-" * 80)
        
        for step in description.steps:
            logger.info(f"步骤 {step.step_number}: [{step.floor}] {step.action} - {step.location} ({step.distance:.2f}米)")
        
        logger.info("=" * 80)
        
        # 7. 验证路径
        logger.info("\n步骤6: 验证路径...")
        
        # 检查是否包含两个楼层
        floors_in_path = set()
        for node in result.path:
            node_info = graph.get_node_info(node)
            if node_info:
                floors_in_path.add(node_info.map_id)
        
        if 'floor1' in floors_in_path and 'floor2' in floors_in_path:
            logger.info("✓ 路径包含楼层1和楼层2，跨楼层连接成功！")
        else:
            logger.warning(f"✗ 路径只包含楼层: {floors_in_path}")
            return False
        
        # 检查是否包含楼梯节点
        has_stairway = any(node[0] == 2 for node in result.path)
        if has_stairway:
            logger.info("✓ 路径包含楼梯节点")
        else:
            logger.warning("✗ 路径不包含楼梯节点")
            return False
        
        logger.info("\n" + "=" * 80)
        logger.info("跨楼层路径规划测试通过！✓")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 路径规划执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_cross_floor_path()
    
    if success:
        print("\n✓ 测试成功")
        exit(0)
    else:
        print("\n✗ 测试失败")
        exit(1)
