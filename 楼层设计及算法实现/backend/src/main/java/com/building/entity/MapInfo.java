package com.building.entity;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class MapInfo {
    private String mapId;
    private String regionName;
    private String imagePath;
    private BigDecimal shipLengthM;
    private BigDecimal shipWidthM;
    private Integer imageWidthPx;
    private Integer imageHeightPx;
}
