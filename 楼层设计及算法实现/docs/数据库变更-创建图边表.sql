-- 创建图的边表，用于存储节点之间的连接关系（简化版）
-- 执行日期: 2026-04-14
-- 说明：所有边都是双向边，支持三种连接类型：
--   1. stairways-stairways（楼梯到楼梯，跨楼层）
--   2. stairways-doors（楼梯到房间/楼道/出入口）
--   3. doors-doors（房间/楼道/出入口之间）

CREATE TABLE IF NOT EXISTS ship_floor.graph_edges (
    id BIGINT AUTO_INCREMENT COMMENT '自增主键' PRIMARY KEY,
    
    -- 节点A信息
    node_a_type TINYINT(1) NOT NULL COMMENT '节点A类型：1-doors表，2-stairways表',
    node_a_id VARCHAR(50) NOT NULL COMMENT '节点A的ID',
    
    -- 节点B信息
    node_b_type TINYINT(1) NOT NULL COMMENT '节点B类型：1-doors表，2-stairways表',
    node_b_id VARCHAR(50) NOT NULL COMMENT '节点B的ID',
    
    -- 边的属性
    weight DECIMAL(10, 2) DEFAULT 1.0 COMMENT '边的权重（距离，单位：米）',
    
    -- 时间戳
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 唯一约束（确保不重复创建边，使用较小的ID在前）
    CONSTRAINT uk_edge UNIQUE (node_a_type, node_a_id, node_b_type, node_b_id),
    
    -- 索引
    INDEX idx_node_a (node_a_type, node_a_id),
    INDEX idx_node_b (node_b_type, node_b_id)
) COMMENT '图的边表，存储节点之间的双向连接关系';

-- 字段说明：
-- 1. node_a_type / node_b_type: 节点类型
--    - 1: doors表中的节点（房间/楼道/出入口）
--    - 2: stairways表中的节点（楼梯）
-- 2. node_a_id / node_b_id: 对应表中的ID
--    - 如果 node_type=1，则为 doors.id
--    - 如果 node_type=2，则为 stairways.stairway_id
-- 3. weight: 边的权重，表示两点之间的距离（米）
-- 4. 所有边都是双向的，可以双向通行

-- 三种边的类型：
-- 类型1：doors-doors（房间/楼道/出入口之间）
-- 类型2：doors-stairways（房间/楼道/出入口到楼梯）
-- 类型3：stairways-stairways（楼梯到楼梯，用于跨楼层连接）

-- 示例数据：

-- 1. doors-doors: 房间到楼道
INSERT INTO ship_floor.graph_edges 
(node_a_type, node_a_id, node_b_type, node_b_id, weight)
VALUES 
(1, '1', 1, '2', 5.5);

-- 2. doors-stairways: 楼道到楼梯
INSERT INTO ship_floor.graph_edges 
(node_a_type, node_a_id, node_b_type, node_b_id, weight)
VALUES 
(1, '2', 2, 'stairway_001', 3.2);

-- 3. stairways-stairways: 楼梯跨楼层连接（同一个楼梯在不同楼层的连接）
-- 注意：这种情况下，两个节点都是同一个楼梯，但在不同楼层
-- 实际上楼梯本身就包含了 upper_map_id 和 lower_map_id，所以这种边可能不需要
-- 如果需要连接不同的楼梯，可以这样：
INSERT INTO ship_floor.graph_edges 
(node_a_type, node_a_id, node_b_type, node_b_id, weight)
VALUES 
(2, 'stairway_001', 2, 'stairway_002', 10.0);

-- 4. doors-doors: 出入口到楼道
INSERT INTO ship_floor.graph_edges 
(node_a_type, node_a_id, node_b_type, node_b_id, weight)
VALUES 
(1, '10', 1, '11', 2.0);

-- 注意事项：
-- 1. 所有边都是双向的，A-B 和 B-A 是同一条边
-- 2. 唯一约束确保不会重复创建边
-- 3. 权重可以根据两点坐标自动计算欧几里得距离
-- 4. 插入时建议将较小的ID放在 node_a，较大的ID放在 node_b（便于查询和去重）

-- 查询示例：

-- 查询某个节点的所有邻接边（双向边，需要查询两个方向）
-- 示例：查询 doors.id=1 的所有邻接边
SELECT * FROM ship_floor.graph_edges 
WHERE (node_a_type = 1 AND node_a_id = '1') 
   OR (node_b_type = 1 AND node_b_id = '1');

-- 查询某个楼梯的所有邻接边
-- 示例：查询 stairway_id='stairway_001' 的所有邻接边
SELECT * FROM ship_floor.graph_edges 
WHERE (node_a_type = 2 AND node_a_id = 'stairway_001') 
   OR (node_b_type = 2 AND node_b_id = 'stairway_001');

-- 查询两个节点之间是否有边
-- 示例：查询 doors.id=1 和 doors.id=2 之间是否有边
SELECT * FROM ship_floor.graph_edges 
WHERE (node_a_type = 1 AND node_a_id = '1' AND node_b_type = 1 AND node_b_id = '2')
   OR (node_a_type = 1 AND node_a_id = '2' AND node_b_type = 1 AND node_b_id = '1');

-- 统计各类型边的数量
SELECT 
    CASE 
        WHEN node_a_type = 1 AND node_b_type = 1 THEN 'doors-doors'
        WHEN node_a_type = 2 AND node_b_type = 2 THEN 'stairways-stairways'
        ELSE 'doors-stairways'
    END AS edge_type,
    COUNT(*) AS count
FROM ship_floor.graph_edges
GROUP BY edge_type;
