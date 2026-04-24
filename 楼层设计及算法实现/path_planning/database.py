"""
数据库连接和查询模块
用于从MySQL数据库中读取地图、节点和边的数据
"""

import pymysql
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, host='localhost', port=3306, user='root', password='1234', database='ship_floor'):
        """
        初始化数据库连接
        
        Args:
            host: 数据库主机地址
            port: 数据库端口
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"成功连接到数据库: {self.database}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            return []
    
    def get_floors(self) -> List[Dict[str, Any]]:
        """获取所有楼层信息"""
        query = "SELECT * FROM floors ORDER BY floor_number"
        return self.execute_query(query)
    
    def get_nodes_by_floor(self, floor_id: int) -> List[Dict[str, Any]]:
        """
        获取指定楼层的所有节点
        
        Args:
            floor_id: 楼层ID
            
        Returns:
            节点列表
        """
        query = "SELECT * FROM nodes WHERE floor_id = %s"
        return self.execute_query(query, (floor_id,))
    
    def get_edges_by_floor(self, floor_id: int) -> List[Dict[str, Any]]:
        """
        获取指定楼层的所有边
        
        Args:
            floor_id: 楼层ID
            
        Returns:
            边列表
        """
        query = """
            SELECT e.* FROM edges e
            JOIN nodes n1 ON e.from_node_id = n1.id
            WHERE n1.floor_id = %s
        """
        return self.execute_query(query, (floor_id,))
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """获取所有边信息"""
        query = "SELECT * FROM edges"
        return self.execute_query(query)
    
    def get_doors(self) -> List[Dict[str, Any]]:
        """获取所有门信息"""
        query = "SELECT * FROM doors"
        return self.execute_query(query)
    
    def get_rfid_devices(self) -> List[Dict[str, Any]]:
        """获取所有RFID设备信息"""
        query = "SELECT * FROM rfid_devices"
        return self.execute_query(query)
    
    def get_stairways(self) -> List[Dict[str, Any]]:
        """获取所有楼梯信息，包括上下层连接关系"""
        query = "SELECT * FROM stairways"
        return self.execute_query(query)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


    def export_table_to_txt(self, table_name: str, output_dir: str = '.') -> bool:
        """
        导出表数据到txt文件（二维表格式，制表符分隔）
        
        Args:
            table_name: 表名
            output_dir: 输出目录
            
        Returns:
            是否成功
        """
        try:
            import os
            from datetime import datetime
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 查询表数据
            query = f"SELECT * FROM {table_name}"
            data = self.execute_query(query)
            
            # 生成文件名
            filename = os.path.join(output_dir, f"{table_name}_data.txt")
            
            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入表头信息
                f.write(f"# 表名: {table_name}\n")
                f.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 记录数量: {len(data)}\n")
                f.write("#" + "=" * 79 + "\n\n")
                
                if data:
                    # 获取列名
                    columns = list(data[0].keys())
                    
                    # 写入列名（表头）
                    f.write('\t'.join(columns) + '\n')
                    
                    # 写入数据行
                    for row in data:
                        values = []
                        for col in columns:
                            value = row[col]
                            # 处理None值和换行符
                            if value is None:
                                values.append('NULL')
                            else:
                                # 转换为字符串并替换制表符和换行符
                                str_value = str(value).replace('\t', ' ').replace('\n', ' ').replace('\r', '')
                                values.append(str_value)
                        f.write('\t'.join(values) + '\n')
                else:
                    f.write("# 表中没有数据\n")
            
            logger.info(f"成功导出表 {table_name} 到 {filename}, 共 {len(data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"导出表 {table_name} 失败: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    # 要导出的表名列表
    tables = ['maps', 'doors', 'stairways', 'rfid_devices', 'graph_edges']
    
    # 使用上下文管理器自动管理连接
    with DatabaseManager(database='ship_floor') as db:
        print("开始导出数据库表信息...\n")
        
        # 导出所有表
        for table in tables:
            print(f"正在导出表: {table}")
            db.export_table_to_txt(table, output_dir='database_export')
        
        print("\n所有表导出完成！文件保存在 database_export 目录中")