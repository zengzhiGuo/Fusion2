package com.building.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class RfidDevice {
    private Long id;
    private String deviceName;
    private String mapId;
    private Double x;
    private Double y;
    private String stairwayId;
    private Long doorId;
    private String description;
    private Boolean isActive;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}


