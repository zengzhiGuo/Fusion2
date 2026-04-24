package com.ship.controller;

import com.ship.dto.RegionDto;
import com.ship.entity.RegionCoordinateEntity;
import com.ship.entity.RegionEntity;
import com.ship.entity.RegionGridCellEntity;
import com.ship.mapper.RegionCoordinateMapper;
import com.ship.mapper.RegionMapper;
import com.ship.service.RegionGridCellService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;

@RestController
@RequestMapping("/api/regions")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class RegionController {

    private final RegionMapper regionMapper;
    private final RegionCoordinateMapper regionCoordinateMapper;
    private final RegionGridCellService regionGridCellService;

    @GetMapping
    public List<RegionEntity> getAllRegions() {
        return regionMapper.selectAll();
    }

    @GetMapping("/{regionId}")
    public RegionEntity getRegionById(@PathVariable String regionId) {
        RegionEntity region = regionMapper.selectById(regionId);
        if (region == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "围栏不存在");
        }
        return region;
    }

    @GetMapping("/{regionId}/coordinates")
    public List<RegionCoordinateEntity> getRegionCoordinates(@PathVariable String regionId) {
        return regionCoordinateMapper.selectByRegionId(regionId);
    }

    @GetMapping("/{regionId}/grid-cells")
    public List<RegionGridCellEntity> getRegionGridCells(@PathVariable String regionId) {
        return regionGridCellService.getByRegionId(regionId);
    }

    @GetMapping("/map/{mapId}")
    public List<RegionEntity> getRegionsByMapId(@PathVariable String mapId) {
        return regionMapper.selectByMapId(mapId);
    }

    @GetMapping("/map/{mapId}/grid-cells")
    public List<RegionGridCellEntity> getMapGridCells(@PathVariable String mapId) {
        return regionGridCellService.getByMapId(mapId);
    }

    @PostMapping("/{regionId}/rebuild-grid-cells")
    @Transactional
    public int rebuildRegionGridCells(@PathVariable String regionId) {
        RegionEntity region = regionMapper.selectById(regionId);
        if (region == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "围栏不存在");
        }

        List<RegionCoordinateEntity> coordinates = regionCoordinateMapper.selectByRegionId(regionId);
        regionGridCellService.rebuildRegionGridCells(regionId, region.getMapId(), coordinates);
        return coordinates.size();
    }

    @PostMapping("/rebuild-grid-cells")
    @Transactional
    public int rebuildAllRegionGridCells() {
        List<RegionEntity> regions = regionMapper.selectAll();
        for (RegionEntity region : regions) {
            List<RegionCoordinateEntity> coordinates = regionCoordinateMapper.selectByRegionId(region.getRegionId());
            regionGridCellService.rebuildRegionGridCells(region.getRegionId(), region.getMapId(), coordinates);
        }
        return regions.size();
    }

    @PostMapping
    @Transactional
    public String createRegion(@RequestBody RegionDto dto) {
        validateRegion(dto, false);

        RegionEntity region = new RegionEntity();
        region.setRegionId(isBlank(dto.getRegionId()) ? UUID.randomUUID().toString() : dto.getRegionId().trim());
        region.setRegionName(dto.getRegionName().trim());
        region.setMapId(dto.getMapId().trim());
        region.setDescription(dto.getDescription());
        region.setColor(dto.getColor() != null ? dto.getColor() : "#3B82F6");
        region.setFillOpacity(dto.getFillOpacity() != null ? dto.getFillOpacity() : 0.3);
        region.setStrokeWidth(dto.getStrokeWidth() != null ? dto.getStrokeWidth() : 0.2);
        region.setIsActive(dto.getIsActive() != null ? dto.getIsActive() : true);

        regionMapper.insert(region);

        List<RegionCoordinateEntity> coordinates = buildCoordinates(region.getRegionId(), dto.getCoordinates());
        regionCoordinateMapper.batchInsert(coordinates);
        regionGridCellService.rebuildRegionGridCells(region.getRegionId(), region.getMapId(), coordinates);

        return region.getRegionId();
    }

    @PutMapping
    @Transactional
    public int updateRegion(@RequestBody RegionDto dto) {
        validateRegion(dto, true);

        RegionEntity region = new RegionEntity();
        region.setRegionId(dto.getRegionId().trim());
        region.setRegionName(dto.getRegionName().trim());
        region.setMapId(dto.getMapId().trim());
        region.setDescription(dto.getDescription());
        region.setColor(dto.getColor());
        region.setFillOpacity(dto.getFillOpacity());
        region.setStrokeWidth(dto.getStrokeWidth());
        region.setIsActive(dto.getIsActive());

        int updated = regionMapper.update(region);
        if (updated == 0) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "围栏不存在");
        }

        regionCoordinateMapper.deleteByRegionId(region.getRegionId());
        List<RegionCoordinateEntity> coordinates = buildCoordinates(region.getRegionId(), dto.getCoordinates());
        regionCoordinateMapper.batchInsert(coordinates);
        regionGridCellService.rebuildRegionGridCells(region.getRegionId(), region.getMapId(), coordinates);

        return updated;
    }

    @DeleteMapping("/{regionId}")
    @Transactional
    public int deleteRegion(@PathVariable String regionId) {
        regionCoordinateMapper.deleteByRegionId(regionId);
        return regionMapper.delete(regionId);
    }

    private List<RegionCoordinateEntity> buildCoordinates(String regionId, List<RegionDto.CoordinateDto> coordinateDtos) {
        return IntStream.range(0, coordinateDtos.size())
            .mapToObj(index -> {
                RegionDto.CoordinateDto dto = coordinateDtos.get(index);
                if (dto.getXCoordinate() == null || dto.getYCoordinate() == null) {
                    throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "坐标点缺失或无效，请检查 xCoordinate/yCoordinate");
                }

                RegionCoordinateEntity coordinate = new RegionCoordinateEntity();
                coordinate.setRegionId(regionId);
                coordinate.setPointOrder(dto.getPointOrder() != null ? dto.getPointOrder() : index + 1);
                coordinate.setXCoordinate(dto.getXCoordinate());
                coordinate.setYCoordinate(dto.getYCoordinate());
                return coordinate;
            })
            .toList();
    }

    private void validateRegion(RegionDto dto, boolean requireId) {
        if (dto == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "请求体不能为空");
        }
        if (requireId && isBlank(dto.getRegionId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "regionId 不能为空");
        }
        if (isBlank(dto.getRegionName())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "regionName 不能为空");
        }
        if (isBlank(dto.getMapId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "mapId 不能为空");
        }
        if (dto.getCoordinates() == null || dto.getCoordinates().size() < 3) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "围栏至少需要 3 个坐标点");
        }
        if (dto.getFillOpacity() != null && (dto.getFillOpacity() < 0 || dto.getFillOpacity() > 1)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "fillOpacity 必须在 0 到 1 之间");
        }
        if (dto.getStrokeWidth() != null && dto.getStrokeWidth() <= 0) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "strokeWidth 必须大于 0");
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
