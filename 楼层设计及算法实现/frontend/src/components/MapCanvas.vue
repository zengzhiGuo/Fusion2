<template>
  <div 
    class="map-wrap" 
    ref="wrapRef" 
    @mousemove="onMouseMove" 
    @mouseleave="onLeave"
    @wheel="onWheel"
    @mousedown="onMouseDown"
    @mouseup="onMouseUp"
    @contextmenu.prevent
  >
    <div class="map-controls-float">
      <button class="control-btn" @click="centerMap" title="居中地图">
        <span class="icon">⊕</span>
      </button>
      <button class="control-btn" @click="resetZoom" title="重置缩放">
        <span class="icon">↺</span>
      </button>
      <button class="control-btn" @click="zoomIn" title="放大">
        <span class="icon">+</span>
      </button>
      <button class="control-btn" @click="zoomOut" title="缩小">
        <span class="icon">−</span>
      </button>
    </div>

    <div class="map-container" :style="containerStyle">
      <div class="content" :style="contentStyle">
        <img 
          ref="imgRef" 
          :src="imgUrl" 
          @load="onImgLoad" 
          draggable="false"
          class="map-image"
        />
        <svg class="overlay" preserveAspectRatio="xMidYMid meet">
          <g :transform="overlayTransform">
            <g v-if="showGrid" class="grid-layer">
              <line
                v-for="x in gridVerticalLines"
                :key="`grid-x-${x}`"
                :x1="toPxX(x)"
                :y1="toPxY(0)"
                :x2="toPxX(x)"
                :y2="toPxY(shipWidth)"
                class="grid-line"
              />
              <line
                v-for="y in gridHorizontalLines"
                :key="`grid-y-${y}`"
                :x1="toPxX(0)"
                :y1="toPxY(y)"
                :x2="toPxX(shipLength)"
                :y2="toPxY(y)"
                class="grid-line"
              />
            </g>
            <!-- 围栏区域层（最底层） -->
            <g v-if="regions && regions.length > 0" class="regions-layer">
              <g v-for="region in regions" :key="region.regionId" class="region-group" @click.stop="onRegionClick(region)">
                <polygon 
                  v-if="getRegionPoints(region).length >= 3"
                  :points="getRegionPolygonPoints(region)"
                  :fill="region.color || '#3B82F6'"
                  :fill-opacity="region.fillOpacity || 0.3"
                  :stroke="region.color || '#3B82F6'"
                  :stroke-width="region.strokeWidth || 2"
                  class="region-polygon"
                />
                <!-- 围栏标签 -->
                <text 
                  v-if="getRegionCenter(region)"
                  :x="getRegionCenter(region).x" 
                  :y="getRegionCenter(region).y"
                  class="region-label"
                  text-anchor="middle"
                  dominant-baseline="central"
                >
                  {{ region.regionName }}
                </text>
              </g>
            </g>

            <g v-if="regionDraftPoints.length > 0" class="region-draft-layer">
              <polygon
                v-if="regionDraftPoints.length >= 3"
                :points="regionDraftPolygonPoints"
                :fill="regionDraftStyle?.color || '#3B82F6'"
                :fill-opacity="regionDraftStyle?.fillOpacity ?? 0.2"
                :stroke="regionDraftStyle?.color || '#3B82F6'"
                :stroke-width="Math.max(Number(regionDraftStyle?.strokeWidth || 2), 1.5)"
                class="region-draft-polygon"
              />
              <polyline
                v-if="regionDraftPoints.length >= 2"
                :points="regionDraftPolygonPoints"
                :stroke="regionDraftStyle?.color || '#3B82F6'"
                :stroke-width="Math.max(Number(regionDraftStyle?.strokeWidth || 2), 1.5)"
                class="region-draft-line"
              />
              <g v-for="(point, index) in regionDraftPoints" :key="`region-draft-${index}`" class="region-draft-point-group">
                <circle
                  :cx="toPxX(point.xCoordinate)"
                  :cy="toPxY(point.yCoordinate)"
                  :r="markerR * 0.75"
                  class="region-draft-point"
                />
                <text
                  :x="toPxX(point.xCoordinate)"
                  :y="toPxY(point.yCoordinate) - 14"
                  text-anchor="middle"
                  class="region-draft-index"
                >
                  {{ index + 1 }}
                </text>
              </g>
            </g>
            
            <!-- 路径折线 -->
            <g v-if="pathSegment.length > 0" class="path-layer">
              <polyline 
                :points="pathPolylinePoints"
                class="path-line"
              />
              <!-- 路径节点标记 -->
              <g v-for="(node, index) in pathSegment" :key="`path-node-${index}`" class="path-node-marker">
                <circle 
                  :cx="toPxX(node.x)" 
                  :cy="toPxY(node.y)" 
                  :r="index === 0 ? 8 : index === pathSegment.length - 1 ? 8 : 5"
                  :class="index === 0 ? 'path-start' : index === pathSegment.length - 1 ? 'path-end' : 'path-waypoint'"
                />
                <text 
                  v-if="index === 0 || index === pathSegment.length - 1"
                  :x="toPxX(node.x)" 
                  :y="toPxY(node.y) - 15" 
                  text-anchor="middle" 
                  class="path-label">
                  {{ index === 0 ? '起点' : '终点' }}
                </text>
              </g>
            </g>
            
            <g v-for="p in points" :key="p.tagCode || (p.x+'-'+p.y)" class="pt">
              <circle :cx="toPxX(p.x)" :cy="toPxY(p.y)" :r="markerR" />
              <text v-if="p.label" :x="toPxX(p.x)" :y="toPxY(p.y) - 12" text-anchor="middle" style="font-size: 10px">{{ p.label }}</text>
            </g>
            <g v-for="s in stairways" :key="'stairway-' + s.stairwayId" class="stairway-marker" @click="onStairwayClick(s)">
              <circle :cx="toPxX(s.x)" :cy="toPxY(s.y)" :r="markerR" class="stairway-circle" />
              <text v-if="s.stairwayName" :x="toPxX(s.x)" :y="toPxY(s.y) - 12" text-anchor="middle" class="stairway-text">{{ s.stairwayName }}</text>
            </g>
            <g v-for="d in doors" :key="'door-' + d.id" class="door-marker" @click="onDoorClick(d)">
              <rect :x="toPxX(d.x) - markerR" :y="toPxY(d.y) - markerR" :width="markerR * 2" :height="markerR * 2" :class="d.roomType === 2 ? 'corridor-rect' : (d.roomType === 3 ? 'entrance-rect' : 'door-rect')" />
              <text v-if="d.roomName" :x="toPxX(d.x)" :y="toPxY(d.y) - 12" text-anchor="middle" class="door-text">{{ d.roomName }}</text>
            </g>
            <g v-for="r in rfidDevices" :key="'rfid-' + r.id" class="rfid-marker" @click="onRfidClick(r)">
              <circle :cx="toPxX(r.x)" :cy="toPxY(r.y)" :r="markerR * 0.8" class="rfid-circle" />
              <text v-if="r.deviceName" :x="toPxX(r.x)" :y="toPxY(r.y) - 12" text-anchor="middle" class="rfid-text">{{ r.deviceName }}</text>
            </g>
          </g>
        </svg>
        <div 
          v-if="enableCoordinates && hoverWorld" 
          class="coord-tip"
          :style="{ left: tipLeft + 'px', top: tipTop + 'px' }"
        >
          x: {{ hoverWorld.x.toFixed(2) }} m， y: {{ hoverWorld.y.toFixed(2) }} m
        </div>
      </div>
    </div>

    <div v-if="showZoomHint" class="zoom-hint">
      使用鼠标滚轮缩放，拖拽移动地图
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onBeforeUnmount, toRefs } from 'vue'

