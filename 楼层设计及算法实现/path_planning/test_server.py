"""
路径规划服务器测试客户端
测试HTTP API接口
"""

import requests
import json
import time


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 80)
    print("测试1: 健康检查")
    print("=" * 80)
    
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_stats():
    """测试统计信息接口"""
    print("\n" + "=" * 80)
    print("测试2: 获取统计信息")
    print("=" * 80)
    
    try:
        response = requests.get('http://localhost:5000/api/stats')
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_plan_path():
    """测试路径规划接口"""
    print("\n" + "=" * 80)
    print("测试3: 跨楼层路径规划")
    print("=" * 80)
    
    # 测试数据：从楼层1的A甲板会议室到楼层2的官员餐厅
    data = {
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
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        start_time = time.time()
        response = requests.post('http://localhost:5000/api/plan_path', json=data)
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应时间: {elapsed_time:.2f} ms")
        
        result = response.json()
        
        if result['success']:
            print(f"\n✓ 路径规划成功！")
            print(f"总距离: {result['total_distance']:.2f} 米")
            print(f"经过楼层: {' -> '.join(result['floors'])}")
            print(f"\n详细步骤:")
            print("-" * 80)
            for step in result['steps']:
                print(f"步骤 {step['step_number']}: [{step['floor']}] {step['action']} - "
                      f"{step['location']} ({step['distance']:.2f}米)")
            print("-" * 80)
            return True
        else:
            print(f"✗ 路径规划失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_plan_path_same_floor():
    """测试同楼层路径规划"""
    print("\n" + "=" * 80)
    print("测试4: 同楼层路径规划")
    print("=" * 80)
    
    # 测试数据：楼层1内的路径规划
    data = {
        "start": {
            "x": 22.4460,
            "y": 13.4433,
            "map_id": "floor1"
        },
        "end": {
            "x": 22.1582,
            "y": 6.4752,
            "map_id": "floor1"
        }
    }
    
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        start_time = time.time()
        response = requests.post('http://localhost:5000/api/plan_path', json=data)
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应时间: {elapsed_time:.2f} ms")
        
        result = response.json()
        
        if result['success']:
            print(f"\n✓ 路径规划成功！")
            print(f"总距离: {result['total_distance']:.2f} 米")
            print(f"经过楼层: {' -> '.join(result['floors'])}")
            print(f"\n详细步骤:")
            print("-" * 80)
            for step in result['steps']:
                print(f"步骤 {step['step_number']}: [{step['floor']}] {step['action']} - "
                      f"{step['location']} ({step['distance']:.2f}米)")
            print("-" * 80)
            return True
        else:
            print(f"✗ 路径规划失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_performance():
    """测试性能：连续调用100次"""
    print("\n" + "=" * 80)
    print("测试5: 性能测试（连续调用100次）")
    print("=" * 80)
    
    data = {
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
    
    times = []
    success_count = 0
    
    print("开始测试...")
    
    for i in range(100):
        try:
            start_time = time.time()
            response = requests.post('http://localhost:5000/api/plan_path', json=data)
            elapsed_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 and response.json()['success']:
                success_count += 1
                times.append(elapsed_time)
            
            if (i + 1) % 10 == 0:
                print(f"已完成 {i + 1}/100 次请求...")
                
        except Exception as e:
            print(f"第 {i + 1} 次请求失败: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n性能统计:")
        print(f"  成功次数: {success_count}/100")
        print(f"  平均响应时间: {avg_time:.2f} ms")
        print(f"  最快响应时间: {min_time:.2f} ms")
        print(f"  最慢响应时间: {max_time:.2f} ms")
        
        return success_count == 100
    else:
        print("✗ 所有请求都失败了")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("路径规划服务器测试")
    print("=" * 80)
    print("请确保服务器已启动: python server.py")
    print("=" * 80)
    
    input("\n按回车键开始测试...")
    
    results = []
    
    # 执行测试
    results.append(("健康检查", test_health_check()))
    results.append(("统计信息", test_stats()))
    results.append(("跨楼层路径规划", test_plan_path()))
    results.append(("同楼层路径规划", test_plan_path_same_floor()))
    results.append(("性能测试", test_performance()))
    
    # 输出测试结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print("=" * 80)
    print(f"总计: {passed}/{total} 通过")
    print("=" * 80)


if __name__ == "__main__":
    main()
