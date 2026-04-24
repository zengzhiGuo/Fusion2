package com.building.service;

import com.building.entity.MapInfo;
import com.building.mapper.MapInfoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class MapInfoService {

    @Autowired
    private MapInfoMapper mapInfoMapper;

    public List<MapInfo> getAllMaps() {
        return mapInfoMapper.selectAllMaps();
    }

    public MapInfo getMapById(String mapId) {
        return mapInfoMapper.selectMapById(mapId);
    }
}
