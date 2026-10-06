---
name: salmon-ecommerce-pipeline
version: 1.0.0
description: >
  三文鱼电商全链路编排 Skill。将 6 个独立 Skill 串联成一条从找品到售后的完整流水线，
  专攻三文鱼产业。当用户说「跑三文鱼全链路」「从找品到售后跑一遍」「三文鱼电商流水线」、
  或需要把找品/数据/运营/图片/广告/售后六环打通时触发。
  六环分别由 ecommerce-skills(找品)、apify-mcp-server(数据)、DeskcommCRM(运营)、
  ecommerce-image-suite(图片)、Generative-Media-Skills(广告)、mall-ai-after-sales-platform(售后) 承担。
metadata:
  stages:
    - "找品: ecommerce-skills"
    - "数据: apify-mcp-server"
    - "运营: DeskcommCRM"
    - "图片: ecommerce-image-suite"
    - "广告: Generative-Media-Skills"
    - "售后: mall-ai-after-sales-platform"
  industry: "salmon / 三文鱼"
---

# 三文鱼电商全链路流水线

## 概览

本 Skill 是 6 个 Skill 的「总调度」。它不替代任何单环能力，而是定义环与环之间的数据契约，
让上一环的产物成为下一环的输入，形成一条可落地的三文鱼电商流水线：

```
①找品 ──candidates──▶ ②数据 ──intel──▶ ③运营 ──plan──▶ ④图片 ──images──▶ ⑤广告 ──creatives──▶ ⑥售后
```

| 环 | 承担仓库 | 目录 | 核心接口 | 产出 |
|----|----------|------|----------|------|
| ① 找品 | ecommerce-skills | `../ecommerce-skills` | Cart MCP: `search_products` `get_trending`；Skill: `/product-research` `/trend-alert` `/niche-analysis` `/supplier-finder` | candidate_products.json |
| ② 数据 | apify-mcp-server | `../apify-mcp-server` | MCP tools: `call-actor` `get-dataset-items`；Actor: 电商/社媒爬虫 | competitive_intel.json |
| ③ 运营 | DeskcommCRM | `../DeskcommCRM` | MCP endpoint `app/api/mcp/route.ts` + REST `/api/v1/*` | operation_plan.json |
| ④ 图片 | ecommerce-image-suite | `../ecommerce-image-suite` | `scripts/check_providers.py` → `analyze.py` → `generate.py` | image_set/ |
| ⑤ 广告 | Generative-Media-Skills | `../Generative-Media-Skills` | MCP 19 tools + Recipe: `ad-creative` `product-video-ad-maker` `ugc-ads-workflow` | ad_creatives/ |
| ⑥ 售后 | mall-ai-after-sales-platform | `../mall-ai-after-sales-platform` | FastAPI Runtime + Skill 白名单 + Java 写入 + `mall-ai-service/app/services/mcp` | after_sales闭环 |

## 运行前提

| 模块 | 必需凭证 / 服务 | 获取路径 |
|------|-----------------|----------|
| 找品 | `CART_API_KEY` + Cart MCP (`@usecart/mcp-server`) | usecart.com/developers |
| 数据 | `APIFY_TOKEN`（或 OAuth mcp.apify.com） | apify.com |
| 运营 | DeskcommCRM 实例（Supabase + Next.js），自托管 | `../DeskcommCRM` 启动 |
| 图片 | `DASHSCOPE_API_KEY`（推荐）或 `ARK_API_KEY` 等 | 阿里云/火山引擎 |
| 广告 | 图像/视频生成 Provider Key（同图片环节可复用） | 见 Generative-Media-Skills README |
| 售后 | Docker Desktop + Provider Key；mall 平台启动 | `../mall-ai-after-sales-platform/scripts/Prepare-PublicDemo.ps1` |

> 未配置凭证的环将进入「模拟模式」：编排器读取该环的产物模板占位，不阻塞后续环。

## 编排流程

执行本 Skill 时，按以下顺序逐环推进，每环产出落盘到 `pipeline-run/<run_id>/` 下，供下一环消费。

