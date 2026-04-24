-- 数据库变更：为楼梯表添加连接的楼梯ID字段
-- 日期：2026-04-16
-- 目的：实现跨楼层路径规划

-- 1. 添加新字段
ALTER TABLE stairways 
ADD COLUMN upper_stairway_id VARCHAR(50) COMMENT '上层连接的楼梯ID',
ADD COLUMN lower_stairway_id VARCHAR(50) COMMENT '下层连接的楼梯ID';

-- 2. 添加外键约束（可选）
-- ALTER TABLE stairways 
-- ADD CONSTRAINT fk_upper_stairway 
-- FOREIGN KEY (upper_stairway_id) REFERENCES stairways(stairway_id);

-- ALTER TABLE stairways 
-- ADD CONSTRAINT fk_lower_stairway 
-- FOREIGN KEY (lower_stairway_id) REFERENCES stairways(stairway_id);

-- 3. 示例数据更新
-- 假设 stairway_A 在 floor1，连接到 floor2 的 stairway_B
-- UPDATE stairways 
-- SET upper_stairway_id = 'stairway_B' 
-- WHERE stairway_id = 'stairway_A';

-- 4. 验证数据
-- SELECT 
--     s1.stairway_id AS '当前楼梯',
--     s1.stairway_name AS '楼梯名称',
--     s1.map_id AS '所在楼层',
--     s1.upper_map_id AS '上层楼层',
--     s1.upper_stairway_id AS '上层楼梯ID',
--     s2.stairway_name AS '上层楼梯名称'
-- FROM stairways s1
-- LEFT JOIN stairways s2 ON s1.upper_stairway_id = s2.stairway_id
-- WHERE s1.upper_stairway_id IS NOT NULL;

-- 说明：
-- 1. upper_stairway_id: 当前楼梯上楼后连接到的楼梯ID
-- 2. lower_stairway_id: 当前楼梯下楼后连接到的楼梯ID
-- 3. 如果楼梯不能上楼/下楼，对应字段为 NULL
-- 4. 连接的楼梯必须在对应的楼层（upper_map_id 或 lower_map_id）
