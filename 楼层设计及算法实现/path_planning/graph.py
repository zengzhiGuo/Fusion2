"""
多层图数据结构
存储图结构并提供查询接口
"""

import logging
import math
from typing import Dict, List, Tuple, Optional
from models import Node, NodeInfo

logger = logging.getLogger(__name__)


class MultiLayerGraph:
    """多层图类"""
    
    def __init__(self):
        """初始化多层图"""
        # 邻接表：{节点: [(邻居节点, 权重), ...]}
        self.adjacency_list: Dict[Node, List[Tuple[Node, float]]] = {}
        
        # 节点信息映射：{节点: 节点信息}
        self.node_info: Dict[Node, NodeInfo] = {}
    
    def add_node(self, node: Node, info: NodeInfo):
        """
        添加节点
        
        Args:
            node: 节点
            info: 节点信息
        """
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []
            self.node_info[node] = info
            logger.debug(f"添加节点: {node}")
    
    def add_edge(self, node_a: Node, node_b: Node, weight: float):
        """
        添加双向边
        
        Args:
            node_a: 节点 A
            node_b: 节点 B
            weight: 边的权重（距离）
        """
        # 确保节点存在
        if node_a not in self.adjacency_list:
            logger.warning(f"节点 {node_a} 不存在，无法添加边")
            return
        if node_b not in self.adjacency_list:
            logger.warning(f"节点 {node_b} 不存在，无法添加边")
            return
        
        # 添加双向边
        self.adjacency_list[node_a].append((node_b, weight))
        self.adjacency_list[node_b].append((node_a, weight))
        logger.debug(f"添加边: {node_a} <-> {node_b}, 权重: {weight}")
    
    def get_neighbors(self, node: Node) -> List[Tuple[Node, float]]:
        """
        获取节点的所有邻居
        
        Args:
            node: 节点
            
        Returns:
            邻居列表，每个元素是 (邻居节点, 权重)
        """
        return self.adjacency_list.get(node, [])
    
    def get_node_info(self, node: Node) -> Optional[NodeInfo]:
        """
        获取节点信息
        
        Args:
            node: 节点
            
        Returns:
            节点信息，如果节点不存在则返回 None
        """
        return self.node_info.get(node)
    
    def find_nearest_node(self, x: float, y: float, map_id: str) -> Optional[Tuple[Node, float]]:
        """
        查找距离给定坐标最近的节点（同楼层）
        
        Args:
            x: X 坐标
            y: Y 坐标
            map_id: 楼层 ID
            
        Returns:
            (最近节点, 距离)，如果没有找到则返回 None
        """
        min_distance = float('inf')
        nearest_node = None
        
        for node, info in self.node_info.items():
            # 只考虑同楼层的节点
            if info.map_id != map_id:
                continue
            
            # 计算欧氏距离
            distance = math.sqrt((info.x - x) ** 2 + (info.y - y) ** 2)
            
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
        
        if nearest_node is None:
            logger.warning(f"在楼层 {map_id} 没有找到任何节点")
            return None
        
        logger.debug(f"最近节点: {nearest_node}, 距离: {min_distance:.2f}米")
        return (nearest_node, min_distance)
    
    def get_all_nodes(self) -> List[Node]:
        """
        获取所有节点
        
        Returns:
            节点列表
        """
        return list(self.adjacency_list.keys())
    
    def get_node_count(self) -> int:
        """
        获取节点数量
        
        Returns:
            节点数量
        """
        return len(self.adjacency_list)
    
    def get_edge_count(self) -> int:
        """
        获取边数量（无向图，每条边计算一次）
        
        Returns:
            边数量
        """
        total = sum(len(neighbors) for neighbors in self.adjacency_list.values())
        return total // 2  # 无向图，每条边被计算了两次
    
    def has_node(self, node: Node) -> bool:
        """
        检查节点是否存在
        
        Args:
            node: 节点
            
        Returns:
            是否存在
        """
        return node in self.adjacency_list
    
    def get_nodes_by_floor(self, map_id: str) -> List[Node]:
        """
        获取指定楼层的所有节点
        
        Args:
            map_id: 楼层 ID
            
        Returns:
            节点列表
        """
        return [node for node, info in self.node_info.items() if info.map_id == map_id]
