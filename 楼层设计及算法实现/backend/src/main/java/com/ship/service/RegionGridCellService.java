package com.ship.service;

import com.ship.entity.RegionCoordinateEntity;
import com.ship.entity.RegionGridCellEntity;
import com.ship.mapper.RegionGridCellMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RegionGridCellService {

    private static final double GRID_SIZE = 1.0d;
    private static final double GRID_CENTER_OFFSET = GRID_SIZE / 2.0d;
    private static final double EPSILON = 1e-9;

    private final RegionGridCellMapper regionGridCellMapper;

    public List<RegionGridCellEntity> getByRegionId(String regionId) {
        return regionGridCellMapper.selectByRegionId(regionId);
    }

    public List<RegionGridCellEntity> getByMapId(String mapId) {
        return regionGridCellMapper.selectByMapId(mapId);
    }

    public void rebuildRegionGridCells(String regionId, String mapId, List<RegionCoordinateEntity> coordinates) {
        regionGridCellMapper.deleteByRegionId(regionId);

        if (coordinates == null || coordinates.size() < 3) {
            return;
        }

        List<RegionGridCellEntity> cells = generateGridCells(regionId, mapId, coordinates);
        if (!cells.isEmpty()) {
            regionGridCellMapper.batchInsert(cells);
        }
    }

    private List<RegionGridCellEntity> generateGridCells(String regionId, String mapId, List<RegionCoordinateEntity> coordinates) {
        List<Point> polygon = coordinates.stream()
            .sorted(Comparator.comparingInt(item -> item.getPointOrder() == null ? Integer.MAX_VALUE : item.getPointOrder()))
            .map(item -> new Point(item.getXCoordinate(), item.getYCoordinate()))
            .toList();

        double minX = polygon.stream().mapToDouble(Point::x).min().orElse(0);
        double maxX = polygon.stream().mapToDouble(Point::x).max().orElse(0);
        double minY = polygon.stream().mapToDouble(Point::y).min().orElse(0);
        double maxY = polygon.stream().mapToDouble(Point::y).max().orElse(0);

        int startGridX = Math.max(0, (int) Math.floor(minX));
        int endGridX = Math.max(startGridX, (int) Math.ceil(maxX));
        int startGridY = Math.max(0, (int) Math.floor(minY));
        int endGridY = Math.max(startGridY, (int) Math.ceil(maxY));

        List<RegionGridCellEntity> cells = new ArrayList<>();
        for (int gridX = startGridX; gridX < endGridX; gridX++) {
            for (int gridY = startGridY; gridY < endGridY; gridY++) {
                double centerX = gridX + GRID_CENTER_OFFSET;
                double centerY = gridY + GRID_CENTER_OFFSET;

                if (!isPointInsidePolygon(centerX, centerY, polygon)) {
                    continue;
                }

                RegionGridCellEntity cell = new RegionGridCellEntity();
                cell.setRegionId(regionId);
                cell.setMapId(mapId);
                cell.setGridX(gridX);
                cell.setGridY(gridY);
                cell.setCenterX(centerX);
                cell.setCenterY(centerY);
                cells.add(cell);
            }
        }

        return cells;
    }

    private boolean isPointInsidePolygon(double x, double y, List<Point> polygon) {
        boolean inside = false;
        int size = polygon.size();

        for (int i = 0, j = size - 1; i < size; j = i++) {
            Point current = polygon.get(i);
            Point previous = polygon.get(j);

            if (isPointOnSegment(x, y, previous, current)) {
                return true;
            }

            boolean intersects = ((current.y() > y) != (previous.y() > y))
                && (x < (previous.x() - current.x()) * (y - current.y()) / (previous.y() - current.y()) + current.x());

            if (intersects) {
                inside = !inside;
            }
        }

        return inside;
    }

    private boolean isPointOnSegment(double x, double y, Point start, Point end) {
        double cross = (x - start.x()) * (end.y() - start.y()) - (y - start.y()) * (end.x() - start.x());
        if (Math.abs(cross) > EPSILON) {
            return false;
        }

        return x >= Math.min(start.x(), end.x()) - EPSILON
            && x <= Math.max(start.x(), end.x()) + EPSILON
            && y >= Math.min(start.y(), end.y()) - EPSILON
            && y <= Math.max(start.y(), end.y()) + EPSILON;
    }

    private record Point(double x, double y) {
    }
}
