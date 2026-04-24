package com.ship.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 围栏坐标点实体类
 */
@Data
public class RegionCoordinateEntity {
    private Long coordId;
    private String regionId;
    private Integer pointOrder;

    @JsonProperty("xCoordinate")
    private Double xCoordinate;

    @JsonProperty("yCoordinate")
    private Double yCoordinate;
    private LocalDateTime createdAt;
}
