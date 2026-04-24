<template>
  <div class="container">
    <header class="header">
      <h1>楼层地图管理</h1>
    </header>

    <div class="content">
      <div class="floor-list-section">
        <div class="floor-list-header">
          <h2>楼层列表</h2>
          <span class="floor-count">{{ mapList.length }} 个楼层</span>
        </div>
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="mapList.length === 0" class="empty-state">
          暂无地图数据
        </div>
        <ul v-else class="floor-list">
          <li 
            v-for="(map, index) in mapList" 
            :key="map.mapId"
            class="floor-item"
            :class="{ active: selectedMap?.mapId === map.mapId }"
            @click="selectMap(map)">
            <span class="floor-index">{{ index + 1 }}</span>
            <span class="floor-name">{{ map.regionName }}</span>
            <span class="floor-size">{{ map.shipLengthM }}m</span>
          </li>
        </ul>
      </div>

      <div class="preview-section">
        <div v-if="selectedMap" class="preview-inner">
          <div class="preview-header">
            <div class="preview-title">
              <span class="preview-index">{{ mapList.findIndex(m => m.mapId === selectedMap.mapId) + 1 }}</span>
              <h2>{{ selectedMap.regionName }}</h2>
            </div>
            <div class="preview-nav">
              <button class="btn-action btn-stairway" @click="openStairwayModal" title="添加楼梯">
                <span class="icon">🪜</span>
              </button>
              <button class="btn-action btn-door" @click="openDoorModal" title="添加房间">
                <span class="icon">🚪</span>
              </button>
              <button class="btn-action btn-corridor" @click="openCorridorModal" title="添加楼道">
                <span class="icon">🛤️</span>
              </button>
              <button class="btn-action btn-entrance" @click="openEntranceModal" title="添加出入口">
                <span class="icon">🚧</span>
              </button>
              <button class="btn-action btn-rfid" @click="openRfidModal" title="添加RFID设备">
                <span class="icon">📡</span>
              </button>
              <button class="btn-action btn-region" @click="toggleRegionDrawing" :class="{ active: isAddingRegion }" title="绘制围栏">
                <span class="icon">围</span>
              </button>
              <button class="btn-action btn-edge" @click="toggleEdgeMode" :class="{ active: isAddingEdge }" title="连接节点">
                <span class="icon">🔗</span>
              </button>
              <button class="btn-action btn-view-connections" @click="toggleViewConnectionsMode" :class="{ active: isViewingConnections }" title="查看连接">
                <span class="icon">👁️</span>
              </button>
              <button class="btn-action btn-path-planning" @click="togglePathPlanning" :class="{ active: showPathPlanning }" title="路径规划">
                <span class="icon">🗺️</span>
              </button>
              <button 
                class="btn-nav" 
                :disabled="mapList.findIndex(m => m.mapId === selectedMap.mapId) <= 0"
                @click="navigateMap(-1)">←</button>
              <span class="nav-info">{{ mapList.findIndex(m => m.mapId === selectedMap.mapId) + 1 }} / {{ mapList.length }}</span>
              <button 
                class="btn-nav" 
                :disabled="mapList.findIndex(m => m.mapId === selectedMap.mapId) >= mapList.length - 1"
                @click="navigateMap(1)">→</button>
            </div>
          </div>
          <div class="preview-content">
            <MapCanvas 
              v-if="mapCanvasUrl"
              :key="selectedMap.mapId"
              :imgUrl="mapCanvasUrl"
              :shipLength="selectedMap.shipLengthM"
              :shipWidth="selectedMap.shipWidthM"
              :imageWidth="selectedMap.imageWidthPx"
              :imageHeight="selectedMap.imageHeightPx"
              :showGrid="true"
              :gridSize="1"
              :points="[]"
              :mapId="selectedMap.mapId"
              :stairways="stairways"
              :doors="doors"
              :rfidDevices="rfidDevices"
              :isAddingStairway="isAddingStairway"
              :isAddingDoor="isAddingDoor"
              :isAddingCorridor="isAddingCorridor"
              :isAddingEntrance="isAddingEntrance"
              :isAddingRfid="isAddingRfid"
              :isAddingRegion="isAddingRegion"
              :isAddingPathPoint="isAddingPathPoint"
              :pathSegment="currentPathSegment"
              :regions="regions"
              :regionCoordinates="regionCoordinates"
              :regionDraftPoints="regionDraftPoints"
              :regionDraftStyle="regionDraftStyle"
              @stairway-click="onStairwayCoordinateClick"
              @path-point-click="onPathPointClick"
              @stairway-detail-click="onStairwayDetailClick"
              @door-click="onDoorCoordinateClick"
              @door-detail-click="onDoorDetailClick"
              @corridor-click="onCorridorCoordinateClick"
              @entrance-click="onEntranceCoordinateClick"
              @rfid-click="onRfidCoordinateClick"
              @rfid-detail-click="onRfidDetailClick"
              @region-point-click="onRegionPointClick"
              @region-detail-click="onRegionDetailClick"
            />
            <div v-if="isAddingRegion && selectedMap" class="region-editor-panel">
              <div class="region-editor-header">
                <div>
                  <h3>{{ editingRegion ? '编辑围栏' : '新建围栏' }}</h3>
                  <p>在地图上单击添加顶点，至少 3 个点</p>
                </div>
                <button class="btn-close-modal" @click="closeRegionEditor">×</button>
              </div>
              <div class="region-editor-body">
                <div class="form-item">
                  <label>围栏名称</label>
                  <input type="text" v-model="regionForm.regionName" placeholder="如：会议区、设备区" />
                </div>
                <div class="form-item">
                  <label>所在楼层</label>
                  <input type="text" :value="getMapName(regionForm.mapId || selectedMap.mapId)" readonly class="readonly" />
                </div>
                <div class="region-editor-grid">
                  <div class="form-item">
                    <label>颜色</label>
                    <input type="color" v-model="regionForm.color" class="color-input" />
                  </div>
                  <div class="form-item">
                    <label>透明度</label>
                    <input type="number" min="0" max="1" step="0.05" v-model.number="regionForm.fillOpacity" />
                  </div>
                  <div class="form-item">
                    <label>线宽</label>
                    <input type="number" min="0.5" step="0.5" v-model.number="regionForm.strokeWidth" />
                  </div>
                </div>
                <div class="form-item">
                  <label>描述</label>
                  <textarea v-model="regionForm.description" placeholder="可选的围栏说明"></textarea>
                </div>
                <div class="region-point-toolbar">
                  <span class="region-point-count">已选 {{ currentRegionPoints.length }} 个点</span>
                  <button class="btn-cancel btn-small" @click="undoRegionPoint" :disabled="currentRegionPoints.length === 0">撤销</button>
                  <button class="btn-cancel btn-small" @click="clearRegionPoints" :disabled="currentRegionPoints.length === 0">清空</button>
                </div>
                <div class="region-point-list">
                  <div v-if="currentRegionPoints.length === 0" class="region-point-empty">点击地图开始绘制围栏</div>
                  <div v-for="(point, index) in currentRegionPoints" :key="`point-${index}`" class="region-point-item">
                    <span>#{{ index + 1 }} X: {{ point.xCoordinate.toFixed(2) }}, Y: {{ point.yCoordinate.toFixed(2) }}</span>
                    <button class="point-remove-btn" @click="removeRegionPoint(index)">删除</button>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn-cancel" @click="closeRegionEditor">取消</button>
                <button class="btn-confirm" @click="submitRegionAndRender" :disabled="currentRegionPoints.length < 3 || !regionForm.regionName?.trim()">
                  {{ editingRegion ? '保存围栏' : '创建围栏' }}
                </button>
              </div>
            </div>
            <div v-if="!mapCanvasUrl" class="map-loading">
              加载地图中...
            </div>
          </div>
          <div class="preview-info">
            <div class="info-item">
              <span class="info-label">地图ID</span>
              <span class="info-value">{{ selectedMap.mapId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">区域名称</span>
              <span class="info-value">{{ selectedMap.regionName }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">船舶尺寸</span>
              <span class="info-value">{{ selectedMap.shipLengthM }}m × {{ selectedMap.shipWidthM }}m</span>
            </div>
            <div class="info-item">
              <span class="info-label">图片尺寸</span>
              <span class="info-value">{{ selectedMap.imageWidthPx }} × {{ selectedMap.imageHeightPx }} px</span>
            </div>
            <div class="info-item">
              <span class="info-label">缩放比例</span>
              <span class="info-value">1px = {{ scale.toFixed(4) }}m</span>
            </div>
          </div>
        </div>
        <div v-else class="no-selection">
          <div class="no-selection-icon">📋</div>
          <p>请从左侧选择楼层查看地图</p>
        </div>
      </div>
    </div>

    <!-- 添加楼梯模态框 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingStairway ? '编辑楼梯' : '添加楼梯连接' }}</h3>
          <button class="btn-close-modal" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>楼梯坐标</label>
            <div class="coord-display">
              X: {{ stairwayForm.x?.toFixed(2) || 0 }} m, Y: {{ stairwayForm.y?.toFixed(2) || 0 }} m
            </div>
          </div>
          <div class="form-item">
            <label>楼梯名称</label>
            <input type="text" v-model="stairwayForm.stairwayName" placeholder="如：连接 floor5 到 floor4" />
          </div>
          <div class="form-item">
            <label>所在楼层</label>
            <input type="text" v-model="stairwayForm.mapId" readonly class="readonly" />
          </div>
          <div class="form-item">
            <label>上层楼层（可选）</label>
            <select v-model="stairwayForm.upperMapId">
              <option value="">-- 选择上层楼层 --</option>
              <option v-for="map in mapList" :key="map.mapId" :value="map.mapId">
                {{ map.regionName }} ({{ map.mapId }})
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>下层楼层（可选）</label>
            <select v-model="stairwayForm.lowerMapId">
              <option value="">-- 选择下层楼层 --</option>
              <option v-for="map in mapList" :key="map.mapId" :value="map.mapId">
                {{ map.regionName }} ({{ map.mapId }})
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="stairwayForm.description" placeholder="可选描述信息"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="editingStairway" class="btn-delete" @click="deleteStairway">删除</button>
          <button class="btn-cancel" @click="closeModal">取消</button>
          <button class="btn-confirm" @click="submitStairway">{{ editingStairway ? '保存修改' : '确认添加' }}</button>
        </div>
      </div>
    </div>

    <!-- 楼梯详情模态框 -->
    <div v-if="showStairwayDetail" class="modal-overlay" @click="closeStairwayDetail">
      <div class="modal-content stairway-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedStairway?.stairwayName }}</h3>
          <button class="btn-close-modal" @click="closeStairwayDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="stairway-info">
            <div class="info-row">
              <span class="info-label">坐标位置</span>
              <span class="info-value">X: {{ selectedStairway?.x?.toFixed(2) }} m, Y: {{ selectedStairway?.y?.toFixed(2) }} m</span>
            </div>
            <div class="info-row">
              <span class="info-label">所在楼层</span>
              <span class="info-value">{{ getMapName(selectedStairway?.mapId) }}</span>
            </div>
            <div class="info-row" v-if="selectedStairway?.upperMapId">
              <span class="info-label">上层楼层</span>
              <span class="info-value">{{ getMapName(selectedStairway?.upperMapId) }}</span>
            </div>
            <div class="info-row" v-if="selectedStairway?.lowerMapId">
              <span class="info-label">下层楼层</span>
              <span class="info-value">{{ getMapName(selectedStairway?.lowerMapId) }}</span>
            </div>
            <div class="info-row" v-if="selectedStairway?.description">
              <span class="info-label">描述</span>
              <span class="info-value">{{ selectedStairway?.description }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer stairway-actions">
          <button v-if="selectedStairway?.upperMapId" class="btn-navigate" @click="navigateToFloor(selectedStairway.upperMapId)">
            ⬆️ 前往上层
          </button>
          <button v-if="selectedStairway?.lowerMapId" class="btn-navigate" @click="navigateToFloor(selectedStairway.lowerMapId)">
            ⬇️ 前往下层
          </button>
          <button class="btn-connection" @click="openStairwayConnectionModal">🔗 管理连接</button>
          <button class="btn-edit" @click="editStairway">✏️ 编辑</button>
          <button class="btn-delete" @click="confirmDeleteStairway">🗑️ 删除</button>
        </div>
      </div>
    </div>

    <!-- 楼梯连接管理模态框 -->
    <StairwayConnectionModal
      v-if="showStairwayConnectionModal && selectedStairway"
      :stairwayId="selectedStairway.stairwayId"
      @close="closeStairwayConnectionModal"
      @updated="onStairwayConnectionUpdated"
    />

    <!-- 添加门模态框 -->
    <div v-if="showDoorModal" class="modal-overlay" @click="closeDoorModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingDoor ? '编辑门' : '添加门' }}</h3>
          <button class="btn-close-modal" @click="closeDoorModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>门坐标</label>
            <div class="coord-display">
              X: {{ doorForm.x?.toFixed(2) || 0 }} m, Y: {{ doorForm.y?.toFixed(2) || 0 }} m
            </div>
          </div>
          <div class="form-item">
            <label>房间名称</label>
            <input type="text" v-model="doorForm.roomName" placeholder="如：会议室A" />
          </div>
          <div class="form-item">
            <label>所在楼层</label>
            <input type="text" v-model="doorForm.mapId" readonly class="readonly" />
          </div>
          <div class="form-item">
            <label>绑定围栏</label>
            <select v-model="doorForm.targetRegionId">
              <option value="">-- 不绑定围栏 --</option>
              <option v-for="region in currentFloorRegions" :key="region.regionId" :value="region.regionId">
                {{ region.regionName }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="doorForm.description" placeholder="可选描述信息"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="editingDoor" class="btn-delete" @click="deleteDoor">删除</button>
          <button class="btn-cancel" @click="closeDoorModal">取消</button>
          <button class="btn-confirm" @click="submitDoor">{{ editingDoor ? '保存修改' : '确认添加' }}</button>
        </div>
      </div>
    </div>

    <!-- 门详情模态框 -->
    <div v-if="showDoorDetail" class="modal-overlay" @click="closeDoorDetail">
      <div class="modal-content door-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedDoor?.roomName }}</h3>
          <button class="btn-close-modal" @click="closeDoorDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="stairway-info">
            <div class="info-row">
              <span class="info-label">类型</span>
              <span class="info-value">{{ selectedDoor?.roomType === 2 ? '楼道' : (selectedDoor?.roomType === 3 ? '出入口' : '房间') }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">坐标位置</span>
              <span class="info-value">X: {{ selectedDoor?.x?.toFixed(2) }} m, Y: {{ selectedDoor?.y?.toFixed(2) }} m</span>
            </div>
            <div class="info-row">
              <span class="info-label">所在楼层</span>
              <span class="info-value">{{ getMapName(selectedDoor?.mapId) }}</span>
            </div>
            <div class="info-row" v-if="selectedDoor?.targetRegionId">
              <span class="info-label">绑定围栏</span>
              <span class="info-value">{{ selectedDoor?.targetRegionName || getRegionName(selectedDoor?.targetRegionId) }}</span>
            </div>
            <div class="info-row" v-if="selectedDoor?.description">
              <span class="info-label">描述</span>
              <span class="info-value">{{ selectedDoor?.description }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer stairway-actions">
          <button v-if="selectedDoor?.targetRegionId" class="btn-edit" @click="openBoundRegionFromDoor">查看围栏</button>
          <button class="btn-edit" @click="editDoor">✏️ 编辑</button>
          <button class="btn-delete" @click="confirmDeleteDoor">🗑️ 删除</button>
        </div>
      </div>
    </div>

    <!-- 添加RFID设备模态框 -->
    <div v-if="showRfidModal" class="modal-overlay" @click="closeRfidModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRfid ? '编辑RFID设备' : '添加RFID设备' }}</h3>
          <button class="btn-close-modal" @click="closeRfidModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>设备坐标</label>
            <div class="coord-display">
              X: {{ rfidForm.x?.toFixed(2) || 0 }} m, Y: {{ rfidForm.y?.toFixed(2) || 0 }} m
            </div>
          </div>
          <div class="form-item">
            <label>设备名称</label>
            <input type="text" v-model="rfidForm.deviceName" placeholder="如：RFID-001" />
          </div>
          <div class="form-item">
            <label>所在楼层</label>
            <input type="text" v-model="rfidForm.mapId" readonly class="readonly" />
          </div>
          <div class="form-item">
            <label>所属楼梯（可选）</label>
            <select v-model="rfidForm.stairwayId">
              <option value="">-- 不属于任何楼梯 --</option>
              <option v-for="stairway in currentFloorStairways" :key="stairway.stairwayId" :value="stairway.stairwayId">
                {{ stairway.stairwayName }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>所属房间/门（可选）</label>
            <select v-model="rfidForm.doorId">
              <option :value="null">-- 不属于任何房间 --</option>
              <option v-for="door in currentFloorDoors" :key="door.id" :value="door.id">
                {{ door.roomName }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="rfidForm.description" placeholder="可选描述信息"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button v-if="editingRfid" class="btn-delete" @click="deleteRfid">删除</button>
          <button class="btn-cancel" @click="closeRfidModal">取消</button>
          <button class="btn-confirm" @click="submitRfid">{{ editingRfid ? '保存修改' : '确认添加' }}</button>
        </div>
      </div>
    </div>

    <!-- RFID设备详情模态框 -->
    <div v-if="showRfidDetail" class="modal-overlay" @click="closeRfidDetail">
      <div class="modal-content rfid-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedRfid?.deviceName }}</h3>
          <button class="btn-close-modal" @click="closeRfidDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="stairway-info">
            <div class="info-row">
              <span class="info-label">坐标位置</span>
              <span class="info-value">X: {{ selectedRfid?.x?.toFixed(2) }} m, Y: {{ selectedRfid?.y?.toFixed(2) }} m</span>
            </div>
            <div class="info-row">
              <span class="info-label">所在楼层</span>
              <span class="info-value">{{ getMapName(selectedRfid?.mapId) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">所属楼梯</span>
              <span class="info-value">{{ getStairwayName(selectedRfid?.stairwayId) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">所属房间</span>
              <span class="info-value">{{ getDoorName(selectedRfid?.doorId) }}</span>
            </div>
            <div class="info-row" v-if="selectedRfid?.description">
              <span class="info-label">描述</span>
              <span class="info-value">{{ selectedRfid?.description }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer stairway-actions">
          <button class="btn-edit" @click="editRfid">✏️ 编辑</button>
          <button class="btn-delete" @click="confirmDeleteRfid">🗑️ 删除</button>
        </div>
      </div>
    </div>

    <div v-if="showRegionDetail" class="modal-overlay" @click="closeRegionDetail">
      <div class="modal-content region-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedRegion?.regionName }}</h3>
          <button class="btn-close-modal" @click="closeRegionDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="stairway-info">
            <div class="info-row">
              <span class="info-label">所在楼层</span>
              <span class="info-value">{{ getMapName(selectedRegion?.mapId) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">点位数量</span>
              <span class="info-value">{{ selectedRegionPoints.length }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">覆盖网格</span>
              <span class="info-value">{{ selectedRegionGridCellCount }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">填充样式</span>
              <span class="info-value region-style-preview">
                <span class="region-color-chip" :style="{ backgroundColor: selectedRegion?.color || '#3B82F6', opacity: selectedRegion?.fillOpacity ?? 0.3 }"></span>
                <span>{{ selectedRegion?.color || '#3B82F6' }} / {{ selectedRegion?.fillOpacity ?? 0.3 }}</span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">线宽</span>
              <span class="info-value">{{ selectedRegion?.strokeWidth }}</span>
            </div>
            <div class="info-row" v-if="selectedRegion?.description">
              <span class="info-label">描述</span>
              <span class="info-value">{{ selectedRegion?.description }}</span>
            </div>
          </div>
          <div class="region-detail-points">
            <h4>顶点坐标</h4>
            <div v-if="selectedRegionPoints.length === 0" class="region-point-empty">暂无坐标数据</div>
            <div v-for="(point, index) in selectedRegionPoints" :key="`detail-point-${index}`" class="region-point-item">
              <span>#{{ index + 1 }} X: {{ Number(point.xCoordinate).toFixed(2) }}, Y: {{ Number(point.yCoordinate).toFixed(2) }}</span>
            </div>
          </div>
          <div class="region-detail-points">
            <h4>房间门绑定</h4>
            <div v-if="selectedRegionDoors.length === 0" class="region-point-empty">当前围栏还没有绑定门</div>
            <div v-for="door in selectedRegionDoors" :key="`region-door-${door.id}`" class="region-door-item">
              <div class="region-door-text">
                <span class="region-door-name">{{ door.roomName }}</span>
                <span class="region-door-meta">{{ getDoorTypeLabel(door.roomType) }} · X: {{ Number(door.x).toFixed(2) }}, Y: {{ Number(door.y).toFixed(2) }}</span>
              </div>
              <button class="btn-cancel btn-small" @click="unbindDoorFromRegion(door)">移除</button>
            </div>
            <div class="region-door-picker">
              <div class="region-door-picker-header">
                <span>添加本层门</span>
                <span class="region-door-hint">支持多选，已绑定其他围栏的门会改绑到当前围栏</span>
              </div>
              <div v-if="bindableDoorsForRegion.length === 0" class="region-point-empty">当前楼层没有可添加的门</div>
              <select v-else v-model="regionDoorSelection" multiple class="region-door-select">
                <option v-for="door in bindableDoorsForRegion" :key="`bind-door-${door.id}`" :value="String(door.id)">
                  {{ formatDoorBindingOption(door) }}
                </option>
              </select>
              <div class="region-door-actions">
                <button class="btn-confirm btn-small" @click="bindSelectedDoorsToRegion" :disabled="regionDoorSelection.length === 0">添加选中门</button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer stairway-actions">
          <button class="btn-edit" @click="editRegion">✎ 编辑</button>
          <button class="btn-delete" @click="confirmDeleteRegion">🗑️ 删除</button>
        </div>
      </div>
    </div>

    <!-- 边管理模态框 -->
    <div v-if="showEdgeModal" class="modal-overlay" @click="closeEdgeModal">
      <div class="modal-content edge-modal" @click.stop>
        <div class="modal-header">
          <h3>连接节点</h3>
          <button class="btn-close-modal" @click="closeEdgeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="edge-info">
            <div class="selected-node">
              <span class="node-label">起点：</span>
              <span class="node-name">{{ selectedNodeForEdge?.nodeName }}</span>
            </div>
            <div class="arrow">↓</div>
            <div class="target-nodes">
              <span class="node-label">选择终点（绿色=已连接，浅绿色=已选择）：</span>
              <div class="node-list">
                <div 
                  v-for="node in availableNodes" 
                  :key="`${node.type}-${node.id}`"
                  class="node-item"
                  :class="{ 
                    connected: isNodesConnected(node.type, node.id),
                    selected: isNodeSelected(node.type, node.id)
                  }"
                  @click="handleNodeClick(node)">
                  <span class="node-icon">{{ node.type === 1 ? '🚪' : '🪜' }}</span>
                  <span class="node-name">{{ node.name }}</span>
                  <span v-if="isNodesConnected(node.type, node.id)" class="connected-badge">已连接</span>
                  <span v-else-if="isNodeSelected(node.type, node.id)" class="selected-badge">已选择</span>
                </div>
              </div>
            </div>
            <div v-if="selectedTargetNodes.length > 0" class="selected-count">
              已选择 {{ selectedTargetNodes.length }} 个节点
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeEdgeModal">关闭</button>
          <button 
            v-if="selectedTargetNodes.length > 0" 
            class="btn-confirm" 
            @click="createEdgesBatch">
            添加 {{ selectedTargetNodes.length }} 条边
          </button>
        </div>
      </div>
    </div>
    <!-- 路径规划面板 -->
    <PathPlanningPanel
      v-if="showPathPlanning"
      ref="pathPlanningPanelRef"
      @close="closePathPlanning"
      @path-result="onPathResult"
      @adding-point-change="onAddingPointChange"
      @navigate-floor="navigateToFloor"
    />

    <!-- 查看连接模态框 -->
    <div v-if="showViewConnectionsModal" class="modal-overlay" @click="closeViewConnectionsModal">
      <div class="modal-content view-connections-modal" @click.stop>
        <div class="modal-header">
          <h3>查看节点连接</h3>
          <button class="btn-close-modal" @click="closeViewConnectionsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="view-connections-info">
            <div class="selected-node">
              <span class="node-label">当前节点：</span>
              <span class="node-name">{{ selectedNodeForView?.nodeName }}</span>
            </div>
            <div class="arrow">↓</div>
            <div class="connected-nodes-section">
              <span class="node-label">已连接的节点（选择后可删除连接）：</span>
              <div v-if="connectedNodes.length === 0" class="empty-connections">
                暂无连接
              </div>
              <div v-else class="node-list">
                <div 
                  v-for="item in connectedNodes" 
                  :key="`edge-${item.edge.id}`"
                  class="node-item"
                  :class="{ selected: isEdgeSelected(item.edge.id) }"
                  @click="toggleEdgeSelection(item.edge.id)">
                  <span class="node-icon">{{ item.node.type === 1 ? '🚪' : '🪜' }}</span>
                  <span class="node-name">{{ item.node.name }}</span>
                  <span class="edge-weight">距离: {{ item.edge.weight }}m</span>
                  <span v-if="isEdgeSelected(item.edge.id)" class="selected-badge">已选择</span>
                </div>
              </div>
            </div>
            <div v-if="selectedEdgesToDelete.length > 0" class="selected-count">
              已选择 {{ selectedEdgesToDelete.length }} 条边
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeViewConnectionsModal">关闭</button>
          <button 
            v-if="selectedEdgesToDelete.length > 0" 
            class="btn-delete" 
            @click="deleteSelectedEdges">
            删除 {{ selectedEdgesToDelete.length }} 条边
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from './utils/api.js'
import MapCanvas from './components/MapCanvas.vue'
import StairwayConnectionModal from './components/StairwayConnectionModal.vue'
import PathPlanningPanel from './components/PathPlanningPanel.vue'

const loading = ref(false)
const mapList = ref([])
const selectedMap = ref(null)
const stairways = ref([])
const doors = ref([])
const rfidDevices = ref([])
const regions = ref([])  // 围栏列表
const regionCoordinates = ref({})  // 围栏坐标点 {regionId: [coords]}
const regionGridCells = ref({})  // 围栏覆盖的1m网格中心点
const isAddingRegion = ref(false)
const isAddingStairway = ref(false)
const isAddingDoor = ref(false)
const isAddingCorridor = ref(false)
const isAddingEntrance = ref(false)
const isAddingRfid = ref(false)
const isAddingEdge = ref(false)
const isViewingConnections = ref(false)
const pendingStairwayCoords = ref(null)

// 路径规划相关状态
const showPathPlanning = ref(false)
const pathPlanningPanelRef = ref(null)
const isAddingPathPoint = ref(false)
const pathData = ref(null)  // 完整的路径数据
const currentPathSegment = ref([])  // 当前楼层的路径段
const pendingDoorCoords = ref(null)
const pendingCorridorCoords = ref(null)
const pendingEntranceCoords = ref(null)
const pendingRfidCoords = ref(null)

// 边管理相关状态
const selectedNodeForEdge = ref(null)  // 第一个选中的节点
const showEdgeModal = ref(false)
const availableNodes = ref([])  // 可连接的节点列表
const edges = ref([])  // 当前楼层的边列表
const selectedTargetNodes = ref([])  // 多选的目标节点列表

// 查看连接相关状态
const showViewConnectionsModal = ref(false)
const selectedNodeForView = ref(null)  // 查看连接的节点
const connectedNodes = ref([])  // 已连接的节点列表
const selectedEdgesToDelete = ref([])  // 选中要删除的边

// 楼梯相关状态
const showModal = ref(false)
const showStairwayDetail = ref(false)
const showStairwayConnectionModal = ref(false)
const selectedStairway = ref(null)
const editingStairway = ref(null)
const stairwayForm = ref({
  stairwayName: '',
  mapId: '',
  upperMapId: '',
  lowerMapId: '',
  x: 0,
  y: 0,
  description: ''
})

// 门相关状态
const showDoorModal = ref(false)
const showDoorDetail = ref(false)
const selectedDoor = ref(null)
const editingDoor = ref(null)
const doorForm = ref({
  roomName: '',
  roomType: 1,  // 1-房间，2-楼道，3-出入口
  mapId: '',
  targetRegionId: '',
  x: 0,
  y: 0,
  description: ''
})

// RFID设备相关状态
const showRfidModal = ref(false)
const showRfidDetail = ref(false)
const selectedRfid = ref(null)
const editingRfid = ref(null)
const rfidForm = ref({
  deviceName: '',
  mapId: '',
  x: 0,
  y: 0,
  stairwayId: '',
  doorId: null,
  description: ''
})

const showRegionDetail = ref(false)
const selectedRegion = ref(null)
const editingRegion = ref(null)
const regionDraftPoints = ref([])
const regionForm = ref(createDefaultRegionForm())
const regionDoorSelection = ref([])

function createDefaultRegionForm(mapId = '') {
  return {
    regionId: '',
    regionName: '',
    mapId,
    description: '',
    color: '#3B82F6',
    fillOpacity: 0.3,
    strokeWidth: 2,
    isActive: true
  }
}

// 当前楼层的楼梯和门列表（用于下拉选择）
const currentFloorStairways = computed(() => stairways.value)
const currentFloorDoors = computed(() => doors.value)
const currentFloorRegions = computed(() => regions.value)
const selectedRegionDoors = computed(() => {
  if (!selectedRegion.value?.regionId) return []
  return currentFloorDoors.value.filter(door => door.targetRegionId === selectedRegion.value.regionId)
})
const bindableDoorsForRegion = computed(() => {
  if (!selectedRegion.value?.mapId) return []
  return currentFloorDoors.value.filter(door =>
    door.mapId === selectedRegion.value.mapId &&
    door.targetRegionId !== selectedRegion.value.regionId
  )
})
const currentRegionPoints = computed(() => resequenceRegionPoints(regionDraftPoints.value))
const selectedRegionPoints = computed(() => {
  if (!selectedRegion.value) return []
  return resequenceRegionPoints(regionCoordinates.value[selectedRegion.value.regionId] || [])
})
const selectedRegionGridCellCount = computed(() => {
  if (!selectedRegion.value) return 0
  return (regionGridCells.value[selectedRegion.value.regionId] || []).length
})
const regionDraftStyle = computed(() => ({
  color: regionForm.value.color || '#3B82F6',
  fillOpacity: Number(regionForm.value.fillOpacity ?? 0.3),
  strokeWidth: Number(regionForm.value.strokeWidth ?? 2)
}))

function normalizeCoordinatePoint(point, index) {
  return {
    pointOrder: index + 1,
    xCoordinate: Number(point?.xCoordinate ?? point?.xcoordinate ?? point?.x ?? 0),
    yCoordinate: Number(point?.yCoordinate ?? point?.ycoordinate ?? point?.y ?? 0)
  }
}

function resequenceRegionPoints(points) {
  return (points || []).map((point, index) => normalizeCoordinatePoint(point, index))
}

function snapToGridCenter(value, maxValue) {
  const numericValue = Number(value)
  const numericMax = Number(maxValue)
  if (!Number.isFinite(numericValue)) return 0.5
  if (!Number.isFinite(numericMax) || numericMax <= 1) {
    return 0.5
  }

  const snapped = Math.floor(numericValue) + 0.5
  const clamped = Math.min(Math.max(snapped, 0.5), numericMax - 0.5)
  return Number(clamped.toFixed(2))
}

function normalizeRegionEntity(region, coordinates = null) {
  const normalizedCoordinates = coordinates ? resequenceRegionPoints(coordinates) : resequenceRegionPoints(region?.coordinates || [])
  return {
    ...region,
    fillOpacity: Number(region?.fillOpacity ?? 0.3),
    strokeWidth: Number(region?.strokeWidth ?? 2),
    isActive: region?.isActive !== false,
    coordinates: normalizedCoordinates
  }
}

function syncRegionState(region, coordinates = null) {
  if (!region?.regionId) return

  const normalizedRegion = normalizeRegionEntity(region, coordinates)
  const nextRegions = [...regions.value]
  const existingIndex = nextRegions.findIndex(item => item.regionId === normalizedRegion.regionId)

  if (existingIndex >= 0) {
    nextRegions.splice(existingIndex, 1, normalizedRegion)
  } else {
    nextRegions.unshift(normalizedRegion)
  }

  regions.value = nextRegions
  regionCoordinates.value = {
    ...regionCoordinates.value,
    [normalizedRegion.regionId]: normalizedRegion.coordinates
  }
}

const scale = computed(() => {
  if (!selectedMap.value || !selectedMap.value.shipLengthM || !selectedMap.value.imageWidthPx) {
    return 0
  }
  return selectedMap.value.shipLengthM / selectedMap.value.imageWidthPx
})

const mapCanvasUrl = computed(() => {
  if (!selectedMap.value || !selectedMap.value.imagePath) return ''
  return `/api/map-info/image?path=${encodeURIComponent(selectedMap.value.imagePath)}`
})

function normalizeListResponse(payload) {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  return []
}

onMounted(() => {
  loadMapList()
})

watch(selectedMap, (newMap) => {
  if (newMap) {
    loadStairways(newMap.mapId)
    loadDoors(newMap.mapId)
    loadRfidDevices(newMap.mapId)
    loadRegions(newMap.mapId)
    updateCurrentPathSegment(newMap.mapId)
  }
})

// 更新当前楼层的路径段
function updateCurrentPathSegment(mapId) {
  if (!pathData.value || !pathData.value.path_nodes) {
    currentPathSegment.value = []
    return
  }
  
  // 筛选当前楼层的节点
  currentPathSegment.value = pathData.value.path_nodes.filter(node => node.map_id === mapId)
}

async function loadMapList() {
  loading.value = true
  try {
    const response = await apiClient.get('/map-info/list')
    // 后端返回格式: {success: true, data: [...]}
    mapList.value = Array.isArray(response?.data) ? response.data : []
  } catch (error) {
    console.error('加载地图列表失败:', error)
    mapList.value = []
  } finally {
    loading.value = false
  }
}

async function loadStairways(mapId) {
  try {
    const response = await apiClient.get(`/stairways/map/${mapId}`)
    // 后端返回格式: {data: [...], total: n}
    stairways.value = Array.isArray(response?.data) ? response.data : []
  } catch (error) {
    console.error('加载楼梯信息失败:', error)
    stairways.value = []
  }
}

async function loadDoors(mapId) {
  try {
    const response = await apiClient.get(`/doors/map/${mapId}`)
    // 后端返回格式: {data: [...], total: n}
    doors.value = Array.isArray(response?.data) ? response.data : []
  } catch (error) {
    console.error('加载门信息失败:', error)
    doors.value = []
  }
}

async function loadRfidDevices(mapId) {
  try {
    const response = await apiClient.get(`/rfid-devices/map/${mapId}`)
    // 后端返回格式: {data: [...], total: n}
    rfidDevices.value = Array.isArray(response?.data) ? response.data : []
  } catch (error) {
    console.error('加载RFID设备信息失败:', error)
    rfidDevices.value = []
  }
}

async function loadRegions(mapId) {
  try {
    const response = await apiClient.get(`/regions/map/${mapId}`)
    const rawRegions = normalizeListResponse(response)
    const nextRegionCoordinates = {}
    const nextRegionGridCells = {}
    const nextRegions = []

    for (const region of rawRegions) {
      let coordinates = []
      let gridCells = []

      try {
        const coordsResponse = await apiClient.get(`/regions/${region.regionId}/coordinates`)
        coordinates = resequenceRegionPoints(normalizeListResponse(coordsResponse))
      } catch (coordError) {
        console.warn(`加载围栏 ${region.regionId} 的坐标点失败:`, coordError)
      }

      try {
        const gridCellsResponse = await apiClient.get(`/regions/${region.regionId}/grid-cells`)
        gridCells = normalizeListResponse(gridCellsResponse)
      } catch (gridCellError) {
        console.warn(`加载围栏 ${region.regionId} 的网格中心点失败:`, gridCellError)
      }

      nextRegionCoordinates[region.regionId] = coordinates
      nextRegionGridCells[region.regionId] = gridCells
      nextRegions.push(normalizeRegionEntity(region, coordinates))
    }

    regions.value = nextRegions
    regionCoordinates.value = nextRegionCoordinates
    regionGridCells.value = nextRegionGridCells
  } catch (error) {
    console.error('加载围栏信息失败:', error)
    regions.value = []
    regionCoordinates.value = {}
    regionGridCells.value = {}
  }
}

function closeRegionEditor() {
  isAddingRegion.value = false
  editingRegion.value = null
  regionDraftPoints.value = []
  regionForm.value = createDefaultRegionForm(selectedMap.value?.mapId || '')
}

function closeRegionDetail() {
  showRegionDetail.value = false
  selectedRegion.value = null
  regionDoorSelection.value = []
}

function startRegionDrawing(region = null) {
  if (!selectedMap.value) return
  closeRegionDetail()
  isAddingRegion.value = true
  isAddingStairway.value = false
  isAddingDoor.value = false
  isAddingCorridor.value = false
  isAddingEntrance.value = false
  isAddingRfid.value = false
  isAddingEdge.value = false
  isViewingConnections.value = false
  isAddingPathPoint.value = false

  if (region) {
    editingRegion.value = region
    regionForm.value = {
      regionId: region.regionId,
      regionName: region.regionName || '',
      mapId: region.mapId || selectedMap.value.mapId,
      description: region.description || '',
      color: region.color || '#3B82F6',
      fillOpacity: Number(region.fillOpacity ?? 0.3),
      strokeWidth: Number(region.strokeWidth ?? 2),
      isActive: region.isActive !== false
    }
    regionDraftPoints.value = resequenceRegionPoints(regionCoordinates.value[region.regionId] || [])
  } else {
    editingRegion.value = null
    regionForm.value = createDefaultRegionForm(selectedMap.value.mapId)
    regionDraftPoints.value = []
  }
}

function toggleRegionDrawing() {
  if (!selectedMap.value) return
  if (isAddingRegion.value) {
    closeRegionEditor()
    return
  }
  startRegionDrawing()
  alert('请在地图上依次点击围栏顶点，至少选择 3 个点')
}

function onRegionPointClick(coords) {
  if (!isAddingRegion.value) return
  const snappedX = snapToGridCenter(coords.x, selectedMap.value?.shipLengthM)
  const snappedY = snapToGridCenter(coords.y, selectedMap.value?.shipWidthM)
  regionDraftPoints.value = resequenceRegionPoints([
    ...regionDraftPoints.value,
    {
      xCoordinate: snappedX,
      yCoordinate: snappedY
    }
  ])
}

function undoRegionPoint() {
  regionDraftPoints.value = resequenceRegionPoints(regionDraftPoints.value.slice(0, -1))
}

function clearRegionPoints() {
  regionDraftPoints.value = []
}

function removeRegionPoint(index) {
  regionDraftPoints.value = resequenceRegionPoints(
    regionDraftPoints.value.filter((_, pointIndex) => pointIndex !== index)
  )
}

async function submitRegion() {
  if (!regionForm.value.regionName || !regionForm.value.regionName.trim()) {
    alert('请输入围栏名称')
    return
  }
  if (currentRegionPoints.value.length < 3) {
    alert('围栏至少需要 3 个点')
    return
  }
  const fillOpacity = Number(regionForm.value.fillOpacity)
  const strokeWidth = Number(regionForm.value.strokeWidth)
  if (Number.isNaN(fillOpacity) || fillOpacity < 0 || fillOpacity > 1) {
    alert('透明度必须在 0 到 1 之间')
    return
  }
  if (Number.isNaN(strokeWidth) || strokeWidth <= 0) {
    alert('线宽必须大于 0')
    return
  }

  try {
    const payload = {
      regionId: editingRegion.value ? regionForm.value.regionId : (regionForm.value.regionId?.trim() || `region_${Date.now()}`),
      regionName: regionForm.value.regionName.trim(),
      mapId: regionForm.value.mapId || selectedMap.value?.mapId,
      description: regionForm.value.description || '',
      color: regionForm.value.color || '#3B82F6',
      fillOpacity,
      strokeWidth,
      isActive: regionForm.value.isActive !== false,
      coordinates: currentRegionPoints.value.map((point, index) => ({
        pointOrder: index + 1,
        xCoordinate: snapToGridCenter(point.xCoordinate, selectedMap.value?.shipLengthM),
        yCoordinate: snapToGridCenter(point.yCoordinate, selectedMap.value?.shipWidthM)
      }))
    }

    let savedRegionId = payload.regionId
    if (editingRegion.value) {
      await apiClient.put('/regions', payload)
      alert('围栏修改成功')
    } else {
      savedRegionId = await apiClient.post('/regions', payload)
      alert('围栏创建成功')
    }

    closeRegionEditor()
    if (selectedMap.value) {
      await loadRegions(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error(editingRegion.value ? '修改围栏失败:' : '创建围栏失败:', error)
    alert((editingRegion.value ? '修改围栏失败: ' : '创建围栏失败: ') + error.message)
  }
}

async function submitRegionAndRender() {
  if (!regionForm.value.regionName || !regionForm.value.regionName.trim()) {
    alert('请输入围栏名称')
    return
  }
  if (currentRegionPoints.value.length < 3) {
    alert('围栏至少需要 3 个点')
    return
  }

  const fillOpacity = Number(regionForm.value.fillOpacity)
  const strokeWidth = Number(regionForm.value.strokeWidth)

  if (Number.isNaN(fillOpacity) || fillOpacity < 0 || fillOpacity > 1) {
    alert('透明度必须在 0 到 1 之间')
    return
  }
  if (Number.isNaN(strokeWidth) || strokeWidth <= 0) {
    alert('线宽必须大于 0')
    return
  }

  try {
    const payload = {
      regionId: editingRegion.value ? regionForm.value.regionId : (regionForm.value.regionId?.trim() || `region_${Date.now()}`),
      regionName: regionForm.value.regionName.trim(),
      mapId: regionForm.value.mapId || selectedMap.value?.mapId,
      description: regionForm.value.description || '',
      color: regionForm.value.color || '#3B82F6',
      fillOpacity,
      strokeWidth,
      isActive: regionForm.value.isActive !== false,
      coordinates: currentRegionPoints.value.map((point, index) => ({
        pointOrder: index + 1,
        xCoordinate: point.xCoordinate,
        yCoordinate: point.yCoordinate
      }))
    }

    let savedRegionId = payload.regionId
    if (editingRegion.value) {
      await apiClient.put('/regions', payload)
      alert('围栏修改成功')
    } else {
      savedRegionId = await apiClient.post('/regions', payload)
      alert('围栏创建成功')
    }

    syncRegionState(
      {
        ...payload,
        regionId: savedRegionId
      },
      payload.coordinates
    )

    closeRegionEditor()
    if (selectedMap.value) {
      await loadRegions(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error(editingRegion.value ? '修改围栏失败:' : '创建围栏失败:', error)
    alert((editingRegion.value ? '修改围栏失败: ' : '创建围栏失败: ') + error.message)
  }
}

function onRegionDetailClick(region) {
  if (isAddingRegion.value) return
  selectedRegion.value = region
  regionDoorSelection.value = []
  showRegionDetail.value = true
}

function editRegion() {
  if (!selectedRegion.value) return
  startRegionDrawing(selectedRegion.value)
}

function confirmDeleteRegion() {
  if (!selectedRegion.value) return
  if (confirm(`确定要删除围栏"${selectedRegion.value.regionName}"吗？`)) {
    deleteRegionById(selectedRegion.value.regionId)
  }
}

async function deleteRegionById(regionId) {
  try {
    await apiClient.delete(`/regions/${regionId}`)
    alert('围栏删除成功')
    closeRegionEditor()
    closeRegionDetail()
    if (selectedMap.value) {
      await loadRegions(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error('删除围栏失败:', error)
    alert('删除围栏失败: ' + error.message)
  }
}

function selectMap(map) {
  closeRegionEditor()
  closeRegionDetail()
  selectedMap.value = map
  isAddingStairway.value = false
  isAddingDoor.value = false
  isAddingCorridor.value = false
  isAddingEntrance.value = false
  isAddingRfid.value = false
  isAddingEdge.value = false
  selectedNodeForEdge.value = null
  pendingStairwayCoords.value = null
  loadEdges(map.mapId)
}

function navigateMap(direction) {
  const currentIndex = mapList.value.findIndex(m => m.mapId === selectedMap.mapId)
  const newIndex = currentIndex + direction
  if (newIndex >= 0 && newIndex < mapList.value.length) {
    closeRegionEditor()
    closeRegionDetail()
    selectedMap.value = mapList.value[newIndex]
  }
}

// 打开添加楼梯模态框
function openStairwayModal() {
  if (!selectedMap.value) return
  closeRegionEditor()
  isAddingStairway.value = true
  pendingStairwayCoords.value = null
  alert('请在地图上点击选择楼梯位置')
}

// 处理地图点击，获取楼梯坐标
function onStairwayCoordinateClick(coords) {
  pendingStairwayCoords.value = coords
  stairwayForm.value = {
    stairwayName: `${selectedMap.value.regionName || selectedMap.value.mapId} 楼梯`,
    mapId: selectedMap.value.mapId,
    upperMapId: selectedMap.value.mapId,
    lowerMapId: '',
    x: coords.x,
    y: coords.y,
    description: ''
  }
  isAddingStairway.value = false
  showModal.value = true
}

// 关闭模态框
function closeModal() {
  showModal.value = false
  isAddingStairway.value = false
  pendingStairwayCoords.value = null
  editingStairway.value = null
  stairwayForm.value = {
    stairwayName: '',
    mapId: '',
    upperMapId: '',
    lowerMapId: '',
    x: 0,
    y: 0,
    description: ''
  }
}

// 提交楼梯信息
async function submitStairway() {
  if (!stairwayForm.value.stairwayName || !stairwayForm.value.stairwayName.trim()) {
    alert('请输入楼梯名称')
    return
  }
  if (!stairwayForm.value.mapId) {
    alert('所在楼层不能为空')
    return
  }
  if (stairwayForm.value.x === null || stairwayForm.value.x === undefined || 
      stairwayForm.value.y === null || stairwayForm.value.y === undefined) {
    alert('楼梯坐标无效')
    return
  }
  try {
    const data = {
      stairwayId: editingStairway.value ? stairwayForm.value.stairwayId : `stairway_${Date.now()}`,
      stairwayName: stairwayForm.value.stairwayName,
      mapId: stairwayForm.value.mapId,
      upperMapId: stairwayForm.value.upperMapId || null,
      lowerMapId: stairwayForm.value.lowerMapId || null,
      x: stairwayForm.value.x,
      y: stairwayForm.value.y,
      description: stairwayForm.value.description || ''
    }
    
    if (editingStairway.value) {
      await apiClient.put('/stairways', data)
      alert('楼梯修改成功')
    } else {
      await apiClient.post('/stairways', data)
      alert('楼梯添加成功')
    }
    
    closeModal()
    // 重新加载楼梯数据
    if (selectedMap.value) {
      loadStairways(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error(editingStairway.value ? '修改楼梯失败:' : '添加楼梯失败:', error)
    alert((editingStairway.value ? '修改楼梯失败: ' : '添加楼梯失败: ') + error.message)
  }
}

// 关闭楼梯详情
function closeStairwayDetail() {
  showStairwayDetail.value = false
  selectedStairway.value = null
}

// 打开楼梯连接管理模态框
function openStairwayConnectionModal() {
  if (!selectedStairway.value) return
  showStairwayConnectionModal.value = true
}

// 关闭楼梯连接管理模态框
function closeStairwayConnectionModal() {
  showStairwayConnectionModal.value = false
}

// 楼梯连接更新后的回调
function onStairwayConnectionUpdated() {
  // 重新加载楼梯数据
  if (selectedMap.value) {
    loadStairways(selectedMap.value.mapId)
  }
}

// 编辑楼梯
function editStairway() {
  if (!selectedStairway.value) return
  editingStairway.value = selectedStairway.value
  stairwayForm.value = {
    stairwayId: selectedStairway.value.stairwayId,
    stairwayName: selectedStairway.value.stairwayName,
    mapId: selectedStairway.value.mapId,
    upperMapId: selectedStairway.value.upperMapId || '',
    lowerMapId: selectedStairway.value.lowerMapId || '',
    x: selectedStairway.value.x,
    y: selectedStairway.value.y,
    description: selectedStairway.value.description || ''
  }
  closeStairwayDetail()
  showModal.value = true
}

// 确认删除楼梯
function confirmDeleteStairway() {
  if (!selectedStairway.value) return
  if (confirm(`确定要删除楼梯"${selectedStairway.value.stairwayName}"吗？`)) {
    deleteStairwayById(selectedStairway.value.stairwayId)
  }
}

// 删除楼梯（从编辑模态框）
async function deleteStairway() {
  if (!editingStairway.value) return
  if (confirm(`确定要删除楼梯"${stairwayForm.value.stairwayName}"吗？`)) {
    await deleteStairwayById(editingStairway.value.stairwayId)
  }
}

// 删除楼梯API调用
async function deleteStairwayById(stairwayId) {
  try {
    await apiClient.delete(`/stairways/${stairwayId}`)
    alert('楼梯删除成功')
    closeModal()
    closeStairwayDetail()
    // 重新加载楼梯数据
    if (selectedMap.value) {
      loadStairways(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error('删除楼梯失败:', error)
    alert('删除楼梯失败: ' + error.message)
  }
}

// 跳转到指定楼层
function navigateToFloor(mapId) {
  const targetMap = mapList.value.find(m => m.mapId === mapId)
  if (targetMap) {
    closeRegionEditor()
    selectedMap.value = targetMap
    closeStairwayDetail()
  } else {
    alert('目标楼层不存在')
  }
}

// 获取地图名称
function getMapName(mapId) {
  const map = mapList.value.find(m => m.mapId === mapId)
  return map ? `${map.regionName} (${map.mapId})` : mapId
}

// ========== 门相关函数 ==========

// 打开添加门模态框
function openDoorModal() {
  if (!selectedMap.value) return
  closeRegionEditor()
  isAddingDoor.value = true
  pendingDoorCoords.value = null
  alert('请在地图上点击选择房间的位置')
}

// 打开添加楼道模态框
function openCorridorModal() {
  if (!selectedMap.value) return
  closeRegionEditor()
  isAddingCorridor.value = true
  pendingCorridorCoords.value = null
  alert('请在地图上点击选择楼道的位置')
}

// 打开添加出入口模态框
function openEntranceModal() {
  if (!selectedMap.value) return
  closeRegionEditor()
  isAddingEntrance.value = true
  pendingEntranceCoords.value = null
  alert('请在地图上点击选择出入口的位置')
}

// 处理地图点击，获取门坐标
function onDoorCoordinateClick(coords) {
  pendingDoorCoords.value = coords
  doorForm.value = {
    roomName: '',
    roomType: 1,  // 房间
    mapId: selectedMap.value.mapId,
    targetRegionId: '',
    x: coords.x,
    y: coords.y,
    description: ''
  }
  isAddingDoor.value = false
  showDoorModal.value = true
}

// 处理地图点击，获取楼道坐标
function onCorridorCoordinateClick(coords) {
  pendingCorridorCoords.value = coords
  doorForm.value = {
    roomName: '',
    roomType: 2,  // 楼道
    mapId: selectedMap.value.mapId,
    targetRegionId: '',
    x: coords.x,
    y: coords.y,
    description: ''
  }
  isAddingCorridor.value = false
  showDoorModal.value = true
}

// 处理地图点击，获取出入口坐标
function onEntranceCoordinateClick(coords) {
  pendingEntranceCoords.value = coords
  doorForm.value = {
    roomName: '',
    roomType: 3,  // 出入口
    mapId: selectedMap.value.mapId,
    targetRegionId: '',
    x: coords.x,
    y: coords.y,
    description: ''
  }
  isAddingEntrance.value = false
  showDoorModal.value = true
}

// 关闭门模态框
function closeDoorModal() {
  showDoorModal.value = false
  isAddingDoor.value = false
  isAddingCorridor.value = false
  isAddingEntrance.value = false
  pendingDoorCoords.value = null
  pendingCorridorCoords.value = null
  pendingEntranceCoords.value = null
  editingDoor.value = null
  doorForm.value = {
    roomName: '',
    roomType: 1,
    mapId: '',
    targetRegionId: '',
    x: 0,
    y: 0,
    description: ''
  }
}

// 提交门信息
async function submitDoor() {
  if (!doorForm.value.roomName || !doorForm.value.roomName.trim()) {
    const typeNames = { 1: '房间', 2: '楼道', 3: '出入口' }
    alert(`请输入${typeNames[doorForm.value.roomType] || '房间'}名称`)
    return
  }
  if (!doorForm.value.mapId) {
    alert('所在楼层不能为空')
    return
  }
  if (doorForm.value.x === null || doorForm.value.x === undefined || 
      doorForm.value.y === null || doorForm.value.y === undefined) {
    alert('坐标无效')
    return
  }
  try {
    const data = {
      id: editingDoor.value ? doorForm.value.id : undefined,
      roomName: doorForm.value.roomName.trim(),
      roomType: doorForm.value.roomType,
      mapId: doorForm.value.mapId,
      targetRegionId: doorForm.value.targetRegionId || null,
      x: doorForm.value.x,
      y: doorForm.value.y,
      description: doorForm.value.description || ''
    }
    
    if (editingDoor.value) {
      await apiClient.put('/doors', data)
      alert('门修改成功')
    } else {
      await apiClient.post('/doors', data)
      alert('门添加成功')
    }
    
    closeDoorModal()
    // 重新加载门数据
    if (selectedMap.value) {
      loadDoors(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error(editingDoor.value ? '修改门失败:' : '添加门失败:', error)
    alert((editingDoor.value ? '修改门失败: ' : '添加门失败: ') + error.message)
  }
}

// 关闭门详情
function closeDoorDetail() {
  showDoorDetail.value = false
  selectedDoor.value = null
}

// 编辑门
function editDoor() {
  if (!selectedDoor.value) return
  editingDoor.value = selectedDoor.value
  doorForm.value = {
    id: selectedDoor.value.id,
    roomName: selectedDoor.value.roomName,
    roomType: selectedDoor.value.roomType || 1,
    mapId: selectedDoor.value.mapId,
    targetRegionId: selectedDoor.value.targetRegionId || '',
    x: selectedDoor.value.x,
    y: selectedDoor.value.y,
    description: selectedDoor.value.description || ''
  }
  closeDoorDetail()
  showDoorModal.value = true
}

function openBoundRegionFromDoor() {
  if (!selectedDoor.value?.targetRegionId) return

  const region = regions.value.find(item => item.regionId === selectedDoor.value.targetRegionId)
  if (!region) {
    alert('未找到门绑定的房间区域')
    return
  }

  closeDoorDetail()
  onRegionDetailClick(region)
}

// 确认删除门
function confirmDeleteDoor() {
  if (!selectedDoor.value) return
  if (confirm(`确定要删除门"${selectedDoor.value.roomName}"吗？`)) {
    deleteDoorById(selectedDoor.value.id)
  }
}

// 删除门（从编辑模态框）
async function deleteDoor() {
  if (!editingDoor.value) return
  if (confirm(`确定要删除门"${doorForm.value.roomName}"吗？`)) {
    await deleteDoorById(editingDoor.value.id)
  }
}

// 删除门API调用
async function deleteDoorById(id) {
  try {
    await apiClient.delete(`/doors/${id}`)
    alert('门删除成功')
    closeDoorModal()
    closeDoorDetail()
    // 重新加载门数据
    if (selectedMap.value) {
      loadDoors(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error('删除门失败:', error)
    alert('删除门失败: ' + error.message)
  }
}

// ========== RFID设备相关函数 ==========

// 打开添加RFID设备模态框
function openRfidModal() {
  if (!selectedMap.value) return
  closeRegionEditor()
  isAddingRfid.value = true
  pendingRfidCoords.value = null
  alert('请在地图上点击选择RFID设备的位置')
}

// 处理地图点击，获取RFID设备坐标
function onRfidCoordinateClick(coords) {
  pendingRfidCoords.value = coords
  rfidForm.value = {
    deviceName: '',
    mapId: selectedMap.value.mapId,
    x: coords.x,
    y: coords.y,
    stairwayId: '',
    doorId: null,
    description: ''
  }
  isAddingRfid.value = false
  showRfidModal.value = true
}

// 关闭RFID设备模态框
function closeRfidModal() {
  showRfidModal.value = false
  isAddingRfid.value = false
  pendingRfidCoords.value = null
  editingRfid.value = null
  rfidForm.value = {
    deviceName: '',
    mapId: '',
    x: 0,
    y: 0,
    stairwayId: '',
    doorId: null,
    description: ''
  }
}

// 提交RFID设备信息
async function submitRfid() {
  if (!rfidForm.value.deviceName || !rfidForm.value.deviceName.trim()) {
    alert('请输入设备名称')
    return
  }
  if (!rfidForm.value.mapId) {
    alert('所在楼层不能为空')
    return
  }
  if (rfidForm.value.x === null || rfidForm.value.x === undefined || 
      rfidForm.value.y === null || rfidForm.value.y === undefined) {
    alert('设备坐标无效')
    return
  }
  try {
    const data = {
      id: editingRfid.value ? rfidForm.value.id : undefined,
      deviceName: rfidForm.value.deviceName,
      mapId: rfidForm.value.mapId,
      x: rfidForm.value.x,
      y: rfidForm.value.y,
      stairwayId: rfidForm.value.stairwayId || null,
      doorId: rfidForm.value.doorId || null,
      description: rfidForm.value.description || ''
    }
    
    if (editingRfid.value) {
      await apiClient.put('/rfid-devices', data)
      alert('RFID设备修改成功')
    } else {
      await apiClient.post('/rfid-devices', data)
      alert('RFID设备添加成功')
    }
    
    closeRfidModal()
    // 重新加载RFID设备数据
    if (selectedMap.value) {
      loadRfidDevices(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error(editingRfid.value ? '修改RFID设备失败:' : '添加RFID设备失败:', error)
    alert((editingRfid.value ? '修改RFID设备失败: ' : '添加RFID设备失败: ') + error.message)
  }
}

// 关闭RFID设备详情
function closeRfidDetail() {
  showRfidDetail.value = false
  selectedRfid.value = null
}

// 编辑RFID设备
function editRfid() {
  if (!selectedRfid.value) return
  editingRfid.value = selectedRfid.value
  rfidForm.value = {
    id: selectedRfid.value.id,
    deviceName: selectedRfid.value.deviceName,
    mapId: selectedRfid.value.mapId,
    x: selectedRfid.value.x,
    y: selectedRfid.value.y,
    stairwayId: selectedRfid.value.stairwayId || '',
    doorId: selectedRfid.value.doorId || null,
    description: selectedRfid.value.description || ''
  }
  closeRfidDetail()
  showRfidModal.value = true
}

// 确认删除RFID设备
function confirmDeleteRfid() {
  if (!selectedRfid.value) return
  if (confirm(`确定要删除RFID设备"${selectedRfid.value.deviceName}"吗？`)) {
    deleteRfidById(selectedRfid.value.id)
  }
}

// 删除RFID设备（从编辑模态框）
async function deleteRfid() {
  if (!editingRfid.value) return
  if (confirm(`确定要删除RFID设备"${rfidForm.value.deviceName}"吗？`)) {
    await deleteRfidById(editingRfid.value.id)
  }
}

// 删除RFID设备API调用
async function deleteRfidById(id) {
  try {
    await apiClient.delete(`/rfid-devices/${id}`)
    alert('RFID设备删除成功')
    closeRfidModal()
    closeRfidDetail()
    // 重新加载RFID设备数据
    if (selectedMap.value) {
      loadRfidDevices(selectedMap.value.mapId)
    }
  } catch (error) {
    console.error('删除RFID设备失败:', error)
    alert('删除RFID设备失败: ' + error.message)
  }
}

// 获取楼梯名称
function getStairwayName(stairwayId) {
  if (!stairwayId) return '无'
  const stairway = stairways.value.find(s => s.stairwayId === stairwayId)
  return stairway ? stairway.stairwayName : stairwayId
}

// 获取门/房间名称
function getDoorName(doorId) {
  if (!doorId) return '无'
  const door = doors.value.find(d => d.id === doorId)
  return door ? door.roomName : `门ID: ${doorId}`
}

function getRegionName(regionId) {
  if (!regionId) return '无'
  const region = regions.value.find(item => item.regionId === regionId)
  return region ? region.regionName : regionId
}

function getDoorTypeLabel(roomType) {
  if (roomType === 2) return '楼道'
  if (roomType === 3) return '出入口'
  return '房间'
}

function formatDoorBindingOption(door) {
  const currentRegionName = door.targetRegionId ? getRegionName(door.targetRegionId) : '未绑定'
  return `${door.roomName} · ${getDoorTypeLabel(door.roomType)} · 当前：${currentRegionName}`
}

function buildDoorBindingPayload(door, targetRegionId) {
  return {
    id: door.id,
    roomName: door.roomName,
    roomType: door.roomType,
    mapId: door.mapId,
    targetRegionId,
    x: door.x,
    y: door.y,
    description: door.description || ''
  }
}

async function bindSelectedDoorsToRegion() {
  if (!selectedRegion.value?.regionId || regionDoorSelection.value.length === 0) return

  const selectedDoors = bindableDoorsForRegion.value.filter(door =>
    regionDoorSelection.value.includes(String(door.id))
  )

  if (selectedDoors.length === 0) return

  try {
    await Promise.all(
      selectedDoors.map(door =>
        apiClient.put('/doors', buildDoorBindingPayload(door, selectedRegion.value.regionId))
      )
    )
    regionDoorSelection.value = []
    await loadDoors(selectedRegion.value.mapId)
    alert(`已为围栏绑定 ${selectedDoors.length} 个门`)
  } catch (error) {
    console.error('绑定围栏门失败:', error)
    alert('绑定围栏门失败: ' + error.message)
  }
}

async function unbindDoorFromRegion(door) {
  if (!door?.id) return

  try {
    await apiClient.put('/doors', buildDoorBindingPayload(door, null))
    await loadDoors(door.mapId)
    alert(`已移除门“${door.roomName}”的围栏绑定`)
  } catch (error) {
    console.error('移除围栏门失败:', error)
    alert('移除围栏门失败: ' + error.message)
  }
}

// ========== 边管理相关函数 ==========

// 加载当前楼层的边
async function loadEdges(mapId) {
  try {
    // 获取当前楼层所有节点的边
    const allEdges = []
    
    // 获取所有doors节点的边
    for (const door of doors.value) {
      const data = await apiClient.get(`/graph-edges/adjacent/1/${door.id}`)
      // GraphEdgeController直接返回List<GraphEdge>，不包装
      if (Array.isArray(data)) {
        allEdges.push(...data)
      }
    }
    
    // 获取所有stairways节点的边
    for (const stairway of stairways.value) {
      const data = await apiClient.get(`/graph-edges/adjacent/2/${stairway.stairwayId}`)
      // GraphEdgeController直接返回List<GraphEdge>，不包装
      if (Array.isArray(data)) {
        allEdges.push(...data)
      }
    }
    
    // 去重
    const uniqueEdges = []
    const edgeIds = new Set()
    for (const edge of allEdges) {
      if (!edgeIds.has(edge.id)) {
        edgeIds.add(edge.id)
        uniqueEdges.push(edge)
      }
    }
    
    edges.value = uniqueEdges
    console.log('加载的边列表:', edges.value)
  } catch (error) {
    console.error('加载边信息失败:', error)
    edges.value = []
  }
}

// 切换边管理模式
function toggleEdgeMode() {
  closeRegionEditor()
  isAddingEdge.value = !isAddingEdge.value
  selectedNodeForEdge.value = null
  
  if (isAddingEdge.value) {
    // 关闭其他模式
    isAddingStairway.value = false
    isAddingDoor.value = false
    isAddingCorridor.value = false
    isAddingEntrance.value = false
    isAddingRfid.value = false
    alert('边管理模式：点击第一个节点，然后选择要连接的节点')
  }
}

// 处理节点点击（用于创建边）
function onNodeClickForEdge(nodeType, nodeId, nodeName, mapId) {
  if (!isAddingEdge.value) return
  
  if (!selectedNodeForEdge.value) {
    // 选择第一个节点
    selectedNodeForEdge.value = { nodeType, nodeId, nodeName, mapId }
    // 加载可连接的节点列表
    loadAvailableNodes()
    showEdgeModal.value = true
  }
}

// 加载可连接的节点列表
function loadAvailableNodes() {
  const nodes = []
  
  // 获取选中节点的楼层ID
  const selectedNodeMapId = selectedNodeForEdge.value.mapId
  
  // 添加同楼层的doors节点
  doors.value.forEach(door => {
    // 只添加同楼层的节点
    if (door.mapId === selectedNodeMapId) {
      const typeText = door.roomType === 1 ? '房间' : (door.roomType === 2 ? '楼道' : '出入口')
      nodes.push({
        type: 1,
        id: door.id,
        name: `${door.roomName} (${typeText})`,
        mapId: door.mapId
      })
    }
  })
  
  // 添加同楼层的stairways节点
  stairways.value.forEach(stairway => {
    // 只添加同楼层的节点
    if (stairway.mapId === selectedNodeMapId) {
      nodes.push({
        type: 2,
        id: stairway.stairwayId,
        name: `${stairway.stairwayName} (楼梯)`,
        mapId: stairway.mapId
      })
    }
  })
  
  // 过滤掉已选中的节点
  availableNodes.value = nodes.filter(node => 
    !(node.type === selectedNodeForEdge.value.nodeType && node.id === selectedNodeForEdge.value.nodeId)
  )
}

// 创建边
async function createEdge(targetNode) {
  if (!selectedNodeForEdge.value) return
  
  try {
    // 计算两点之间的距离作为权重
    const node1 = getNodeCoordinates(selectedNodeForEdge.value.nodeType, selectedNodeForEdge.value.nodeId)
    const node2 = getNodeCoordinates(targetNode.type, targetNode.id)
    
    let weight = 1.0
    if (node1 && node2) {
      const distance = Math.sqrt(
        Math.pow(node2.x - node1.x, 2) + 
        Math.pow(node2.y - node1.y, 2)
      )
      weight = Math.round(distance * 100) / 100
    }
    
    const edgeData = {
      nodeAType: selectedNodeForEdge.value.nodeType,
      nodeAId: selectedNodeForEdge.value.nodeId,
      nodeBType: targetNode.type,
      nodeBId: targetNode.id,
      weight: weight
    }
    
    await apiClient.post('/graph-edges', edgeData)
    
    // 重新加载边
    if (selectedMap.value) {
      await loadEdges(selectedMap.value.mapId)
    }
    
    // 重新加载可用节点列表（更新连接状态）
    loadAvailableNodes()
    
    // 不关闭模态框，允许继续选择
  } catch (error) {
    console.error('创建边失败:', error)
    // 处理后端返回的错误信息
    const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message
    alert('创建边失败: ' + errorMessage)
  }
}

// 获取节点坐标
function getNodeCoordinates(nodeType, nodeId) {
  if (nodeType === 1) {
    // doors节点
    const door = doors.value.find(d => d.id == nodeId)
    return door ? { x: door.x, y: door.y } : null
  } else if (nodeType === 2) {
    // stairways节点
    const stairway = stairways.value.find(s => s.stairwayId === nodeId)
    return stairway ? { x: stairway.x, y: stairway.y } : null
  }
  return null
}

// 检查两个节点之间是否已有连接
function isNodesConnected(nodeType, nodeId) {
  if (!selectedNodeForEdge.value) return false
  
  return edges.value.some(edge => {
    // 检查双向连接
    return (
      (edge.nodeAType === selectedNodeForEdge.value.nodeType && 
       edge.nodeAId === selectedNodeForEdge.value.nodeId &&
       edge.nodeBType === nodeType && 
       edge.nodeBId === nodeId) ||
      (edge.nodeBType === selectedNodeForEdge.value.nodeType && 
       edge.nodeBId === selectedNodeForEdge.value.nodeId &&
       edge.nodeAType === nodeType && 
       edge.nodeAId === nodeId)
    )
  })
}

// 删除边
async function deleteEdge(targetNode) {
  if (!selectedNodeForEdge.value) return
  
  try {
    // 查找边
    const edge = edges.value.find(e => {
      return (
        (e.nodeAType === selectedNodeForEdge.value.nodeType && 
         e.nodeAId === selectedNodeForEdge.value.nodeId &&
         e.nodeBType === targetNode.type && 
         e.nodeBId === targetNode.id) ||
        (e.nodeBType === selectedNodeForEdge.value.nodeType && 
         e.nodeBId === selectedNodeForEdge.value.nodeId &&
         e.nodeAType === targetNode.type && 
         e.nodeAId === targetNode.id)
      )
    })
    
    if (!edge) {
      alert('未找到该边')
      return
    }
    
    await apiClient.delete(`/graph-edges/${edge.id}`)
    
    // 重新加载边
    if (selectedMap.value) {
      await loadEdges(selectedMap.value.mapId)
    }
    
    // 重新加载可用节点列表（更新连接状态）
    loadAvailableNodes()
    
  } catch (error) {
    console.error('删除边失败:', error)
    const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message
    alert('删除边失败: ' + errorMessage)
  }
}

// 处理节点点击（多选模式）
function handleNodeClick(targetNode) {
  if (isNodesConnected(targetNode.type, targetNode.id)) {
    // 已连接，不能选择
    return
  }
  
  // 检查是否已在选中列表中
  const index = selectedTargetNodes.value.findIndex(
    node => node.type === targetNode.type && node.id === targetNode.id
  )
  
  if (index >= 0) {
    // 已选中，取消选择
    selectedTargetNodes.value.splice(index, 1)
  } else {
    // 未选中，添加到选中列表
    selectedTargetNodes.value.push(targetNode)
  }
}

// 检查节点是否被选中
function isNodeSelected(nodeType, nodeId) {
  return selectedTargetNodes.value.some(
    node => node.type === nodeType && node.id === nodeId
  )
}

// 批量创建边
async function createEdgesBatch() {
  if (!selectedNodeForEdge.value || selectedTargetNodes.value.length === 0) {
    alert('请至少选择一个节点')
    return
  }
  
  try {
    // 构建边数据列表
    const edgesData = []
    
    for (const targetNode of selectedTargetNodes.value) {
      // 计算两点之间的距离作为权重
      const node1 = getNodeCoordinates(selectedNodeForEdge.value.nodeType, selectedNodeForEdge.value.nodeId)
      const node2 = getNodeCoordinates(targetNode.type, targetNode.id)
      
      let weight = 1.0
      if (node1 && node2) {
        const distance = Math.sqrt(
          Math.pow(node2.x - node1.x, 2) + 
          Math.pow(node2.y - node1.y, 2)
        )
        weight = Math.round(distance * 100) / 100
      }
      
      edgesData.push({
        nodeAType: selectedNodeForEdge.value.nodeType,
        nodeAId: selectedNodeForEdge.value.nodeId,
        nodeBType: targetNode.type,
        nodeBId: targetNode.id,
        weight: weight
      })
    }
    
    console.log('发送批量创建边请求:', edgesData)
    
    // 调用批量创建API
    // 注意：apiClient的响应拦截器已经返回了response.data，所以result就是数据本身
    const result = await apiClient.post('/graph-edges/batch', edgesData)
    
    console.log('批量创建边响应:', result)
    
    if (!result) {
      alert('服务器返回数据为空')
      return
    }
    
    let message = `成功创建 ${result.successCount || 0} 条边`
    if (result.skipCount > 0) {
      message += `\n跳过 ${result.skipCount} 条边（已存在或错误）`
      if (result.skippedEdges && result.skippedEdges.length > 0) {
        message += '\n跳过的边：\n' + result.skippedEdges.join('\n')
      }
    }
    alert(message)
    
    // 清空选中列表
    selectedTargetNodes.value = []
    
    // 重新加载边
    if (selectedMap.value) {
      await loadEdges(selectedMap.value.mapId)
    }
    
    // 重新加载可用节点列表（更新连接状态）
    loadAvailableNodes()
    
  } catch (error) {
    console.error('批量创建边失败:', error)
    alert('批量创建边失败: ' + error.message)
  }
}

// 关闭边模态框
function closeEdgeModal() {
  showEdgeModal.value = false
  selectedNodeForEdge.value = null
  availableNodes.value = []
  selectedTargetNodes.value = []
}

// ========== 查看连接功能 ==========

// 切换查看连接模式
function toggleViewConnectionsMode() {
  closeRegionEditor()
  isViewingConnections.value = !isViewingConnections.value
  selectedNodeForView.value = null
  
  if (isViewingConnections.value) {
    // 关闭其他模式
    isAddingStairway.value = false
    isAddingDoor.value = false
    isAddingCorridor.value = false
    isAddingEntrance.value = false
    isAddingRfid.value = false
    isAddingEdge.value = false
    alert('查看连接模式：点击节点查看其已建立的连接')
  }
}

// 处理节点点击（查看连接）
function onNodeClickForView(nodeType, nodeId, nodeName, mapId) {
  if (!isViewingConnections.value) return
  
  selectedNodeForView.value = { nodeType, nodeId, nodeName, mapId }
  loadConnectedNodes()
  showViewConnectionsModal.value = true
}

// 加载已连接的节点
async function loadConnectedNodes() {
  if (!selectedNodeForView.value) return
  
  try {
    // 获取该节点的所有邻接边
    const adjacentEdges = await apiClient.get(
      `/graph-edges/adjacent/${selectedNodeForView.value.nodeType}/${selectedNodeForView.value.nodeId}`
    )
    
    console.log('当前节点:', selectedNodeForView.value)
    console.log('邻接边:', adjacentEdges)
    
    if (!Array.isArray(adjacentEdges)) {
      connectedNodes.value = []
      return
    }
    
    // 构建连接节点列表
    const connections = []
    for (const edge of adjacentEdges) {
      console.log('处理边:', edge)
      
      // 确定对方节点（注意类型转换）
      let targetNodeType, targetNodeId
      const currentNodeId = String(selectedNodeForView.value.nodeId)
      const edgeNodeAId = String(edge.nodeAId)
      const edgeNodeBId = String(edge.nodeBId)
      
      if (edge.nodeAType === selectedNodeForView.value.nodeType && edgeNodeAId === currentNodeId) {
        // 当前节点是A，对方是B
        targetNodeType = edge.nodeBType
        targetNodeId = edge.nodeBId
        console.log('当前节点是A，对方是B:', targetNodeType, targetNodeId)
      } else if (edge.nodeBType === selectedNodeForView.value.nodeType && edgeNodeBId === currentNodeId) {
        // 当前节点是B，对方是A
        targetNodeType = edge.nodeAType
        targetNodeId = edge.nodeAId
        console.log('当前节点是B，对方是A:', targetNodeType, targetNodeId)
      } else {
        console.warn('无法确定对方节点:', edge, selectedNodeForView.value)
        continue
      }
      
      // 获取节点信息
      let nodeName = ''
      if (targetNodeType === 1) {
        // doors节点
        const door = doors.value.find(d => String(d.id) === String(targetNodeId))
        console.log('查找door:', targetNodeId, '找到:', door)
        if (door) {
          const typeText = door.roomType === 1 ? '房间' : (door.roomType === 2 ? '楼道' : '出入口')
          nodeName = `${door.roomName} (${typeText})`
        }
      } else if (targetNodeType === 2) {
        // stairways节点
        const stairway = stairways.value.find(s => String(s.stairwayId) === String(targetNodeId))
        console.log('查找stairway:', targetNodeId, '找到:', stairway)
        if (stairway) {
          nodeName = `${stairway.stairwayName} (楼梯)`
        }
      }
      
      console.log('节点名称:', nodeName)
      
      if (nodeName) {
        connections.push({
          edge: edge,
          node: {
            type: targetNodeType,
            id: targetNodeId,
            name: nodeName
          }
        })
      }
    }
    
    connectedNodes.value = connections
    console.log('最终连接节点列表:', connectedNodes.value)
  } catch (error) {
    console.error('加载连接节点失败:', error)
    connectedNodes.value = []
  }
}

// 切换边选择状态
function toggleEdgeSelection(edgeId) {
  const index = selectedEdgesToDelete.value.indexOf(edgeId)
  if (index >= 0) {
    selectedEdgesToDelete.value.splice(index, 1)
  } else {
    selectedEdgesToDelete.value.push(edgeId)
  }
}

// 检查边是否被选中
function isEdgeSelected(edgeId) {
  return selectedEdgesToDelete.value.includes(edgeId)
}

// 批量删除选中的边
async function deleteSelectedEdges() {
  if (selectedEdgesToDelete.value.length === 0) {
    alert('请至少选择一条边')
    return
  }
  
  if (!confirm(`确定要删除选中的 ${selectedEdgesToDelete.value.length} 条边吗？`)) {
    return
  }
  
  try {
    const result = await apiClient.delete('/graph-edges/batch', {
      data: selectedEdgesToDelete.value
    })
    
    alert(`成功删除 ${result.deletedCount} 条边`)
    
    // 清空选中列表
    selectedEdgesToDelete.value = []
    
    // 重新加载边
    if (selectedMap.value) {
      await loadEdges(selectedMap.value.mapId)
    }
    
    // 重新加载连接节点列表
    await loadConnectedNodes()
    
  } catch (error) {
    console.error('批量删除边失败:', error)
    alert('批量删除边失败: ' + error.message)
  }
}

// 关闭查看连接模态框
function closeViewConnectionsModal() {
  showViewConnectionsModal.value = false
  selectedNodeForView.value = null
  connectedNodes.value = []
  selectedEdgesToDelete.value = []
}

// 修改节点详情点击处理，支持边管理模式和查看连接模式
function onStairwayDetailClick(stairway) {
  if (isAddingEdge.value) {
    onNodeClickForEdge(2, stairway.stairwayId, stairway.stairwayName, stairway.mapId)
  } else if (isViewingConnections.value) {
    onNodeClickForView(2, stairway.stairwayId, stairway.stairwayName, stairway.mapId)
  } else {
    selectedStairway.value = stairway
    showStairwayDetail.value = true
  }
}

function onDoorDetailClick(door) {
  if (isAddingEdge.value) {
    const typeText = door.roomType === 1 ? '房间' : (door.roomType === 2 ? '楼道' : '出入口')
    onNodeClickForEdge(1, door.id, `${door.roomName}(${typeText})`, door.mapId)
  } else if (isViewingConnections.value) {
    const typeText = door.roomType === 1 ? '房间' : (door.roomType === 2 ? '楼道' : '出入口')
    onNodeClickForView(1, door.id, `${door.roomName}(${typeText})`, door.mapId)
  } else {
    selectedDoor.value = door
    showDoorDetail.value = true
  }
}

function onRfidDetailClick(device) {
  // RFID设备不参与边管理
  selectedRfid.value = device
  showRfidDetail.value = true
}

// ========== 路径规划相关函数 ==========

// 切换路径规划面板
function togglePathPlanning() {
  closeRegionEditor()
  showPathPlanning.value = !showPathPlanning.value
  if (!showPathPlanning.value) {
    // 关闭时清理状态
    isAddingStairway.value = false
    isAddingDoor.value = false
    isAddingCorridor.value = false
    isAddingEntrance.value = false
    isAddingRfid.value = false
    isAddingEdge.value = false
    isViewingConnections.value = false
    isAddingPathPoint.value = false
  }
}

// 关闭路径规划面板
function closePathPlanning() {
  showPathPlanning.value = false
  isAddingPathPoint.value = false
}

// 处理添加点模式变化
function onAddingPointChange(isAdding) {
  console.log('[App] onAddingPointChange 被调用，参数:', isAdding)
  if (isAdding) {
    closeRegionEditor()
  }
  isAddingPathPoint.value = isAdding
  console.log('[App] isAddingPathPoint 设置为:', isAddingPathPoint.value)
  if (isAdding) {
    // 关闭其他模式
    isAddingStairway.value = false
    isAddingDoor.value = false
    isAddingCorridor.value = false
    isAddingEntrance.value = false
    isAddingRfid.value = false
    isAddingEdge.value = false
    isViewingConnections.value = false
  }
}

// 处理路径规划点击
function onPathPointClick(coords) {
  console.log('[App] onPathPointClick 被调用')
  console.log('[App] coords:', coords)
  console.log('[App] pathPlanningPanelRef.value:', pathPlanningPanelRef.value)
  console.log('[App] isAddingPathPoint.value:', isAddingPathPoint.value)
  
  if (pathPlanningPanelRef.value && isAddingPathPoint.value) {
    console.log('[App] 调用 addPoint')
    pathPlanningPanelRef.value.addPoint({
      x: coords.x,
      y: coords.y,
      map_id: selectedMap.value.mapId
    })
  } else {
    console.log('[App] 未调用 addPoint，条件不满足')
  }
}

// 处理路径规划结果
function onPathResult(result) {
  console.log('路径规划结果:', result)
  
  // 保存完整的路径数据
  pathData.value = result
  
  // 更新当前楼层的路径段
  if (selectedMap.value) {
    updateCurrentPathSegment(selectedMap.value.mapId)
  }
  
  // 显示成功消息
  const floorCount = result.floors.length
  const message = floorCount > 1 
    ? `路径规划成功！总距离：${result.total_distance.toFixed(2)}米，经过${floorCount}个楼层`
    : `路径规划成功！总距离：${result.total_distance.toFixed(2)}米`
  
  alert(message)
}

</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:global(html),
:global(body),
:global(#app) {
  min-height: 100%;
}

:global(body) {
  overflow-x: hidden;
  overflow-y: auto;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 24px;
  color: #1a1a1a;
  font-weight: 600;
}

.content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
}

.floor-list-section {
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.floor-list-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.floor-list-header h2 {
  font-size: 16px;
  color: #1a1a1a;
  font-weight: 600;
}

.floor-count {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.floor-list {
  list-style: none;
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.floor-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  gap: 12px;
}

.floor-item:hover {
  background: #f0f7ff;
}

.floor-item.active {
  background: #1890ff;
  color: white;
}

.floor-item.active .floor-size {
  color: rgba(255, 255, 255, 0.8);
}

.floor-index {
  width: 24px;
  height: 24px;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  flex-shrink: 0;
}

.floor-item.active .floor-index {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.floor-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.floor-size {
  font-size: 12px;
  color: #999;
}

.preview-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-index {
  width: 28px;
  height: 28px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.preview-title h2 {
  font-size: 18px;
  color: #1a1a1a;
  font-weight: 600;
}

.preview-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-nav {
  width: 32px;
  height: 32px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-nav:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-info {
  font-size: 13px;
  color: #666;
  min-width: 60px;
  text-align: center;
}

.preview-content {
  flex: 1;
  margin: 16px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.region-editor-panel {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 360px;
  max-width: calc(100% - 32px);
  max-height: calc(100% - 32px);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.16);
  z-index: 20;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
}

.region-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.region-editor-header h3 {
  font-size: 16px;
  color: #0f172a;
  font-weight: 600;
}

.region-editor-header p {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.region-editor-body {
  padding: 16px 18px 0;
  overflow-y: auto;
}

.region-editor-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.color-input {
  padding: 4px;
  min-height: 40px;
}

.region-point-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0 12px;
  flex-wrap: wrap;
}

.region-point-count {
  margin-right: auto;
  font-size: 13px;
  font-weight: 600;
  color: #0f766e;
}

.btn-small {
  padding: 6px 10px;
  font-size: 12px;
}

.region-point-list,
.region-detail-points {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.region-point-empty {
  padding: 14px;
  border-radius: 10px;
  background: #f8fafc;
  color: #64748b;
  font-size: 13px;
  text-align: center;
}

.region-point-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 13px;
  color: #0f172a;
}

.point-remove-btn {
  border: none;
  background: transparent;
  color: #dc2626;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.map-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

.preview-info {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-wrap: wrap;
  gap: 16px 32px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #999;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.no-selection-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-selection p {
  font-size: 14px;
}

@media (max-width: 900px) {
  .content {
    flex-direction: column;
    height: auto;
  }

  .floor-list-section {
    width: 100%;
    max-height: 300px;
  }

  .preview-section {
    min-height: 400px;
  }

  .region-editor-panel {
    width: calc(100% - 24px);
    top: 12px;
    left: 12px;
    max-height: calc(100% - 24px);
  }

  .region-editor-grid {
    grid-template-columns: 1fr;
  }
}

/* 添加按钮 */
.btn-action {
  width: 32px;
  height: 32px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  background: #52c41a;
  color: white;
  border-color: #52c41a;
}

.btn-action.btn-stairway:hover {
  background: #52c41a;
  border-color: #52c41a;
}

.btn-action.btn-door:hover {
  background: #3b82f6;
  border-color: #3b82f6;
}

.btn-action.btn-corridor:hover {
  background: #a855f7;
  border-color: #a855f7;
}

.btn-action.btn-entrance:hover {
  background: #ef4444;
  border-color: #ef4444;
}

.btn-action.btn-rfid:hover {
  background: #f59e0b;
  border-color: #f59e0b;
}

.btn-action.btn-region:hover {
  background: #0f766e;
  border-color: #0f766e;
}

.btn-action.btn-region.active {
  background: #0f766e;
  color: white;
  border-color: #0f766e;
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18);
}

.btn-action.btn-edge {
  position: relative;
}

.btn-action.btn-edge:hover {
  background: #8b5cf6;
  border-color: #8b5cf6;
}

.btn-action.btn-edge.active {
  background: #8b5cf6;
  color: white;
  border-color: #8b5cf6;
}

.btn-action.btn-view-connections {
  position: relative;
}

.btn-action.btn-view-connections:hover {
  background: #06b6d4;
  border-color: #06b6d4;
}

.btn-action.btn-view-connections.active {
  background: #06b6d4;
  color: white;
  border-color: #06b6d4;
}

.btn-action.btn-path-planning {
  position: relative;
}

.btn-action.btn-path-planning:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.btn-action.btn-path-planning.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow-y: auto;
  padding: 24px 16px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  max-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
}

.btn-close-modal:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-item input,
.form-item select,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-item input:focus,
.form-item select:focus,
.form-item textarea:focus {
  border-color: #1890ff;
}

.form-item input.readonly {
  background: #f5f5f5;
  color: #666;
}

.form-item textarea {
  min-height: 80px;
  resize: vertical;
}

.coord-display {
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  font-family: monospace;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-confirm {
  padding: 8px 16px;
  border: none;
  background: #1890ff;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-confirm:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

/* 楼梯详情模态框 */
.stairway-detail-modal {
  max-width: 500px;
}

.region-detail-modal {
  max-width: 560px;
}

.stairway-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.region-style-preview {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.region-color-chip {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid rgba(15, 23, 42, 0.18);
  flex-shrink: 0;
}

.region-detail-points h4 {
  font-size: 14px;
  color: #334155;
  margin: 8px 0 10px;
}

.region-door-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

.region-door-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.region-door-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.region-door-meta {
  font-size: 12px;
  color: #64748b;
}

.region-door-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.region-door-picker-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.region-door-hint {
  font-size: 12px;
  color: #64748b;
}

.region-door-select {
  min-height: 120px;
  padding: 10px;
  border: 1px solid #d9e2ec;
  border-radius: 10px;
  font-size: 13px;
  background: #fff;
}

.region-door-actions {
  display: flex;
  justify-content: flex-end;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-row .info-value {
  font-size: 14px;
  color: #333;
}

.stairway-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-navigate {
  padding: 8px 16px;
  border: 1px solid #1890ff;
  background: white;
  color: #1890ff;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-navigate:hover {
  background: #1890ff;
  color: white;
}

.btn-connection {
  padding: 8px 16px;
  border: 1px solid #722ed1;
  background: white;
  color: #722ed1;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-connection:hover {
  background: #722ed1;
  color: white;
}

.btn-edit {
  padding: 8px 16px;
  border: 1px solid #52c41a;
  background: white;
  color: #52c41a;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #52c41a;
  color: white;
}

.btn-delete {
  padding: 8px 16px;
  border: 1px solid #ff4d4f;
  background: white;
  color: #ff4d4f;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #ff4d4f;
  color: white;
}

/* 边管理模态框 */
.edge-modal {
  max-width: 500px;
}

.edge-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.selected-node {
  padding: 12px;
  background: #f0f7ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.node-name {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.arrow {
  text-align: center;
  font-size: 24px;
  color: #8b5cf6;
}

.target-nodes {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.node-item {
  padding: 12px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.node-item:hover {
  background: #f0f7ff;
  border-color: #8b5cf6;
}

.node-item.connected {
  background: #d1fae5;
  border-color: #10b981;
}

.node-item.connected:hover {
  background: #a7f3d0;
  border-color: #059669;
  cursor: not-allowed;
}

.node-item.selected {
  background: #dbeafe;
  border-color: #3b82f6;
}

.node-item.selected:hover {
  background: #bfdbfe;
  border-color: #2563eb;
}

.node-icon {
  font-size: 18px;
}

.node-name {
  flex: 1;
}

.connected-badge {
  font-size: 12px;
  color: #059669;
  background: #d1fae5;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.selected-badge {
  font-size: 12px;
  color: #2563eb;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.selected-count {
  padding: 12px;
  background: #f0f7ff;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  color: #1890ff;
  font-weight: 600;
  margin-top: 12px;
}

/* 查看连接模态框 */
.view-connections-modal {
  max-width: 500px;
}

.view-connections-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.connected-nodes-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-connections {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.edge-weight {
  font-size: 12px;
  color: #666;
  margin-left: auto;
  padding-right: 8px;
}
</style>
