package com.ship.mapper;

import com.ship.entity.RegionCoordinateEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * 围栏坐标点Mapper
 */
@Mapper
public interface RegionCoordinateMapper {
    /**
     * 根据围栏ID查询坐标点
     */
    List<RegionCoordinateEntity> selectByRegionId(@Param("regionId") String regionId);
    
    /**
     * 插入坐标点
     */
    int insert(RegionCoordinateEntity entity);
    
    /**
     * 批量插入坐标点
     */
    int batchInsert(@Param("coordinates") List<RegionCoordinateEntity> coordinates);
    
    /**
     * 删除围栏的所有坐标点
     */
    int deleteByRegionId(@Param("regionId") String regionId);
}
