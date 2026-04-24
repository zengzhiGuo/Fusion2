package com.building.service;

import com.building.entity.Door;
import com.ship.entity.RegionEntity;
import com.ship.mapper.RegionMapper;
import com.building.mapper.DoorMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class DoorService {

    @Autowired
    private DoorMapper doorMapper;
    
    @Autowired
    private RegionMapper regionMapper;

    public List<Door> getAllDoors() {
        return doorMapper.selectAllDoors();
    }

    public Door getDoorById(Long id) {
        return doorMapper.selectById(id);
    }

    public List<Door> getDoorsByMapId(String mapId) {
        return doorMapper.selectByMapId(mapId);
    }

    public List<Door> getDoorsByRoomName(String roomName) {
        return doorMapper.selectByRoomName(roomName);
    }

    public List<Door> getDoorsByRoomType(Integer roomType) {
        return doorMapper.selectByRoomType(roomType);
    }

    public boolean addDoor(Door door) {
        validateDoor(door, false);
        door.setIsActive(true);
        door.setCreateTime(LocalDateTime.now());
        door.setUpdateTime(LocalDateTime.now());
        return doorMapper.insertDoor(door) > 0;
    }

    public boolean updateDoor(Door door) {
        validateDoor(door, true);
        door.setUpdateTime(LocalDateTime.now());
        return doorMapper.updateDoor(door) > 0;
    }

    public boolean deleteDoor(Long id) {
        return doorMapper.deleteDoor(id, LocalDateTime.now()) > 0;
    }

    private void validateDoor(Door door, boolean requireId) {
        if (door == null) {
            throw new IllegalArgumentException("门数据不能为空");
        }
        if (requireId && door.getId() == null) {
            throw new IllegalArgumentException("门ID不能为空");
        }
        if (isBlank(door.getRoomName())) {
            throw new IllegalArgumentException("门名称不能为空");
        }
        if (isBlank(door.getMapId())) {
            throw new IllegalArgumentException("所在楼层不能为空");
        }
        if (door.getX() == null || door.getY() == null) {
            throw new IllegalArgumentException("门坐标不能为空");
        }

        if (!isBlank(door.getTargetRegionId())) {
            RegionEntity region = regionMapper.selectById(door.getTargetRegionId());
            if (region == null) {
                throw new IllegalArgumentException("绑定的围栏不存在");
            }
            if (!door.getMapId().equals(region.getMapId())) {
                throw new IllegalArgumentException("门和围栏必须位于同一楼层");
            }
            door.setTargetRegionId(region.getRegionId());
        } else {
            door.setTargetRegionId(null);
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
