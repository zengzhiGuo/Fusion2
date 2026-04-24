package com.building.controller;

import com.building.entity.RfidDevice;
import com.building.service.RfidDeviceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/rfid-devices")
@CrossOrigin(origins = "*")
public class RfidDeviceController {

    @Autowired
    private RfidDeviceService rfidDeviceService;

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getAllDevices() {
        List<RfidDevice> list = rfidDeviceService.getAllDevices();
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getDeviceById(@PathVariable Long id) {
        RfidDevice device = rfidDeviceService.getDeviceById(id);
        Map<String, Object> result = new HashMap<>();
        if (device != null) {
            result.put("data", device);
            return ResponseEntity.ok(result);
        } else {
            result.put("message", "RFID设备不存在");
            return ResponseEntity.badRequest().body(result);
        }
    }

    @GetMapping("/map/{mapId}")
    public ResponseEntity<Map<String, Object>> getDevicesByMapId(@PathVariable String mapId) {
        List<RfidDevice> list = rfidDeviceService.getDevicesByMapId(mapId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/stairway/{stairwayId}")
    public ResponseEntity<Map<String, Object>> getDevicesByStairwayId(@PathVariable String stairwayId) {
        List<RfidDevice> list = rfidDeviceService.getDevicesByStairwayId(stairwayId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @GetMapping("/door/{doorId}")
    public ResponseEntity<Map<String, Object>> getDevicesByDoorId(@PathVariable Long doorId) {
        List<RfidDevice> list = rfidDeviceService.getDevicesByDoorId(doorId);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return ResponseEntity.ok(result);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addDevice(@RequestBody RfidDevice device) {
        Map<String, Object> result = new HashMap<>();
        boolean success = rfidDeviceService.addDevice(device);
        result.put("success", success);
        result.put("message", success ? "添加成功" : "添加失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    @PutMapping
    public ResponseEntity<Map<String, Object>> updateDevice(@RequestBody RfidDevice device) {
        Map<String, Object> result = new HashMap<>();
        boolean success = rfidDeviceService.updateDevice(device);
        result.put("success", success);
        result.put("message", success ? "更新成功" : "更新失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteDevice(@PathVariable Long id) {
        Map<String, Object> result = new HashMap<>();
        boolean success = rfidDeviceService.deleteDevice(id);
        result.put("success", success);
        result.put("message", success ? "删除成功" : "删除失败");
        return success ? ResponseEntity.ok(result) : ResponseEntity.badRequest().body(result);
    }
}
