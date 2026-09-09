---
name: ui-slice-extractor
description: 从单张无图层 PNG/JPG/UI 截图中，逆向识别并重建前端可用的静态资源包。适用于用户提供一张设计图，希望自动找出 logo、icon、背景图、装饰图、组件壳等切图资产，并根据资产类型选择裁切、SVG 重绘、脚本重建、生图重建、透明化、校验、预览和打包的场景。
---

# UI 切图资产提取 Skill v3｜混合重建版

## 0. 核心前提

用户通常只会提供一张 **扁平 PNG / JPG / 截图**。

没有 Figma 图层。  
没有 PSD 图层。  
不能真正“导出图层”。

所以这个 Skill 的任务不是简单裁切，而是：

> 视觉理解整张扁平图 → 推断隐藏的 UI 层级 → 找出所有可复用资产 → 为每个资产选择最合适的重建方式 → 输出前端可直接引用的静态资源包。

一句话：  
**这不是截图裁剪，而是从像素里逆向重建设计资产。**

---

## 1. 这个 Skill 什么时候使用

当用户表达类似需求时，使用本 Skill：

- “我只给你一张 png，没有图层结构”
- “从这张设计图里切出所有小图”
- “帮我形成一个前端静态资源包”
- “logo、icon、背景图、组件壳都帮我拆出来”
- “SVG 复刻不出来的可以用生图模型生成”
- “生图后再透明化”
- “我要真透明 PNG，不要棋盘格”
- “不要漏掉小叶子、小星星、小装饰”
- “类似 UI 切图，但只能靠视觉理解”

---

## 2. 最终交付标准

默认输出一个完整资源包：

```text
ui-slice-output/
  icons/                 # 图标、logo、状态小图
  backgrounds/           # 页面背景、模块背景、背景-only 图
  overlays/              # 真透明装饰层，如叶子、星星、光晕、相机装饰组
  components/            # 组件外壳，如卡片壳、虚线框背景
  previews/              # 预览图
  manifest.json          # 资源清单
  validation-report.json # 校验报告
  README.md              # 使用说明
  asset_pack.zip         # 打包文件
```

---

## 3. 关键原则：不要只裁图，要判断“生产路径”

每一个候选资产都必须被分配到下面 5 条路径之一：

1. `crop_or_isolate`：直接裁切 / 简单抠出
2. `svg_redraw`：SVG 矢量重绘
3. `scripted_rebuild`：用代码/矢量脚本重建
4. `imagegen_then_transparentize`：生图重建后透明化
5. `background_reconstruction`：背景-only 重建

不要默认 SVG。  
不要默认裁切。  
要根据资产特征选择最合适的方式。

---

## 4. 全图扫描：必须先看完整张设计图

在输出任何资产前，先完整扫描整张图，识别：

- 页面整体背景
- 大面积氛围图 / hero 背景图
- 卡片壳、组件外壳
- logo / icon / 小图标
- 重复状态图标，例如早餐、午餐、晚餐、夜宵
- badge、状态标识、小符号
- 装饰层：叶子、星星、点、光晕、阴影、halo
- 方向敏感元素：月亮、箭头、折角、叶子倾斜方向
- 被文字或 UI 遮挡，但可以视觉推断的资产

不要只看红框。  
红框只是用户当前关注点，不代表整张图只有这一个资产。

---

## 5. 视觉拆层：从扁平图里推断隐藏结构

对于复杂组件，要先在脑中拆层：

```text
组件 =
  背景层
  容器壳
  边框 / 虚线框
  阴影 / 光晕
  图标 / 装饰组
  文字 / 业务内容
```

如果用户说“我要背景图”，通常要移除：
- 文字
- 按钮
- 中间内容
- 业务卡片
- 导航栏
- 进度条

只保留该层真正属于“背景”的视觉元素。

如果用户圈的是几个小装饰元素，要理解为：  
**用户要的是装饰组，而不是整个卡片。**

---

## 6. 五条生产路径的判断规则

### 6.1 `crop_or_isolate`：直接裁切 / 隔离

适合：

- 资产在截图中已经完整清晰
- 背景干净
- 没有被文字、卡片、按钮覆盖
- 用户确实想要截图里的原始片段

输出：

- PNG / WebP
- 如果需要独立放置，输出透明 PNG

避免用于：

- 被 UI 遮挡的背景
- 混在复杂背景里的图标
- 需要可缩放的图标
- 需要干净重建的资产

---

### 6.2 `svg_redraw`：SVG 矢量重绘

适合：

- 几何感强
- 图形规则
- 边缘清晰
- 需要放大不糊
- 方向需要精确控制

典型资产：

- 太阳图标
- 月亮图标
- 箭头
- 简单相机 glyph
- AI badge 外框
- 虚线框
- 简单 tab icon

输出：

- SVG 主文件
- 必要时补 PNG fallback

注意：

SVG 不适合所有东西。  
如果资产有柔光、渐变、插画感、轻质感，强行 SVG 会很硬。

---

### 6.3 `scripted_rebuild`：脚本/矢量代码重建

适合：

- 必须保证真透明
- 图形主要由圆、线、叶子、星星、月亮、虚线构成
- 需要精准控制方向
- 生图模型容易画错或画进假透明棋盘格

典型资产：

