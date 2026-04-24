# TASK 8: 简化版图数据库实现 - 完成总结

## 任务状态：✅ 已完成

## 完成时间：2026-04-14

## 功能概述
实现了简化版的图数据库结构，所有边都是双向的，支持三种边类型：
1. doors-doors（房间/楼道/出入口之间）
2. doors-stairways（房间/楼道/出入口到楼梯）
3. stairways-stairways（楼梯到楼梯，用于跨楼层或连接不同楼梯）

## 简化内容

### 移除的字段
- ❌ edge_id（边的唯一标识）
- ❌ edge_name（边的名称）
- ❌ is_bidirectional（是否双向）- 所有边都是双向
- ❌ map_id（所在楼层ID）- 可从节点获取
- ❌ is_active（是否启用）
- ❌ is_accessible（是否可通行）
- ❌ description（边的描述）

### 保留的字段
- ✅ id（主键）
- ✅ node_a_type（节点A类型）
- ✅ node_a_id（节点A的ID）
- ✅ node_b_type（节点B类型）
- ✅ node_b_id（节点B的ID）
- ✅ weight（边的权重/距离）
- ✅ create_time（创建时间）
- ✅ update_time（更新时间）

## 数据库设计

### graph_edges 表结构
```sql
CREATE TABLE graph_edges (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_a_type TINYINT(1) NOT NULL,  -- 1-doors, 2-stairways
    node_a_id VARCHAR(50) NOT NULL,
    node_b_type TINYINT(1) NOT NULL,  -- 1-doors, 2-stairways
    node_b_id VARCHAR(50) NOT NULL,
    weight DECIMAL(10, 2) DEFAULT 1.0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_edge (node_a_type, node_a_id, node_b_type, node_b_id),
    INDEX idx_node_a (node_a_type, node_a_id),
    INDEX idx_node_b (node_b_type, node_b_id)
);
```

### 唯一约束
- 通过 `uk_edge` 确保不会重复创建边
- 建议插入时将较小的ID放在 node_a

## 后端实现

### 1. 实体类（GraphEdge.java）
```java
@Data
public class GraphEdge {
    private Long id;
    private Integer nodeAType;
    private String nodeAId;
    private Integer nodeBType;
    private String nodeBId;
    private BigDecimal weight;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
```

### 2. Mapper 接口（GraphEdgeMapper.java）
主要方法：
- `insert()`: 插入新边
- `update()`: 更新边（只能更新权重）
- `deleteById()`: 根据ID删除边
- `deleteByNodes()`: 根据两个节点删除边
- `selectById()`: 根据ID查询边
- `selectAll()`: 查询所有边
- `selectAdjacentEdges()`: 查询节点的所有邻接边
- `selectByNodes()`: 查询两个节点之间的边
- `deleteByNode()`: 删除节点相关的所有边
- `countByType()`: 按边类型统计数量

### 3. Service 层（GraphEdgeService.java）
封装业务逻辑，提供事务支持

### 4. Controller 层（GraphEdgeController.java）
REST API 接口：
- `POST /api/graph-edges`: 创建边
- `PUT /api/graph-edges`: 更新边
- `DELETE /api/graph-edges/{id}`: 删除边
- `DELETE /api/graph-edges/nodes`: 根据节点删除边
- `GET /api/graph-edges/{id}`: 查询边
- `GET /api/graph-edges/list`: 查询所有边
- `GET /api/graph-edges/adjacent/{nodeType}/{nodeId}`: 查询邻接边
- `GET /api/graph-edges/between`: 查询两节点间的边
- `DELETE /api/graph-edges/node/{nodeType}/{nodeId}`: 删除节点相关边
- `GET /api/graph-edges/stats/by-type`: 按类型统计

## 三种边类型

### 1. doors-doors
连接房间、楼道、出入口之间
```java
GraphEdge edge = new GraphEdge();
edge.setNodeAType(1);  // doors
edge.setNodeAId("1");  // 房间A
edge.setNodeBType(1);  // doors
edge.setNodeBId("2");  // 楼道B
edge.setWeight(new BigDecimal("5.5"));
```

### 2. doors-stairways
连接房间/楼道/出入口到楼梯
```java
GraphEdge edge = new GraphEdge();
edge.setNodeAType(1);  // doors
edge.setNodeAId("2");  // 楼道
edge.setNodeBType(2);  // stairways
edge.setNodeBId("stairway_001");
edge.setWeight(new BigDecimal("3.2"));
```

### 3. stairways-stairways
连接不同楼梯（较少使用）
```java
GraphEdge edge = new GraphEdge();
edge.setNodeAType(2);  // stairways
edge.setNodeAId("stairway_001");
edge.setNodeBType(2);  // stairways
edge.setNodeBId("stairway_002");
edge.setWeight(new BigDecimal("10.0"));
```

