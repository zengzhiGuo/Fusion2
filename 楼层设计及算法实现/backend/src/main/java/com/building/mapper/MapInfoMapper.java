package com.building.mapper;

import com.building.entity.MapInfo;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;

@Mapper
public interface MapInfoMapper {

    @Select("SELECT * FROM maps")
    List<MapInfo> selectAllMaps();

    @Select("SELECT * FROM maps WHERE map_id = #{mapId}")
    MapInfo selectMapById(String mapId);
}
