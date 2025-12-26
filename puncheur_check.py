#!/usr/bin/env python3
"""
IWWC Puncheur 数据异常一键检查工具 - 横向对比版
快速横向对比多个关键commit的数据变化
"""

import subprocess
import json

# 关键commit列表（发现的异常数据点）
KEY_COMMITS = [
    {
        'hash': '1b9ea3c3',
        'short': '1b9ea3c3',
        'date': '2025-09-01',
        'description': '首次记录'
    },
    {
        'hash': '36236f18',
        'short': '36236f18',
        'date': '2025-09-08',
        'description': '正常增长'
    },
    {
        'hash': '0f3eaa39',
        'short': '0f3eaa39',
        'date': '2025-09-15',
        'description': '正常增长'
    },
    {
        'hash': 'd77cf892',
        'short': 'd77cf892',
        'date': '2025-09-22',
        'description': '⚠️ 异常开始'
    },
    {
        'hash': '3a143ab6',
        'short': '3a143ab6',
        'date': '2025-10-01',
        'description': '⚠️ 持续异常'
    },
]

def get_player_data(commit_hash, filename, player_id):
    """获取指定commit中玩家的数据"""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit_hash}:{filename}'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get(player_id, None)
    except:
        return None

def main():
    player_id = 'Puncheur'
    filename = 'iwwc-custom-2025.json'
    
    print("\n" + "="*130)
    print("🔍 IWWC Puncheur 数据异常横向对比")
    print("="*130)
    print(f"玩家: {player_id}")
    print(f"数据文件: {filename}\n")
    
    # 关键指标 - 增加更多综合比较指标
    key_fields = [
        'drone_sender', 
        'crafter', 
        'trekker', 
        'ap', 
        'lifetime_ap', 
        'hacker',
        'engineer',
        'level',
        'explorer',
        'builder',
        'connector',
    ]
    
    # 收集所有commit的数据
    all_data = []
    for commit_info in KEY_COMMITS:
        data = get_player_data(commit_info['hash'], filename, player_id)
        if data:
            all_data.append({
                'commit': commit_info,
                'data': data
            })
        else:
            print(f"⚠️  无法获取 {commit_info['hash']} 的数据")
    
    if not all_data:
        print("❌ 没有获取到任何数据")
        return
    
    # 打印表头 - 日期
    print(f"{'指标':<20}", end='')
    for item in all_data:
        commit = item['commit']
        print(f"{commit['date']:>20} ", end='')
    print()
    
    # 打印表头 - Commit短hash
    print(f"{'':20}", end='')
    for item in all_data:
        commit = item['commit']
        print(f"{commit['short'][:8]:>20} ", end='')
    print()
    
    print("-" * 130)
    
    # 打印每个指标的横向对比
    for field in key_fields:
        print(f"{field:<20}", end='')
        
        prev_value = None
        for idx, item in enumerate(all_data):
            value = item['data'].get(field, 'N/A')
            commit_date = item['commit']['date']
            
            # 格式化数值
            if isinstance(value, (int, float)):
                formatted = f"{value:,}"
                
                # 计算增量（相对于上一个commit）
                is_anomaly = False
                if prev_value is not None and isinstance(prev_value, (int, float)):
                    delta = value - prev_value
                    
                    # 判断是否为异常增长
                    # drone_sender增长>100, 其他指标增长>300视为异常
                    if field == 'drone_sender' and delta > 100:
                        is_anomaly = True
                    elif field in ['hacker', 'explorer', 'builder'] and delta > 300:
                        is_anomaly = True
                    elif field in ['ap', 'lifetime_ap'] and delta > 500000:
                        is_anomaly = True
                    
                    if delta > 0:
                        formatted = f"{formatted} (+{delta:,})"
                    elif delta < 0:
                        formatted = f"{formatted} ({delta:,})"
                
                # 给异常数据加方括号
                if is_anomaly:
                    formatted = f"[{formatted}]"
                
                prev_value = value
            else:
                formatted = str(value)
                prev_value = None
            
            # 控制列宽
            if len(formatted) > 20:
                formatted = formatted[:17] + "..."
            print(f"{formatted:>20} ", end='')
        print()
    
    print("-" * 130)
    
    # 打印关键发现
    print("\n🔍 关键发现:")
    if len(all_data) >= 2:
        # drone_sender的变化
        ds_values = [(item['commit']['date'], item['data'].get('drone_sender', 0)) for item in all_data]
        print(f"  • drone_sender: ", end='')
        for i, (date, val) in enumerate(ds_values):
            if i > 0:
                prev_val = ds_values[i-1][1]
                delta = val - prev_val
                if delta > 100:  # 显著增长
                    print(f"\n    {date}: {prev_val} → {val:,} (⚠️ +{delta:,})", end='')
                else:
                    print(f"{val:,}", end='')
                    if i < len(ds_values) - 1:
                        print(" → ", end='')
            else:
                print(f"{val:,} → ", end='')
        print()
    
    # 打印GitHub链接
    print("\n📎 Commit 链接:")
    for item in all_data:
        commit = item['commit']
        print(f"  • {commit['date']} ({commit['short'][:8]}): https://github.com/Xyinkl/iwwc-stats-data-snapshot-20251225/commit/{commit['hash']}")
    
    print("\n💡 使用 compare_commits.py 可以详细比较任意两个commit")
    print("   示例: python3 compare_commits.py d77cf89 3a143ab6 Puncheur")
    print("="*130 + "\n")

if __name__ == '__main__':
    main()
