package com.ship.mapper;

import com.ship.entity.RegionEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * 围栏Mapper
 */
@Mapper
public interface RegionMapper {
    /**
     * 查询所有围栏
     */
    List<RegionEntity> selectAll();
    
    /**
     * 根据ID查询围栏
     */
    RegionEntity selectById(@Param("regionId") String regionId);
    
    /**
     * 根据地图ID查询围栏
     */
    List<RegionEntity> selectByMapId(@Param("mapId") String mapId);
    
    /**
     * 插入围栏
     */
    int insert(RegionEntity entity);
    
    /**
     * 更新围栏
     */
    int update(RegionEntity entity);
    
    /**
     * 删除围栏
     */
    int delete(@Param("regionId") String regionId);
}
