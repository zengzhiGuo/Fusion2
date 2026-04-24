package com.building.mapper;

import com.building.entity.GraphEdge;
import org.apache.ibatis.annotations.*;

import java.util.List;

/**
 * 图的边Mapper接口（简化版）
 * 所有边都是双向的
 */
@Mapper
public interface GraphEdgeMapper {
    
    /**
     * 插入新边
     */
    @Insert("INSERT INTO graph_edges (node_a_type, node_a_id, node_b_type, node_b_id, weight) " +
            "VALUES (#{nodeAType}, #{nodeAId}, #{nodeBType}, #{nodeBId}, #{weight})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(GraphEdge edge);
    
    /**
     * 更新边信息
     */
    @Update("UPDATE graph_edges SET weight = #{weight} " +
            "WHERE node_a_type = #{nodeAType} AND node_a_id = #{nodeAId} " +
            "AND node_b_type = #{nodeBType} AND node_b_id = #{nodeBId}")
    int update(GraphEdge edge);
    
    /**
     * 根据ID删除边
     */
    @Delete("DELETE FROM graph_edges WHERE id = #{id}")
    int deleteById(Long id);
    
    /**
     * 根据两个节点删除边
     */
    @Delete("DELETE FROM graph_edges " +
            "WHERE (node_a_type = #{nodeAType} AND node_a_id = #{nodeAId} " +
            "AND node_b_type = #{nodeBType} AND node_b_id = #{nodeBId}) " +
            "OR (node_a_type = #{nodeBType} AND node_a_id = #{nodeBId} " +
            "AND node_b_type = #{nodeAType} AND node_b_id = #{nodeAId})")
    int deleteByNodes(@Param("nodeAType") Integer nodeAType, 
                      @Param("nodeAId") String nodeAId,
                      @Param("nodeBType") Integer nodeBType, 
                      @Param("nodeBId") String nodeBId);
    
    /**
     * 根据ID查询边
     */
    @Select("SELECT * FROM graph_edges WHERE id = #{id}")
    GraphEdge selectById(Long id);
    
    /**
     * 查询所有边
     */
    @Select("SELECT * FROM graph_edges ORDER BY create_time DESC")
    List<GraphEdge> selectAll();
    
    /**
     * 查询某个节点的所有邻接边（双向边，查询两个方向）
     */
    @Select("SELECT * FROM graph_edges " +
            "WHERE (node_a_type = #{nodeType} AND node_a_id = #{nodeId}) " +
            "OR (node_b_type = #{nodeType} AND node_b_id = #{nodeId})")
    List<GraphEdge> selectAdjacentEdges(@Param("nodeType") Integer nodeType, 
                                         @Param("nodeId") String nodeId);
    
    /**
     * 查询两个节点之间的边
     */
    @Select("SELECT * FROM graph_edges " +
            "WHERE (node_a_type = #{nodeAType} AND node_a_id = #{nodeAId} " +
            "AND node_b_type = #{nodeBType} AND node_b_id = #{nodeBId}) " +
            "OR (node_a_type = #{nodeBType} AND node_a_id = #{nodeBId} " +
            "AND node_b_type = #{nodeAType} AND node_b_id = #{nodeAId})")
    GraphEdge selectByNodes(@Param("nodeAType") Integer nodeAType, 
                           @Param("nodeAId") String nodeAId,
                           @Param("nodeBType") Integer nodeBType, 
                           @Param("nodeBId") String nodeBId);
    
    /**
     * 删除与某个节点相关的所有边
     */
    @Delete("DELETE FROM graph_edges " +
            "WHERE (node_a_type = #{nodeType} AND node_a_id = #{nodeId}) " +
            "OR (node_b_type = #{nodeType} AND node_b_id = #{nodeId})")
    int deleteByNode(@Param("nodeType") Integer nodeType, 
                     @Param("nodeId") String nodeId);
    
    /**
     * 按边类型统计数量
     */
    @Select("SELECT " +
            "CASE " +
            "  WHEN node_a_type = 1 AND node_b_type = 1 THEN 'doors-doors' " +
            "  WHEN node_a_type = 2 AND node_b_type = 2 THEN 'stairways-stairways' " +
            "  ELSE 'doors-stairways' " +
            "END AS edge_type, " +
            "COUNT(*) AS count " +
            "FROM graph_edges " +
            "GROUP BY edge_type")
    @MapKey("edge_type")
    List<java.util.Map<String, Object>> countByType();
}
