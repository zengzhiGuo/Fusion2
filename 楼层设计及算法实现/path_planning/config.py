"""
配置文件
"""

import logging

# 日志配置
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 路径规划配置
CROSS_FLOOR_WEIGHT = 10.0  # 跨楼层边的权重（米）
MAX_NEAREST_NODE_DISTANCE = 50.0  # 最近节点的最大距离（米）
PATH_CALCULATION_TIMEOUT = 5.0  # 路径计算超时时间（秒）

# 数据文件路径
DATA_DIR = 'path_planning/database_export'
MAPS_FILE = f'{DATA_DIR}/maps_data.txt'
DOORS_FILE = f'{DATA_DIR}/doors_data.txt'
STAIRWAYS_FILE = f'{DATA_DIR}/stairways_data.txt'
GRAPH_EDGES_FILE = f'{DATA_DIR}/graph_edges_data.txt'
RFID_DEVICES_FILE = f'{DATA_DIR}/rfid_devices_data.txt'


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )
