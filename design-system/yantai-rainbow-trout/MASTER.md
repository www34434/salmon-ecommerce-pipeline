# 烟台虹鳟 · 品牌专属设计系统 MASTER

> **逻辑：** 构建具体页面时，先查 `pages/[page].md` 是否存在；存在则覆盖本文件规则，否则严格遵循本文件。

---

**品牌：** 烟台虹鳟（山东烟台 · 深海虹鳟三文鱼）
**品类：** 高端生鲜电商
**生成：** 2026-10-08
**设计调节器：** Variance 5/10（平衡现代）| Motion 4/10（标准）| Density 5/10（标准）

---

## 品牌故事锚点

| 锚点 | 设计映射 |
|---|---|
| 山东烟台 · 黄海深海 | 深海蓝 `#0E1223` + 黑金奢华 |
| 虹鳟三文鱼·粉橙肌理 | 三文鱼橙 `#C2410C` 品类点睛 |
| 液氮急冻锁鲜 | 鲜绿 `#059669` 冷链标识 |
| 刺身级·高端体验 | Liquid Glass 玻璃拟态 + Cormorant 衬线 |

---

## 全局规则

### 一、三层色 Token

#### Layer 1 — Primitive（不可变原子色）

| Token | HEX | 用途 |
|---|---|---|
| `--primitive-black` | `#0C0A09` | 最深文字 |
| `--primitive-charcoal` | `#1C1917` | 主背景深色 |
| `--primitive-stone` | `#44403C` | 次级深色 |
| `--primitive-gold` | `#A16207` | 品牌金 |
| `--primitive-salmon` | `#C2410C` | **三文鱼橙（品类标识）** |
| `--primitive-deepsea` | `#0E1223` | **深海蓝（产地氛围）** |
| `--primitive-fresh` | `#059669` | **鲜绿（冷链锁鲜）** |
| `--primitive-white` | `#FFFFFF` | 纯白 |
| `--primitive-ivory` | `#FAFAF9` | 暖底 |
| `--primitive-muted` | `#E8ECF0` | 灰阶 |

#### Layer 2 — Semantic（语义映射）

| 语义 Token | 映射 Primitive | CSS 变量 |
|---|---|---|
| 品牌主色（Primary） | `--primitive-charcoal` | `--color-primary` |
| 品牌金色（Accent/CTA） | `--primitive-gold` | `--color-accent` |
| **品类标识色（Salmon）** | `--primitive-salmon` | `--color-salmon` |
| **产地氛围色（Deepsea）** | `--primitive-deepsea` | `--color-deepsea` |
| **冷链锁鲜色（Fresh）** | `--primitive-fresh` | `--color-fresh` |
| 页面背景 | `--primitive-ivory` | `--color-background` |
| 卡片背景 | `--primitive-white` | `--color-card` |
| 正文前景 | `--primitive-black` | `--color-foreground` |
| 次级前景 | `--primitive-stone` | `--color-muted-foreground` |

#### Layer 3 — Component（组件级）

| 组件 | 色值 | 说明 |
|---|---|---|
| CTA 主按钮 | `--color-salmon` + 白字 | **三文鱼橙做 CTA，比金色更有品类识别** |
| Hero 徽章 | `--color-fresh` + 白字 | "液氮急冻" 徽章用鲜绿 |
| 产地标签 | `--color-deepsea` + 白字 | "山东烟台" 标签用深海蓝 |
| 评分聚合 | `--color-gold` | 4.5★ 金色，延续奢侈品感 |
| 价格数字 | `--color-salmon` tabular-nums | 价格用三文鱼橙，一眼抓住 |

### 二、字体系统

| 用途 | 字体 | Weight | 来源 |
|---|---|---|---|
| 标题/品牌名 | **Cormorant** | 500-700 | Google Fonts |
| 正文/按钮 | **Montserrat** | 400-600 | Google Fonts |
| 数字/价格 | Montserrat + `tabular-nums` | 600 | 等宽对齐价格 |

```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');
```

| 层级 | Size | Line-Height | Weight |
|---|---|---|---|
| Hero 标题 | 48-64px | 1.1 | Cormorant 700 |
| Section 标题 | 32-40px | 1.2 | Cormorant 600 |
| 卡片标题 | 20-24px | 1.3 | Montserrat 600 |
| 正文 | 16px | 1.5 | Montserrat 400 |
| 辅助文字 | 14px | 1.5 | Montserrat 300 |
| 价格 | 28-36px | 1.2 | Montserrat 700 tabular-nums |

### 三、间距系统（Density 5/10 标准）

| Token | 值 | 用途 |
|---|---|---|
| `--space-xs` | 4px | 图标间隙 |
| `--space-sm` | 8px | 内联间距 |
| `--space-md` | 16px | 标准 padding |
| `--space-lg` | 24px | 区块内 padding |
| `--space-xl` | 32px | 大间距 |
| `--space-2xl` | 48px | 区块 margin |
| `--space-3xl` | 64px | Hero padding |

