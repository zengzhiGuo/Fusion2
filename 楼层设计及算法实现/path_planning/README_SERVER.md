# 路径规划服务器使用说明

## 概述

路径规划服务器是一个常驻进程，提供HTTP API接口，支持实时路径规划。

### 特点

- ✅ **高性能**：数据加载到内存，毫秒级响应
- ✅ **实时调用**：支持高频路径规划请求
- ✅ **热加载**：支持数据更新后无需重启
- ✅ **RESTful API**：标准HTTP接口，易于集成
- ✅ **跨域支持**：支持前端跨域调用

## 安装依赖

```bash
pip install flask flask-cors
```

## 启动服务器

### 方法1：直接启动

```bash
cd path_planning
python server.py
```

### 方法2：使用完整路径

```bash
C:/Users/19534/.conda/envs/myenv/python.exe path_planning/server.py
```

启动成功后会看到：

```
================================================================================
路径规划服务器启动成功！
================================================================================

启动HTTP服务器...
监听地址: http://0.0.0.0:5000
API文档:
  - GET  /health                    健康检查
  - POST /api/plan_path             路径规划
  - POST /api/plan_path_from_rfid   从RFID规划路径
  - POST /api/reload                重新加载数据
  - GET  /api/stats                 获取统计信息
================================================================================
```

## API 接口文档

### 1. 健康检查

**接口**: `GET /health`

**响应示例**:
```json
{
  "status": "ok",
  "service": "path_planning",
  "nodes": 126,
  "edges": 143
}
```

### 2. 路径规划

**接口**: `POST /api/plan_path`

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

**响应示例**:
```json
{
  "success": true,
  "distance": 24.36,
  "total_distance": 24.36,
  "floors": ["floor1", "floor2"],
  "steps": [
    {
      "step_number": 1,
      "floor": "floor1",
      "action": "出发",
      "location": "A甲板会议室",
      "distance": 4.70
    },
    {
      "step_number": 2,
      "floor": "floor1",
      "action": "经过",
      "location": "A甲板楼道",
      "distance": 2.36
    },
    ...
  ],
  "path_nodes": [
    {
      "node_type": 1,
      "node_id": 1,
      "map_id": "floor1"
    },
    ...
  ]
}
```

### 3. 从RFID设备规划路径

**接口**: `POST /api/plan_path_from_rfid`

**请求体**:
```json
{
  "rfid_id": "RFID_001",
  "end": {
    "x": 21.1138,
    "y": 12.9260,
    "map_id": "floor2"
  }
}
```

**响应格式**: 与路径规划接口相同

### 4. 重新加载数据（热加载）

**接口**: `POST /api/reload`

**使用场景**: 数据库数据更新后，重新导出txt文件，然后调用此接口刷新内存数据

**响应示例**:
```json
{
  "success": true,
  "message": "数据重新加载成功",
  "nodes": 126,
  "edges": 143
}
```

### 5. 获取统计信息

**接口**: `GET /api/stats`

**响应示例**:
```json
{
  "success": true,
  "stats": {
    "maps": 8,
    "doors": 65,
    "stairways": 26,
    "edges": 79,
    "rfid_devices": 35,
    "graph_nodes": 126,
    "graph_edges": 143
  }
}
```

## 测试服务器

运行测试脚本：

```bash
# 启动服务器（终端1）
python server.py

# 运行测试（终端2）
python test_server.py
```

测试脚本会执行：
1. 健康检查
2. 获取统计信息
3. 跨楼层路径规划
4. 同楼层路径规划
5. 性能测试（100次连续调用）

## 使用示例

### Python客户端

```python
import requests

# 路径规划
response = requests.post('http://localhost:5000/api/plan_path', json={
    "start": {"x": 22.4460, "y": 13.4433, "map_id": "floor1"},
    "end": {"x": 21.1138, "y": 12.9260, "map_id": "floor2"}
})

result = response.json()
if result['success']:
    print(f"总距离: {result['total_distance']:.2f} 米")
    for step in result['steps']:
        print(f"{step['action']} - {step['location']}")
```

### JavaScript客户端

```javascript
// 路径规划
fetch('http://localhost:5000/api/plan_path', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    start: {x: 22.4460, y: 13.4433, map_id: 'floor1'},
    end: {x: 21.1138, y: 12.9260, map_id: 'floor2'}
  })
})
.then(response => response.json())
.then(result => {
  if (result.success) {
    console.log(`总距离: ${result.total_distance} 米`);
    result.steps.forEach(step => {
      console.log(`${step.action} - ${step.location}`);
    });
  }
});
```

### curl命令

```bash
# 路径规划
curl -X POST http://localhost:5000/api/plan_path \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 22.4460, "y": 13.4433, "map_id": "floor1"},
    "end": {"x": 21.1138, "y": 12.9260, "map_id": "floor2"}
  }'
```

## 数据更新流程

当地图数据需要更新时：

```bash
# 步骤1：在数据库中修改数据（通过前端或后端API）

# 步骤2：重新导出txt文件
cd path_planning
python database.py

# 步骤3：调用热加载接口（无需重启服务器）
curl -X POST http://localhost:5000/api/reload
```

## 性能指标

- **启动时间**: 约1-2秒（加载数据+构建图）
- **单次路径规划**: 1-10毫秒
- **并发支持**: 支持多线程并发请求
- **内存占用**: 约50-100MB（取决于数据规模）

## 生产环境部署

### 使用Gunicorn（推荐）

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### 使用systemd（Linux）

创建服务文件 `/etc/systemd/system/path-planning.service`:

```ini
[Unit]
Description=Path Planning Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/path_planning
ExecStart=/path/to/python /path/to/path_planning/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl start path-planning
sudo systemctl enable path-planning
```

## 故障排查

### 问题1：服务启动失败

**原因**: 数据文件不存在

**解决**: 先运行 `python database.py` 导出数据文件

### 问题2：端口被占用

**错误**: `Address already in use`

**解决**: 修改 `server.py` 中的端口号，或关闭占用5000端口的程序

### 问题3：路径规划失败

**原因**: 起点或终点坐标不在任何节点附近

**解决**: 检查坐标是否正确，确保在地图范围内

## 日志

服务器会输出详细的日志信息：

- `INFO`: 正常操作日志
- `WARNING`: 警告信息（如最近节点距离过远）
- `ERROR`: 错误信息

日志格式：
```
2026-04-17 09:11:14,552 - __main__ - INFO - 路径规划服务器启动成功！
```

## 联系方式

如有问题，请查看日志或联系开发团队。
