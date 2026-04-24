package com.building.service.impl;

import com.building.entity.MapImage;
import com.building.service.MapImageService;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

@Service
public class MapImageServiceImpl implements MapImageService {

    private static final String UPLOAD_DIR = "uploads/map-images/";
    private final Map<Long, MapImage> imageStore = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public MapImageServiceImpl() {
        initUploadDir();
    }

    private void initUploadDir() {
        try {
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }
        } catch (IOException e) {
            throw new RuntimeException("无法创建上传目录", e);
        }
    }

    @Override
    public MapImage saveMapImage(MultipartFile file, String remark) throws IOException {
        String originalFilename = file.getOriginalFilename();
        String extension = getFileExtension(originalFilename);
        String newFilename = System.currentTimeMillis() + "_" + originalFilename;

        Path targetPath = Paths.get(UPLOAD_DIR).resolve(newFilename);
        Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);

        MapImage mapImage = new MapImage();
        mapImage.setId(idGenerator.getAndIncrement());
        mapImage.setImageName(originalFilename);
        mapImage.setImagePath("/api/map/image/" + newFilename);
        mapImage.setFileSize(file.getSize());
        mapImage.setContentType(file.getContentType());
        mapImage.setUploadTime(LocalDateTime.now());
        mapImage.setRemark(remark);

        imageStore.put(mapImage.getId(), mapImage);
        return mapImage;
    }

    @Override
    public List<MapImage> getAllMapImages() {
        return imageStore.values().stream()
                .sorted((a, b) -> b.getUploadTime().compareTo(a.getUploadTime()))
                .collect(Collectors.toList());
    }

    @Override
    public boolean deleteMapImage(Long id) {
        MapImage image = imageStore.remove(id);
        if (image != null) {
            String filename = image.getImagePath().substring(image.getImagePath().lastIndexOf("/") + 1);
            try {
                Path filePath = Paths.get(UPLOAD_DIR).resolve(filename);
                Files.deleteIfExists(filePath);
            } catch (IOException ignored) {
            }
            return true;
        }
        return false;
    }

    private String getFileExtension(String filename) {
        if (filename == null || filename.isEmpty()) {
            return "";
        }
        int lastDot = filename.lastIndexOf(".");
        return lastDot == -1 ? "" : filename.substring(lastDot);
    }
}
