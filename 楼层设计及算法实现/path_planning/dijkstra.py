"""
Dijkstra 最短路径算法
计算图中两点之间的最短路径
"""

import logging
import heapq
from typing import Dict, Optional
from models import Node, PathResult
from graph import MultiLayerGraph

logger = logging.getLogger(__name__)


class DijkstraAlgorithm:
    """Dijkstra 算法类"""
    
    def __init__(self, graph: MultiLayerGraph):
        """
        初始化 Dijkstra 算法
        
        Args:
            graph: 多层图
        """
        self.graph = graph
    
    def find_shortest_path(self, start: Node, end: Node) -> PathResult:
        """
        查找最短路径
        
        Args:
            start: 起点节点
            end: 终点节点
            
        Returns:
            路径结果
        """
        # 检查节点是否存在
        if not self.graph.has_node(start):
            logger.error(f"起点节点不存在: {start}")
            return PathResult(
                path=[],
                distance=0.0,
                success=False,
                error_message=f"起点节点不存在: {start}"
            )
        
        if not self.graph.has_node(end):
            logger.error(f"终点节点不存在: {end}")
            return PathResult(
                path=[],
                distance=0.0,
                success=False,
                error_message=f"终点节点不存在: {end}"
            )
        
        # 特殊情况：起点=终点
        if start == end:
            logger.info("起点和终点相同")
            return PathResult(
                path=[start],
                distance=0.0,
                success=True
            )
        
        # 初始化距离字典和前驱字典
        distances: Dict[Node, float] = {start: 0.0}
        predecessors: Dict[Node, Optional[Node]] = {start: None}
        
        # 优先队列：(距离, 节点)
        priority_queue = [(0.0, start)]
        
        # 已访问节点集合
        visited = set()
        
        # Dijkstra 算法主循环
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # 如果已经访问过，跳过
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # 如果到达终点，提前结束
            if current_node == end:
                break
            
            # 遍历当前节点的所有邻居
            for neighbor, weight in self.graph.get_neighbors(current_node):
                if neighbor in visited:
                    continue
                
                # 计算新距离
                new_distance = current_distance + weight
                
                # 如果找到更短的路径，更新
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # 检查是否找到路径
        if end not in predecessors:
            logger.warning(f"无法从 {start} 到达 {end}")
            return PathResult(
                path=[],
                distance=0.0,
                success=False,
                error_message=f"起点和终点之间不存在可达路径"
            )
        
        # 回溯构建路径
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        
        total_distance = distances[end]
        
        logger.info(f"找到路径：{len(path)} 个节点，总距离 {total_distance:.2f} 米")
        
        return PathResult(
            path=path,
            distance=total_distance,
            success=True
        )
