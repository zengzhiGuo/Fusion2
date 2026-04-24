package com.building.controller;

import com.building.config.MapsConfig;
import com.building.entity.MapInfo;
import com.building.service.MapInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/map-info")
@CrossOrigin(origins = "*")
public class MapInfoController {

    @Autowired
    private MapInfoService mapInfoService;

    @Autowired
    private MapsConfig mapsConfig;

    @Value("${upload.base-path:D:/uploads}")
    private String uploadBasePath;

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getMapList() {
        Map<String, Object> response = new HashMap<>();
        try {
            List<MapInfo> maps = mapInfoService.getAllMaps();
            response.put("success", true);
            response.put("data", maps);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "查询失败: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @GetMapping("/detail/{mapId}")
    public ResponseEntity<Map<String, Object>> getMapDetail(@PathVariable String mapId) {
        Map<String, Object> response = new HashMap<>();
        try {
            MapInfo mapInfo = mapInfoService.getMapById(mapId);
            if (mapInfo != null) {
                response.put("success", true);
                response.put("data", mapInfo);
                return ResponseEntity.ok(response);
            } else {
                response.put("success", false);
                response.put("message", "地图不存在");
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
            }
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "查询失败: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @GetMapping("/image")
    public ResponseEntity<Resource> getMapImage(
            @RequestParam("path") String imagePath) {
        try {
            String staticPath = mapsConfig.getStaticPath();
            Path filePath;

            if (imagePath.startsWith("maps/") && staticPath != null && !staticPath.isEmpty()) {
                String filename = imagePath.substring(5);
                filePath = Paths.get(staticPath).resolve(filename).normalize();
            } else {
                filePath = Paths.get(uploadBasePath).resolve(imagePath).normalize();
            }

            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                String contentType = getContentType(imagePath);
                return ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType(contentType))
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    private String getContentType(String filename) {
        String lowerName = filename.toLowerCase();
        if (lowerName.endsWith(".png")) return "image/png";
        if (lowerName.endsWith(".jpg") || lowerName.endsWith(".jpeg")) return "image/jpeg";
        if (lowerName.endsWith(".gif")) return "image/gif";
        if (lowerName.endsWith(".webp")) return "image/webp";
        if (lowerName.endsWith(".svg")) return "image/svg+xml";
        return "application/octet-stream";
    }
}
