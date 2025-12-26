#!/usr/bin/env python3
"""
比较两个commit之间某个玩家的数据差异
"""

import subprocess
import json
import sys

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
    except Exception as e:
        print(f"错误: {e}")
        return None

def compare_data(old_data, new_data, player_id):
    """比较两个数据字典的差异"""
    if not old_data and not new_data:
        print(f"两个commit中都没有找到 {player_id}")
        return
    
    if not old_data:
        print(f"玩家 {player_id} 在旧commit中不存在，在新commit中是新增的")
        return
    
    if not new_data:
        print(f"玩家 {player_id} 在新commit中不存在，已被删除")
        return
    
    # 找出所有字段
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    changes = []
    unchanged = []
    
    for key in sorted(all_keys):
        old_val = old_data.get(key, '不存在')
        new_val = new_data.get(key, '不存在')
        
        if old_val != new_val:
            delta = ''
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                delta = f" (变化: {new_val - old_val:+,})"
            changes.append({
                'field': key,
                'old': old_val,
                'new': new_val,
                'delta': delta
            })
        else:
            unchanged.append({
                'field': key,
                'value': old_val
            })
    
    return changes, unchanged

def main():
    if len(sys.argv) < 4:
        print("用法: python3 compare_commits.py <旧commit> <新commit> <玩家ID> [文件名]")
        print("示例: python3 compare_commits.py d77cf89 HEAD Puncheur")
        print("示例: python3 compare_commits.py d77cf89 HEAD Puncheur iwwc-custom-2024.json")
        sys.exit(1)
    
    old_commit = sys.argv[1]
    new_commit = sys.argv[2]
    player_id = sys.argv[3]
    filename = sys.argv[4] if len(sys.argv) > 4 else 'iwwc-custom-2025.json'
    
    print(f"\n{'='*80}")
    print(f"比较玩家 {player_id} 在两个commit之间的数据变化")
    print(f"{'='*80}")
    print(f"文件: {filename}")
    print(f"旧commit: {old_commit}")
    print(f"新commit: {new_commit}")
    print(f"{'='*80}\n")
    
    # 获取两个commit的数据
    print("正在获取数据...")
    old_data = get_player_data(old_commit, filename, player_id)
    new_data = get_player_data(new_commit, filename, player_id)
    
    if old_data is None and new_data is None:
        print(f"\n❌ 在两个commit中都未找到玩家 {player_id}")
        return
    
    # 比较数据
    result = compare_data(old_data, new_data, player_id)
    
    if result is None:
        return
    
    changes, unchanged = result
    
    # 显示变化
    if changes:
        print(f"\n🔥 发现 {len(changes)} 个字段变化:\n")
        print(f"{'字段':<30} {'旧值':<20} {'新值':<20} {'变化'}")
        print(f"{'-'*100}")
        
        for change in changes:
            old_str = str(change['old'])[:18]
            new_str = str(change['new'])[:18]
            print(f"{change['field']:<30} {old_str:<20} {new_str:<20} {change['delta']}")
    else:
        print("\n✅ 没有发现数据变化")
    
    # 显示未变化的字段统计
    print(f"\n📊 统计信息:")
    print(f"  - 变化字段: {len(changes)}")
    print(f"  - 未变化字段: {len(unchanged)}")
    print(f"  - 总字段数: {len(changes) + len(unchanged)}")
    
    # 询问是否显示未变化的字段
    if unchanged:
        show_unchanged = input(f"\n是否显示 {len(unchanged)} 个未变化的字段? (y/n): ").lower()
        if show_unchanged == 'y':
            print(f"\n📋 未变化的字段:\n")
            print(f"{'字段':<30} {'值'}")
            print(f"{'-'*60}")
            for item in unchanged:
                val_str = str(item['value'])[:28]
                print(f"{item['field']:<30} {val_str}")
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    main()
