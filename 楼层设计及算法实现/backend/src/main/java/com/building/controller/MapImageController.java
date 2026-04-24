package com.building.controller;

import com.building.config.MapsConfig;
import com.building.entity.MapImage;
import com.building.service.MapImageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/map")
@CrossOrigin(origins = "*")
public class MapImageController {

    @Autowired
    private MapImageService mapImageService;

    @Autowired
    private MapsConfig mapsConfig;

    private static final String UPLOAD_DIR = "uploads/map-images/";

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadMapImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "remark", required = false) String remark) {
        Map<String, Object> response = new HashMap<>();
        try {
            MapImage savedImage = mapImageService.saveMapImage(file, remark);
            response.put("success", true);
            response.put("message", "地图图片上传成功");
            response.put("data", savedImage);
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            response.put("success", false);
            response.put("message", "上传失败: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> getMapImageList() {
        Map<String, Object> response = new HashMap<>();
        List<MapImage> images = mapImageService.getAllMapImages();
        response.put("success", true);
        response.put("data", images);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/image/{filename}")
    public ResponseEntity<Resource> getMapImage(@PathVariable String filename) {
        try {
            Path filePath = Paths.get(UPLOAD_DIR).resolve(filename).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                String contentType = getContentType(filename);
                return ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType(contentType))
                        .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filename + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/static/{filename}")
    public ResponseEntity<Resource> getStaticMapImage(@PathVariable String filename) {
        try {
            String staticPath = mapsConfig.getStaticPath();
            if (staticPath == null || staticPath.isEmpty()) {
                staticPath = "../frontend/maps";
            }
            Path filePath = Paths.get(staticPath).resolve(filename).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                String contentType = getContentType(filename);
                return ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType(contentType))
                        .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filename + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/download/{filename}")
    public ResponseEntity<Resource> downloadMapImage(@PathVariable String filename) {
        try {
            Path filePath = Paths.get(UPLOAD_DIR).resolve(filename).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                return ResponseEntity.ok()
                        .contentType(MediaType.APPLICATION_OCTET_STREAM)
                        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                        .body(resource);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (IOException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/delete/{id}")
    public ResponseEntity<Map<String, Object>> deleteMapImage(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        boolean success = mapImageService.deleteMapImage(id);
        if (success) {
            response.put("success", true);
            response.put("message", "删除成功");
        } else {
            response.put("success", false);
            response.put("message", "删除失败，图片不存在");
        }
        return ResponseEntity.ok(response);
    }

    private String getContentType(String filename) {
        String lowerName = filename.toLowerCase();
        if (lowerName.endsWith(".png")) return "image/png";
        if (lowerName.endsWith(".jpg") || lowerName.endsWith(".jpeg")) return "image/jpeg";
        if (lowerName.endsWith(".gif")) return "image/gif";
        if (lowerName.endsWith(".webp")) return "image/webp";
        return "application/octet-stream";
    }
}
