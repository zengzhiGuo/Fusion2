"""
API 接口层
对外提供路径规划功能的接口
"""

import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import asdict
from path_planning.models import Position
from path_planning.path_planning_service import PathPlanningService
from path_planning.path_formatter import PathFormatter
from path_planning.graph import MultiLayerGraph

logger = logging.getLogger(__name__)


class PathPlanningAPI:
    """路径规划 API 类"""
    
    def __init__(self, service: PathPlanningService, formatter: PathFormatter):
        """
        初始化 API
        
        Args:
            service: 路径规划服务
            formatter: 路径格式化器
        """
        self.service = service
        self.formatter = formatter
    
    def _validate_position(self, x: float, y: float, map_id: str) -> Optional[str]:
        """
        验证位置参数
        
        Args:
            x: X 坐标
            y: Y 坐标
            map_id: 楼层 ID
            
        Returns:
            错误信息，如果验证通过则返回 None
        """
        if not isinstance(x, (int, float)):
            return "X 坐标必须是数字"
        if not isinstance(y, (int, float)):
            return "Y 坐标必须是数字"
        if not isinstance(map_id, str) or not map_id:
            return "楼层 ID 必须是非空字符串"
        return None
    
    def _log_api_call(self, method: str, params: Dict[str, Any], result: Dict[str, Any], duration: float):
        """
        记录 API 调用日志
        
        Args:
            method: 方法名
            params: 参数
            result: 结果
            duration: 耗时（秒）
        """
        logger.info(f"API 调用: {method}, 参数: {params}, "
                   f"成功: {result.get('success', False)}, 耗时: {duration:.3f}秒")
    
    def plan_path(
        self,
        start_x: float,
        start_y: float,
        start_map_id: str,
        end_x: float,
        end_y: float,
        end_map_id: str
    ) -> Dict[str, Any]:
        """
        规划单点路径
        
        Args:
            start_x: 起点 X 坐标
            start_y: 起点 Y 坐标
            start_map_id: 起点楼层 ID
            end_x: 终点 X 坐标
            end_y: 终点 Y 坐标
            end_map_id: 终点楼层 ID
            
        Returns:
            路径规划结果字典
        """
        start_time = time.time()
        params = {
            'start': (start_x, start_y, start_map_id),
            'end': (end_x, end_y, end_map_id)
        }
        
        # 参数验证
        error = self._validate_position(start_x, start_y, start_map_id)
        if error:
            result = {
                'success': False,
                'error_code': 'INVALID_PARAMETER',
                'error_message': f"起点参数错误: {error}"
            }
            self._log_api_call('plan_path', params, result, time.time() - start_time)
            return result
        
        error = self._validate_position(end_x, end_y, end_map_id)
        if error:
            result = {
                'success': False,
                'error_code': 'INVALID_PARAMETER',
                'error_message': f"终点参数错误: {error}"
            }
            self._log_api_call('plan_path', params, result, time.time() - start_time)
            return result
        
        # 调用服务
        start_pos = Position(x=start_x, y=start_y, map_id=start_map_id)
        end_pos = Position(x=end_x, y=end_y, map_id=end_map_id)
        
        planning_result = self.service.plan_path(start_pos, end_pos)
        
        if not planning_result.success:
            result = {
                'success': False,
                'error_code': 'PATH_NOT_FOUND',
                'error_message': planning_result.error_message
            }
            self._log_api_call('plan_path', params, result, time.time() - start_time)
            return result
        
        # 格式化路径
        description = self.formatter.format_path(planning_result.path)
        
        result = {
            'success': True,
            'path': [list(node) for node in planning_result.path],
            'distance': planning_result.distance,
            'description': {
                'total_distance': description.total_distance,
                'floors': description.floors,
                'steps': [asdict(step) for step in description.steps]
            }
        }
        
        self._log_api_call('plan_path', params, result, time.time() - start_time)
        return result
    
    def plan_multi_waypoint_path(
        self,
        start_x: float,
        start_y: float,
        start_map_id: str,
        waypoints: List[Dict[str, Any]],
        end_x: float,
        end_y: float,
        end_map_id: str
    ) -> Dict[str, Any]:
        """
        规划多点顺序路径
        
        Args:
            start_x: 起点 X 坐标
            start_y: 起点 Y 坐标
            start_map_id: 起点楼层 ID
            waypoints: 途经点列表，每个元素是 {'x': float, 'y': float, 'map_id': str}
            end_x: 终点 X 坐标
            end_y: 终点 Y 坐标
            end_map_id: 终点楼层 ID
            
        Returns:
            路径规划结果字典
        """
        start_time = time.time()
        params = {
            'start': (start_x, start_y, start_map_id),
            'waypoints': waypoints,
            'end': (end_x, end_y, end_map_id)
        }
        
        # 参数验证
        error = self._validate_position(start_x, start_y, start_map_id)
        if error:
            result = {
                'success': False,
                'error_code': 'INVALID_PARAMETER',
                'error_message': f"起点参数错误: {error}"
            }
            self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
            return result
        
        error = self._validate_position(end_x, end_y, end_map_id)
        if error:
            result = {
                'success': False,
                'error_code': 'INVALID_PARAMETER',
                'error_message': f"终点参数错误: {error}"
            }
            self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
            return result
        
        # 验证途经点
        waypoint_positions = []
        for i, wp in enumerate(waypoints):
            if not isinstance(wp, dict):
                result = {
                    'success': False,
                    'error_code': 'INVALID_PARAMETER',
                    'error_message': f"途经点 {i} 格式错误"
                }
                self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
                return result
            
            error = self._validate_position(wp.get('x'), wp.get('y'), wp.get('map_id'))
            if error:
                result = {
                    'success': False,
                    'error_code': 'INVALID_PARAMETER',
                    'error_message': f"途经点 {i} 参数错误: {error}"
                }
                self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
                return result
            
            waypoint_positions.append(Position(x=wp['x'], y=wp['y'], map_id=wp['map_id']))
        
        # 调用服务
        start_pos = Position(x=start_x, y=start_y, map_id=start_map_id)
        end_pos = Position(x=end_x, y=end_y, map_id=end_map_id)
        
        planning_result = self.service.plan_multi_waypoint_path(start_pos, waypoint_positions, end_pos)
        
        if not planning_result.success:
            result = {
                'success': False,
                'error_code': 'PATH_NOT_FOUND',
                'error_message': planning_result.error_message
            }
            self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
            return result
        
        # 格式化路径
        description = self.formatter.format_path(planning_result.path)
        
        result = {
            'success': True,
            'path': [list(node) for node in planning_result.path],
            'distance': planning_result.distance,
            'description': {
                'total_distance': description.total_distance,
                'floors': description.floors,
                'steps': [asdict(step) for step in description.steps]
            }
        }
        
        self._log_api_call('plan_multi_waypoint_path', params, result, time.time() - start_time)
        return result
    
    def get_node_info(self, node_type: int, node_id: Any, map_id: str) -> Dict[str, Any]:
        """
        获取节点信息
        
        Args:
            node_type: 节点类型（1=门，2=楼梯）
            node_id: 节点 ID
            map_id: 楼层 ID
            
        Returns:
            节点信息字典
        """
        start_time = time.time()
        params = {'node_type': node_type, 'node_id': node_id, 'map_id': map_id}
        
        # 参数验证
        if node_type not in [1, 2]:
            result = {
                'success': False,
                'error_code': 'INVALID_PARAMETER',
                'error_message': "节点类型必须是 1（门）或 2（楼梯）"
            }
            self._log_api_call('get_node_info', params, result, time.time() - start_time)
            return result
        
        # 查询节点信息
        node = (node_type, node_id, map_id)
        info = self.service.graph.get_node_info(node)
        
        if info is None:
            result = {
                'success': False,
                'error_code': 'NODE_NOT_FOUND',
                'error_message': f"节点 {node} 不存在"
            }
            self._log_api_call('get_node_info', params, result, time.time() - start_time)
            return result
        
        result = {
            'success': True,
            'node_info': {
                'node': list(info.node),
                'name': info.name,
                'node_type': info.node_type,
                'map_id': info.map_id,
                'x': info.x,
                'y': info.y
            }
        }
        
        self._log_api_call('get_node_info', params, result, time.time() - start_time)
        return result
