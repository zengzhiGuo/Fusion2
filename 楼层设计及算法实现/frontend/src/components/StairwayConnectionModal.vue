<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content stairway-connection-modal" @click.stop>
      <div class="modal-header">
        <h3>楼梯连接管理</h3>
        <button class="btn-close-modal" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <div class="stairway-info">
          <h4>当前楼梯信息</h4>
          <div class="info-row">
            <span class="info-label">楼梯名称：</span>
            <span class="info-value">{{ stairway?.stairwayName }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">所在楼层：</span>
            <span class="info-value">{{ stairway?.mapId }}</span>
          </div>
        </div>

        <!-- 上层连接 -->
        <div v-if="stairway?.upperMapId" class="connection-section">
          <h4>上层连接 ({{ stairway.upperMapId }})</h4>
          <div class="form-item">
            <label>选择上层楼梯</label>
            <select v-model="upperStairwayId" @change="updateUpperConnection">
              <option value="">-- 未连接 --</option>
              <option 
                v-for="s in availableUpperStairways" 
                :key="s.stairwayId" 
                :value="s.stairwayId"
              >
                {{ s.stairwayName }} ({{ s.stairwayId }})
              </option>
            </select>
          </div>
          <div v-if="upperStairway" class="connected-info">
            <span class="status-badge connected">已连接</span>
            <span>{{ upperStairway.stairwayName }}</span>
          </div>
        </div>
        <div v-else class="connection-section disabled">
          <h4>上层连接</h4>
          <p class="no-connection">此楼梯不能上楼 (upper_map_id 为空)</p>
        </div>

        <!-- 下层连接 -->
        <div v-if="stairway?.lowerMapId" class="connection-section">
          <h4>下层连接 ({{ stairway.lowerMapId }})</h4>
          <div class="form-item">
            <label>选择下层楼梯</label>
            <select v-model="lowerStairwayId" @change="updateLowerConnection">
              <option value="">-- 未连接 --</option>
              <option 
                v-for="s in availableLowerStairways" 
                :key="s.stairwayId" 
                :value="s.stairwayId"
              >
                {{ s.stairwayName }} ({{ s.stairwayId }})
              </option>
            </select>
          </div>
          <div v-if="lowerStairway" class="connected-info">
            <span class="status-badge connected">已连接</span>
            <span>{{ lowerStairway.stairwayName }}</span>
          </div>
        </div>
        <div v-else class="connection-section disabled">
          <h4>下层连接</h4>
          <p class="no-connection">此楼梯不能下楼 (lower_map_id 为空)</p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import apiClient from '../utils/api'

const props = defineProps({
  stairwayId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'updated'])

const stairway = ref(null)
const upperStairway = ref(null)
const lowerStairway = ref(null)
const availableUpperStairways = ref([])
const availableLowerStairways = ref([])
const upperStairwayId = ref('')
const lowerStairwayId = ref('')

// 加载楼梯连接信息
async function loadConnections() {
  try {
    const response = await apiClient.get(`/stairways/${props.stairwayId}/connections`)
    const data = response.data
    
    stairway.value = data.stairway
    upperStairway.value = data.upperStairway || null
    lowerStairway.value = data.lowerStairway || null
    availableUpperStairways.value = data.availableUpperStairways || []
    availableLowerStairways.value = data.availableLowerStairways || []
    
    upperStairwayId.value = stairway.value.upperStairwayId || ''
    lowerStairwayId.value = stairway.value.lowerStairwayId || ''
  } catch (error) {
    console.error('加载楼梯连接信息失败:', error)
    alert('加载楼梯连接信息失败: ' + error.message)
  }
}

// 更新上层连接
async function updateUpperConnection() {
  try {
    await apiClient.put(`/stairways/${props.stairwayId}/upper-connection`, {
      upperStairwayId: upperStairwayId.value || null
    })
    alert('上层连接更新成功')
    await loadConnections()
    emit('updated')
  } catch (error) {
    console.error('更新上层连接失败:', error)
    alert('更新上层连接失败: ' + error.message)
    // 恢复原值
    upperStairwayId.value = stairway.value.upperStairwayId || ''
  }
}

// 更新下层连接
async function updateLowerConnection() {
  try {
    await apiClient.put(`/stairways/${props.stairwayId}/lower-connection`, {
      lowerStairwayId: lowerStairwayId.value || null
    })
    alert('下层连接更新成功')
    await loadConnections()
    emit('updated')
  } catch (error) {
    console.error('更新下层连接失败:', error)
    alert('更新下层连接失败: ' + error.message)
    // 恢复原值
    lowerStairwayId.value = stairway.value.lowerStairwayId || ''
  }
}

onMounted(() => {
  loadConnections()
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.stairway-connection-modal {
  max-width: 600px;
  width: 90%;
  background: white;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-close-modal:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
  background: white;
}

.stairway-info {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stairway-info h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
}

.info-value {
  color: #333;
}

.connection-section {
  margin-bottom: 25px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.connection-section.disabled {
  background: #fafafa;
  opacity: 0.7;
}

.connection-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 15px;
}

.form-item {
  margin-bottom: 15px;
}

.form-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
  font-size: 14px;
}

.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.form-item select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.connected-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #e8f5e9;
  border-radius: 4px;
  margin-top: 10px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.connected {
  background: #4caf50;
  color: white;
}

.no-connection {
  color: #999;
  font-style: italic;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  background: white;
}

.btn-secondary {
  padding: 8px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #5a6268;
}
</style>
