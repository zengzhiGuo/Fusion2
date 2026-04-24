"""
数据加载器
从文本文件加载船舶结构数据
"""

import logging
from typing import List, Optional
from models import Map, Door, Stairway, GraphEdge, RFIDDevice

logger = logging.getLogger(__name__)


class DataFormatError(Exception):
    """数据格式错误"""
    pass


class DataValidationError(Exception):
    """数据验证错误"""
    pass


class DataLoader:
    """数据加载器类"""
    
    def __init__(self):
        """初始化数据加载器"""
        pass
    
    def _read_tsv_file(self, file_path: str) -> List[List[str]]:
        """
        读取制表符分隔的文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            数据行列表，每行是一个字符串列表
            
        Raises:
            FileNotFoundError: 文件不存在
            DataFormatError: 文件格式错误
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 跳过注释行（以 # 开头）
            data_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    data_lines.append(line)
            
            if len(data_lines) < 2:
                raise DataFormatError(f"文件 {file_path} 数据不足（至少需要表头和一行数据）")
            
            # 解析数据
            result = []
            for line in data_lines:
                fields = line.split('\t')
                result.append(fields)
            
            return result
            
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise DataFormatError(f"读取文件失败: {e}")
    
    def _parse_optional_int(self, value: str) -> Optional[int]:
        """解析可选的整数值"""
        if value == 'NULL' or value == '':
            return None
        try:
            return int(value)
        except ValueError:
            return None
    
    def _parse_optional_float(self, value: str) -> Optional[float]:
        """解析可选的浮点数值"""
        if value == 'NULL' or value == '':
            return None
        try:
            return float(value)
        except ValueError:
            return None
    
    def _parse_optional_str(self, value: str) -> Optional[str]:
        """解析可选的字符串值"""
        if value == 'NULL' or value == '':
            return None
        return value
    
    def _parse_bool(self, value: str) -> bool:
        """解析布尔值"""
        return value == '1' or value.lower() == 'true'
    
    def load_maps(self, file_path: str) -> List[Map]:
        """
        加载地图数据
        
        Args:
            file_path: 地图数据文件路径
            
        Returns:
            地图对象列表
        """
        try:
            data = self._read_tsv_file(file_path)
            headers = data[0]
            
            maps = []
            for i, row in enumerate(data[1:], start=2):
                try:
                    if len(row) != len(headers):
                        logger.warning(f"第 {i} 行字段数量不匹配，跳过")
                        continue
                    
                    map_obj = Map(
                        map_id=row[0],
                        region_name=row[1],
                        image_path=row[2],
                        ship_length_m=float(row[3]),
                        ship_width_m=float(row[4]),
                        image_width_px=self._parse_optional_int(row[5]),
                        image_height_px=self._parse_optional_int(row[6])
                    )
                    maps.append(map_obj)
                except Exception as e:
                    logger.error(f"解析第 {i} 行数据失败: {e}")
                    raise DataFormatError(f"解析第 {i} 行数据失败: {e}")
            
            logger.info(f"成功加载 {len(maps)} 个地图")
            return maps
            
        except Exception as e:
            logger.error(f"加载地图数据失败: {e}")
            raise
    
    def load_doors(self, file_path: str) -> List[Door]:
        """
        加载门节点数据
        
        Args:
            file_path: 门数据文件路径
            
        Returns:
            门对象列表
        """
        try:
            data = self._read_tsv_file(file_path)
            headers = data[0]
            
            doors = []
            for i, row in enumerate(data[1:], start=2):
                try:
                    if len(row) != len(headers):
                        logger.warning(f"第 {i} 行字段数量不匹配，跳过")
                        continue
                    
                    door = Door(
                        id=int(row[0]),
                        room_name=row[1],
                        room_type=int(row[2]),
                        map_id=row[3],
                        x=float(row[4]),
                        y=float(row[5]),
                        description=row[6],
                        is_active=self._parse_bool(row[7])
                    )
                    doors.append(door)
                except Exception as e:
                    logger.error(f"解析第 {i} 行数据失败: {e}")
                    raise DataFormatError(f"解析第 {i} 行数据失败: {e}")
            
            logger.info(f"成功加载 {len(doors)} 个门节点")
            return doors
            
        except Exception as e:
            logger.error(f"加载门数据失败: {e}")
            raise
    
    def load_stairways(self, file_path: str) -> List[Stairway]:
        """
        加载楼梯数据
        
        Args:
            file_path: 楼梯数据文件路径
            
        Returns:
            楼梯对象列表
        """
        try:
            data = self._read_tsv_file(file_path)
            headers = data[0]
            
            stairways = []
            for i, row in enumerate(data[1:], start=2):
                try:
                    if len(row) != len(headers):
                        logger.warning(f"第 {i} 行字段数量不匹配，跳过")
                        continue
                    
                    stairway = Stairway(
                        id=int(row[0]),
                        stairway_id=row[1],
                        stairway_name=row[2],
                        map_id=row[3],
                        upper_map_id=self._parse_optional_str(row[4]),
                        lower_map_id=self._parse_optional_str(row[5]),
                        x=float(row[6]),
                        y=float(row[7]),
                        description=row[8],
                        is_active=self._parse_bool(row[9]),
                        upper_stairway_id=self._parse_optional_str(row[12]) if len(row) > 12 else None,
                        lower_stairway_id=self._parse_optional_str(row[13]) if len(row) > 13 else None
                    )
                    stairways.append(stairway)
                except Exception as e:
                    logger.error(f"解析第 {i} 行数据失败: {e}")
                    raise DataFormatError(f"解析第 {i} 行数据失败: {e}")
            
            logger.info(f"成功加载 {len(stairways)} 个楼梯")
            return stairways
            
        except Exception as e:
            logger.error(f"加载楼梯数据失败: {e}")
            raise
    
    def load_graph_edges(self, file_path: str) -> List[GraphEdge]:
        """
        加载图边数据
        
        Args:
            file_path: 图边数据文件路径
            
        Returns:
            图边对象列表
        """
        try:
            data = self._read_tsv_file(file_path)
            headers = data[0]
            
            edges = []
            for i, row in enumerate(data[1:], start=2):
                try:
                    if len(row) != len(headers):
                        logger.warning(f"第 {i} 行字段数量不匹配，跳过")
                        continue
                    
                    # node_a_id 和 node_b_id 可能是整数或字符串
                    node_a_id = row[2]
                    if row[1] == '1':  # 门节点，ID 是整数
                        node_a_id = int(node_a_id)
                    
                    node_b_id = row[4]
                    if row[3] == '1':  # 门节点，ID 是整数
                        node_b_id = int(node_b_id)
                    
                    edge = GraphEdge(
                        id=int(row[0]),
                        node_a_type=int(row[1]),
                        node_a_id=node_a_id,
                        node_b_type=int(row[3]),
                        node_b_id=node_b_id,
                        weight=float(row[5])
                    )
                    edges.append(edge)
                except Exception as e:
                    logger.error(f"解析第 {i} 行数据失败: {e}")
                    raise DataFormatError(f"解析第 {i} 行数据失败: {e}")
            
            logger.info(f"成功加载 {len(edges)} 条边")
            return edges
            
        except Exception as e:
            logger.error(f"加载图边数据失败: {e}")
            raise
    
    def load_rfid_devices(self, file_path: str) -> List[RFIDDevice]:
        """
        加载 RFID 设备数据
        
        Args:
            file_path: RFID 设备数据文件路径
            
        Returns:
            RFID 设备对象列表
        """
        try:
            data = self._read_tsv_file(file_path)
            headers = data[0]
            
            devices = []
            for i, row in enumerate(data[1:], start=2):
                try:
                    if len(row) != len(headers):
                        logger.warning(f"第 {i} 行字段数量不匹配，跳过")
                        continue
                    
                    device = RFIDDevice(
                        id=int(row[0]),
                        device_name=row[1],
                        map_id=row[2],
                        x=float(row[3]),
                        y=float(row[4]),
                        stairway_id=self._parse_optional_str(row[5]),
                        door_id=self._parse_optional_int(row[6]),
                        is_active=self._parse_bool(row[8])
                    )
                    devices.append(device)
                except Exception as e:
                    logger.error(f"解析第 {i} 行数据失败: {e}")
                    raise DataFormatError(f"解析第 {i} 行数据失败: {e}")
            
            logger.info(f"成功加载 {len(devices)} 个 RFID 设备")
            return devices
            
        except Exception as e:
            logger.error(f"加载 RFID 设备数据失败: {e}")
            raise