### Stage 1 · 找品（Product Discovery）

**目标**：发现高潜力三文鱼 SKU、趋势品、细分赛道与货源。

1. 调 `/product-research salmon`（或 `三文鱼`、`smoked salmon`、`salmon sashimi`）：取 top 20-50 商品、价格分布、卖家集中度、差异化空间。
2. 调 `/trend-alert`：取三文鱼当前 trending SKU、增速最快店铺、新兴细分（如即食三文鱼、宠物三文鱼零食、冷烟熏）。
3. 调 `/niche-analysis salmon`：市场规模、竞争等级、进入难度、机会分。
4. 调 `/supplier-finder salmon`：三文鱼货源/代发/POD 供应商（挪威、智利、阿拉斯加源头）。

**数据契约 → 下一环**：`candidate_products.json`
```json
{
  "keyword": "salmon",
  "candidates": [{"sku":"...","title":"...","price":0,"store":"...","trending":true,"velocity":"..."}],
  "pricing": {"min":0,"max":0,"median":0,"common":[]},
  "vendors": [{"name":"...","product_count":0}],
  "suppliers": [{"name":"...","origin":"Norway/Chile/Alaska","type":"dropship/wholesale"}],
  "opportunity_score": 0,
  "recommended_focus": "即食鲜切三文鱼 / 冷烟熏三文鱼 / 三文鱼边角料"
}
```

### Stage 2 · 数据（Data Extraction）

**目标**：用 Apify Actors 抓取竞品三文鱼店铺的多平台运营数据（价格、评价、广告、供应链信号）。

1. `search-actors` 检索三文鱼相关爬虫：Amazon Product、Google Shopping、Instagram、Facebook Posts、Google Maps（线下水产市场）。
2. `call-actor` 运行选定 Actor，输入由 Stage 1 给出的竞品域名/关键词/ASIN。
3. `get-dataset-items` 拉取结果：价格趋势、评价分布、负面词云（新鲜度/化冻/异味）、广告投放素材。

**数据契约 → 下一环**：`competitive_intel.json`
```json
{
  "competitors": [{"domain":"...","traffic":"...","top_skus":[...],"price_range":[0,0]}],
  "reviews": {"avg":0,"negatives":["不新鲜","化冻","包装破损"],"positives":[...]},
  "ad_activity": [{"platform":"Facebook/Instagram","creative":"...","duration":"..."}],
  "supply_chain_signals": {"origin_concentration":"Norway 60% / Chile 30%","cold_chain_tech":"..."}
}
```

### Stage 3 · 运营（Business Operation）

**目标**：把找品+数据结论沉淀进 CRM，建立销售漏斗、联系人、任务与商品目录。

通过 DeskcommCRM 的 MCP endpoint（`app/api/mcp/route.ts`）或 REST `/api/v1/*`：
1. 创建商品目录：候选三文鱼 SKU 入库（products）。
2. 建销售漏斗阶段：测款→爆款→复购，配阶段（stages）。
3. 录联系人：货源供应商、带货 KOL、线下水产档口（contacts）。
4. 拆任务：测款上架、定价策略、备货补货、差评处置（tasks）。

**数据契约 → 下一环**：`operation_plan.json`
```json
{
  "selected_skus": [{"sku":"...","title":"...","target_price":0,"stage":"测款/爆款"}],
  "funnel_stages": ["测款","爆款","复购"],
  "contacts": [{"name":"...","role":"supplier/kol/wholesale"}],
  "tasks": [{"title":"...","owner":"...","due":"...","priority":"high"}],
  "kpi": {"target_gmv":0,"target_conv":0,"repurchase_rate":0}
}
```

### Stage 4 · 图片（Product Image）

**目标**：为选定 SKU 生成符合平台规范的电商套图（白底主图、卖点图、刺身摆盘场景图、详情图）。

