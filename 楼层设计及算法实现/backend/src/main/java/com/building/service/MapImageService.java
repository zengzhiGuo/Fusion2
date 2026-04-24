package com.building.service;

import com.building.entity.MapImage;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

public interface MapImageService {

    MapImage saveMapImage(MultipartFile file, String remark) throws IOException;

    List<MapImage> getAllMapImages();

    boolean deleteMapImage(Long id);
}
