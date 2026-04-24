package com.building.controller;

import com.building.entity.Stairway;
import com.building.service.StairwayService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/stairways")
@CrossOrigin(origins = "*")
public class StairwayController {

    @Autowired
    private StairwayService stairwayService;

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getAllStairways() {
        List<Stairway> list = stairwayService.getAllStairways();
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{stairwayId}")
    public ResponseEntity<Map<String, Object>> getStairwayById(@PathVariable String stairwayId) {
        Stairway stairway = stairwayService.getStairwayById(stairwayId);
        Map<String, Object> result = new HashMap<>();
        if (stairway != null) {
            result.put("data", stairway);
            return ResponseEntity.ok(result);
        } else {
            result.put("message", "楼梯不存在");
            return ResponseEntity.badRequest().body(result);
        }
    }

    @GetMapping("/map/{mapId}")
    public ResponseEntity<Map<String, Object>> getStairwaysByMapId(@PathVariable String mapId) {
        List<Stairway> list = stairwayService.getStairwaysByMapId(mapId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addStairway(@RequestBody Stairway stairway) {
        Map<String, Object> result = new HashMap<>();
        boolean success = stairwayService.addStairway(stairway);
        result.put("success", success);
        result.put("message", success ? "添加成功" : "添加失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    @PutMapping
    public ResponseEntity<Map<String, Object>> updateStairway(@RequestBody Stairway stairway) {
        Map<String, Object> result = new HashMap<>();
        boolean success = stairwayService.updateStairway(stairway);
        result.put("success", success);
        result.put("message", success ? "更新成功" : "更新失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    @DeleteMapping("/{stairwayId}")
    public ResponseEntity<Map<String, Object>> deleteStairway(@PathVariable String stairwayId) {
        Map<String, Object> result = new HashMap<>();
        boolean success = stairwayService.deleteStairway(stairwayId);
        result.put("success", success);
        result.put("message", success ? "删除成功" : "删除失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    /**
     * 获取指定楼层的所有楼梯（用于选择连接）
     */
    @GetMapping("/floor/{mapId}/available")
    public ResponseEntity<Map<String, Object>> getAvailableStairwaysForConnection(@PathVariable String mapId) {
        List<Stairway> list = stairwayService.getStairwaysByMapId(mapId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    /**
     * 更新楼梯的上层连接
     */
    @PutMapping("/{stairwayId}/upper-connection")
    public ResponseEntity<Map<String, Object>> updateUpperConnection(
            @PathVariable String stairwayId,
            @RequestBody Map<String, String> request) {
        Map<String, Object> result = new HashMap<>();
        String upperStairwayId = request.get("upperStairwayId");
        boolean success = stairwayService.updateUpperConnection(stairwayId, upperStairwayId);
        result.put("success", success);
        result.put("message", success ? "上层连接更新成功" : "上层连接更新失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    /**
     * 更新楼梯的下层连接
     */
    @PutMapping("/{stairwayId}/lower-connection")
    public ResponseEntity<Map<String, Object>> updateLowerConnection(
            @PathVariable String stairwayId,
            @RequestBody Map<String, String> request) {
        Map<String, Object> result = new HashMap<>();
        String lowerStairwayId = request.get("lowerStairwayId");
        boolean success = stairwayService.updateLowerConnection(stairwayId, lowerStairwayId);
        result.put("success", success);
        result.put("message", success ? "下层连接更新成功" : "下层连接更新失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    /**
     * 获取楼梯的连接信息（包括连接的楼梯详情）
     */
    @GetMapping("/{stairwayId}/connections")
    public ResponseEntity<Map<String, Object>> getStairwayConnections(@PathVariable String stairwayId) {
        Map<String, Object> connections = stairwayService.getStairwayConnections(stairwayId);
        Map<String, Object> result = new HashMap<>();
        if (connections != null) {
            result.put("data", connections);
            return ResponseEntity.ok(result);
        } else {
            result.put("message", "楼梯不存在");
            return ResponseEntity.badRequest().body(result);
        }
    }
}
