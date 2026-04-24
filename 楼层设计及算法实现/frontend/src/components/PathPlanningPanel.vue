<template>
  <div ref="panelRef" class="path-planning-panel" :style="panelStyle">
    <div class="panel-header" @mousedown="startDrag">
      <h3>🗺️ 路径规划</h3>
      <button class="btn-close" @click="$emit('close')">×</button>
    </div>

    <div class="panel-body">
      <!-- 添加坐标点 -->
      <div class="section">
        <h4>添加坐标点</h4>
        <div class="add-point-controls">
          <button 
            class="btn-add-point" 
            :class="{ active: isAddingPoint }"
            @click="toggleAddPoint">
            {{ isAddingPoint ? '取消添加' : '📍 点击地图添加点' }}
          </button>
        </div>
      </div>

      <!-- 坐标点列表 -->
      <div class="section">
        <h4>坐标点列表 ({{ points.length }}个)</h4>
        <div v-if="points.length === 0" class="empty-state">
          暂无坐标点，请点击地图添加
        </div>
        <draggable 
          v-else
          v-model="points" 
          class="points-list"
          item-key="id"
          handle=".drag-handle">
          <template #item="{ element, index }">
            <div class="point-item">
              <span class="drag-handle">☰</span>
              <span class="point-type">
                {{ index === 0 ? '🚩 起点' : index === points.length - 1 ? '🏁 终点' : `📍 途经点${index}` }}
              </span>
              <span class="point-coords">
                {{ element.map_id }} ({{ element.x.toFixed(2) }}, {{ element.y.toFixed(2) }})
              </span>
              <button class="btn-delete-point" @click="removePoint(index)">×</button>
            </div>
          </template>
        </draggable>
      </div>

      <!-- 路径规划结果 -->
      <div v-if="pathResult" class="section result-section">
        <h4>规划结果</h4>
        <div class="result-summary">
          <div class="result-item">
            <span class="label">总距离：</span>
            <span class="value">{{ pathResult.total_distance.toFixed(2) }} 米</span>
          </div>
          <div class="result-item">
            <span class="label">经过楼层：</span>
            <span class="value">{{ pathResult.floors.join(' → ') }}</span>
          </div>
        </div>
        
        <!-- 楼层导航 -->
        <div v-if="pathResult.floors.length > 1" class="floor-navigation">
          <h5>楼层导航：</h5>
          <div class="floor-buttons">
            <button 
              v-for="floor in pathResult.floors" 
              :key="floor"
              class="btn-floor"
              @click="$emit('navigate-floor', floor)">
              {{ getFloorName(floor) }}
            </button>
          </div>
        </div>
        
        <div v-if="pathResult.floor_grid_centers?.length" class="grid-centers-section">
          <h5>经过网格中心点</h5>
          <div
            v-for="floorItem in pathResult.floor_grid_centers"
            :key="`grid-floor-${floorItem.map_id}`"
            class="grid-floor-card">
            <div class="grid-floor-header">
              <span>{{ getFloorName(floorItem.map_id) }}</span>
              <span>{{ floorItem.grid_centers.length }} 个</span>
            </div>
            <div class="grid-centers-list">
              <span
                v-for="gridPoint in floorItem.grid_centers"
                :key="`grid-point-${floorItem.map_id}-${gridPoint.order}`"
                class="grid-center-chip">
                {{ formatGridCenter(gridPoint) }}
              </span>
            </div>
          </div>
        </div>

        <div class="steps-list">
          <h5>详细步骤：</h5>
          <div 
            v-for="step in pathResult.steps" 
            :key="step.step_number"
            class="step-item">
            <span class="step-number">{{ step.step_number }}</span>
            <span class="step-floor">[{{ step.floor }}]</span>
            <span class="step-action">{{ step.action }}</span>
            <span class="step-location">{{ step.location }}</span>
            <span class="step-distance">{{ step.distance.toFixed(2) }}m</span>
          </div>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="error-message">
        ❌ {{ error }}
      </div>
    </div>

    <div class="panel-footer">
      <button 
        class="btn-clear" 
        @click="clearPoints"
        :disabled="points.length === 0">
        清空
      </button>
      <button 
        class="btn-plan" 
        @click="planPath"
        :disabled="points.length < 2 || isPlanning">
        {{ isPlanning ? '规划中...' : '开始规划' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits, defineExpose, watch, onBeforeUnmount } from 'vue'
import draggable from 'vuedraggable/src/vuedraggable'
import axios from 'axios'

const emit = defineEmits(['close', 'path-result', 'adding-point-change', 'navigate-floor'])

const isAddingPoint = ref(false)
const points = ref([])
const pathResult = ref(null)
const error = ref(null)
const isPlanning = ref(false)
const panelRef = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const dragState = {
  active: false,
  startX: 0,
  startY: 0,
  baseX: 0,
  baseY: 0
}
const panelStyle = computed(() => ({
  transform: `translate(${dragOffset.value.x}px, ${dragOffset.value.y}px)`
}))

// 监听添加点模式变化，通知父组件
watch(isAddingPoint, (newValue) => {
  emit('adding-point-change', newValue)
})

// 切换添加点模式
function toggleAddPoint() {
  console.log('[PathPlanningPanel] toggleAddPoint 被调用，当前状态:', isAddingPoint.value)
  isAddingPoint.value = !isAddingPoint.value
  console.log('[PathPlanningPanel] 新状态:', isAddingPoint.value)
  if (isAddingPoint.value) {
    error.value = null
  }
}

// 添加坐标点（由父组件调用）
function addPoint(point) {
  console.log('[PathPlanningPanel] addPoint 被调用，参数:', point)
  points.value.push({
    id: Date.now(),
    x: point.x,
    y: point.y,
    map_id: point.map_id
  })
  console.log('[PathPlanningPanel] 当前点列表:', points.value)
  error.value = null
  pathResult.value = null
}

// 删除坐标点
function removePoint(index) {
  console.log('[PathPlanningPanel] removePoint 被调用，索引:', index)
  points.value.splice(index, 1)
  pathResult.value = null
}

// 清空所有点
function clearPoints() {
  console.log('[PathPlanningPanel] clearPoints 被调用')
  points.value = []
  pathResult.value = null
  error.value = null
  isAddingPoint.value = false
}

// 执行路径规划
async function planPath() {
  if (points.value.length < 2) {
    error.value = '至少需要2个坐标点（起点和终点）'
    return
  }

  isPlanning.value = true
  error.value = null
  pathResult.value = null

  try {
    const start = points.value[0]
    const end = points.value[points.value.length - 1]
    const waypoints = points.value.slice(1, -1)

    let response
    
    if (waypoints.length === 0) {
      // 两点路径规划
      response = await axios.post('http://localhost:5000/api/plan_path', {
        start: {
          x: start.x,
          y: start.y,
          map_id: start.map_id
        },
        end: {
          x: end.x,
          y: end.y,
          map_id: end.map_id
        }
      })
    } else {
      // 多点路径规划
      response = await axios.post('http://localhost:5000/api/plan_multi_waypoint_path', {
        start: {
          x: start.x,
          y: start.y,
          map_id: start.map_id
        },
        waypoints: waypoints.map(wp => ({
          x: wp.x,
          y: wp.y,
          map_id: wp.map_id
        })),
        end: {
          x: end.x,
          y: end.y,
          map_id: end.map_id
        }
      })
    }

    if (response.data.success) {
      pathResult.value = response.data
      emit('path-result', response.data)
    } else {
      error.value = response.data.error || '路径规划失败'
    }
  } catch (err) {
    console.error('路径规划失败:', err)
    error.value = err.response?.data?.error || err.message || '网络请求失败'
  } finally {
    isPlanning.value = false
  }
}

// 获取楼层显示名称
function getFloorName(mapId) {
  // 简单处理，可以根据实际情况优化
  return mapId.replace('floor', '第').replace('_', ' ') + '层'
}

// 暴露方法给父组件
function formatGridCenter(gridPoint) {
  return `(${Number(gridPoint.center_x).toFixed(1)}, ${Number(gridPoint.center_y).toFixed(1)})`
}

function startDrag(event) {
  if (event.button !== 0) return
  if (event.target.closest('.btn-close')) return

  dragState.active = true
  dragState.startX = event.clientX
  dragState.startY = event.clientY
  dragState.baseX = dragOffset.value.x
  dragState.baseY = dragOffset.value.y

  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
}

function onDrag(event) {
  if (!dragState.active) return

  dragOffset.value = {
    x: dragState.baseX + (event.clientX - dragState.startX),
    y: dragState.baseY + (event.clientY - dragState.startY)
  }
}

function stopDrag() {
  dragState.active = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
}

onBeforeUnmount(() => {
  stopDrag()
})

defineExpose({
  addPoint,
  isAddingPoint
})
</script>

<style scoped>
.path-planning-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 400px;
  max-height: calc(100vh - 100px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  cursor: move;
  user-select: none;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #333;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.section h5 {
  margin: 12px 0 8px 0;
  font-size: 13px;
  color: #666;
  font-weight: 600;
}

.add-point-controls {
  display: flex;
  gap: 8px;
}

.btn-add-point {
  flex: 1;
  padding: 10px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-add-point:hover {
  background: #45a049;
}

.btn-add-point.active {
  background: #f44336;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.points-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.point-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 13px;
}

.drag-handle {
  cursor: move;
  color: #999;
  font-size: 16px;
}

.point-type {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.point-coords {
  flex: 1;
  color: #666;
  font-family: monospace;
  font-size: 12px;
}

.btn-delete-point {
  background: none;
  border: none;
  color: #f44336;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-delete-point:hover {
  background: #ffebee;
}

.result-section {
  background: #e8f5e9;
  padding: 16px;
  border-radius: 8px;
}

.result-summary {
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.result-item .label {
  color: #666;
  font-weight: 600;
}

.result-item .value {
  color: #2e7d32;
  font-weight: 600;
}

.floor-navigation {
  margin-bottom: 16px;
  padding-top: 12px;
  border-top: 1px solid #c8e6c9;
}

.grid-centers-section {
  margin-bottom: 16px;
  padding-top: 12px;
  border-top: 1px solid #c8e6c9;
}

.grid-floor-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 10px;
  margin-top: 8px;
}

.grid-floor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #2e7d32;
  font-weight: 600;
}

.grid-centers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 120px;
  overflow-y: auto;
}

.grid-center-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #ffffff;
  color: #1f2937;
  font-size: 12px;
  font-family: monospace;
}

.floor-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.btn-floor {
  padding: 6px 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-floor:hover {
  background: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.steps-list {
  max-height: 300px;
  overflow-y: auto;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 12px;
}

.step-number {
  background: #4CAF50;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-floor {
  color: #666;
  font-weight: 600;
  min-width: 60px;
}

.step-action {
  color: #333;
  font-weight: 600;
  min-width: 40px;
}

.step-location {
  flex: 1;
  color: #666;
}

.step-distance {
  color: #4CAF50;
  font-weight: 600;
  font-family: monospace;
}

.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
}

.panel-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-clear,
.btn-plan {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-clear {
  background: #f5f5f5;
  color: #666;
}

.btn-clear:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-plan {
  background: #2196F3;
  color: white;
}

.btn-plan:hover:not(:disabled) {
  background: #1976D2;
}

.btn-clear:disabled,
.btn-plan:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
