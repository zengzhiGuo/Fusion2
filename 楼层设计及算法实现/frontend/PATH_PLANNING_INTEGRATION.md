# 路径规划功能集成说明

## 概述

本文档说明如何将路径规划功能集成到现有的前端系统中。

## 前提条件

1. ✅ Python后端服务器已启动（`python path_planning/server.py`）
2. ✅ 后端监听在 `http://localhost:5000`
3. ✅ 已安装 `vuedraggable` 依赖

## 安装依赖

```bash
cd frontend
npm install vuedraggable
```

## 集成步骤

### 步骤1：在 App.vue 中导入路径规划组件

在 `<script setup>` 部分添加：

```javascript
import PathPlanningPanel from './components/PathPlanningPanel.vue'
```

### 步骤2：添加状态变量

在 `<script setup>` 部分添加：

```javascript
// 路径规划相关状态
const showPathPlanning = ref(false)
const pathPlanningPanelRef = ref(null)
```

### 步骤3：添加路径规划按钮

在 `preview-nav` 区域添加按钮（在查看连接按钮后面）：

```vue
<button 
  class="btn-action btn-path-planning" 
  @click="togglePathPlanning" 
  :class="{ active: showPathPlanning }" 
  title="路径规划">
  <span class="icon">🗺️</span>
</button>
```

### 步骤4：添加路径规划面板组件

在模态框区域后面添加：

```vue
<!-- 路径规划面板 -->
<PathPlanningPanel
  v-if="showPathPlanning"
  ref="pathPlanningPanelRef"
  @close="closePathPlanning"
  @path-result="onPathResult"
/>
```

### 步骤5：修改 MapCanvas 组件，支持路径规划点击

在 MapCanvas 的 props 中添加：

```vue
:isAddingPathPoint="pathPlanningPanelRef?.isAddingPoint || false"
@path-point-click="onPathPointClick"
```

### 步骤6：添加方法

在 `<script setup>` 部分添加以下方法：

```javascript
// 切换路径规划面板
function togglePathPlanning() {
  showPathPlanning.value = !showPathPlanning.value
  if (!showPathPlanning.value) {
    // 关闭时清理状态
    isAddingStairway.value = false
    isAddingDoor.value = false
    isAddingCorridor.value = false
    isAddingEntrance.value = false
    isAddingRfid.value = false
    isAddingEdge.value = false
  }
}

// 关闭路径规划面板
function closePathPlanning() {
  showPathPlanning.value = false
}

// 处理路径规划点击
function onPathPointClick(coords) {
  if (pathPlanningPanelRef.value && pathPlanningPanelRef.value.isAddingPoint) {
    pathPlanningPanelRef.value.addPoint({
      x: coords.x,
      y: coords.y,
      map_id: selectedMap.value.mapId
    })
  }
}

// 处理路径规划结果
function onPathResult(result) {
  console.log('路径规划结果:', result)
  // 可以在这里添加路径可视化逻辑
  alert(`路径规划成功！总距离：${result.total_distance.toFixed(2)}米`)
}
```

### 步骤7：添加样式

在 `<style scoped>` 部分添加：

```css
.btn-path-planning {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-path-planning:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-path-planning.active {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}
```

## 使用流程

1. **启动后端服务器**
   ```bash
   cd path_planning
   python server.py
   ```

2. **启动前端开发服务器**
   ```bash
   cd frontend
   npm run dev
   ```

3. **使用路径规划功能**
   - 点击 🗺️ 按钮打开路径规划面板
   - 点击"📍 点击地图添加点"按钮
   - 在地图上依次点击添加坐标点（起点、途经点、终点）
   - 可以拖动调整点的顺序
   - 点击"开始规划"按钮执行路径规划
   - 查看规划结果

## API 接口

### 两点路径规划

**接口**: `POST http://localhost:5000/api/plan_path`

**请求体**:
```json
{
  "start": {
    "x": 22.4460,
    "y": 13.4433,
    "map_id": "floor1"
  },
  "end": {
    "x": 21.1138,
    "y": 12.9260,
    "map_id": "floor2"
  }
}
```

### 多点路径规划

**接口**: `POST http://localhost:5000/api/plan_multi_waypoint_path`

**请求体**:
```json
{
  "start": {
    "x": 22.4460,
    "y": 13.4433,
    "map_id": "floor1"
  },
  "waypoints": [
    {
      "x": 22.1582,
      "y": 6.4752,
      "map_id": "floor1"
    }
  ],
  "end": {
    "x": 21.1138,
    "y": 12.9260,
    "map_id": "floor2"
  }
}
```

**响应**:
```json
{
  "success": true,
  "distance": 35.58,
  "total_distance": 35.58,
  "floors": ["floor1", "floor2"],
  "steps": [
    {
      "step_number": 1,
      "floor": "floor1",
      "action": "出发",
      "location": "A甲板会议室",
      "distance": 4.70
    },
    ...
  ],
  "path_nodes": [...]
}
```

## 故障排查

### 问题1：无法连接到后端

**错误**: `Network Error` 或 `ERR_CONNECTION_REFUSED`

**解决**:
1. 确认后端服务器已启动：`python path_planning/server.py`
2. 确认端口5000未被占用
3. 检查防火墙设置

### 问题2：CORS跨域错误

**错误**: `Access-Control-Allow-Origin`

**解决**:
1. 安装flask-cors：`pip install flask-cors`
2. 或者在前端配置代理（vite.config.js）

### 问题3：路径规划失败

**错误**: `无法从起点到达终点`

**原因**: 起点和终点之间没有连通的路径

**解决**:
1. 检查数据库中的边连接是否完整
2. 确认楼梯之间的连接关系正确
3. 重新导出数据：`python path_planning/database.py`

## 下一步优化

1. **路径可视化**: 在地图上绘制路径线条
2. **实时更新**: 支持数据更新后自动刷新
3. **历史记录**: 保存常用路径
4. **导出功能**: 导出路径为PDF或图片
5. **语音导航**: 添加语音播报功能

## 联系方式

如有问题，请查看日志或联系开发团队。
