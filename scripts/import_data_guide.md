# UptimeFlare 数据导入指南

此文档包含用于在本地和生产环境之间导入/迁移数据的说明。

## 1. 导入到本地开发环境 (`import_local_data.py`)

### 1.1 导出远程数据

查询远程数据库名称，运行 `npx wrangler d1 list`。

在项目根目录运行以下命令导出数据（请将 `<YOUR_DB_NAME>` 替换为实际名称）：

```bash
npx wrangler d1 execute <YOUR_DB_NAME> \
  -c /dev/null \
  --remote \
  --command "SELECT value FROM uptimeflare WHERE key = 'state'" \
  --json > backup_data.json
```

### 1.2 初始化本地数据库

如果本地还没生成数据库文件，需先启动一次开发服务器：

```bash
pnpm dev
```

### 1.3 导入数据

运行脚本（已自动绕过 Wrangler 长度限制写入 sqlite）：

```bash
python3 scripts/import_local_data.py
```

完成后重启 `pnpm dev` 即可查看数据。

---

## 2. 导入到生产环境 (`import_data.py`)

用于将备份数据恢复到生产环境 D1 数据库。

```bash
# 1. 确保根目录下有 backup_data.json 备份文件
# 2. 执行导入（脚本会进行二次确认）
python3 scripts/import_data.py
```

---

## 附加说明

**备份数据格式示例 (`backup_data.json`)：**

```json
[
  {
    "results": [
      {
        "value": "{\"overallUp\":5,\"overallDown\":0,\"lastUpdate\":1738483200,\"incident\":{},\"latency\":{}}"
      }
    ]
  }
]
```

**常见故障排查：**

- **未安装 Node/npm**：macOS 可通过 `brew install node` 安装。
- **未登录 Cloudflare**：请先运行 `npx wrangler login`。
- **权限错误**：给脚本添加执行权限：`chmod +x scripts/*.py`。
- **JSON 错误**：使用 `cat backup_data.json | python3 -m json.tool` 验证文件。
