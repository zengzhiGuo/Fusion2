package com.building.mapper;

import com.building.entity.RfidDevice;
import org.apache.ibatis.annotations.*;
import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface RfidDeviceMapper {

    @Select("SELECT * FROM rfid_devices WHERE is_active = 1 ORDER BY id")
    List<RfidDevice> selectAllDevices();

    @Select("SELECT * FROM rfid_devices WHERE id = #{id} AND is_active = 1")
    RfidDevice selectById(Long id);

    @Select("SELECT * FROM rfid_devices WHERE map_id = #{mapId} AND is_active = 1")
    List<RfidDevice> selectByMapId(String mapId);

    @Select("SELECT * FROM rfid_devices WHERE stairway_id = #{stairwayId} AND is_active = 1")
    List<RfidDevice> selectByStairwayId(String stairwayId);

    @Select("SELECT * FROM rfid_devices WHERE door_id = #{doorId} AND is_active = 1")
    List<RfidDevice> selectByDoorId(Long doorId);

    @Insert("INSERT INTO rfid_devices (device_name, map_id, x, y, stairway_id, door_id, description, is_active, create_time, update_time) " +
            "VALUES (#{deviceName}, #{mapId}, #{x}, #{y}, #{stairwayId}, #{doorId}, #{description}, #{isActive}, #{createTime}, #{updateTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertDevice(RfidDevice device);

    @Update("UPDATE rfid_devices SET device_name = #{deviceName}, map_id = #{mapId}, x = #{x}, y = #{y}, " +
            "stairway_id = #{stairwayId}, door_id = #{doorId}, description = #{description}, update_time = #{updateTime} WHERE id = #{id}")
    int updateDevice(RfidDevice device);

    @Update("UPDATE rfid_devices SET is_active = 0, update_time = #{updateTime} WHERE id = #{id}")
    int deleteDevice(@Param("id") Long id, @Param("updateTime") LocalDateTime updateTime);
}
