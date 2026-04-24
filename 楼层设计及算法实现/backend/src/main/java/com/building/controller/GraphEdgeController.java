package com.building.controller;

import com.building.entity.GraphEdge;
import com.building.service.GraphEdgeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 图的边控制器（简化版）
 * 所有边都是双向的
 */
@RestController
@RequestMapping("/api/graph-edges")
@CrossOrigin(origins = "*")
public class GraphEdgeController {
    
    @Autowired
    private GraphEdgeService graphEdgeService;
    
    /**
     * 创建新边
     */
    @PostMapping
    public ResponseEntity<?> createEdge(@RequestBody GraphEdge edge) {
        try {
            GraphEdge created = graphEdgeService.createEdge(edge);
            return ResponseEntity.ok(created);
        } catch (RuntimeException e) {
            // 返回错误信息给前端
            return ResponseEntity.badRequest()
                    .body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "创建边失败"));
        }
    }
    
    /**
     * 批量创建边
     */
    @PostMapping("/batch")
    public ResponseEntity<?> createEdgesBatch(@RequestBody List<GraphEdge> edges) {
        try {
            Map<String, Object> result = graphEdgeService.createEdgesBatch(edges);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "批量创建边失败: " + e.getMessage()));
        }
    }
    
    /**
     * 批量删除边
     */
    @DeleteMapping("/batch")
    public ResponseEntity<?> deleteEdgesBatch(@RequestBody List<Long> edgeIds) {
        try {
            int deletedCount = 0;
            for (Long edgeId : edgeIds) {
                if (graphEdgeService.deleteEdge(edgeId)) {
                    deletedCount++;
                }
            }
            Map<String, Object> result = new java.util.HashMap<>();
            result.put("deletedCount", deletedCount);
            result.put("totalCount", edgeIds.size());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "批量删除边失败: " + e.getMessage()));
        }
    }
    
    /**
     * 更新边信息（只能更新权重）
     */
    @PutMapping
    public ResponseEntity<GraphEdge> updateEdge(@RequestBody GraphEdge edge) {
        try {
            GraphEdge updated = graphEdgeService.updateEdge(edge);
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 根据ID删除边
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteEdge(@PathVariable Long id) {
        try {
            boolean deleted = graphEdgeService.deleteEdge(id);
            if (deleted) {
                return ResponseEntity.ok().build();
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 根据两个节点删除边
     */
    @DeleteMapping("/nodes")
    public ResponseEntity<Void> deleteEdgeByNodes(@RequestBody Map<String, Object> body) {
        try {
            Integer nodeAType = (Integer) body.get("nodeAType");
            String nodeAId = (String) body.get("nodeAId");
            Integer nodeBType = (Integer) body.get("nodeBType");
            String nodeBId = (String) body.get("nodeBId");
            
            boolean deleted = graphEdgeService.deleteEdgeByNodes(nodeAType, nodeAId, nodeBType, nodeBId);
            if (deleted) {
                return ResponseEntity.ok().build();
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 根据ID查询边
     */
    @GetMapping("/{id}")
    public ResponseEntity<GraphEdge> getEdge(@PathVariable Long id) {
        GraphEdge edge = graphEdgeService.getEdgeById(id);
        if (edge != null) {
            return ResponseEntity.ok(edge);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 查询所有边
     */
    @GetMapping("/list")
    public ResponseEntity<List<GraphEdge>> getAllEdges() {
        List<GraphEdge> edges = graphEdgeService.getAllEdges();
        return ResponseEntity.ok(edges);
    }
    
    /**
     * 查询某个节点的所有邻接边
     */
    @GetMapping("/adjacent/{nodeType}/{nodeId}")
    public ResponseEntity<List<GraphEdge>> getAdjacentEdges(
            @PathVariable Integer nodeType,
            @PathVariable String nodeId) {
        List<GraphEdge> edges = graphEdgeService.getAdjacentEdges(nodeType, nodeId);
        return ResponseEntity.ok(edges);
    }
    
    /**
     * 查询两个节点之间的边
     */
    @GetMapping("/between")
    public ResponseEntity<GraphEdge> getEdgeBetweenNodes(
            @RequestParam Integer nodeAType,
            @RequestParam String nodeAId,
            @RequestParam Integer nodeBType,
            @RequestParam String nodeBId) {
        GraphEdge edge = graphEdgeService.getEdgeByNodes(nodeAType, nodeAId, nodeBType, nodeBId);
        if (edge != null) {
            return ResponseEntity.ok(edge);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 删除与某个节点相关的所有边
     */
    @DeleteMapping("/node/{nodeType}/{nodeId}")
    public ResponseEntity<Map<String, Integer>> deleteEdgesByNode(
            @PathVariable Integer nodeType,
            @PathVariable String nodeId) {
        try {
            int count = graphEdgeService.deleteEdgesByNode(nodeType, nodeId);
            return ResponseEntity.ok(Map.of("deletedCount", count));
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 按边类型统计数量
     */
    @GetMapping("/stats/by-type")
    public ResponseEntity<List<Map<String, Object>>> getEdgeStatsByType() {
        List<Map<String, Object>> stats = graphEdgeService.countByType();
        return ResponseEntity.ok(stats);
    }
}
