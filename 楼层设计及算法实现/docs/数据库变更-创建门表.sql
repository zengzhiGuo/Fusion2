-- 创建门信息表
-- 执行日期: 2026-04-14

create table if not exists ship_floor.doors (
    id            bigint auto_increment comment '门唯一标识（主键）'
        primary key,
    room_name     varchar(100)                         not null comment '房间名称',
    map_id        varchar(50)                          not null comment '门所在楼层ID',
    x             decimal(10, 4)                       not null comment '门X坐标（米）',
    y             decimal(10, 4)                       not null comment '门Y坐标（米）',
    description   varchar(500)                         null comment '门描述',
    is_active     tinyint(1) default 1                 null comment '是否启用：0-禁用，1-启用',
    create_time   datetime   default CURRENT_TIMESTAMP null comment '创建时间',
    update_time   datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间'
)
    comment '门信息表';

-- 创建索引
create index idx_map_id
    on ship_floor.doors (map_id);

create index idx_room_name
    on ship_floor.doors (room_name);

-- 字段说明：
-- id: 门的唯一标识（自增主键）
-- room_name: 房间名称，表示这个门通向哪个房间
-- map_id: 门所在的楼层ID，决定门标记显示在哪个地图上
-- x, y: 门在地图上的坐标位置（单位：米）
-- description: 可选的描述信息
-- is_active: 软删除标记

-- 示例数据：
-- INSERT INTO ship_floor.doors (room_name, map_id, x, y, description) 
-- VALUES ('会议室A', 'floor3', 10.5, 20.3, '主入口');