export default {
  name: 'MapCanvas',
  props: {
    imgUrl: { type: String, required: true },
    shipLength: { type: Number, required: true },
    shipWidth: { type: Number, required: true },
    imageWidth: { type: Number, default: 0 },
    imageHeight: { type: Number, default: 0 },
    showGrid: { type: Boolean, default: false },
    gridSize: { type: Number, default: 1 },
    points: { type: Array, default: () => [] },
    scale: { type: Number, default: 1 },
    mapId: { type: String, default: '' },
    stairways: { type: Array, default: () => [] },
    doors: { type: Array, default: () => [] },
    rfidDevices: { type: Array, default: () => [] },
    isAddingStairway: { type: Boolean, default: false },
    isAddingDoor: { type: Boolean, default: false },
    isAddingCorridor: { type: Boolean, default: false },
    isAddingEntrance: { type: Boolean, default: false },
    isAddingRfid: { type: Boolean, default: false },
    isAddingRegion: { type: Boolean, default: false },
    isAddingPathPoint: { type: Boolean, default: false },
    pathSegment: { type: Array, default: () => [] },  // 当前楼层的路径段
    regions: { type: Array, default: () => [] },  // 围栏列表
    regionCoordinates: { type: Object, default: () => ({}) },
    regionDraftPoints: { type: Array, default: () => [] },
    regionDraftStyle: { type: Object, default: () => ({}) }
  },
  emits: ['point-click', 'center-map', 'stairway-click', 'stairway-detail-click', 'door-click', 'door-detail-click', 'corridor-click', 'entrance-click', 'rfid-click', 'rfid-detail-click', 'path-point-click', 'region-point-click', 'region-detail-click'],
  setup(props, { emit }) {
    const wrapRef = ref(null)
    const imgRef = ref(null)
    const showZoomHint = ref(false)
    const isDragging = ref(false)
    const lastMousePos = ref({ x: 0, y: 0 })
    const hoverWorld = ref(null)
    const tipLeft = ref(0)
    const tipTop = ref(0)

    // 解构props以便在模板中使用
    const { regions, regionCoordinates, pathSegment, regionDraftPoints, regionDraftStyle, showGrid, shipWidth, shipLength } = toRefs(props)

    const mapTransform = reactive({
      scale: 1,
      translateX: 0,
      translateY: 0
    })

    const imgNat = reactive({ w: props.imageWidth || 0, h: props.imageHeight || 0 })
    const view = reactive({ cw: 0, ch: 0, scale: 1, w: 0, h: 0, ox: 0, oy: 0 })

    let ro = null
    let hintTimer = null

    const markerR = 6
    const enableCoordinates = true

    const overlayTransform = computed(() => `translate(${view.ox},${view.oy}) scale(${view.scale})`)

    // 计算路径折线的点字符串
    const pathPolylinePoints = computed(() => {
      if (!props.pathSegment || props.pathSegment.length === 0) return ''
      return props.pathSegment
        .map(node => `${toPxX(node.x)},${toPxY(node.y)}`)
        .join(' ')
    })

    const gridVerticalLines = computed(() => {
      const size = Number(props.gridSize || 1)
      const shipLength = Number(props.shipLength || 0)
      if (size <= 0 || shipLength <= 0) return []

      const lines = []
      for (let x = 0; x <= shipLength; x += size) {
        lines.push(Number(x.toFixed(4)))
      }
      return lines
    })

    const gridHorizontalLines = computed(() => {
      const size = Number(props.gridSize || 1)
      const shipWidth = Number(props.shipWidth || 0)
      if (size <= 0 || shipWidth <= 0) return []

      const lines = []
      for (let y = 0; y <= shipWidth; y += size) {
        lines.push(Number(y.toFixed(4)))
      }
      return lines
    })

    const regionDraftPolygonPoints = computed(() => {
      if (!props.regionDraftPoints || props.regionDraftPoints.length === 0) return ''
      return props.regionDraftPoints
        .map(point => `${toPxX(point.xCoordinate)},${toPxY(point.yCoordinate)}`)
        .join(' ')
    })

    const containerStyle = computed(() => ({
      transform: `translate(${mapTransform.translateX}px, ${mapTransform.translateY}px) scale(${mapTransform.scale})`,
      transformOrigin: 'center center',
      transition: isDragging.value ? 'none' : 'transform 0.2s ease-out',
      cursor: props.isAddingStairway || props.isAddingDoor || props.isAddingCorridor || props.isAddingEntrance || props.isAddingRfid || props.isAddingRegion || props.isAddingPathPoint ? 'crosshair' : (isDragging.value ? 'grabbing' : 'grab')
    }))

    const contentStyle = computed(() => ({
      transform: `translate(-50%, -50%) scale(${props.scale || 1})`,
      transformOrigin: 'center center'
    }))

    function onImgLoad() {
      if (!imgRef.value) return
      imgNat.w = imgRef.value.naturalWidth
      imgNat.h = imgRef.value.naturalHeight
      calcView()
    }

    function calcView() {
      const el = wrapRef.value
      if (!el || !imgNat.w || !imgNat.h) return
      const rect = el.getBoundingClientRect()
      view.cw = rect.width
      view.ch = rect.height
      const s = Math.min(view.cw / imgNat.w, view.ch / imgNat.h)
      view.scale = s
      view.w = imgNat.w * s
      view.h = imgNat.h * s
      view.ox = (view.cw - view.w) / 2
      view.oy = (view.ch - view.h) / 2
    }

    function toPxX(x) {
      return (Number(x) / Number(props.shipLength || 1)) * imgNat.w
    }

    function toPxY(y) {
      return (Number(y) / Number(props.shipWidth || 1)) * imgNat.h
    }

    function updateCoordinateHover(e) {
      if (!wrapRef.value) return
      const rect = wrapRef.value.getBoundingClientRect()
      const cx = e.clientX - rect.left
      const cy = e.clientY - rect.top

      const centerX = view.cw / 2
      const centerY = view.ch / 2
      const s = mapTransform.scale || 1
      const tx = mapTransform.translateX
      const ty = mapTransform.translateY

      const invX = centerX + (cx - tx - centerX) / s
      const invY = centerY + (cy - ty - centerY) / s

      const xIn = invX - view.ox
      const yIn = invY - view.oy

      if (xIn < 0 || yIn < 0 || xIn > view.w || yIn > view.h) {
        hoverWorld.value = null
        return
      }

      const imgX = xIn / view.scale
      const imgY = yIn / view.scale
      hoverWorld.value = {
        x: (imgX / imgNat.w) * props.shipLength,
        y: (imgY / imgNat.h) * props.shipWidth
      }

      tipLeft.value = cx + 12
      tipTop.value = cy + 8
    }

    function getWorldCoordinates(e) {
      if (!wrapRef.value) return null
      const rect = wrapRef.value.getBoundingClientRect()
      const cx = e.clientX - rect.left
      const cy = e.clientY - rect.top

      const centerX = view.cw / 2
      const centerY = view.ch / 2
      const s = mapTransform.scale || 1
      const tx = mapTransform.translateX
      const ty = mapTransform.translateY

      const invX = centerX + (cx - tx - centerX) / s
      const invY = centerY + (cy - ty - centerY) / s

      const xIn = invX - view.ox
      const yIn = invY - view.oy

      if (xIn < 0 || yIn < 0 || xIn > view.w || yIn > view.h) {
        return null
      }

      const imgX = xIn / view.scale
      const imgY = yIn / view.scale
      return {
        x: (imgX / imgNat.w) * props.shipLength,
        y: (imgY / imgNat.h) * props.shipWidth
      }
    }

    function onStairwayClick(stairway) {
      emit('stairway-detail-click', stairway)
    }

    function onDoorClick(door) {
      emit('door-detail-click', door)
    }

    function onRfidClick(device) {
      emit('rfid-detail-click', device)
    }

    function onRegionClick(region) {
      emit('region-detail-click', region)
    }

    function onLeave() {
      hoverWorld.value = null
      isDragging.value = false
    }

    function onWheel(e) {
      e.preventDefault()
      const zoomSpeed = 0.1
      const zoomDirection = e.deltaY > 0 ? -1 : 1
      const newScale = Math.max(0.5, Math.min(5, mapTransform.scale + zoomDirection * zoomSpeed))

      const rect = wrapRef.value.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      const scaleChange = newScale / mapTransform.scale
      mapTransform.translateX = mouseX - (mouseX - mapTransform.translateX) * scaleChange
      mapTransform.translateY = mouseY - (mouseY - mapTransform.translateY) * scaleChange
      mapTransform.scale = newScale
    }

    function onMouseDown(e) {
      if (e.button !== 0) return
      
      console.log('[MapCanvas] onMouseDown 被调用')
      console.log('[MapCanvas] isAddingPathPoint:', props.isAddingPathPoint)
      
      // 如果正在添加楼梯模式，点击地图获取坐标
      if (props.isAddingStairway) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('stairway-click', coords)
        }
        return
      }
      
      // 如果正在添加门模式，点击地图获取坐标
      if (props.isAddingDoor) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('door-click', coords)
        }
        return
      }
      
      // 如果正在添加楼道模式，点击地图获取坐标
      if (props.isAddingCorridor) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('corridor-click', coords)
        }
        return
      }
      
      // 如果正在添加出入口模式，点击地图获取坐标
      if (props.isAddingEntrance) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('entrance-click', coords)
        }
        return
      }
      
      // 如果正在添加RFID设备模式，点击地图获取坐标
      if (props.isAddingRfid) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('rfid-click', coords)
        }
        return
      }
      
      // 如果正在添加路径规划点模式，点击地图获取坐标
      if (props.isAddingRegion) {
        const coords = getWorldCoordinates(e)
        if (coords) {
          emit('region-point-click', coords)
        }
        return
      }

      if (props.isAddingPathPoint) {
        console.log('[MapCanvas] 进入路径规划点击模式')
        const coords = getWorldCoordinates(e)
        console.log('[MapCanvas] 获取的坐标:', coords)
        if (coords) {
          console.log('[MapCanvas] 触发 path-point-click 事件')
          emit('path-point-click', coords)
        } else {
          console.log('[MapCanvas] 坐标无效，未触发事件')
        }
        return
      }
      
      isDragging.value = true
      lastMousePos.value = { x: e.clientX, y: e.clientY }
      document.addEventListener('mousemove', onDocumentMouseMove)
      document.addEventListener('mouseup', onDocumentMouseUp)
    }

    function onMouseMove(e) {
      if (isDragging.value) {
        const deltaX = e.clientX - lastMousePos.value.x
        const deltaY = e.clientY - lastMousePos.value.y
        mapTransform.translateX += deltaX
        mapTransform.translateY += deltaY
        lastMousePos.value = { x: e.clientX, y: e.clientY }
      }
      updateCoordinateHover(e)
    }

    function onMouseUp() {
      isDragging.value = false
    }

    function onDocumentMouseMove(e) {
      if (!isDragging.value) return
      const deltaX = e.clientX - lastMousePos.value.x
      const deltaY = e.clientY - lastMousePos.value.y
      mapTransform.translateX += deltaX
      mapTransform.translateY += deltaY
      lastMousePos.value = { x: e.clientX, y: e.clientY }
    }

    function onDocumentMouseUp() {
      isDragging.value = false
      document.removeEventListener('mousemove', onDocumentMouseMove)
      document.removeEventListener('mouseup', onDocumentMouseUp)
    }

    function centerMap() {
      mapTransform.translateX = 0
      mapTransform.translateY = 0
      mapTransform.scale = 1
      emit('center-map')
    }

    function resetZoom() {
      mapTransform.scale = 1
    }

    function zoomIn() {
      mapTransform.scale = Math.min(5, mapTransform.scale + 0.2)
    }

    function zoomOut() {
      mapTransform.scale = Math.max(0.5, mapTransform.scale - 0.2)
    }

    // 围栏相关函数
    function getRegionPoints(regionOrId) {
      const region = typeof regionOrId === 'object' ? regionOrId : null
      const regionId = region?.regionId || regionOrId

      if (region && Array.isArray(region.coordinates) && region.coordinates.length > 0) {
        return region.coordinates
      }

      return regionCoordinates.value[regionId] || []
    }

    function getRegionPolygonPoints(regionOrId) {
      const coords = getRegionPoints(regionOrId)
      if (coords.length < 3) return ''
      return coords
        .map(c => `${toPxX(c.xCoordinate)},${toPxY(c.yCoordinate)}`)
        .join(' ')
    }

    function getRegionCenter(regionOrId) {
      const coords = getRegionPoints(regionOrId)
      if (coords.length < 3) return null
      
      // 计算多边形中心点（质心）
      let sumX = 0
      let sumY = 0
      coords.forEach(c => {
        sumX += Number(c.xCoordinate)
        sumY += Number(c.yCoordinate)
      })
      
      return {
        x: toPxX(sumX / coords.length),
        y: toPxY(sumY / coords.length)
      }
    }

    onMounted(() => {
      if (wrapRef.value) {
        ro = new ResizeObserver(calcView)
        ro.observe(wrapRef.value)
      }
      showZoomHint.value = true
      hintTimer = setTimeout(() => {
        showZoomHint.value = false
      }, 3000)
    })

    onBeforeUnmount(() => {
      if (ro) ro.disconnect()
      if (hintTimer) clearTimeout(hintTimer)
    })

    return {
      wrapRef,
      imgRef,
      showZoomHint,
      hoverWorld,
      tipLeft,
      tipTop,
      overlayTransform,
      pathPolylinePoints,
      gridVerticalLines,
      gridHorizontalLines,
      regionDraftPolygonPoints,
      containerStyle,
      contentStyle,
      markerR,
      enableCoordinates,
      showGrid,
      shipWidth,
      shipLength,
      regions,
      regionCoordinates,
      regionDraftPoints,
      regionDraftStyle,
      pathSegment,
      onImgLoad,
      onMouseMove,
      onLeave,
      onWheel,
      onMouseDown,
      onMouseUp,
      centerMap,
      resetZoom,
      zoomIn,
      zoomOut,
      toPxX,
      toPxY,
      onStairwayClick,
      onDoorClick,
      onRfidClick,
      onRegionClick,
      getRegionPoints,
      getRegionPolygonPoints,
      getRegionCenter
    }
  }
}
</script>

