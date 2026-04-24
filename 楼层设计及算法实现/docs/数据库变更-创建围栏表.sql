-- 创建围栏主表
CREATE TABLE IF NOT EXISTS regions (
    region_id VARCHAR(50) PRIMARY KEY COMMENT '围栏ID',
    region_name VARCHAR(100) NOT NULL COMMENT '围栏名称',
    map_id VARCHAR(50) NOT NULL COMMENT '关联地图ID',
    description TEXT COMMENT '描述信息',
    color VARCHAR(20) DEFAULT '#3B82F6' COMMENT '围栏颜色',
    fill_opacity DECIMAL(3,2) DEFAULT 0.3 COMMENT '填充透明度(0-1)',
    stroke_width DECIMAL(5,2) DEFAULT 0.2 COMMENT '边框宽度',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_map_id (map_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='围栏主表';

-- 创建围栏坐标点表
CREATE TABLE IF NOT EXISTS region_coordinates (
    coord_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '坐标点ID',
    region_id VARCHAR(50) NOT NULL COMMENT '围栏ID',
    point_order INT NOT NULL COMMENT '顶点顺序(从1开始)',
    x_coordinate DECIMAL(10,4) NOT NULL COMMENT 'X坐标(米)',
    y_coordinate DECIMAL(10,4) NOT NULL COMMENT 'Y坐标(米)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (region_id) REFERENCES regions(region_id) ON DELETE CASCADE,
    INDEX idx_region_id (region_id),
    UNIQUE KEY uk_region_point (region_id, point_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='围栏坐标点表';
