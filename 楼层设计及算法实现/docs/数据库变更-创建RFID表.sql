-- 创建RFID设备信息表
-- 执行日期: 2026-04-14

create table if not exists ship_floor.rfid_devices (
    id              bigint auto_increment comment 'RFID设备唯一标识（主键）'
        primary key,
    device_name     varchar(100)                         not null comment 'RFID设备名称',
    map_id          varchar(50)                          not null comment 'RFID设备所在楼层ID',
    x               decimal(10, 4)                       not null comment 'RFID设备X坐标（米）',
    y               decimal(10, 4)                       not null comment 'RFID设备Y坐标（米）',
    stairway_id     varchar(50)                          null comment '所属楼梯ID（可为空）',
    door_id         bigint                               null comment '所属门ID（可为空）',
    description     varchar(500)                         null comment 'RFID设备描述',
    is_active       tinyint(1) default 1                 null comment '是否启用：0-禁用，1-启用',
    create_time     datetime   default CURRENT_TIMESTAMP null comment '创建时间',
    update_time     datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_rfid_door
        foreign key (door_id) references doors (id)
            on delete set null
)
    comment 'RFID设备信息表';

-- 创建索引
create index idx_map_id
    on ship_floor.rfid_devices (map_id);

create index idx_stairway_id
    on ship_floor.rfid_devices (stairway_id);

create index idx_door_id
    on ship_floor.rfid_devices (door_id);

-- 字段说明：
-- id: RFID设备的唯一标识（自增主键）
-- device_name: RFID设备名称，用于标识设备
-- map_id: RFID设备所在的楼层ID，决定设备标记显示在哪个地图上（必填）
-- x, y: RFID设备在地图上的坐标位置（单位：米，必填）
-- stairway_id: 所属楼梯的ID，如果RFID设备安装在楼梯处（可选）
-- door_id: 所属门的ID，如果RFID设备安装在门处（可选）
-- description: 可选的描述信息
-- is_active: 软删除标记

-- 注意事项：
-- 1. stairway_id 和 door_id 都可以为空，表示RFID设备不属于任何楼梯或门
-- 2. stairway_id 和 door_id 可以同时为空，也可以只设置其中一个
-- 3. door_id 有外键约束，删除门时会自动将关联的RFID设备的door_id设为NULL

-- 示例数据：
-- 独立的RFID设备（不属于楼梯或门）
-- INSERT INTO ship_floor.rfid_devices (device_name, map_id, x, y, description) 
-- VALUES ('RFID-001', 'floor3', 10.5, 20.3, '走廊中央');

-- 属于楼梯的RFID设备
-- INSERT INTO ship_floor.rfid_devices (device_name, map_id, x, y, stairway_id, description) 
-- VALUES ('RFID-002', 'floor3', 15.2, 25.8, 'stairway_123', '楼梯入口');

-- 属于门的RFID设备
-- INSERT INTO ship_floor.rfid_devices (device_name, map_id, x, y, door_id, description) 
-- VALUES ('RFID-003', 'floor3', 8.7, 18.4, 1, '会议室门口');
