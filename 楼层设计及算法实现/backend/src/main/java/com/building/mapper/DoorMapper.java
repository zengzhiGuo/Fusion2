package com.building.mapper;

import com.building.entity.Door;
import org.apache.ibatis.annotations.*;
import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface DoorMapper {

    String BASE_COLUMNS = "SELECT d.id, d.room_name, d.room_type, d.map_id, d.target_region_id, " +
            "r.region_name AS target_region_name, d.x, d.y, d.description, d.is_active, d.create_time, d.update_time " +
            "FROM doors d LEFT JOIN regions r ON d.target_region_id = r.region_id ";

    @Select(BASE_COLUMNS + "WHERE d.is_active = 1 ORDER BY d.id")
    List<Door> selectAllDoors();

    @Select(BASE_COLUMNS + "WHERE d.id = #{id} AND d.is_active = 1")
    Door selectById(Long id);

    @Select(BASE_COLUMNS + "WHERE d.map_id = #{mapId} AND d.is_active = 1")
    List<Door> selectByMapId(String mapId);

    @Select(BASE_COLUMNS + "WHERE d.room_name LIKE CONCAT('%', #{roomName}, '%') AND d.is_active = 1")
    List<Door> selectByRoomName(String roomName);

    @Select(BASE_COLUMNS + "WHERE d.room_type = #{roomType} AND d.is_active = 1")
    List<Door> selectByRoomType(Integer roomType);

    @Insert("INSERT INTO doors (room_name, room_type, map_id, target_region_id, x, y, description, is_active, create_time, update_time) " +
            "VALUES (#{roomName}, #{roomType}, #{mapId}, #{targetRegionId}, #{x}, #{y}, #{description}, #{isActive}, #{createTime}, #{updateTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertDoor(Door door);

    @Update("UPDATE doors SET room_name = #{roomName}, room_type = #{roomType}, map_id = #{mapId}, target_region_id = #{targetRegionId}, x = #{x}, y = #{y}, " +
            "description = #{description}, update_time = #{updateTime} WHERE id = #{id}")
    int updateDoor(Door door);

    @Update("UPDATE doors SET is_active = 0, update_time = #{updateTime} WHERE id = #{id}")
    int deleteDoor(@Param("id") Long id, @Param("updateTime") LocalDateTime updateTime);
}