<style scoped>
.map-wrap { 
  position: relative; 
  width: 100%; 
  height: 100%; 
  overflow: hidden;
  background: #f5f5f5;
  border-radius: 8px;
}

.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.content { 
  position: absolute; 
  top: 50%; 
  left: 50%; 
  width: 100%; 
  height: 100%;
}

.map-image { 
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  user-select: none;
  -webkit-user-drag: none;
}

.overlay { 
  position: absolute; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%;
  pointer-events: none;
}

.grid-layer {
  pointer-events: none;
}

.grid-line {
  stroke: rgba(15, 23, 42, 0.18);
  stroke-width: 1;
  shape-rendering: crispEdges;
}

circle { 
  fill: #ef4444;
  opacity: 0.9;
}

text { 
  fill: #1f2937;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 2px;
}

.pt { cursor: pointer; }

.pt:hover circle {
  opacity: 1;
  stroke: #3b82f6;
  stroke-width: 2px;
}

.stairway-marker {
  cursor: pointer;
  pointer-events: all;
}

.stairway-circle {
  fill: #22c55e;
  opacity: 0.9;
}

.stairway-marker:hover .stairway-circle {
  opacity: 1;
  stroke: #16a34a;
  stroke-width: 2px;
}

.stairway-text {
  fill: #1f2937;
  font-size: 10px;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 2px;
}

