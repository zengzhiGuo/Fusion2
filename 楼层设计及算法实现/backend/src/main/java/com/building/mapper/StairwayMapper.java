package com.building.mapper;

import com.building.entity.Stairway;
import org.apache.ibatis.annotations.*;
import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface StairwayMapper {

    @Select("SELECT * FROM stairways WHERE is_active = 1 ORDER BY stairway_id")
    List<Stairway> selectAllStairways();

    @Select("SELECT * FROM stairways WHERE stairway_id = #{stairwayId} AND is_active = 1")
    Stairway selectByStairwayId(String stairwayId);

    @Select("SELECT * FROM stairways WHERE map_id = #{mapId} AND is_active = 1")
    List<Stairway> selectByMapId(String mapId);

    @Insert("INSERT INTO stairways (stairway_id, stairway_name, map_id, upper_map_id, lower_map_id, upper_stairway_id, lower_stairway_id, x, y, description, is_active, create_time, update_time) " +
            "VALUES (#{stairwayId}, #{stairwayName}, #{mapId}, #{upperMapId}, #{lowerMapId}, #{upperStairwayId}, #{lowerStairwayId}, #{x}, #{y}, #{description}, #{isActive}, #{createTime}, #{updateTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertStairway(Stairway stairway);

    @Update("UPDATE stairways SET stairway_name = #{stairwayName}, map_id = #{mapId}, upper_map_id = #{upperMapId}, lower_map_id = #{lowerMapId}, " +
            "upper_stairway_id = #{upperStairwayId}, lower_stairway_id = #{lowerStairwayId}, " +
            "x = #{x}, y = #{y}, description = #{description}, update_time = #{updateTime} WHERE stairway_id = #{stairwayId}")
    int updateStairway(Stairway stairway);

    @Update("UPDATE stairways SET is_active = 0, update_time = #{updateTime} WHERE stairway_id = #{stairwayId}")
    int deleteStairway(@Param("stairwayId") String stairwayId, @Param("updateTime") LocalDateTime updateTime);

    @Update("UPDATE stairways SET upper_stairway_id = #{upperStairwayId}, update_time = #{updateTime} WHERE stairway_id = #{stairwayId}")
    int updateUpperConnection(@Param("stairwayId") String stairwayId,
                              @Param("upperStairwayId") String upperStairwayId,
                              @Param("updateTime") LocalDateTime updateTime);

    @Update("UPDATE stairways SET lower_stairway_id = #{lowerStairwayId}, update_time = #{updateTime} WHERE stairway_id = #{stairwayId}")
    int updateLowerConnection(@Param("stairwayId") String stairwayId,
                              @Param("lowerStairwayId") String lowerStairwayId,
                              @Param("updateTime") LocalDateTime updateTime);
}
