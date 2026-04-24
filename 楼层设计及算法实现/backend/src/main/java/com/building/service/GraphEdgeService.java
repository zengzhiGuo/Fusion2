package com.building.service;

import com.building.entity.GraphEdge;
import com.building.mapper.GraphEdgeMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 图的边服务类（简化版）
 * 所有边都是双向的
 */
@Service
public class GraphEdgeService {
    
    @Autowired
    private GraphEdgeMapper graphEdgeMapper;
    
    /**
     * 创建新边（检查是否已存在）
     */
    @Transactional
    public GraphEdge createEdge(GraphEdge edge) {
        // 检查边是否已存在（双向检查）
        GraphEdge existingEdge = graphEdgeMapper.selectByNodes(
            edge.getNodeAType(), edge.getNodeAId(),
            edge.getNodeBType(), edge.getNodeBId()
        );
        
        if (existingEdge != null) {
            // 边已存在，抛出异常
            throw new RuntimeException("边已存在：节点 " + edge.getNodeAId() + " 和节点 " + edge.getNodeBId() + " 之间已有连接");
        }
        
        // 设置默认权重
        if (edge.getWeight() == null) {
            edge.setWeight(new BigDecimal("1.0"));
        }
        
        graphEdgeMapper.insert(edge);
        return edge;
    }
    
    /**
     * 批量创建边
     */
    @Transactional
    public Map<String, Object> createEdgesBatch(List<GraphEdge> edges) {
        int successCount = 0;
        int skipCount = 0;
        List<String> skippedEdges = new java.util.ArrayList<>();
        List<GraphEdge> createdEdges = new java.util.ArrayList<>();
        
        for (GraphEdge edge : edges) {
            try {
                // 检查边是否已存在
                GraphEdge existingEdge = graphEdgeMapper.selectByNodes(
                    edge.getNodeAType(), edge.getNodeAId(),
                    edge.getNodeBType(), edge.getNodeBId()
                );
                
                if (existingEdge != null) {
                    // 边已存在，跳过
                    skipCount++;
                    skippedEdges.add("节点 " + edge.getNodeAId() + " - " + edge.getNodeBId());
                    continue;
                }
                
                // 设置默认权重
                if (edge.getWeight() == null) {
                    edge.setWeight(new BigDecimal("1.0"));
                }
                
                graphEdgeMapper.insert(edge);
                createdEdges.add(edge);
                successCount++;
            } catch (Exception e) {
                skipCount++;
                skippedEdges.add("节点 " + edge.getNodeAId() + " - " + edge.getNodeBId() + " (错误: " + e.getMessage() + ")");
            }
        }
        
        Map<String, Object> result = new java.util.HashMap<>();
        result.put("successCount", successCount);
        result.put("skipCount", skipCount);
        result.put("skippedEdges", skippedEdges);
        result.put("createdEdges", createdEdges);
        
        return result;
    }
    
    /**
     * 更新边信息（只能更新权重）
     */
    @Transactional
    public GraphEdge updateEdge(GraphEdge edge) {
        graphEdgeMapper.update(edge);
        return graphEdgeMapper.selectById(edge.getId());
    }
    
    /**
     * 根据ID删除边
     */
    @Transactional
    public boolean deleteEdge(Long id) {
        return graphEdgeMapper.deleteById(id) > 0;
    }
    
    /**
     * 根据两个节点删除边
     */
    @Transactional
    public boolean deleteEdgeByNodes(Integer nodeAType, String nodeAId, 
                                     Integer nodeBType, String nodeBId) {
        return graphEdgeMapper.deleteByNodes(nodeAType, nodeAId, nodeBType, nodeBId) > 0;
    }
    
    /**
     * 根据ID查询边
     */
    public GraphEdge getEdgeById(Long id) {
        return graphEdgeMapper.selectById(id);
    }
    
    /**
     * 查询所有边
     */
    public List<GraphEdge> getAllEdges() {
        return graphEdgeMapper.selectAll();
    }
    
    /**
     * 查询某个节点的所有邻接边
     */
    public List<GraphEdge> getAdjacentEdges(Integer nodeType, String nodeId) {
        return graphEdgeMapper.selectAdjacentEdges(nodeType, nodeId);
    }
    
    /**
     * 查询两个节点之间的边
     */
    public GraphEdge getEdgeByNodes(Integer nodeAType, String nodeAId, 
                                    Integer nodeBType, String nodeBId) {
        return graphEdgeMapper.selectByNodes(nodeAType, nodeAId, nodeBType, nodeBId);
    }
    
    /**
     * 删除与某个节点相关的所有边
     */
    @Transactional
    public int deleteEdgesByNode(Integer nodeType, String nodeId) {
        return graphEdgeMapper.deleteByNode(nodeType, nodeId);
    }
    
    /**
     * 按边类型统计数量
     */
    public List<Map<String, Object>> countByType() {
        return graphEdgeMapper.countByType();
    }
}
