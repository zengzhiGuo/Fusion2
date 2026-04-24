-- 为 stairways 表添加所在楼层ID字段
-- 执行日期: 2026-04-13

ALTER TABLE ship_floor.stairways
ADD COLUMN map_id varchar(50) null comment '楼梯所在楼层ID' AFTER stairway_name;

-- 字段说明：
-- map_id: 楼梯所在的楼层ID，表示这个楼梯标注在哪个楼层的地图上（必填，只读）
-- 与 upper_map_id 和 lower_map_id 的区别：
--   - map_id: 楼梯标注的物理位置所在的楼层（决定楼梯标记显示在哪个地图上）
--   - upper_map_id: 楼梯连接的上层楼层（逻辑连接关系，可选）
--   - lower_map_id: 楼梯连接的下层楼层（逻辑连接关系，可选）

-- 重要：楼梯标记只会显示在 map_id 对应的地图上，不会显示在 upper_map_id 或 lower_map_id 的地图上

-- 示例：
-- 如果在3楼地图上标注了一个楼梯，这个楼梯连接3楼和2楼
-- 则：map_id = 'floor3', upper_map_id = 'floor3', lower_map_id = 'floor2'
-- 这个楼梯标记只会显示在3楼的地图上
