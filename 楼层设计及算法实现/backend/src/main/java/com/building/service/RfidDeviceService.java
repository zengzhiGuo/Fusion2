package com.building.service;

import com.building.entity.RfidDevice;
import com.building.mapper.RfidDeviceMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class RfidDeviceService {

    @Autowired
    private RfidDeviceMapper rfidDeviceMapper;

    public List<RfidDevice> getAllDevices() {
        return rfidDeviceMapper.selectAllDevices();
    }

    public RfidDevice getDeviceById(Long id) {
        return rfidDeviceMapper.selectById(id);
    }

    public List<RfidDevice> getDevicesByMapId(String mapId) {
        return rfidDeviceMapper.selectByMapId(mapId);
    }

    public List<RfidDevice> getDevicesByStairwayId(String stairwayId) {
        return rfidDeviceMapper.selectByStairwayId(stairwayId);
    }

    public List<RfidDevice> getDevicesByDoorId(Long doorId) {
        return rfidDeviceMapper.selectByDoorId(doorId);
    }

    public boolean addDevice(RfidDevice device) {
        device.setIsActive(true);
        device.setCreateTime(LocalDateTime.now());
        device.setUpdateTime(LocalDateTime.now());
        return rfidDeviceMapper.insertDevice(device) > 0;
    }

    public boolean updateDevice(RfidDevice device) {
        device.setUpdateTime(LocalDateTime.now());
        return rfidDeviceMapper.updateDevice(device) > 0;
    }

    public boolean deleteDevice(Long id) {
        return rfidDeviceMapper.deleteDevice(id, LocalDateTime.now()) > 0;
    }
}