### 四、阴影深度

| Level | 值 | 用途 |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | 轻微悬浮 |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.08)` | 卡片/按钮 |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.12)` | 弹窗/下拉 |
| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Hero 图片/特色卡 |

---

## 风格：Liquid Glass 玻璃拟态

| 项 | 规范 |
|---|---|
| 关键词 | 动态材质 · 光学玻璃 · 半透明 · 透镜折射 · 流体形变 |
| 最佳场景 | Apple 风格导航 · 控件 · 生鲜"新鲜透亮"质感 |
| 性能成本 | 中等（blur + animation）|
| 可访问性风险 | 条件性（需 4.5:1 对比 + 键盘导航 + 可见 focus）|
| **安卓降级** | 不支持 `backdrop-filter` 时 → 半透明纯色 `rgba(255,255,255,0.85)` |

---

## 页面 Pattern：Feature-Rich Showcase

**Section 顺序**（落地页 Hero + Features + Testimonials + CTA）：

```
Hero（价值主张 + 产地徽章 + 浮动价卡）
  ↓
产地溯源卡组（山东烟台 + 冷链时间轴）
  ↓
核心卖点卡（刺身级 · 液氮急冻 · 源产地直送）
  ↓
评分聚合（4.45★ / 69,338 条 + 正负反馈对比）
  ↓
限时库存 CTA（渐变背景 + 立即下单）
  ↓
Footer（烟台深海虹鳟 · 产地溯源链接）
```

**CTA 位置**：Hero（sticky）+ Features 后 + 底部

---

## 组件规范

### CTA 主按钮（三文鱼橙）

```css
.btn-primary {
  background: var(--color-salmon);
  color: #FFFFFF;
  padding: 14px 32px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}
.btn-primary:hover {
  opacity: 0.92;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

### 产地标签（深海蓝）

```css
.tag-origin {
  background: var(--color-deepsea);
  color: #FFFFFF;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
```

### 鲜度徽章（鲜绿）

```css
.badge-fresh {
  background: var(--color-fresh);
  color: #FFFFFF;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}
```

### 玻璃卡（Liquid Glass）

```css
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 28px;
  box-shadow: var(--shadow-lg);
  transition: all 250ms ease;
}
/* 安卓降级 */
@supports not (backdrop-filter: blur(12px)) {
  .glass-card { background: rgba(255, 255, 255, 0.92); }
}
.glass-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-xl);
}
```

### 价格数字

```css
.price {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  color: var(--color-salmon);
  font-size: 32px;
  font-variant-numeric: tabular-nums;
}
```

---

## 动效

**Stagger List（标准 4/10）** — 触发：加载/滚动 | 时长：300-450ms | 缓动：`back.out(1.4)`

```js
gsap.from('.grid-item', {
  opacity: 0, scale: 0.92, y: 16,
  duration: 0.4,
  stagger: { each: 0.06, from: 'start', grid: 'auto' },
  ease: 'back.out(1.4)'
});
// 尊重减少动效偏好
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  gsap.set('.grid-item', { opacity: 1, y: 0 });
}
```

✅ 可与 `from: 'center'` 配合做 bento-grid 聚焦视线
❌ 不要在密集数据表格上用 back.out 过冲

---

## 反模式（严禁）

| ❌ | 原因 | 替代 |
|---|---|---|
| 表情符号当图标 | 奢侈品级品牌调性不符 | Lucide/Heroicons SVG `stroke="currentColor"` |
| 纯金色 CTA 按钮 | 金色用于评分/徽章，CTA 用三文鱼橙更有品类识别 | `.btn-primary` 用 `--color-salmon` |
| 跳过产地/冷链信息 | 生鲜信任核心 | Hero + 溯源卡 + 时间轴必须完整 |
| 文本 < 12px 正文 | 可访问性 | 最低 14px |
| 原始 Hex 直接写组件 | 破坏 token 一致性 | 必须用 CSS 变量 |
| 移动端禁止缩放 | 无障碍违规 | 保留 viewport 缩放 |

---

## 交付前检查清单

- [ ] 无 emoji 图标（用 Lucide/Heroicons SVG）
- [ ] `cursor-pointer` 所有可点击元素
- [ ] Hover 状态过渡 150-300ms
- [ ] 浅色模式文本对比 4.5:1+
- [ ] Focus 状态键盘可见
- [ ] `prefers-reduced-motion` 已尊重
- [ ] 响应式：375 / 768 / 1024 / 1440px
- [ ] 无固定导航后被遮挡内容
- [ ] 移动端无水平滚动
- [ ] 图片 `loading="lazy"` + 预留宽高（CLS < 0.1）
- [ ] 玻璃卡安卓降级已做（`@supports not backdrop-filter`）
