package com.building.controller;

import com.building.entity.Door;
import com.building.service.DoorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/doors")
@CrossOrigin(origins = "*")
public class DoorController {

    @Autowired
    private DoorService doorService;

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getAllDoors() {
        List<Door> list = doorService.getAllDoors();
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getDoorById(@PathVariable Long id) {
        Door door = doorService.getDoorById(id);
        Map<String, Object> result = new HashMap<>();
        if (door == null) {
            result.put("message", "门不存在");
            return ResponseEntity.badRequest().body(result);
        }

        result.put("data", door);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/map/{mapId}")
    public ResponseEntity<Map<String, Object>> getDoorsByMapId(@PathVariable String mapId) {
        List<Door> list = doorService.getDoorsByMapId(mapId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/search")
    public ResponseEntity<Map<String, Object>> searchDoorsByRoomName(@RequestParam String roomName) {
        List<Door> list = doorService.getDoorsByRoomName(roomName);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/type/{roomType}")
    public ResponseEntity<Map<String, Object>> getDoorsByRoomType(@PathVariable Integer roomType) {
        List<Door> list = doorService.getDoorsByRoomType(roomType);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addDoor(@RequestBody Door door) {
        Map<String, Object> result = new HashMap<>();
        try {
            boolean success = doorService.addDoor(door);
            result.put("success", success);
            result.put("message", success ? "添加成功" : "添加失败");
            return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
        } catch (IllegalArgumentException e) {
            result.put("success", false);
            result.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PutMapping
    public ResponseEntity<Map<String, Object>> updateDoor(@RequestBody Door door) {
        Map<String, Object> result = new HashMap<>();
        try {
            boolean success = doorService.updateDoor(door);
            result.put("success", success);
            result.put("message", success ? "更新成功" : "更新失败");
            return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
        } catch (IllegalArgumentException e) {
            result.put("success", false);
            result.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteDoor(@PathVariable Long id) {
        Map<String, Object> result = new HashMap<>();
        boolean success = doorService.deleteDoor(id);
        result.put("success", success);
        result.put("message", success ? "删除成功" : "删除失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }
}
