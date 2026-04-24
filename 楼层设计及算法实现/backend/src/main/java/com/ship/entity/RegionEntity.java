package com.ship.entity;

import lombok.Data;
import java.time.LocalDateTime;

/**
 * 围栏实体类
 */
@Data
public class RegionEntity {
    private String regionId;
    private String regionName;
    private String mapId;
    private String description;
    private String color;
    private Double fillOpacity;
    private Double strokeWidth;
    private Boolean isActive;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
