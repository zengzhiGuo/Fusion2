package com.ship.entity;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class RegionGridCellEntity {
    private Long id;
    private String regionId;
    private String mapId;
    private Integer gridX;
    private Integer gridY;
    private Double centerX;
    private Double centerY;
    private LocalDateTime createdAt;
}
