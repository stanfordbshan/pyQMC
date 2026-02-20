# pyQMC GUI 联动说明（中文）

本文档解释 GUI 如何通过 `index.html`、`app.js` 与 `app.py` 调用后端计算逻辑，以及新增功能时应该遵循的改造流程。

适用目录：
- `src/pyqmc/gui/assets/index.html`
- `src/pyqmc/gui/assets/app.js`
- `src/pyqmc/gui/app.py`

---

## 1. 三个文件分别做什么

## 1.1 `index.html`：界面结构层

职责：
- 定义页面元素（输入框、按钮、结果显示区域）。
- 提供可被 JS 定位的 DOM id（例如 `n_steps`、`run-btn`、`result`）。
- 加载 `app.js` 执行业务交互。

你可以把它理解为“控件与布局定义”，不负责计算。

---

## 1.2 `app.js`：前端交互与调用编排层

职责：
- 从 URL 参数读取运行模式：
  - `compute_mode=auto|direct|api`
  - `api_base_url=...`（可选）
- 收集表单输入并组装 payload。
- 根据模式选择调用路径：
  - `direct`：通过 `window.pywebview.api` 直接调用 Python bridge（不走 HTTP）。
  - `api`：通过 `fetch` 调用 FastAPI endpoint。
  - `auto`：先尝试 `direct`，失败再回退 `api`。
- 解析返回结果并渲染到页面。

关键函数：
- `payloadFromForm()`：把表单数据转成 JSON。
- `runViaLocalBridge(payload)`：走本地直算。
- `runViaApi(payload)`：走 HTTP API。
- `runWithConfiguredMode(payload)`：模式决策与回退策略。

---

## 1.3 `app.py`：GUI 宿主与 Python 侧桥接层

职责：
- 启动 pywebview 窗口并加载 `index.html`。
- 把 `compute_mode`、`api_base_url` 通过 URL query 传给前端 JS。
- 注册 `js_api=LocalComputeBridge()`，让 JS 可以直接调用 Python 方法。
- 在需要 API 通道时，负责：
  - 连接外部 API（`--api-url`）或
  - 启动嵌入式本地 API 子进程。
- GUI 关闭时回收嵌入式 API 子进程。

关键类/函数：
- `LocalComputeBridge.run_vmc_harmonic_oscillator(payload)`：本地直算入口。
- `_resolve_api_backend(...)`：决定是否需要 API，以及使用本地/远程 API。
- `_build_frontend_url(...)`：将运行模式和 API 地址注入前端 URL。
- `launch_gui(...)`：整体启动流程。

---

## 2. 端到端调用链路

## 2.1 本地直算链路（不走 HTTP）

1. 用户在 `index.html` 输入参数并点击按钮。
2. `app.js` 收集 payload。
3. `app.js -> window.pywebview.api.run_vmc_harmonic_oscillator(payload)`。
4. `app.py` 中 `LocalComputeBridge` 接收 payload。
5. bridge 构造 `SimulationConfig` 并调用 `pyqmc.vmc.solver`。
6. 计算结果返回 JS，`app.js` 渲染到页面。

特点：
- 无网络请求。
- 低开销，适合本机桌面场景。

## 2.2 API 链路（本地/远程 HTTP）

1. 用户在页面输入参数并提交。
2. `app.js` 发送 `fetch POST /simulate/vmc/harmonic-oscillator`。
3. FastAPI 路由处理请求并调用后端 solver。
4. JSON 响应返回前端，`app.js` 渲染结果。

特点：
- 便于与远程服务统一。
- 适合部署与跨进程调用。

## 2.3 `auto` 模式行为

- 先尝试本地直算。
- 若 bridge 不可用或失败，再尝试 API（如果存在 `api_base_url`）。

---

## 3. 三种 GUI 运行模式

- `pyqmc gui --compute-mode direct`
  - 仅本地直算。
- `pyqmc gui --compute-mode api`
  - 仅 HTTP API。
  - 若未给 `--api-url`，会自动启动嵌入式本地 API。
- `pyqmc gui`（默认 `auto`）
  - 直算优先，API 回退。

---

## 4. 新增功能时的标准流程

下面给出“新增一个计算功能”时的推荐步骤。

## Step 1：先实现后端计算函数

先在 `core/vmc/dmc/...` 完成计算逻辑并可单独测试。

示例目标：新增“某新系统模拟”函数：
- `run_new_feature(config) -> dict or SimulationResult`

## Step 2：更新 Python bridge（直算路径）

在 `src/pyqmc/gui/app.py`：

1. 在 `LocalComputeBridge` 增加方法，例如：

```python
class LocalComputeBridge:
    def run_new_feature(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = _build_new_feature_config(payload)
        result = run_new_feature(config)
        return result.to_dict()
```

2. 增加 payload 解析/校验函数（仿照 `_build_vmc_config_from_payload`）。

这样 `app.js` 才能直接调用该本地能力。

## Step 3：更新 API（如果需要 API 路径）

在 `src/pyqmc/api` 同步新增：
- `models.py`：请求/响应模型
- `service.py`：业务编排
- `api.py`：新 endpoint

说明：
- 如果该功能只用于本地直算，可暂不新增 API。
- 若希望远程部署可用，必须补 API。

## Step 4：更新 `app.js` 调用逻辑

1. 扩展 payload 组装。
2. 扩展本地调用分支：
   - 调 `window.pywebview.api.run_new_feature(...)`
3. 扩展 API 调用分支：
   - 调新 endpoint
4. 扩展结果渲染逻辑。

## Step 5：更新 `index.html` 与样式

- 增加新控件（输入参数、按钮、结果区域）。
- 保持 id 命名与 `app.js` 一致。

## Step 6：补测试

至少覆盖：
- GUI bridge 单测（`tests/unit`）：
  - 正常 payload
  - 非法 payload
- API 集成测试（若新增 API）：
  - 200 成功
  - 422 参数错误
- CLI/GUI 参数帮助检查（必要时）。

---

## 5. 常见改造场景

## 场景 A：新增一个输入参数（如 `time_step`）

你需要同时改：
1. `index.html`：加输入框
2. `app.js`：payload 加字段
3. `app.py` bridge：解析并传给 config
4. API 模型/服务/路由（若使用 API）
5. 测试

## 场景 B：新增一个返回字段（如 `autocorrelation_time`）

你需要同时改：
1. 后端结果对象
2. API 响应模型（若使用 API）
3. `app.js` 渲染逻辑
4. 测试断言

---

## 6. 开发检查清单

每次改动前后，建议逐项检查：

- 页面 id 与 JS 读取 id 是否一致。
- JS payload 字段名与 Python 解析字段名是否一致。
- 直算模式是否可跑通。
- API 模式是否可跑通（本地或远程）。
- `auto` 模式是否符合“先直算后回退”预期。
- 新功能是否有最小测试覆盖。

---

## 7. 一句话总结

`index.html` 提供界面，`app.js` 负责交互与路由决策，`app.py` 负责桥接 Python 计算与可选 API 后端；三者配合实现了“桌面本地直算 + HTTP API 可回退”的 GUI 架构。
