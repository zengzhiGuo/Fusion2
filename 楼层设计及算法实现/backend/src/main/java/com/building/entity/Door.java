package com.building.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Door {
    private Long id;
    private String roomName;
    private Integer roomType;  // 1-房间，2-楼道
    private String mapId;
    private String targetRegionId;
    private String targetRegionName;
    private Double x;
    private Double y;
    private String description;
    private Boolean isActive;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
