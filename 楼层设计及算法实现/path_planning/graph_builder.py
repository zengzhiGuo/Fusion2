"""
图构建器
根据加载的数据构建多层图模型
"""

import logging
from typing import List, Set
from models import Door, Stairway, GraphEdge, Node, NodeInfo, ConnectivityReport
from graph import MultiLayerGraph
from config import CROSS_FLOOR_WEIGHT

logger = logging.getLogger(__name__)


class GraphBuilder:
    """图构建器类"""
    
    def __init__(self, doors: List[Door], stairways: List[Stairway], edges: List[GraphEdge]):
        """
        初始化图构建器
        
        Args:
            doors: 门节点列表
            stairways: 楼梯列表
            edges: 图边列表
        """
        self.doors = doors
        self.stairways = stairways
        self.edges = edges
        self.graph = MultiLayerGraph()
    
    def build_graph(self) -> MultiLayerGraph:
        """
        构建多层图
        
        Returns:
            构建好的多层图
        """
        logger.info("开始构建多层图...")
        
        # 1. 添加门节点
        self._add_door_nodes()
        
        # 2. 添加楼梯节点（包括虚拟节点）
        self._add_stairway_nodes()
        
        # 3. 添加同层边
        self._add_same_floor_edges()
        
        # 4. 添加跨层边
        self._add_cross_floor_edges()
        
        logger.info(f"图构建完成：{self.graph.get_node_count()} 个节点，{self.graph.get_edge_count()} 条边")
        
        return self.graph
    
    def _add_door_nodes(self):
        """添加门节点"""
        for door in self.doors:
            node = (1, door.id, door.map_id)
            info = NodeInfo(
                node=node,
                name=door.room_name,
                node_type=1,
                map_id=door.map_id,
                x=door.x,
                y=door.y
            )
            self.graph.add_node(node, info)
        
        logger.info(f"添加了 {len(self.doors)} 个门节点")
    
    def _add_stairway_nodes(self):
        """添加楼梯节点（包括虚拟节点）"""
        stairway_count = 0
        
        for stairway in self.stairways:
            # 在楼梯所在楼层添加节点
            node = (2, stairway.stairway_id, stairway.map_id)
            info = NodeInfo(
                node=node,
                name=stairway.stairway_name,
                node_type=2,
                map_id=stairway.map_id,
                x=stairway.x,
                y=stairway.y
            )
            self.graph.add_node(node, info)
            stairway_count += 1
            
            # 如果有上层连接，在上层创建虚拟节点
            if stairway.upper_map_id:
                upper_node = (2, stairway.stairway_id, stairway.upper_map_id)
                upper_info = NodeInfo(
                    node=upper_node,
                    name=f"{stairway.stairway_name}(上层出口)",
                    node_type=2,
                    map_id=stairway.upper_map_id,
                    x=stairway.x,  # 使用相同的坐标
                    y=stairway.y
                )
                self.graph.add_node(upper_node, upper_info)
                stairway_count += 1
            
            # 如果有下层连接，在下层创建虚拟节点
            if stairway.lower_map_id:
                lower_node = (2, stairway.stairway_id, stairway.lower_map_id)
                lower_info = NodeInfo(
                    node=lower_node,
                    name=f"{stairway.stairway_name}(下层出口)",
                    node_type=2,
                    map_id=stairway.lower_map_id,
                    x=stairway.x,  # 使用相同的坐标
                    y=stairway.y
                )
                self.graph.add_node(lower_node, lower_info)
                stairway_count += 1
        
        logger.info(f"添加了 {stairway_count} 个楼梯节点（包括虚拟节点）")
    
    def _add_same_floor_edges(self):
        """添加同层边"""
        edge_count = 0
        
        for edge in self.edges:
            # 确定节点 A 的 map_id
            if edge.node_a_type == 1:  # 门节点
                door_a = next((d for d in self.doors if d.id == edge.node_a_id), None)
                if not door_a:
                    logger.warning(f"找不到门节点 {edge.node_a_id}")
                    continue
                map_id_a = door_a.map_id
            else:  # 楼梯节点
                stairway_a = next((s for s in self.stairways if s.stairway_id == edge.node_a_id), None)
                if not stairway_a:
                    logger.warning(f"找不到楼梯节点 {edge.node_a_id}")
                    continue
                map_id_a = stairway_a.map_id
            
            # 确定节点 B 的 map_id
            if edge.node_b_type == 1:  # 门节点
                door_b = next((d for d in self.doors if d.id == edge.node_b_id), None)
                if not door_b:
                    logger.warning(f"找不到门节点 {edge.node_b_id}")
                    continue
                map_id_b = door_b.map_id
            else:  # 楼梯节点
                stairway_b = next((s for s in self.stairways if s.stairway_id == edge.node_b_id), None)
                if not stairway_b:
                    logger.warning(f"找不到楼梯节点 {edge.node_b_id}")
                    continue
                map_id_b = stairway_b.map_id
            
            # 创建节点
            node_a = (edge.node_a_type, edge.node_a_id, map_id_a)
            node_b = (edge.node_b_type, edge.node_b_id, map_id_b)
            
            # 添加边
            self.graph.add_edge(node_a, node_b, edge.weight)
            edge_count += 1
        
        logger.info(f"添加了 {edge_count} 条同层边")
    
    def _add_cross_floor_edges(self):
        """添加跨层边（包括楼梯内部连接和楼梯之间连接）"""
        edge_count = 0
        
        # 1. 添加楼梯内部的跨层边（同一楼梯的上下层连接）
        for stairway in self.stairways:
            current_node = (2, stairway.stairway_id, stairway.map_id)
            
            # 添加到上层的跨层边
            if stairway.upper_map_id:
                upper_node = (2, stairway.stairway_id, stairway.upper_map_id)
                self.graph.add_edge(current_node, upper_node, CROSS_FLOOR_WEIGHT)
                edge_count += 1
                logger.debug(f"添加跨层边（上楼）: {current_node} -> {upper_node}")
            
            # 添加到下层的跨层边
            if stairway.lower_map_id:
                lower_node = (2, stairway.stairway_id, stairway.lower_map_id)
                self.graph.add_edge(current_node, lower_node, CROSS_FLOOR_WEIGHT)
                edge_count += 1
                logger.debug(f"添加跨层边（下楼）: {current_node} -> {lower_node}")
        
        logger.info(f"添加了 {edge_count} 条楼梯内部跨层边（权重={CROSS_FLOOR_WEIGHT}米）")
        
        # 2. 添加楼梯之间的连接边（不同楼梯之间的连接）
        stairway_connection_count = 0
        
        for stairway in self.stairways:
            # 处理上层楼梯连接
            if stairway.upper_stairway_id:
                # 找到目标楼梯
                target_stairway = next((s for s in self.stairways if s.stairway_id == stairway.upper_stairway_id), None)
                if target_stairway:
                    # 当前楼梯在其所在楼层的节点
                    current_node = (2, stairway.stairway_id, stairway.map_id)
                    # 目标楼梯在其所在楼层的节点
                    target_node = (2, target_stairway.stairway_id, target_stairway.map_id)
                    
                    # 添加双向边（因为楼梯之间是双向可通行的）
                    self.graph.add_edge(current_node, target_node, CROSS_FLOOR_WEIGHT)
                    stairway_connection_count += 1
                    logger.debug(f"添加楼梯连接边（上层）: {current_node} <-> {target_node}")
                else:
                    logger.warning(f"找不到上层连接的楼梯: {stairway.upper_stairway_id}")
            
            # 处理下层楼梯连接
            if stairway.lower_stairway_id:
                # 找到目标楼梯
                target_stairway = next((s for s in self.stairways if s.stairway_id == stairway.lower_stairway_id), None)
                if target_stairway:
                    # 当前楼梯在其所在楼层的节点
                    current_node = (2, stairway.stairway_id, stairway.map_id)
                    # 目标楼梯在其所在楼层的节点
                    target_node = (2, target_stairway.stairway_id, target_stairway.map_id)
                    
                    # 添加双向边（因为楼梯之间是双向可通行的）
                    self.graph.add_edge(current_node, target_node, CROSS_FLOOR_WEIGHT)
                    stairway_connection_count += 1
                    logger.debug(f"添加楼梯连接边（下层）: {current_node} <-> {target_node}")
                else:
                    logger.warning(f"找不到下层连接的楼梯: {stairway.lower_stairway_id}")
        
        logger.info(f"添加了 {stairway_connection_count} 条楼梯之间连接边（权重={CROSS_FLOOR_WEIGHT}米）")
    
    def validate_connectivity(self) -> ConnectivityReport:
        """
        验证图的连通性
        
        Returns:
            连通性报告
        """
        logger.info("开始验证图的连通性...")
        
        all_nodes = self.graph.get_all_nodes()
        if not all_nodes:
            return ConnectivityReport(
                is_connected=True,
                isolated_nodes=[],
                num_components=0,
                warnings=["图中没有节点"]
            )
        
        # 使用 DFS 查找连通分量
        visited: Set[Node] = set()
        components = []
        
        def dfs(node: Node, component: List[Node]):
            """深度优先搜索"""
            visited.add(node)
            component.append(node)
            for neighbor, _ in self.graph.get_neighbors(node):
                if neighbor not in visited:
                    dfs(neighbor, component)
        
        # 查找所有连通分量
        for node in all_nodes:
            if node not in visited:
                component = []
                dfs(node, component)
                components.append(component)
        
        # 查找孤立节点（没有邻居的节点）
        isolated_nodes = [node for node in all_nodes if len(self.graph.get_neighbors(node)) == 0]
        
        # 生成报告
        is_connected = len(components) == 1
        warnings = []
        
        if isolated_nodes:
            warnings.append(f"发现 {len(isolated_nodes)} 个孤立节点")
        
        if not is_connected:
            warnings.append(f"图不连通，存在 {len(components)} 个连通分量")
            for i, component in enumerate(components, 1):
                warnings.append(f"  连通分量 {i}: {len(component)} 个节点")
        
        report = ConnectivityReport(
            is_connected=is_connected,
            isolated_nodes=isolated_nodes,
            num_components=len(components),
            warnings=warnings
        )
        
        if warnings:
            for warning in warnings:
                logger.warning(warning)
        else:
            logger.info("图连通性验证通过")
        
        return report
