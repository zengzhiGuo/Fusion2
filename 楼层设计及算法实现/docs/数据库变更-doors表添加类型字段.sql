-- 为 doors 表添加类型字段，用于区分房间、楼道和出入口
-- 执行日期: 2026-04-14

ALTER TABLE ship_floor.doors
ADD COLUMN room_type TINYINT(1) DEFAULT 1 NOT NULL COMMENT '房间类型：1-房间，2-楼道，3-出入口' AFTER room_name;

-- 创建索引
CREATE INDEX idx_room_type ON ship_floor.doors (room_type);

-- 字段说明：
-- room_type: 房间类型
--   1 = 房间（默认值）
--   2 = 楼道
--   3 = 出入口

-- 注意事项：
-- 1. 默认值为1，所以现有数据会自动标记为"房间"
-- 2. 前端显示时根据 room_type 使用不同颜色：
--    - 房间：蓝色方块
--    - 楼道：紫色方块
--    - 出入口：红色方块
-- 3. 楼道和出入口可以包含多个RFID设备
-- 4. room_name 字段存储对应的名称

-- 示例数据：
-- 添加房间
-- INSERT INTO ship_floor.doors (room_name, room_type, map_id, x, y, description) 
-- VALUES ('会议室A', 1, 'floor3', 10.5, 20.3, '主会议室');

-- 添加楼道
-- INSERT INTO ship_floor.doors (room_name, room_type, map_id, x, y, description) 
-- VALUES ('东侧走廊', 2, 'floor3', 15.2, 25.8, '连接各个房间的走廊');

-- 添加出入口
-- INSERT INTO ship_floor.doors (room_name, room_type, map_id, x, y, description) 
-- VALUES ('主入口', 3, 'floor1', 5.0, 10.0, '船舶主入口');
