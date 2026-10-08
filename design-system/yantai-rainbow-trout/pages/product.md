# 烟台虹鳟 · 产品详情页 Override

> 本文件覆盖 MASTER.md 规则，仅适用于产品详情页（`product.html`）

---

## 页面信息

**页面：** 产品详情页（PDP）
**Pattern：** Product Demo + Ratings Focused（左大图 + 右信息 + 评分区 + 冷链时间轴 + CTA）
**设备：** 移动优先（375px → 桌面 1440px）

---

## 页面结构

```
固定顶栏（同首页）
  ↓
1. 面包屑导航（烟台虹鳟 · 刺身级 · 冰鲜虹鳟刺身）
  ↓
2. 主图区（左：大图 + 缩略图；右：标题 + 价格 + 标签 + CTA）
  ↓
3. 规格选择（重量规格：300g/400g/500g + 切法：刺身/切片/切块）
  ↓
4. 评分聚合（4.45★ / 69,338 条 + 正负反馈）
  ↓
5. 冷链时间轴（复用首页时间轴 + 温度实时记录）
  ↓
6. 产地溯源卡（烟台主产地 + 批次码查询）
  ↓
7. Footer
```

---

## 主图区

| 项 | 规范 |
|---|---|
| 布局 | 桌面：左 56% 大图 + 右 44% 信息；移动：单列堆叠 |
| 主图 | 白底主图v2.jpg，`object-fit:contain`，占满左区高度 |
| 缩略图 | 3-4 张，点击切换主图；移动端横向滚动 |
| 主图尺寸 | 桌面 560×560 / 移动 320×320 |

### 右侧信息区

| 元素 | 样式 |
|---|---|
| 标题 | Cormorant 700 28-32px `--color-primary` |
| 副标题 | Montserrat 400 14px `--color-muted-foreground` |
| 价格 | `.price` 类：Montserrat 700 `--color-salmon` tabular-nums |
| 原价 | 划线 `text-decoration:line-through` `--color-muted-foreground` |
| 折扣 | `--color-fresh` 徽章：限时/产地/急冻 |
| 标签 | `tag-origin` 深海蓝 "烟台·黄海深海" + `badge-fresh` 鲜绿 "液氮急冻" |
| 评分 | 金色 `--color-accent` tabular-nums 4.45★ + 69,338 条 |

### CTA 区

| 按钮 | 样式 |
|---|---|
| 立即购买（主） | `.btn-primary`（三文鱼橙）|
| 加入购物车 | 半透明描边按钮 `border:2px solid var(--color-primary)` |
| 加入收藏 | 图标按钮（心形 SVG `stroke="currentColor"`）|

---

## 规格选择

### 重量规格（radio group）

```
○ 300g  ¥128
● 400g  ¥158  ← 默认选中（三文鱼橙边框 + 背景）
○ 500g  ¥198
```

| 态 | 样式 |
|---|---|
| 默认 | `border:1px solid var(--color-border); background:var(--color-card)` |
| 选中 | `border:2px solid var(--color-salmon); background:rgba(194,65,12,0.05)` |
| Hover | `border:1px solid var(--color-primary)` |

### 切法选择

| 选项 | 说明 |
|---|---|
| 刺身 | 1-2cm 厚切 · 保留肌理 |
| 切片 | 0.5cm 薄片 · 方便摆盘 |
| 切块 | 3cm 方块 · 适合烹饪 |

### 数量选择器

```
[−]  1  [+]
```
- 数字 tabular-nums，输入框居中
- 最小 1，最大 10
- 步进器用 SVG 图标按钮

---

## 评分聚合区

| 项 | 规范 |
|---|---|
| 布局 | 左评分总览 + 右正负反馈对比 |
| 总评分 | Cormorant 700 48px `--color-accent` tabular-nums 4.45★ |
| 评论数 | Montserrat 500 16px 69,338 条真实评价 |
| 分布 | 5★/4★/3★/2★/1★ 条形图（横向填充）|
| 正反馈 | `--color-fresh` 绿色圆点 + 文字 |
| 负反馈 | `--color-salmon` 橙色圆点 + 文字 |

### 评分分布条形图

```
5★ ████████████████████ 62%
4★ ██████████████        23%
3★ █████                  8%
2★ ███                    4%
1★ █                      3%
```
- 条形高 8px，圆角 4px
- 填充色：5★ `--color-fresh` → 1★ `--color-salmon` 渐变

---

## 产品详情专属反模式

| ❌ | 原因 |
|---|---|
| 跳过规格选择 | 高端生鲜必须给重量/切法选项 |
| 价格不用 tabular-nums | 价格数字不对齐，显得不专业 |
| 缩略图点击无反馈 | Active 态必须有视觉指示（参考 UX 搜索 Result 2）|
| CTA 只有一个按钮 | 高端电商至少"立即购买"+"加入购物车"双 CTA |
| 冷链时间轴简略 | 生鲜信任核心，PDP 必须完整展示温度记录 |
| 图片不懒加载 | UX 搜索 Result 1：大图会拖慢 PDP 首屏 |