.door-marker {
  cursor: pointer;
  pointer-events: all;
}

.door-rect {
  fill: #3b82f6;
  opacity: 0.9;
}

.corridor-rect {
  fill: #a855f7;
  opacity: 0.9;
}

.entrance-rect {
  fill: #ef4444;
  opacity: 0.9;
}

.door-marker:hover .door-rect {
  opacity: 1;
  stroke: #1d4ed8;
  stroke-width: 2px;
}

.door-marker:hover .corridor-rect {
  opacity: 1;
  stroke: #7e22ce;
  stroke-width: 2px;
}

.door-marker:hover .entrance-rect {
  opacity: 1;
  stroke: #dc2626;
  stroke-width: 2px;
}

.door-text {
  fill: #1f2937;
  font-size: 10px;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 2px;
}

.rfid-marker {
  cursor: pointer;
  pointer-events: all;
}

.rfid-circle {
  fill: #f59e0b;
  opacity: 0.9;
}

.rfid-marker:hover .rfid-circle {
  opacity: 1;
  stroke: #d97706;
  stroke-width: 2px;
}

.rfid-text {
  fill: #1f2937;
  font-size: 10px;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 2px;
}

.coord-tip { 
  position: absolute;
  pointer-events: none; 
  padding: 4px 8px; 
  background: rgba(0, 0, 0, 0.8); 
  color: #fff; 
  font-size: 12px; 
  border-radius: 4px;
  white-space: nowrap;
}

