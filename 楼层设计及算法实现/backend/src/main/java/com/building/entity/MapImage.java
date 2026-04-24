package com.building.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class MapImage {
    private Long id;
    private String imageName;
    private String imagePath;
    private Long fileSize;
    private String contentType;
    private LocalDateTime uploadTime;
    private String remark;
}
