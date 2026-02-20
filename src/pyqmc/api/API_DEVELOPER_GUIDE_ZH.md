# pyQMC API 开发说明（中文）

本文档面向开发者，说明 `src/pyqmc/api` 在当前架构中的职责，以及如何在新增功能时与 `application`、`core`、`gui` 协同。

核心原则：
- `api/` 是 HTTP 适配层，不承载业务编排逻辑。
- 业务用例放在 `src/pyqmc/application/`。
- 参数映射与默认值在共享模块 `src/pyqmc/core/vmc_input.py` 中统一。

---

## 1. API 目录结构

当前核心文件：
- `__init__.py`
- `__main__.py`
- `api_server.py`
- `api.py`
- `models.py`
- `API_DEVELOPER_GUIDE_ZH.md`

说明：
- 旧的 `service.py` 已移除。
- 业务编排职责已迁移到 `src/pyqmc/application/`。

推荐阅读顺序：
1. `api.py`（路由）
2. `models.py`（请求/响应 schema）
3. `api_server.py`（服务启动）
4. `src/pyqmc/application/*`（实际用例）

---

## 2. 文件级说明

## 2.1 `__init__.py`

职责：
- 对外暴露 `create_app`。
- 延迟导入 FastAPI，避免非 API 场景因依赖缺失报错。

## 2.2 `__main__.py`

职责：
- 支持 `python -m pyqmc.api`。
- 内部转发到 `api_server.main()`。

## 2.3 `api_server.py`

职责：
- API 进程入口。
- 参数解析（host/port/reload/log-level）。
- 启动 uvicorn 并做依赖检查。

## 2.4 `models.py`

职责：
- 定义 API 输入/输出契约（Pydantic）。
- 负责输入边界与跨字段校验（例如 `burn_in < n_steps`）。

注意：
- `VMC` 的默认参数来自 `core/vmc_input.py`，避免 API 与 GUI 默认值漂移。

## 2.5 `api.py`

职责：
- 创建 FastAPI app。
- 配置中间件（CORS）。
- 注册路由并把请求转发给 `application` 用例。

分层要求：
- 路由函数保持薄：
  - 接收 `models.py` 请求模型。
  - 调用 `application` 用例（非 `core` 细节拼装）。
  - 将结果封装为响应模型。

---

## 3. 与 application 层的关系

`application` 是 transport-agnostic 用例层，API 只做协议适配。

当前 API 对应关系：
- `GET /methods` -> `application.catalog.get_available_methods()`
- `GET /systems` -> `application.catalog.get_available_systems()`
- `POST /simulate/vmc/harmonic-oscillator` -> `application.vmc.run_vmc_harmonic_oscillator_use_case(...)`
- `POST /benchmark/vmc/harmonic-oscillator` -> `application.vmc.run_vmc_harmonic_oscillator_benchmark_use_case(...)`

收益：
- CLI / GUI direct / API 共用同一业务用例，行为一致。
- API 目录保持干净，不与计算实现耦合。

---

## 4. 调用链（GUI 与 API 并存）

A. GUI 直算路径：
1. `gui/assets/app.js` 组装 payload。
2. 调 `window.pywebview.api`。
3. `gui/app.py` bridge 调 `application` 用例。
4. 返回结果渲染。

B. API 路径：
1. 前端 `fetch` 请求 API。
2. `api.py` 路由收参（Pydantic）。
3. 路由调用 `application` 用例。
4. 返回响应模型 JSON。

`--compute-mode auto` 下一般先走 A，失败后回退 B。

---

## 5. 新增 API 功能的标准流程

以新增 `DMC Hydrogen` 为例：

1. 后端实现：
- 在 `core/` + `dmc/` 实现计算逻辑与 solver。

2. application 用例：
- 在 `src/pyqmc/application/` 新增/扩展用例函数，入参用 primitive types。

3. API 模型：
- 在 `models.py` 增加请求/响应模型与校验。

4. API 路由：
- 在 `api.py` 注册 endpoint。
- 路由只做 schema 适配，调用 `application` 用例。

5. GUI 与 CLI（如需）：
- GUI 直算路径调用同一 `application` 用例。
- CLI 子命令也调用同一 `application` 用例。

6. 测试：
- API 集成测试：200/422。
- 用例单测与相关数值测试。

---

## 6. 常见错误与建议

1. 错误：把业务编排写在 `api.py` 路由里。
- 建议：下沉到 `application/`。

2. 错误：API 和 GUI 分别维护默认值/映射规则。
- 建议：统一复用 `core/vmc_input.py`。

3. 错误：新增参数只改 API，没改 GUI direct 路径。
- 建议：检查 `application` 用例签名 + GUI bridge + API model 三处同步。

---

## 7. 调试命令

启动 API：
```bash
pyqmc serve-api --host 127.0.0.1 --port 8000
```

查看 Swagger：
- `http://127.0.0.1:8000/docs`

运行测试：
```bash
pytest
```

只跑 API 集成测试：
```bash
pytest tests/integration/test_api.py
```
