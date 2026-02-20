# pyQMC API 开发说明（中文）

本文档面向开发者，详细说明 `src/pyqmc/api` 目录下各 Python 文件的职责、调用链路，以及在新增功能或调整 GUI 时如何正确新增/修改 API。

## 1. 目录结构与职责总览

`src/pyqmc/api` 当前核心文件：

- `__init__.py`
- `__main__.py`
- `api_server.py`
- `api.py`
- `models.py`
- `service.py`

推荐理解顺序：
1. `api.py`（路由定义）
2. `models.py`（请求/响应模型）
3. `service.py`（业务编排层）
4. `api_server.py`（服务启动）
5. `__init__.py` / `__main__.py`（导入和入口适配）

---

## 2. 文件级详细说明

## 2.1 `__init__.py`

核心作用：
- 对外暴露 `create_app`。
- **延迟导入** FastAPI 依赖，避免“仅导入包就触发 fastapi 缺失错误”。

当前行为要点：
- `__all__ = ["create_app"]`
- `create_app()` 内部再 `from .api import create_app as _create_app`

适用场景：
- 当某些 CLI 功能不需要 API 依赖时，仍能安全导入 `pyqmc.api`。

---

## 2.2 `__main__.py`

核心作用：
- 支持命令 `python -m pyqmc.api`。
- 内部转发到 `api_server.main()`。

这让 API 服务具备模块执行入口，便于调试和脚本化调用。

---

## 2.3 `api_server.py`

核心作用：
- API 进程入口（命令行参数解析 + uvicorn 启动）。

关键函数：
- `build_parser()`：定义 `--host/--port/--log-level/--reload`。
- `run_server(...)`：检查依赖，调用 `uvicorn.run(..., factory=True)`。
- `main(argv)`：命令行入口，异常转换为可读错误消息并返回退出码。

设计意图：
- 将“服务进程启动逻辑”与“路由定义逻辑”分离。
- 在依赖缺失时给出明确安装提示：`pip install -e '.[api]'`。

---

## 2.4 `api.py`

核心作用：
- FastAPI app factory。
- 注册中间件和路由。

关键点：
- `create_app() -> FastAPI`
- 配置 CORS（目前 `allow_origins=["*"]`，方便本地 GUI 和静态页面调试）。
- 当前路由：
  - `GET /health`
  - `GET /methods`
  - `GET /systems`
  - `POST /simulate/vmc/harmonic-oscillator`
  - `POST /benchmark/vmc/harmonic-oscillator`

分层原则：
- 路由函数应保持“薄”：
  - 接收 `models.py` 中的请求模型。
  - 调用 `service.py` 业务函数。
  - 将结果转换为响应模型。

---

## 2.5 `models.py`

核心作用：
- 定义 API 输入/输出契约（Pydantic 模型）。

当前模型分两类：

1. 请求模型（Request）
- `VmcHarmonicOscillatorRequest`
- `VmcHarmonicOscillatorBenchmarkRequest`

2. 响应模型（Response）
- `SimulationResultResponse`
- `MethodInfo`
- `SystemInfo`
- `BenchmarkCaseResponse`
- `BenchmarkSuiteResponse`

建模要点：
- 用 `Field(gt=..., ge=...)` 表达数值边界。
- 用 `@model_validator(mode="after")` 执行跨字段验证（例如 `burn_in < n_steps`）。

收益：
- 错误输入会自动返回 HTTP 422，减少业务层防御代码。

---

## 2.6 `service.py`

核心作用：
- API 层与后端计算层的“编排适配层”。

当前函数：
- `list_methods()`
- `list_systems()`
- `run_vmc_harmonic_oscillator(request)`
- `run_vmc_harmonic_oscillator_benchmark_suite(request)`

职责边界：
- **应该做**：
  - 将 API Request 模型映射为后端 `SimulationConfig` 等对象。
  - 调用 `pyqmc.core / pyqmc.vmc / pyqmc.benchmarks`。
- **不应该做**：
  - HTTP 细节（状态码、路由标签）。
  - GUI 逻辑。

---

## 3. 请求调用链（从 GUI 到后端）

以 GUI 中“运行 VMC”为例：

1. `src/pyqmc/gui/assets/app.js`
   - 组装 JSON payload。
   - 调用 `POST /simulate/vmc/harmonic-oscillator`。
2. `api.py` 路由接收请求，解析为 `VmcHarmonicOscillatorRequest`。
3. `service.py` 将请求映射到 `SimulationConfig`。
4. 调用 `pyqmc.vmc.solver.run_vmc_harmonic_oscillator(...)`。
5. 返回 `SimulationResult`。
6. `api.py` 将结果转换为 `SimulationResultResponse` 返回 GUI。

这个链路体现了“前端/UI 与计算核心解耦”。

---

## 4. 现有 API 使用示例

## 4.1 健康检查

```bash
curl -s http://127.0.0.1:8000/health
```

返回示例：

```json
{"status":"ok"}
```

## 4.2 运行 VMC 模拟

```bash
curl -s -X POST http://127.0.0.1:8000/simulate/vmc/harmonic-oscillator \
  -H "Content-Type: application/json" \
  -d '{
    "n_steps": 12000,
    "burn_in": 2000,
    "step_size": 1.0,
    "alpha": 0.95,
    "initial_position": 0.0,
    "seed": 7
  }'
```

## 4.3 运行基准测试

