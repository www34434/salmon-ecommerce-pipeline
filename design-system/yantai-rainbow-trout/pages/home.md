# 烟台虹鳟 · 首页 Override

> 本文件覆盖 MASTER.md 规则，仅适用于首页（`index.html`）

---

## 页面信息

**页面：** 落地首页
**Pattern：** Hero + Features + Testimonials + CTA（Feature-Rich Showcase）
**设备：** 移动优先（375px → 桌面 1440px）

---

## Hero 区域（第一屏）

| 项 | 规范 |
|---|---|
| 高度 | 移动端 100vh / 桌面 80vh |
| 背景 | 深海渐变 `linear-gradient(135deg, #0E1223 0%, #1C1917 50%, #0E1223 100%)` |
| 主图 | 三文鱼产品图（白底主图v2.jpg），`object-fit: cover` + 底部蒙层 `linear-gradient(transparent, rgba(12,10,9,0.7))` |
| 标题 | **"山东烟台·深海虹鳟"** — Cormorant 700 48px 白字 |
| 副标题 | **"一口黄海的原生三文鱼"** — Montserrat 400 18px 浅金 `#CA8A04` |
| 产地徽章 | `tag-origin` "烟台·黄海深海" 叠在主图左上角 |
| 浮动价卡 | 玻璃卡 `glass-card` + `.price` "¥128" + "烟台冰鲜虹鳟刺身 300g" + `.btn-primary` "立即下单" |

### Hero 布局（移动端优先）

```
┌─────────────────────────┐
│ [烟台·黄海深海]          │  ← tag-origin 左上
│                         │
│    🐟 三文鱼主图         │  ← object-fit:cover
│                         │
│  山东烟台·深海虹鳟       │  ← Cormorant 700 48px
│  一口黄海的原生三文鱼     │  ← Montserrat 18px #CA8A04
│                         │
│ ┌───────────────────┐   │
│ │ ¥128 tabular-nums │   │  ← .glass-card 浮动价卡
│ │ 烟台冰鲜虹鳟刺身   │   │
│ │ [立即下单] 橙按钮  │   │
│ └───────────────────┘   │
└─────────────────────────┘
```

---

## 产地溯源卡组（第二屏）

| 项 | 规范 |
|---|---|
| 布局 | Grid：移动端单列 → 桌面 3 列 |
| 卡片 | `glass-card` + 国旗 SVG + 鲜度进度条（.fresh-bar） |
| 主产地卡（大） | "山东烟台 · 黄海深海" + 60% 占比 + `.badge-fresh` "液氮急冻" + 溯源查询入口 |
| 副产地卡（2） | "挪威峡湾" 30% + "阿拉斯加" 10% |

### 鲜度进度条

```css
.fresh-bar {
  height: 6px;
  background: #E8ECF0;
  border-radius: 3px;
  overflow: hidden;
}
.fresh-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-fresh), var(--color-salmon));
  border-radius: 3px;
}
```

---

## 冷链时间轴（第三屏）

| 阶段 | 图标 | 文字 | 颜色 |
|---|---|---|---|
| 深海捕捞 | 🌊 → Lucide `anchor` | 烟台黄海 · 40m 深海 | `--color-deepsea` |
| 液氮急冻 | ❄️ → Lucide `thermometer-snowflake` | -196℃ · 3 分钟锁鲜 | `--color-fresh` |
| 干冰运输 | 🚚 → Lucide `truck` | 干冰冷链 · 全程 -18℃ | `--color-gold` |
| 蓄冷箱交付 | 📦 → Lucide `package-check` | 蓄冷箱 · 48h 直达 | `--color-salmon` |

时间轴线：渐变 `linear-gradient(90deg, #059669, #C2410C)`

---

## 评分聚合（第四屏）

| 项 | 规范 |
|---|---|
| 左侧 | 核心卖点图（key_features.jpg） |
| 右侧上 | `.price` 4.45★（金色 `#A16207` tabular-nums） + Montserrat 600 "69,338 条真实评价" |
| 右侧中 | 正负反馈对比（2 列） |
| 右侧下 | `.btn-primary` "查看完整评价" |

### 正负反馈对比

| 正反馈（鲜绿 `#059669`） | 负反馈（三文鱼橙 `#C2410C`）|
|---|---|
| 刺身级口感 | 化冻痕迹 |
| 产地溯源可查 | 冷链断链（Stage 6 回流）|
| 急冻锁鲜到位 | — |

---

## CTA 限时库存（第五屏）

| 项 | 规范 |
|---|---|
| 背景 | 渐变 `linear-gradient(135deg, #1C1917 0%, #0E1223 100%)` |
| 标题 | Cormorant 700 "限时库存" + `.badge-fresh` "今日新捕" |
| 库存数 | Montserrat 700 tabular-nums "1,240 份" + `--color-salmon` |
| 4 条保障 | SVG 图标 + Montserrat 400：产地溯源 / 液氮急冻 / 48h 直达 / 不满意退 |
| CTA | `.btn-primary` 大字 "立即下单 · ¥128 起" |

---

## Footer

| 项 | 规范 |
|---|---|
| 品牌名 | "烟台深海虹鳟" — Cormorant 600 |
| 链接 | 产地溯源 / 冷链保障 / 售后政策 / 关于我们 |
| 产地标签 | `tag-origin` "山东烟台 · 黄海深海" |
| 版权 | "© 2026 烟台虹鳟 · 产地直供" |

---

## 首页专属反模式

| ❌ | 原因 |
|---|---|
| Hero 跳过产地徽章 | 烟台产地是核心差异化 |
| 冷链时间轴省略某阶段 | 生鲜信任链不能断 |
| CTA 用金色按钮 | 首页 CTA 必须三文鱼橙，品类识别 |
| 浮动价卡仅桌面显示 | 移动端也要有 sticky 或浮动 CTA |
| 图片无 loading="lazy" | CLS 会破坏 Lighthouse 分数 |