1. `python3 ../ecommerce-image-suite/scripts/check_providers.py` 校验图像生成 Key（首选 `DASHSCOPE_API_KEY`）。
2. `analyze.py` 对三文鱼实物图做视觉分析 → `product.json`（主体、卖点、配色）。
3. `generate.py` 生成套图，三文鱼重点图型：
   - `white_bg` 白底主图（电商首图）
   - `selling_pt` 卖点图（「挪威原切」「-196℃急冻」「刺身级」）
   - `lifestyle` 场景图（刺身摆盘、烟熏三文鱼早餐、健身餐）
   - `ecommerce_detail` 详情页（产地溯源、冷链、检测报告）
4. 平台规范：国内（淘宝 800×800、抖音 1080×1080）/ 跨境（Amazon 2000×2000、独立站）。

**数据契约 → 下一环**：`image_set/` 目录 + `image_manifest.json`
```json
{"images":[{"type":"white_bg","path":"...","platform":"taobao"},{"type":"lifestyle","path":"..."}]}
```

### Stage 5 · 广告（Advertising）

**目标**：基于套图产出广告创意素材包（主图+文案变体+商品视频广告+UGC 种草）。

调用 Generative-Media-Skills 的 Recipe Pack（经 MCP 或 CLI）：
1. `ad-creative`：输入三文鱼商品+受众（健身/宝妈/日料爱好者）+目标+调性 → 主图、文案变体、多平台裁剪。
2. `product-video-ad-maker`：从三文鱼套图 → 高端商业视频广告。
3. `ugc-ads-workflow`：真人/产品图 → UGC 风格短视频 + 脚本（种草抖音/小红书）。
4. 可选 `cinematic-product-ad`：电影感 5-10s 三文鱼广告。

**数据契约 → 下一环**：`ad_creatives/` + `ad_manifest.json`
```json
{"creatives":[{"type":"main_image","path":"...","copy":"..."},{"type":"video","path":"...","duration":15,"platform":"douyin"}]}
```

### Stage 6 · 售后（After-sales）

**目标**：处理三文鱼特有的售后（新鲜度争议、化冻、包装破损、缺重），并引导复购。

通过 mall-ai-after-sales-platform（FastAPI Runtime + Java 写入）：
1. 客户自然语言「三文鱼到货化冻了/不新鲜」→ Agent Runtime 调查订单与政策事实。
2. 版本化政策 RAG 给出退换规则（生鲜品类特例：化冻≤X% 可补发，超阈值全额退）。
3. 生成 ActionProposal（补发/退款/优惠券）→ 用户确认 → Java 重校验 → 幂等写入。
4. 复购引导：基于售后画像推送「刺身级复购券」「会员周期购」。
5. 能力延伸：暂停恢复、事实变化重规划（订单状态变了让旧方案失效）。

**产出**：`after_sales_report.json`（工单闭环 + 复购建议 + 负面词云回流到 Stage 2）

## 负反馈闭环

售后环的负面词云与复购数据回流到 Stage 2 数据环，形成持续优化闭环：
```
⑥售后 ──负面词云/复购画像──▶ ②数据（下一轮竞品/选品校准）
```

## 运行方式

```bash
# 一键跑全链路（未配凭证的环走模拟模式）
python3 run_pipeline.py --keyword "salmon" --industry salmon

# 只跑指定环
python3 run_pipeline.py --keyword "salmon" --stages sourcing,data

# 查看各环状态与凭证要求
python3 run_pipeline.py --check
```

产出目录结构：
```
pipeline-run/<run_id>/
├── candidate_products.json     # Stage 1
├── competitive_intel.json      # Stage 2
├── operation_plan.json         # Stage 3
├── image_set/                  # Stage 4
├── ad_creatives/                # Stage 5
└── after_sales_report.json     # Stage 6
```

## 三文鱼产业高价值情报锚点

跑全链路时，每环都应优先输出以下三文鱼独家商业信息（来自系统人设）：
- 全球三文鱼供需动态（挪威/智利/阿拉斯加产量、配额）
- 进出口关税与冷链技术趋势
- 消费口味偏好变化（刺身级 vs 烟熏 vs 即食）
- 高利润衍生品方向（三文鱼油、宠物零食、预制寿司卷）
- 成本结构（不同细分：整鱼 vs 鱼柳 vs 边角料）