.map-controls-float {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 18px;
}

.control-btn:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.icon { font-size: 18px; line-height: 1; }

.zoom-hint {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  animation: fadeInOut 3s ease-in-out;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  10%, 90% { opacity: 1; }
}

/* 路径可视化样式 */
.path-layer {
  pointer-events: none;
}

.path-line {
  fill: none;
  stroke: #2196F3;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.8;
}

.path-node-marker {
  pointer-events: none;
}

.path-start {
  fill: #4CAF50;
  stroke: #ffffff;
  stroke-width: 2;
  opacity: 1;
}

.path-end {
  fill: #f44336;
  stroke: #ffffff;
  stroke-width: 2;
  opacity: 1;
}

.path-waypoint {
  fill: #2196F3;
  stroke: #ffffff;
  stroke-width: 1.5;
  opacity: 0.9;
}

.path-label {
  fill: #1f2937;
  font-size: 11px;
  font-weight: 600;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 3px;
}

/* 围栏样式 */
.regions-layer {
  pointer-events: all;
}

.region-group {
  cursor: pointer;
  transition: opacity 0.2s;
}

.region-group:hover .region-polygon {
  opacity: 0.8;
  filter: brightness(1.1);
}

.region-polygon {
  transition: all 0.2s;
}

.region-label {
  fill: #1f2937;
  font-size: 12px;
  font-weight: 600;
  user-select: none;
  paint-order: stroke;
  stroke: #ffffff;
  stroke-width: 3px;
  pointer-events: none;
}

.region-draft-layer {
  pointer-events: none;
}

.region-draft-polygon {
  stroke-dasharray: 8 4;
}

.region-draft-line {
  fill: none;
  stroke-dasharray: 8 4;
}

.region-draft-point {
  fill: #ffffff;
  stroke: #2563eb;
  stroke-width: 2px;
}

.region-draft-index {
  fill: #1d4ed8;
  font-size: 11px;
  font-weight: 700;
  stroke: #ffffff;
  stroke-width: 3px;
}
</style>