## 双向边处理

### 查询邻接边
由于所有边都是双向的，查询时需要检查两个方向：
```sql
SELECT * FROM graph_edges 
WHERE (node_a_type = ? AND node_a_id = ?) 
   OR (node_b_type = ? AND node_b_id = ?);
```

### 删除边
删除时也需要检查两个方向：
```sql
DELETE FROM graph_edges 
WHERE (node_a_type = ? AND node_a_id = ? AND node_b_type = ? AND node_b_id = ?)
   OR (node_a_type = ? AND node_a_id = ? AND node_b_type = ? AND node_b_id = ?);
```

## 使用示例

### 创建边
```java
GraphEdge edge = new GraphEdge();
edge.setNodeAType(1);
edge.setNodeAId("room_a");
edge.setNodeBType(1);
edge.setNodeBId("corridor_b");
edge.setWeight(new BigDecimal("5.5"));
graphEdgeService.createEdge(edge);
```

### 查询邻接边
```java
// 查询房间A的所有邻接边
List<GraphEdge> edges = graphEdgeService.getAdjacentEdges(1, "room_a");
```

### 查询两节点间的边
```java
GraphEdge edge = graphEdgeService.getEdgeByNodes(1, "room_a", 1, "corridor_b");
```

### 删除节点相关的所有边
```java
// 删除房间A相关的所有边
int count = graphEdgeService.deleteEdgesByNode(1, "room_a");
```

## 优势

1. **简单明了**：字段少，易于理解和维护
2. **双向默认**：所有边都是双向的，符合大多数场景
3. **唯一约束**：防止重复创建边
4. **高效查询**：通过索引优化性能
5. **灵活扩展**：支持三种边类型，覆盖所有场景

## 权重计算

### 自动计算距离
可以根据节点坐标自动计算欧几里得距离：
```java
double distance = Math.sqrt(
    Math.pow(node2.getX() - node1.getX(), 2) + 
    Math.pow(node2.getY() - node1.getY(), 2)
);
edge.setWeight(new BigDecimal(distance));
```

### 手动设置权重
也可以手动设置权重，考虑其他因素：
- 实际步行距离
- 通行时间
- 拥挤程度

## 路径规划支持

### Dijkstra 算法
```java
// 构建邻接表
Map<String, List<Edge>> graph = new HashMap<>();
for (GraphEdge edge : edges) {
    String nodeA = edge.getNodeAType() + ":" + edge.getNodeAId();
    String nodeB = edge.getNodeBType() + ":" + edge.getNodeBId();
    
    // 双向边，添加两个方向
    graph.computeIfAbsent(nodeA, k -> new ArrayList<>())
         .add(new Edge(nodeB, edge.getWeight()));
    graph.computeIfAbsent(nodeB, k -> new ArrayList<>())
         .add(new Edge(nodeA, edge.getWeight()));
}
```

## 数据完整性

### 级联删除
删除节点时，自动删除相关的边：
```java
// 删除房间时
doorService.deleteDoor(doorId);
graphEdgeService.deleteEdgesByNode(1, doorId);

// 删除楼梯时
stairwayService.deleteStairway(stairwayId);
graphEdgeService.deleteEdgesByNode(2, stairwayId);
```

## 统计功能

### 按类型统计边数量
```java
List<Map<String, Object>> stats = graphEdgeService.countByType();
// 返回：
// [
//   {"edge_type": "doors-doors", "count": 50},
//   {"edge_type": "doors-stairways", "count": 20},
//   {"edge_type": "stairways-stairways", "count": 5}
// ]
```

## 测试建议

1. 测试创建三种类型的边
2. 测试查询邻接边（双向）
3. 测试删除边
4. 测试更新权重
5. 测试级联删除
6. 测试唯一约束（防止重复）
7. 测试统计功能
8. 性能测试（大量边）

## 后续开发

1. **前端边管理界面**
   - 可视化显示边
   - 手动创建/删除边
   - 自动创建边（基于距离）

2. **路径规划算法**
   - 实现 Dijkstra 算法
   - 实现 A* 算法
   - 路径可视化

3. **自动边生成**
   - 根据节点距离自动创建边
   - 设置距离阈值
   - 避免冗余边

4. **权重优化**
   - 根据实际距离计算
   - 考虑楼层切换成本
   - 动态调整权重

## 总结

简化版的图数据库设计去除了不必要的字段，保留了核心功能，使系统更加简洁高效。所有边都是双向的，符合室内导航的实际场景。通过三种边类型，可以完整地表示室内空间的连接关系，为路径规划提供了坚实的数据基础。
