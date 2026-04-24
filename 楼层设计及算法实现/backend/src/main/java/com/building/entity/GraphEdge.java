package com.building.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 图的边实体类（简化版）
 * 用于存储节点之间的双向连接关系
 * 支持三种边类型：doors-doors, doors-stairways, stairways-stairways
 */
@Data
public class GraphEdge {
    /**
     * 主键ID
     */
    private Long id;
    
    /**
     * 节点A类型：1-doors表，2-stairways表
     */
    private Integer nodeAType;
    
    /**
     * 节点A的ID
     */
    private String nodeAId;
    
    /**
     * 节点B类型：1-doors表，2-stairways表
     */
    private Integer nodeBType;
    
    /**
     * 节点B的ID
     */
    private String nodeBId;
    
    /**
     * 边的权重（距离，单位：米）
     */
    private BigDecimal weight;
    
    /**
     * 创建时间
     */
    private LocalDateTime createTime;
    
    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
}
