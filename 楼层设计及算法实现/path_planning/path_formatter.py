"""
路径格式化器
将路径节点序列转换为人类可读的描述
"""

import logging
from typing import List
from models import Node, PathDescription, Step
from graph import MultiLayerGraph

logger = logging.getLogger(__name__)


class PathFormatter:
    """路径格式化器类"""
    
    def __init__(self, graph: MultiLayerGraph):
        """
        初始化路径格式化器
        
        Args:
            graph: 多层图
        """
        self.graph = graph
    
    def format_path(self, path: List[Node]) -> PathDescription:
        """
        格式化路径
        
        Args:
            path: 节点路径
            
        Returns:
            路径描述
        """
        if not path:
            return PathDescription(
                total_distance=0.0,
                floors=[],
                steps=[]
            )
        
        # 计算总距离
        total_distance = self._calculate_total_distance(path)
        
        # 提取经过的楼层
        floors = self._extract_floors(path)
        
        # 生成步骤描述
        steps = self._generate_steps(path)
        
        return PathDescription(
            total_distance=total_distance,
            floors=floors,
            steps=steps
        )
    
    def _calculate_total_distance(self, path: List[Node]) -> float:
        """
        计算路径总距离
        
        Args:
            path: 节点路径
            
        Returns:
            总距离
        """
        total = 0.0
        
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            # 查找边的权重
            neighbors = self.graph.get_neighbors(current)
            for neighbor, weight in neighbors:
                if neighbor == next_node:
                    total += weight
                    break
        
        return total
    
    def _extract_floors(self, path: List[Node]) -> List[str]:
        """
        提取路径经过的楼层（去重，保持顺序）
        
        Args:
            path: 节点路径
            
        Returns:
            楼层列表
        """
        floors = []
        seen = set()
        
        for node in path:
            info = self.graph.get_node_info(node)
            if info and info.map_id not in seen:
                floors.append(info.map_id)
                seen.add(info.map_id)
        
        return floors
    
    def _generate_steps(self, path: List[Node]) -> List[Step]:
        """
        生成步骤描述
        
        Args:
            path: 节点路径
            
        Returns:
            步骤列表
        """
        steps = []
        
        for i, node in enumerate(path):
            info = self.graph.get_node_info(node)
            if not info:
                continue
            
            # 计算本步距离
            distance = 0.0
            if i < len(path) - 1:
                next_node = path[i + 1]
                neighbors = self.graph.get_neighbors(node)
                for neighbor, weight in neighbors:
                    if neighbor == next_node:
                        distance = weight
                        break
            
            # 确定动作
            action = self._determine_action(i, path)
            
            step = Step(
                step_number=i + 1,
                floor=info.map_id,
                action=action,
                location=info.name,
                distance=distance
            )
            steps.append(step)
        
        return steps
    
    def _determine_action(self, index: int, path: List[Node]) -> str:
        """
        确定步骤的动作类型
        
        Args:
            index: 当前节点在路径中的索引
            path: 完整路径
            
        Returns:
            动作描述
        """
        # 第一个节点：出发
        if index == 0:
            return "出发"
        
        # 最后一个节点：到达
        if index == len(path) - 1:
            return "到达"
        
        # 检查是否是跨层移动
        current_node = path[index]
        prev_node = path[index - 1]
        
        current_info = self.graph.get_node_info(current_node)
        prev_info = self.graph.get_node_info(prev_node)
        
        if current_info and prev_info:
            # 如果楼层不同，说明是跨层移动
            if current_info.map_id != prev_info.map_id:
                # 判断是上楼还是下楼
                # 这里简单判断：如果当前节点是楼梯节点，则根据楼层名称判断
                if current_info.node_type == 2:  # 楼梯节点
                    # 简单的楼层顺序判断（可以根据实际情况优化）
                    floor_order = ['underg3', 'underg1', 'underg2', 'floor1', 'floor2', 'floor3', 'floor4', 'floor5']
                    try:
                        prev_floor_idx = floor_order.index(prev_info.map_id)
                        current_floor_idx = floor_order.index(current_info.map_id)
                        if current_floor_idx > prev_floor_idx:
                            return "上楼"
                        else:
                            return "下楼"
                    except ValueError:
                        return "跨层"
        
        # 默认：经过
        return "经过"
    
    def format_path_to_string(self, description: PathDescription) -> str:
        """
        将路径描述格式化为字符串
        
        Args:
            description: 路径描述
            
        Returns:
            格式化的字符串
        """
        lines = []
        lines.append(f"总距离：{description.total_distance:.2f} 米")
        lines.append(f"经过楼层：{' -> '.join(description.floors)}")
        lines.append("")
        lines.append("详细路径：")
        
        for step in description.steps:
            if step.distance > 0:
                lines.append(f"{step.step_number}. [{step.floor}] {step.action} {step.location} ({step.distance:.2f}米)")
            else:
                lines.append(f"{step.step_number}. [{step.floor}] {step.action} {step.location}")
        
        return "\n".join(lines)
