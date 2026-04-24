package com.ship.dto;

import lombok.Data;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 围栏DTO
 */
@Data
public class RegionDto {
    private String regionId;
    private String regionName;
    private String mapId;
    private String description;
    private String color;
    private Double fillOpacity;
    private Double strokeWidth;
    private Boolean isActive;
    private List<CoordinateDto> coordinates;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CoordinateDto {
        private Integer pointOrder;

        @JsonProperty("xCoordinate")
        @JsonAlias({"x", "lng", "lon"})
        private Double xCoordinate;

        @JsonProperty("yCoordinate")
        @JsonAlias({"y", "lat"})
        private Double yCoordinate;
    }
}