```bash
curl -s -X POST http://127.0.0.1:8000/benchmark/vmc/harmonic-oscillator \
  -H "Content-Type: application/json" \
  -d '{
    "n_steps": 12000,
    "burn_in": 2000,
    "step_size": 1.0,
    "initial_position": 0.0,
    "seed": 7
  }'
```

---

## 5. 新增 API 功能的标准步骤（强烈推荐）

假设要新增一个能力：`DMC Hydrogen`。

## Step 1：先实现后端计算能力（非 API 层）

在 `pyqmc.dmc` 中提供稳定函数，例如：
- `run_dmc_hydrogen(config) -> SimulationResult`

原则：
- 后端先跑通（CLI 或单测先验证）。

## Step 2：在 `models.py` 增加请求/响应模型

示例（节选）：

```python
class DmcHydrogenRequest(BaseModel):
    n_steps: int = Field(default=20000, gt=0)
    burn_in: int = Field(default=2000, ge=0)
    time_step: float = Field(default=0.01, gt=0)
    seed: int | None = 12345

    @model_validator(mode="after")
    def validate_burn_in(self) -> "DmcHydrogenRequest":
        if self.burn_in >= self.n_steps:
            raise ValueError("burn_in must be smaller than n_steps")
        return self
```

## Step 3：在 `service.py` 增加编排函数

示例（节选）：

```python
def run_dmc_hydrogen_service(request: DmcHydrogenRequest) -> SimulationResult:
    config = DmcConfig(
        n_steps=request.n_steps,
        burn_in=request.burn_in,
        time_step=request.time_step,
        seed=request.seed,
    )
    return run_dmc_hydrogen(config)
```

## Step 4：在 `api.py` 注册路由

示例（节选）：

```python
@app.post(
    "/simulate/dmc/hydrogen",
    response_model=SimulationResultResponse,
    tags=["simulate"],
)
def simulate_dmc_hydrogen(payload: DmcHydrogenRequest) -> SimulationResultResponse:
    result = run_dmc_hydrogen_service(payload)
    return SimulationResultResponse(**result.to_dict())
```

## Step 5：补齐测试

至少包含：
- `tests/integration/test_api.py`：
  - 正常输入返回 200。
  - 非法输入返回 422。
- `tests/integration/test_cli.py`（如果 CLI 也暴露该能力）。
- 相关单元测试（后端数值和配置验证）。

## Step 6：更新 GUI（如果前端需要）

- 修改 `src/pyqmc/gui/assets/app.js`：
  - 调整 payload 字段。
  - 调整 fetch URL。
  - 调整结果渲染字段。
- 若新增独立页面控件，同步更新 `index.html` 与 `styles.css`。

---

## 6. 修改已有 API 的实战指南

## 场景 A：新增一个请求参数

例：给 VMC 模拟新增 `proposal_mode`。

改动顺序：
1. `models.py`：给 `VmcHarmonicOscillatorRequest` 加字段与枚举/校验。
2. `service.py`：把字段传给后端配置对象。
3. 后端 solver/sampler：支持新参数。
4. `app.js`：提交新字段。
5. API/CLI 测试更新。

注意：
- 如果是破坏性变更（字段语义变化），建议新增 endpoint 或做兼容分支，不要直接让旧 GUI 失效。

## 场景 B：响应结构变化

例：新增 `autocorrelation_time`。

改动顺序：
1. 后端结果对象产出该值。
2. `SimulationResultResponse` 增加字段。
3. 路由返回自动包含新字段。
4. GUI 渲染逻辑增加显示（旧字段不删除，优先增量兼容）。

---

## 7. API 与 GUI 协同开发检查清单

每次改 API 前后，请检查：

- 路径是否和前端 fetch 一致。
- 请求字段名是否和前端 JSON 一致。
- 响应字段名是否和前端渲染一致。
- `model_validator` 是否覆盖关键跨字段约束。
- Swagger (`/docs`) 能否正确展示新模型。
- 集成测试是否覆盖成功/失败路径。

---

## 8. 调试与运行命令

启动 API：

```bash
pyqmc serve-api --host 127.0.0.1 --port 8000
```

或：

```bash
pyqmc-api --host 127.0.0.1 --port 8000
```

开发热重载：

```bash
pyqmc serve-api --reload
```

运行测试：

```bash
pytest
```

仅跑 API 集成测试：

```bash
pytest tests/integration/test_api.py
```

---

## 9. 代码风格建议（本项目语境）

- 路由函数保持薄，业务逻辑放 `service.py`。
- Request/Response 模型要完整、明确，避免返回“无结构 dict”。
- 新功能优先“加法式扩展”，减少对现有 GUI/客户端的破坏。
- 错误消息面向使用者，尽量具体（例如参数约束失败原因）。

---

## 10. 常见问题（FAQ）

## Q1：为什么不在 `api.py` 里直接拼配置并调用 solver？

A：可以，但会让路由层过重，后续维护困难。`service.py` 的存在让路由更稳定，也便于复用与测试。

## Q2：什么时候需要改 CORS？

A：当 GUI 或外部前端部署到特定域名时，建议把 `allow_origins=["*"]` 收紧为白名单。

## Q3：新增功能时，最容易漏掉哪一步？

A：最常见是“后端改了但模型没改”或“API 改了但 app.js 还在发旧字段”。建议每次按第 5 节步骤逐项执行。

