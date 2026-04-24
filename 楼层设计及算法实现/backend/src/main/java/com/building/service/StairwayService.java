package com.building.service;

import com.building.entity.Stairway;
import com.building.mapper.StairwayMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class StairwayService {

    @Autowired
    private StairwayMapper stairwayMapper;

    public List<Stairway> getAllStairways() {
        return stairwayMapper.selectAllStairways();
    }

    public Stairway getStairwayById(String stairwayId) {
        return stairwayMapper.selectByStairwayId(stairwayId);
    }

    public List<Stairway> getStairwaysByMapId(String mapId) {
        return stairwayMapper.selectByMapId(mapId);
    }

    public boolean addStairway(Stairway stairway) {
        stairway.setIsActive(true);
        stairway.setCreateTime(LocalDateTime.now());
        stairway.setUpdateTime(LocalDateTime.now());
        return stairwayMapper.insertStairway(stairway) > 0;
    }

    public boolean updateStairway(Stairway stairway) {
        stairway.setUpdateTime(LocalDateTime.now());
        return stairwayMapper.updateStairway(stairway) > 0;
    }

    public boolean deleteStairway(String stairwayId) {
        return stairwayMapper.deleteStairway(stairwayId, LocalDateTime.now()) > 0;
    }

    /**
     * 更新楼梯的上层连接
     */
    public boolean updateUpperConnection(String stairwayId, String upperStairwayId) {
        Stairway stairway = stairwayMapper.selectByStairwayId(stairwayId);
        if (stairway == null) {
            return false;
        }

        // 验证目标楼梯是否在上层楼层
        if (upperStairwayId != null && !upperStairwayId.isEmpty()) {
            Stairway targetStairway = stairwayMapper.selectByStairwayId(upperStairwayId);
            if (targetStairway == null) {
                return false;
            }
            // 检查目标楼梯是否在 upper_map_id 指定的楼层
            if (stairway.getUpperMapId() == null ||
                    !stairway.getUpperMapId().equals(targetStairway.getMapId())) {
                return false;
            }
        }

        return stairwayMapper.updateUpperConnection(stairwayId, upperStairwayId, LocalDateTime.now()) > 0;
    }

    /**
     * 更新楼梯的下层连接
     */
    public boolean updateLowerConnection(String stairwayId, String lowerStairwayId) {
        Stairway stairway = stairwayMapper.selectByStairwayId(stairwayId);
        if (stairway == null) {
            return false;
        }

        // 验证目标楼梯是否在下层楼层
        if (lowerStairwayId != null && !lowerStairwayId.isEmpty()) {
            Stairway targetStairway = stairwayMapper.selectByStairwayId(lowerStairwayId);
            if (targetStairway == null) {
                return false;
            }
            // 检查目标楼梯是否在 lower_map_id 指定的楼层
            if (stairway.getLowerMapId() == null ||
                    !stairway.getLowerMapId().equals(targetStairway.getMapId())) {
                return false;
            }
        }

        return stairwayMapper.updateLowerConnection(stairwayId, lowerStairwayId, LocalDateTime.now()) > 0;
    }

    /**
     * 获取楼梯的连接信息
     */
    public Map<String, Object> getStairwayConnections(String stairwayId) {
        Stairway stairway = stairwayMapper.selectByStairwayId(stairwayId);
        if (stairway == null) {
            return null;
        }

        Map<String, Object> result = new HashMap<>();
        result.put("stairway", stairway);

        // 获取上层连接的楼梯信息
        if (stairway.getUpperStairwayId() != null) {
            Stairway upperStairway = stairwayMapper.selectByStairwayId(stairway.getUpperStairwayId());
            result.put("upperStairway", upperStairway);
        }

        // 获取下层连接的楼梯信息
        if (stairway.getLowerStairwayId() != null) {
            Stairway lowerStairway = stairwayMapper.selectByStairwayId(stairway.getLowerStairwayId());
            result.put("lowerStairway", lowerStairway);
        }

        // 获取可用的上层楼梯列表
        if (stairway.getUpperMapId() != null) {
            List<Stairway> upperFloorStairways = stairwayMapper.selectByMapId(stairway.getUpperMapId());
            result.put("availableUpperStairways", upperFloorStairways);
        }

        // 获取可用的下层楼梯列表
        if (stairway.getLowerMapId() != null) {
            List<Stairway> lowerFloorStairways = stairwayMapper.selectByMapId(stairway.getLowerMapId());
            result.put("availableLowerStairways", lowerFloorStairways);
        }

        return result;
    }
}
