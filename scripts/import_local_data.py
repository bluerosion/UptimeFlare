#!/usr/bin/env python3
"""
UptimeFlare - 数据导入脚本
详细文档查看: scripts/import_data_guide.md
运行此脚本: python3 scripts/import_local_data.py
"""

import json
import subprocess
import sys
import os

def main():
    # 检查备份文件是否存在
    backup_file = "backup_data.json"
    if not os.path.exists(backup_file):
        print(f"❌ 错误: 找不到备份文件 '{backup_file}'")
        print("\n请先从生产环境导出数据:")
        print('  npx wrangler d1 execute <YOUR_DB_NAME> \\')
        print('    -c /dev/null \\')
        print('    --remote \\')
        print('    --command "SELECT value FROM uptimeflare WHERE key = \'state\'" \\')
        print('    --json > backup_data.json')
        sys.exit(1)

    # 读取备份数据
    print(f"📖 读取备份文件: {backup_file}")
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 错误: JSON 格式错误 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: 读取文件失败 - {e}")
        sys.exit(1)

    # 提取 state 数据
    if not data or len(data) == 0:
        print("❌ 错误: 备份文件为空")
        sys.exit(1)

    # Wrangler 导出的格式可能包含 results
    state_value = None
    if isinstance(data, list) and len(data) > 0:
        if 'results' in data[0] and data[0]['results']:
            state_value = data[0]['results'][0].get('value')
        else:
            state_value = data[0].get('value')
    elif isinstance(data, dict):
        if 'results' in data and data['results']:
            state_value = data['results'][0].get('value')
        else:
            state_value = data.get('value')
    else:
        print("❌ 错误: 无法识别的数据格式")
        sys.exit(1)

    if not state_value:
        print("❌ 错误: 找不到 'value' 字段")
        sys.exit(1)

    print(f"✅ 成功读取数据 ({len(state_value)} 字符)")

    # 转义 JSON 字符串中的特殊字符
    # 将单引号替换为两个单引号（SQLite 转义方式）
    # 将单引号替换为两个单引号（SQLite 转义方式）
    escaped_value = state_value.replace("'", "''")

    print("\n🔄 准备导入数据...")
    import glob
    db_files = glob.glob('.wrangler/state/v3/d1/miniflare-D1DatabaseObject/*.sqlite')
    if not db_files:
        print("❌ 错误: 找不到本地数据库，请先运行一次 npm run dev 初始化")
        sys.exit(1)

    latest_db = max(db_files, key=os.path.getmtime)
    print(f"🔄 绕过 Wrangler 限制，使用 sqlite3 直接写入数据库...")

    try:
        sql = f"INSERT OR REPLACE INTO uptimeflare (key, value) VALUES ('state', '{escaped_value}');"
        subprocess.run(['sqlite3', latest_db], input=sql, text=True, check=True)
        print("✅ 数据导入成功!")
        print("\n✨ 完成! 现在可以重启开发服务器:")
        print("  npm run dev")
    except Exception as e:
        print(f"❌ 错误: 导入失败 - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
