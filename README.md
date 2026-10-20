# 聊天记录导出工具

Windows 本地 Streamlit 网页原型，Python 3.11。数据在本机处理，不连接云端，也不自动访问微信目录。

## 使用

在项目目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

访问 http://127.0.0.1:8501 。保持终端运行；Ctrl+C 停止。也可在 PowerShell 中运行 `./start.ps1`，如执行策略不允许，使用上面的 Python 命令即可。

1. 选择示例数据体验，或导入符合格式的 JSON/CSV。
2. 选择一个或多个会话、开始/结束日期、消息类型，可选关键词。
3. 查看预览。结束日期当天全部包含，时间统一为北京时间。
4. 点击生成，再下载合并 Word、合并 PDF，或按会话分开存放 Word/PDF 的 ZIP。
5. 修改条件后需要重新生成，旧结果不会作为新筛选结果下载。

## 导入协议

示例见 `sample_messages.json`。JSON 顶层是消息数组；CSV 使用以下列名。所有字段必须为字符串：

| 字段 | 含义 |
| --- | --- |
| conversation_id | 稳定的会话 ID，同名好友应使用不同 ID |
| conversation | 显示名称 |
| sender | 发送人名称 |
| timestamp | ISO 时间或 `2026-10-20 10:30:00`，无时区按北京时间 |
| type | `text` 为文字；其他类型输出文字说明 |
| content | 消息正文或附件说明，可包含换行 |

编码必须为 UTF-8（允许 BOM）；单次最多 20 MB、100000 条。相同内容的重复消息保留。预览显示前 500 条，导出包含所有筛选结果。导出长时间范围会耗时并占用内存，建议按会话或月份分批。

## 当前边界

- 尚未连接微信，不能直接导入微信数据库、备份、任意第三方 JSON 或 CSV。需要针对来源编写格式适配器。
- 只导出文字及非文字消息的说明，图片、语音、视频、文件尚未嵌入；不会将附件路径作为本地文件读取。
- PDF 支持普通中文和拉丁文字，特殊符号、emoji 和生僻字的字形尚未全面验证。
- 导出说明包含来源、筛选条件、生成时间和附件限制；无法证明历史记录完整或内容真实性。
- 用户导入内容和下载结果驻留本地进程/浏览器内存，浏览器下载由用户决定保存位置。应用不主动保存导入原件，不将其写入全局缓存。

## 验证

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_chat
```

测试覆盖日期末秒、次日排除、关键词和类型、错误文件、时区转换、Word 内容、ZIP 结构及网页筛选/生成交互。
PDF 示例已渲染检查。Word 已验证可重新打开、内容与结构正确；环境缺少 LibreOffice，自动视觉检查未完成，需要在 Word/WPS 中核对分页。

初始原型已保留为 `app.initial.py`。
