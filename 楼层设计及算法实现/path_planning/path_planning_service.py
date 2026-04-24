"""
路径规划服务
提供路径规划的业务逻辑
"""

import logging
from typing import List, Optional
from models import Position, Node, PathPlanningResult, RFIDDevice
from graph import MultiLayerGraph
from dijkstra import DijkstraAlgorithm
from config import MAX_NEAREST_NODE_DISTANCE

logger = logging.getLogger(__name__)


class PathPlanningService:
    """路径规划服务类"""
    
    def __init__(self, graph: MultiLayerGraph, rfid_devices: List[RFIDDevice]):
        """
        初始化路径规划服务
        
        Args:
            graph: 多层图
            rfid_devices: RFID 设备列表
        """
        self.graph = graph
        self.algorithm = DijkstraAlgorithm(graph)
        self.rfid_devices = {device.device_name: device for device in rfid_devices}
    
    def _position_to_node(self, position: Position) -> Optional[Node]:
        """
        将位置坐标映射到最近的图节点
        
        Args:
            position: 位置坐标
            
        Returns:
            最近的节点，如果找不到则返回 None
        """
        result = self.graph.find_nearest_node(position.x, position.y, position.map_id)
        
        if result is None:
            logger.error(f"在楼层 {position.map_id} 没有找到任何节点")
            return None
        
        node, distance = result
        
        if distance > MAX_NEAREST_NODE_DISTANCE:
            logger.warning(f"最近节点距离 {distance:.2f} 米，超过阈值 {MAX_NEAREST_NODE_DISTANCE} 米")
        
        return node
    
    def plan_path(self, start_pos: Position, end_pos: Position) -> PathPlanningResult:
        """
        规划单点路径
        
        Args:
            start_pos: 起点位置
            end_pos: 终点位置
            
        Returns:
            路径规划结果
        """
        logger.info(f"规划路径：从 ({start_pos.x}, {start_pos.y}, {start_pos.map_id}) "
                   f"到 ({end_pos.x}, {end_pos.y}, {end_pos.map_id})")
        
        # 将位置映射到节点
        start_node = self._position_to_node(start_pos)
        if start_node is None:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=f"起点位置 ({start_pos.x}, {start_pos.y}, {start_pos.map_id}) 附近没有找到节点"
            )
        
        end_node = self._position_to_node(end_pos)
        if end_node is None:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=f"终点位置 ({end_pos.x}, {end_pos.y}, {end_pos.map_id}) 附近没有找到节点"
            )
        
        # 计算最短路径
        path_result = self.algorithm.find_shortest_path(start_node, end_node)
        
        if not path_result.success:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=path_result.error_message
            )
        
        return PathPlanningResult(
            success=True,
            path=path_result.path,
            distance=path_result.distance,
            description=None  # 将由 PathFormatter 生成
        )
    
    def plan_multi_waypoint_path(
        self,
        start_pos: Position,
        waypoints: List[Position],
        end_pos: Position
    ) -> PathPlanningResult:
        """
        规划多点顺序路径
        
        Args:
            start_pos: 起点位置
            waypoints: 途经点列表
            end_pos: 终点位置
            
        Returns:
            路径规划结果
        """
        logger.info(f"规划多点路径：起点 -> {len(waypoints)} 个途经点 -> 终点")
        
        # 如果途经点列表为空，直接规划单点路径
        if not waypoints:
            logger.info("途经点列表为空，使用单点路径规划")
            return self.plan_path(start_pos, end_pos)
        
        # 构建完整的点列表
        all_positions = [start_pos] + waypoints + [end_pos]
        
        # 将所有位置映射到节点
        all_nodes = []
        for i, pos in enumerate(all_positions):
            node = self._position_to_node(pos)
            if node is None:
                return PathPlanningResult(
                    success=False,
                    path=None,
                    distance=None,
                    description=None,
                    error_message=f"第 {i} 个点 ({pos.x}, {pos.y}, {pos.map_id}) 附近没有找到节点"
                )
            all_nodes.append(node)
        
        # 计算每段子路径
        total_path = []
        total_distance = 0.0
        
        for i in range(len(all_nodes) - 1):
            segment_result = self.algorithm.find_shortest_path(all_nodes[i], all_nodes[i + 1])
            
            if not segment_result.success:
                return PathPlanningResult(
                    success=False,
                    path=None,
                    distance=None,
                    description=None,
                    error_message=f"无法从第 {i} 个点到达第 {i + 1} 个点：{segment_result.error_message}"
                )
            
            # 合并路径（避免重复节点）
            if i == 0:
                total_path.extend(segment_result.path)
            else:
                total_path.extend(segment_result.path[1:])  # 跳过第一个节点（与上一段的最后一个节点重复）
            
            total_distance += segment_result.distance
        
        logger.info(f"多点路径规划成功：{len(total_path)} 个节点，总距离 {total_distance:.2f} 米")
        
        return PathPlanningResult(
            success=True,
            path=total_path,
            distance=total_distance,
            description=None  # 将由 PathFormatter 生成
        )
    
    def plan_path_from_rfid(self, rfid_id: str, end_pos: Position) -> PathPlanningResult:
        """
        从 RFID 设备位置规划路径
        
        Args:
            rfid_id: RFID 设备 ID
            end_pos: 终点位置
            
        Returns:
            路径规划结果
        """
        logger.info(f"从 RFID 设备 {rfid_id} 规划路径")
        
        # 查找 RFID 设备
        if rfid_id not in self.rfid_devices:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=f"RFID 设备 {rfid_id} 不存在"
            )
        
        device = self.rfid_devices[rfid_id]
        
        # 检查设备状态
        if not device.is_active:
            logger.warning(f"RFID 设备 {rfid_id} 状态为非活动，但仍允许使用")
        
        # 确定起点节点
        start_node = None
        
        # 如果设备关联到门节点
        if device.door_id is not None:
            start_node = (1, device.door_id, device.map_id)
            logger.info(f"RFID 设备关联到门节点: {start_node}")
        
        # 如果设备关联到楼梯节点
        elif device.stairway_id is not None:
            start_node = (2, device.stairway_id, device.map_id)
            logger.info(f"RFID 设备关联到楼梯节点: {start_node}")
        
        # 如果没有关联节点，使用设备坐标查找最近节点
        else:
            start_pos = Position(x=device.x, y=device.y, map_id=device.map_id)
            start_node = self._position_to_node(start_pos)
            if start_node is None:
                return PathPlanningResult(
                    success=False,
                    path=None,
                    distance=None,
                    description=None,
                    error_message=f"RFID 设备 {rfid_id} 位置附近没有找到节点"
                )
        
        # 检查起点节点是否存在
        if not self.graph.has_node(start_node):
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=f"RFID 设备关联的节点 {start_node} 不存在于图中"
            )
        
        # 将终点位置映射到节点
        end_node = self._position_to_node(end_pos)
        if end_node is None:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=f"终点位置 ({end_pos.x}, {end_pos.y}, {end_pos.map_id}) 附近没有找到节点"
            )
        
        # 计算最短路径
        path_result = self.algorithm.find_shortest_path(start_node, end_node)
        
        if not path_result.success:
            return PathPlanningResult(
                success=False,
                path=None,
                distance=None,
                description=None,
                error_message=path_result.error_message
            )
        
        return PathPlanningResult(
            success=True,
            path=path_result.path,
            distance=path_result.distance,
            description=None  # 将由 PathFormatter 生成
        )
