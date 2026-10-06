# Stage 6 售后环 · 三文鱼化冻投诉闭环演示记录

- 日期：2026-10-06
- 平台：mall-ai-after-sales-platform（FastAPI :8002 + Java mall 模拟器 :8085）
- LLM：DashScope 兼容端点 qwen-flash（DEEPSEEK_BASE_URL 替换方案）
- RAG：本地 bge-small-zh-v1.5（ModelScope 手动下载）+ Chroma 政策索引（15 块）
- 会话：cc272324-e8a4-4220-986b-807428a32416

## 演示轮次（用户：salmon_user / 订单 20260922001）

| # | 用户输入 | 系统行为 | 关键产物 |
|---|---------|---------|----------|
| 1 | 「三文鱼刺身到货冰袋全化了…要求退货退款」 | 意图路由 apply_after_sales → 建草稿；订单号误提取(20260922001)未命中→按设计请求澄清 | draft_id=316c1eb0, missing_fields=[order_sn] |
| 2 | 「订单号：20260922001」 | 订单+物流+库存三源核验（mock Java facts）+ 政策RAG命中「七天无理由退货」 | verified_facts×4, evidence_status=complete |
| 3 | 「继续办理，质量问题退货退款」 | 资格核验通过(eligible_to_apply)，但政策库无「生鲜质量问题退货」依据 → **接地拦截，转人工**（正当拒绝，防幻觉） | eligibility=eligible, answer=建议人工 |
| 4 | 「订单…质量问题…申请换货」（新会话） | 换货政策有依据 → 方案生成 status=awaiting_confirmation + 政策说明 | after_sales_proposal |
| 5 | 「确认提交」 | 事务门放行 → Java 写权威 POST /after-sales/ai/applications（幂等键 599fe6ea…）→ 进入 submission_unknown | 事务性提交(ADR-0006) |
| 6 | 「确认」 | 幂等核实 GET /after-sales/ai/submissions/{key} → status=created | application_id=90001, 待审核 |

## 平台治理要点（演示中实际触发）

- **Provider Guard**：fail-closed 外呼授权，live 模式需 release/batch/ledger/commit 四件套
- **接地生成**：RAG 证据不足时不生成方案（生鲜退货退款正当拒绝）
- **Java 唯一写权威**（ADR-0001）：AI 只读+提案，写入经事务门+幂等核实
- **不臆造**：订单号错误时请求澄清而非编造

## 启动命令

```powershell
# 1. FastAPI 服务
cd mall-ai-after-sales-platform/mall-ai-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
# 2. Java mall 模拟器
.\.venv\Scripts\python.exe ..\..\salmon-ecommerce-pipeline\mock_mall_java.py
# 3. 登录 → POST /auth/login {"username":"salmon_user","password":"salmon123"}
# 4. 对话 → POST /customer-service {message, session_id(UUID), Authorization}
```

## 排障记录（本次修复清单）

1. `_agent_reasoning_control` 注入 DeepSeek 专有 thinking 参数 → DashScope 400 → 端点判断后跳过
2. fastembed 下载源 storage.googleapis.com 被墙 → ModelScope 手动下载 model.onnx 重命名 model_optimized.onnx
3. 中间件 mode 读 `MALL_RUNTIME_PROVIDER_MODE`（非 MALL_PROVIDER_MODE）→ 补环境变量
4. session_id 必须 UUID；订单号提取只认纯数字（≥6位）
5. mock 契约对齐：eligibility 视图、application 视图（+canCancel/canModify）、submissions 响应 `{status:"created", application:{…}}`、status 枚举 pending_review
