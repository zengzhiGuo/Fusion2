package com.ship.mapper;

import com.ship.entity.RegionGridCellEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RegionGridCellMapper {
    List<RegionGridCellEntity> selectByRegionId(@Param("regionId") String regionId);

    List<RegionGridCellEntity> selectByMapId(@Param("mapId") String mapId);

    int batchInsert(@Param("cells") List<RegionGridCellEntity> cells);

    int deleteByRegionId(@Param("regionId") String regionId);
}
