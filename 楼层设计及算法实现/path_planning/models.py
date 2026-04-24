"""
数据模型定义
定义船舶路径规划系统的核心数据结构
"""

from dataclasses import dataclass
from typing import Optional, Union, Tuple, List


# 节点类型定义
Node = Tuple[int, Union[int, str], str]
# (node_type, node_id, map_id)
# 例如：(1, 46, "floor1") 表示 floor1 的 46 号门
# 例如：(2, "stairway_xxx", "floor2") 表示 floor2 的某楼梯


@dataclass
class Map:
    """地图数据模型"""
    map_id: str
    region_name: str
    image_path: str
    ship_length_m: float
    ship_width_m: float
    image_width_px: Optional[int]
    image_height_px: Optional[int]


@dataclass
class Door:
    """门节点数据模型（包括房间、楼道、出入口）"""
    id: int
    room_name: str
    room_type: int  # 1=房间, 2=楼道, 3=出入口
    map_id: str
    x: float
    y: float
    description: str
    is_active: bool


@dataclass
class Stairway:
    """楼梯节点数据模型"""
    id: int
    stairway_id: str
    stairway_name: str
    map_id: str  # 楼梯所在楼层
    upper_map_id: Optional[str]  # 可以上到的楼层
    lower_map_id: Optional[str]  # 可以下到的楼层
    x: float
    y: float
    description: str
    is_active: bool
    upper_stairway_id: Optional[str] = None  # 上层连接的楼梯ID
    lower_stairway_id: Optional[str] = None  # 下层连接的楼梯ID


@dataclass
class GraphEdge:
    """图边数据模型"""
    id: int
    node_a_type: int  # 1=门, 2=楼梯
    node_a_id: Union[int, str]
    node_b_type: int
    node_b_id: Union[int, str]
    weight: float  # 距离（米）


@dataclass
class RFIDDevice:
    """RFID 设备数据模型"""
    id: int
    device_name: str
    map_id: str
    x: float
    y: float
    stairway_id: Optional[str]
    door_id: Optional[int]
    is_active: bool


@dataclass
class Position:
    """位置数据模型"""
    x: float
    y: float
    map_id: str


@dataclass
class NodeInfo:
    """节点信息"""
    node: Node
    name: str
    node_type: int  # 1=门, 2=楼梯
    map_id: str
    x: float
    y: float


@dataclass
class PathResult:
    """路径计算结果"""
    path: List[Node]  # 节点序列
    distance: float   # 总距离
    success: bool     # 是否成功
    error_message: Optional[str] = None


@dataclass
class Step:
    """路径中的一步"""
    step_number: int
    floor: str
    action: str  # "出发", "经过", "上楼", "下楼", "到达"
    location: str  # 房间名/楼梯名
    distance: float  # 本步距离


@dataclass
class PathDescription:
    """路径描述"""
    total_distance: float
    floors: List[str]  # 经过的楼层
    steps: List[Step]  # 每一步的描述


@dataclass
class PathPlanningResult:
    """路径规划结果"""
    success: bool
    path: Optional[List[Node]]
    distance: Optional[float]
    description: Optional[PathDescription]
    error_message: Optional[str] = None


@dataclass
class ConnectivityReport:
    """连通性报告"""
    is_connected: bool
    isolated_nodes: List[Node]
    num_components: int
    warnings: List[str]