- 月亮方向修正
- 星星 + 叶子 + 光晕装饰组
- 简单相机图标
- 圆形 badge
- 餐食状态图标家族

输出：

- SVG
- 真透明 PNG
- validation-report.json

---

### 6.4 `imagegen_then_transparentize`：生图重建 + 透明化

这是 v3 的重点。

适合那些 **SVG 复刻不自然，但视觉上可以被重建** 的资产。

典型资产：

- 带柔光的相机装饰组
- 绿色圆形 badge + 光晕 + 相机 + 星星 + 叶子
- 有轻插画感的小装饰图
- 带阴影、渐变、高光的小模块
- 被文字或卡片遮挡，但视觉风格明确的元素
- 需要“像设计稿里自然长出来”的小图

正确流程：

```text
视觉识别目标资产
→ 写生图 prompt，只描述这个资产本身
→ 明确排除文字、卡片、按钮、边框、截图背景
→ 生图生成干净版本
→ 去背景 / 透明化
→ 检查 alpha 是否真透明
→ 输出完整画布版 + 裁剪紧凑版
```

必须避免：

- 让生图模型画“透明棋盘格”
- 把整个组件生成出来
- 把文字也生成进去
- 把红色标注框生成进去
- 输出一张看似透明、实际背景是灰白格子的图片

如果生图结果是假透明，要继续处理：
- 用 `scripts/transparentize_asset.py`
- 或者改用 `scripted_rebuild`
- 或重新生成明确要求透明背景

---

### 6.5 `background_reconstruction`：背景-only 重建

适合：

- 用户要“背景图”
- 原截图里背景被 UI 卡片、文字、按钮遮挡
- 背景里有食物、场景、插画、渐变、氛围光
- 直接裁切会把 UI 内容也带进去

典型资产：

- 沙拉 / 食物 hero 背景
- App 首页大背景
- 上传组件背后的淡绿色背景
- 带漂浮叶子的大面积背景
- 卡片壳背景，不含文字内容

正确流程：

```text
理解原图背景风格
→ 推断干净背景层
→ 生图或重建背景-only
→ 移除所有 UI 内容
→ 保留可放前端组件的留白
→ 输出 PNG / WebP
```

---

## 7. 候选资产记录字段

在开始生成前，内部要为每个候选资产记录：

```json
{
  "asset_name": "upload_deco_cluster",
  "source_region": "上传识别卡片中部",
  "category": "overlay",
  "visual_description": "左侧星星，中间浅绿色光晕圆形 badge，相机图标，右侧叶子",
  "hidden_layers": ["glow", "camera_icon", "sparkles", "leaves"],
  "method": "imagegen_then_transparentize",
  "transparent_required": true,
  "output_formats": ["png"],
  "reuse_reason": "可作为上传组件的独立装饰层",
  "risk_notes": "要避免生成假透明棋盘格"
}
```

---

## 8. manifest.json 规范

每个资源必须进入 `manifest.json`：

```json
{
  "filename": "upload_deco_cluster_transparent.png",
  "folder": "overlays",
  "type": "overlay",
  "format": "png",
  "transparent": true,
  "dimensions": "1536x1024",
  "source_basis": "flat image visual inference",
  "reconstruction_method": "imagegen_then_transparentize",
  "recommended_usage": "作为上传卡片中心装饰层，前端 absolute 定位覆盖",
  "notes": "真透明 PNG，已做 alpha 校验"
}
```

合法的 `reconstruction_method`：

- `crop_or_isolate`
- `svg_redraw`
- `scripted_rebuild`
- `imagegen_then_transparentize`
- `background_reconstruction`

---

## 9. 交付前必须校验

输出前必须尽量运行：

```bash
python scripts/validate_assets.py <output_dir>
python scripts/make_preview.py <output_dir>
python scripts/package_assets.py <output_dir> <project_name>
```

校验重点：

- 透明 PNG 是否真的有 alpha 通道
- 需要透明的地方 alpha_min 是否为 0
- 是否有假棋盘格背景
- SVG 文件是否可读
- 方向敏感资产是否正确
- 预览图是否生成
- manifest 是否完整
- ZIP 是否生成

---

## 10. 之前案例沉淀的规则

这些规则必须记住：

1. 用户给的是扁平 PNG，不是图层文件。
2. 最终目标是前端静态资源包，不是截图碎片。
3. 有些资产应该走生图模型生成，再透明化。
4. SVG 适合规则 icon，不适合所有柔光插画资产。
5. 真透明不是灰白棋盘格。
6. “背景图”通常要去掉文字、卡片、按钮和业务内容。
7. “我喜欢的是这几个部分”通常表示要抽出装饰组，不是整个组件。
8. 小叶子、小星星、小光晕都可能是独立资产，不要漏。
9. 月亮、箭头、叶子这种方向敏感元素要二次确认。
10. 如果用户纠正方向，比如“左边一个，弯右边”，要重建，而不是随便微调。
11. 复杂资产可以同时给多个版本：完整透明 PNG、裁剪版、SVG fallback、preview。

---

## 11. 最终回复方式

最终回答要直接：

1. 先给 ZIP 链接
2. 给 preview 链接
3. 简单说包含哪些资产
4. 说明透明校验是否通过
5. 不要长篇解释
