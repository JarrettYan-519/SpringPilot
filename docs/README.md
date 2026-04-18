# SpringPilot 使用说明

## 项目简介

SpringPilot 是一个本地 Web 应用，帮助你同时管理春招求职和健身计划。

**功能模块：**
- **求职管理** — 投递记录跟踪、学习任务看板、JD 分析、AI 模拟面试
- **健身管理** — 体重趋势、饮食记录、训练日志、教练计划解析
- **AI 助手** — 支持多模型（OpenAI / DeepSeek / Claude / 智谱），提供 JD 匹配分析、面试题生成、热量估算、每日综合建议

**技术栈：** FastAPI 后端 + Vue 3 前端 + SQLite + LangChain AI + MinerU 文档解析

---

## 环境要求

- Python 3.11+
- Node.js 18+
- npm

---

## 启动方式

需要开两个终端窗口，分别启动后端和前端。

### 1. 启动后端

```bash
cd ~/Desktop/SpringPilot
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

看到 `Uvicorn running on http://127.0.0.1:8000` 表示启动成功。

验证后端是否正常：

```bash
curl http://localhost:8000/api/health
# 返回 {"status":"ok"}
```

### 2. 启动前端

新开一个终端窗口：

```bash
cd ~/Desktop/SpringPilot/frontend
npm run dev
```

看到 `Local: http://localhost:5173/` 后，用浏览器打开这个地址。

前端的 `/api` 请求会通过 Vite 代理自动转发到后端的 8000 端口，无需额外配置。

---

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

API 文档页面由 FastAPI 自动生成，可以直接在浏览器里测试所有接口。

---

## 配置 AI 模型

在使用 AI 功能（JD 分析、模拟面试、热量估算等）之前，需要先配置 LLM 的 API Key。

打开前端的 **设置** 页面，或直接调用 API：

```bash
# 配置默认使用 DeepSeek
curl -X PUT http://localhost:8000/api/settings/llm_provider_default \
  -H "Content-Type: application/json" \
  -d '{"value": "deepseek"}'

# 配置 DeepSeek 的 API Key
curl -X PUT http://localhost:8000/api/settings/llm_api_key_deepseek \
  -H "Content-Type: application/json" \
  -d '{"value": "你的API Key"}'
```

**支持的模型提供商：**

| 提供商 | provider 名称 | 默认模型 |
|--------|--------------|----------|
| OpenAI | `openai` | gpt-4o-mini |
| DeepSeek | `deepseek` | deepseek-chat |
| Claude | `claude` | claude-sonnet-4-6 |
| 智谱 | `glm` | glm-4-flash |

配置项命名规则：
- `llm_provider_default` — 默认使用哪个提供商
- `llm_api_key_{provider}` — 对应提供商的 API Key
- `llm_base_url_{provider}` — 自定义 API 地址（可选）
- `llm_model_{provider}` — 自定义模型名称（可选）

---

## 配置 MinerU 文档解析（可选）

用于解析教练发的 PDF/DOCX 训练计划文件：

```bash
curl -X PUT http://localhost:8000/api/settings/mineru_api_key \
  -H "Content-Type: application/json" \
  -d '{"value": "你的MinerU API Key"}'
```

不配置也可以使用，但上传 PDF/DOCX 会解析失败。Markdown 文件不需要 API Key。

---

## 项目结构

```
SpringPilot/
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口 + 路由注册
│   ├── config.py             # 配置（数据库路径、上传目录等）
│   ├── database.py           # SQLAlchemy 引擎 + Session
│   ├── models/               # 数据库模型
│   ├── schemas/              # Pydantic 请求/响应模式
│   ├── routers/              # API 路由
│   ├── services/             # 业务服务（AI、MinerU）
│   └── tests/                # 测试
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/              # Axios API 客户端
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── router/           # Vue Router 路由配置
│   │   ├── views/            # 页面组件
│   │   └── App.vue           # 主布局（侧边栏导航）
│   └── vite.config.js        # Vite 配置（含代理）
├── .venv/                    # Python 虚拟环境
└── docs/                     # 文档
```

---

## API 接口一览

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 投递 | POST | `/api/applications` | 创建投递记录 |
| 投递 | GET | `/api/applications` | 列表（支持 status_filter 筛选） |
| 投递 | GET | `/api/applications/{id}` | 详情 |
| 投递 | PATCH | `/api/applications/{id}` | 更新 |
| 投递 | POST | `/api/applications/{id}/status` | 更新状态（含日志） |
| 投递 | DELETE | `/api/applications/{id}` | 删除 |
| 学习 | POST | `/api/study-tasks` | 创建学习任务 |
| 学习 | GET | `/api/study-tasks` | 列表 |
| 学习 | PATCH | `/api/study-tasks/{id}` | 更新（标记完成等） |
| 学习 | DELETE | `/api/study-tasks/{id}` | 删除 |
| 体重 | POST | `/api/weight` | 记录体重 |
| 体重 | GET | `/api/weight` | 查询记录 |
| 饮食 | POST | `/api/diet` | 记录饮食 |
| 饮食 | GET | `/api/diet` | 查询（支持日期筛选） |
| 训练 | POST | `/api/training` | 记录训练 |
| 训练 | PATCH | `/api/training/{id}` | 更新（标记完成） |
| 训练计划 | GET | `/api/trainer-plans` | 列表 |
| 训练计划 | POST | `/api/trainer-plans` | 上传计划文件 |
| AI | POST | `/api/ai/analyze-jd` | JD 分析 |
| AI | POST | `/api/ai/generate-questions` | 生成面试题 |
| AI | POST | `/api/ai/mock-interview` | 模拟面试对话 |
| AI | POST | `/api/ai/estimate-calories` | 估算热量 |
| AI | POST | `/api/ai/daily-advice` | 每日综合建议 |
| 设置 | GET | `/api/settings` | 获取所有配置 |
| 设置 | GET | `/api/settings/{key}` | 获取单个配置 |
| 设置 | PUT | `/api/settings/{key}` | 设置配置 |
| 健康检查 | GET | `/api/health` | 服务状态 |

---

## 运行测试

```bash
cd ~/Desktop/SpringPilot
source .venv/bin/activate
pytest backend/tests/ -v
```

---

## 常见问题

**Q: 启动后端报错 `ModuleNotFoundError`**

确认你在 SpringPilot 根目录下运行命令，并且已激活虚拟环境：
```bash
cd ~/Desktop/SpringPilot
source .venv/bin/activate
```

**Q: 前端页面打开了但没有数据**

确认后端也在运行。两个服务需要同时启动。

**Q: AI 功能返回 400 错误**

需要先在设置中配置 LLM 的 API Key，参考上方「配置 AI 模型」章节。

**Q: 上传 PDF 文件解析失败**

需要配置 MinerU API Key。Markdown 文件可以直接解析，不需要 Key。
