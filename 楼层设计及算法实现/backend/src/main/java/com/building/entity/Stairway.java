package com.building.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Stairway {
    private Long id;
    private String stairwayId;
    private String stairwayName;
    private String mapId;
    private String upperMapId;
    private String lowerMapId;
    private String upperStairwayId;
    private String lowerStairwayId;
    private Double x;
    private Double y;
    private String description;
    private Boolean isActive;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
