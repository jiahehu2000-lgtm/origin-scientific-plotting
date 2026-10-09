# Nature / Science / Cell：期刊规格与科研选图指南（Origin）

**先按数据关系选图，再按具体期刊和最终印刷尺寸调整样式。** 三个期刊系列没有一套通用的“CNS 官方模板”。本页把可核实的投稿要求与本项目归纳的选图建议分开，方便在 Origin 中执行。

核验日期：**2026-10-09**。公开示例均为合成数据，使用本机 Origin 原生绘制；没有使用私人实验数据，也没有转载论文中的图或出版社手册。

[四张可编辑 Origin 示例](journal-gallery/README.md) · [完整来源记录](journal-sources.json) · [Skill 中的执行规则](../skills/origin-scientific-plotting/references/journal-style.md)

## 1. 已有人总结吗？

有，下面是可以直接查看的公开资源。它们的用途不同：

| 资源 | 适合学习什么 | 使用边界 |
|---|---|---|
| [Nature Methods：Points of View](https://blogs.nature.com/methagora/2013/07/data-visualization-points-of-view.html) | 按样本、颜色、时间、热图等问题理解科研可视化 | 官方历史文章索引；方法建议不等于当前投稿硬性要求 |
| [SciencePlots](https://github.com/garrettj403/SciencePlots) | 把字体、线条、图宽等组织成可组合的 Matplotlib 样式 | 作者维护的开源工具；名字里的 `science` 不是 AAAS 官方认证 |
| [cnsplots](https://github.com/faridrashidi/cnsplots) | 统一科研图外观、尺寸控制和展示图库 | 作者维护的 Python 工具；“Cell/Nature/Science 风格”是项目定位，不能替代期刊指南 |

本项目借鉴的是“可配置样式＋公开示例＋数据类型决策”的组织方式。下面的规则为独立整理，没有复制这些项目的实现。

## 2. 先区分期刊、阶段与硬性要求

**数字指最终排版后的尺寸和字号。** 初稿审阅用图、修回用图、接收后的生产图，以及图形摘要可能有不同要求。一个系列中的不同刊物也可能不同。

| 刊物及来源范围 | 官方列出的图宽 | 字体、普通字与面板字母 | 线条及说明 |
|---|---|---|---|
| [Nature 终稿页](https://www.nature.com/nature/for-authors/final-submission) | 单栏 89 mm；双栏 183 mm | Arial/Helvetica；普通字 5–7 pt；面板小写、粗体正体 8 pt | 线宽 0.25–1 pt；其新版[图形指南](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)给最大图高 170 mm |
| [Nature Methods AIP 页面](https://www.nature.com/nmeth/submission-guidelines/aip-and-formatting)及其链接的[品牌终稿指南](https://www.nature.com/documents/NRJs-guide-to-preparing-final-artwork.pdf) | AIP 页面宽度最多 180 mm；链接指南研究/综述为 88/180 mm | 5–7 pt；具体面板规则应核对当前刊物通知 | 不将 Nature 的全部数字自动套到该刊 |
| [Nature Communications](https://www.nature.com/ncomms/submit/how-to-submit) | 88/180 mm | 清楚、一致的无衬线字；该页没有明确数字字号；面板小写粗体，与其他文字同字号 | 最细线 ≥1 pt；不能机械沿用 Nature 的更细线条 |
| [Science 网页](https://www.science.org/content/page/instructions-preparing-initial-manuscript#preparation-of-figures) | 57/121/184 mm，分别对应网页所述 1/2/3 栏 | 约 7 pt，至少 5 pt；无衬线；面板大写粗体 10 pt | 网页列出最终线宽 ≥0.5 pt |
| [Science 2025 官方图件 PDF](https://www.science.org/cms/asset/67f37ac8-4d02-4625-8a05-230568cb8323/author_prep_guide_2025.pdf) | 单栏 90 mm；双栏 183 mm | Arial/Helvetica；普通字 6–9 pt；面板大写粗体 10 pt | ≥0.28 pt；与网页的图宽、线宽存在冲突，尚未核实优先级 |
| [Science Advances 2026 官方图件 PDF](https://www.science.org/cms/asset/76887697-528f-4a22-afea-cee904504e76/sciadv_guide_to_preparing_figures_2026.pdf) | 单栏 90 mm；双栏 184 mm | Myriad 或同类无衬线；默认 8 pt，至少 6 pt；面板大写粗体 9 pt | 最终线宽 ≥0.28 pt；与 Science 单独配置 |
| [Cell](https://www.cell.com/cell/author-resources) / [Cell Reports](https://www.cell.com/cell-reports/author-resources) | **本轮未核实** | **本轮未核实** | 当前官方页面访问失败（403）；不把第三方的 85/174 mm、Arial/Avenir 或字号说法写成已验证要求 |

需要注意的来源差异：

- [Nature 初稿页](https://www.nature.com/nature/for-authors/initial-submission)中提前给出的终稿建议为 90/180 mm，而终稿页为 89/183 mm。不要把不同官方来源给出的终稿建议拼成一套标准。终稿页的 247 mm 是页深，不能当成任意图件可占用的高度。
- Nature 新版图形指南与终稿页对单独提交位图的表述不同；Science 网页与 2025 PDF 的宽度、线宽也不同。**记录来源和冲突，最终按目标期刊的编辑通知及提交系统确认。** 可编辑矢量图是这些曲线、散点和组合图的可靠工作格式，但不是自动通过审稿的证明。
- Science Advances 2026 PDF 同时包含黑白位图线稿 ≥1200 dpi 与 >600 dpi 降采样等条款，适用关系未完全说明。本项目保留冲突，不宣称所有图统一 600 dpi 即可。

### Cell 官方暂时无法核实时怎么做？

可以先完成可编辑 Origin 图，再补目标刊物的终尺寸。核实到的 [Elsevier 通用指南](https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing)有 90/140/190 mm 尺寸示例，以及普通字 7 pt、上下标至少 6 pt 的**经验规则**。这些不是 Cell / Cell Reports 专属硬性要求。

[Elsevier 通用图件类型指南](https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-types)还区分照片、混合图与黑白位图线稿的分辨率。不能用图形摘要的正方形尺寸替代主文数据图；也不能把 Journal of Cell Biology 误认为 Cell Press 的 Cell。

## 3. 什么数据用什么图？

下表是**方法学文献与本项目的归纳建议**，不是期刊逐条规定。先问要表达哪一种关系，再选图型。

| 数据 / 要回答的问题 | 推荐图型 | 建议呈现方式与需要保留的信息 | 当前批量 helper |
|---|---|---|---|
| 电流、温度、响应等随时间变化 | 曲线；离散观测可叠散点 | 时间沿横轴；不同条件固定颜色并加线型/点形；断测区间不要擅自连线 | 曲线、散点支持；缺口分段需准备系列 |
| 已有实测值与已有模型曲线是否一致 | 实测散点＋模型线；必要时加残差图 | 点表示观测，线表示模型；图注明拟合/验证范围。绘图操作本身不重新拟合 | 点、线支持；残差需另提供 |
| 两个连续变量的关系 | 散点图 | 每个点对应一个观测；有多组时用颜色＋点形；仅在已有分析支持时加回归/区间 | 散点支持；拟合不由 helper 计算 |
| 少量独立样本的组间比较 | 个体点图；可叠已计算的中心值/误差 | 显示每个观测和 n；横向错位只用于避免重叠，不能改变测量值 | 散点支持；误差值需提供 |
| 同一样本的前后或配对比较 | 配对点＋连接线；必要时另画差值 | 连线依据真实配对 ID；六对样本不能写成十二个独立重复 | 点、线支持 |
| 多组、较多观测的分布差异 | 箱线图＋点；适量数据可用小提琴图＋点 | 说明箱线须定义；小提琴的核密度形状依赖数据量和带宽，不宜掩盖稀少观测 | 需在 Origin 原生适配 |
| 多个独立实验、每次实验内又有多个细胞/读数 | SuperPlot 或分层点图 | 区分独立实验与实验内观测；推断用与研究设计相符的独立单位 | 可画已准备的点/线；层级统计需另外完成 |
| 类别计数、组成或频数 | 柱图；类别很多可用横向点/条图 | 普通柱图从零开始；明确是数目、比例还是百分比；不要把连续样本只剩一个均值柱 | 简单柱图支持；堆叠/分组需适配 |
| 准确率、F1、器件指标随有序参数变化 | 点线图；类别条件可用点＋误差 | 参数有顺序才连线；误差注明来自独立重复、受试者还是折次；保留训练/测试定义 | 点线、对称误差支持 |
| 单个变量的总体分布 | 直方图 / ECDF；有意义时加密度曲线 | 直方图说明分箱；ECDF 避免分箱依赖；不要为了好看删长尾 | 需在 Origin 原生适配 |
| 多变量/样本的数值矩阵 | 热图 | 有序幅度用顺序色，也可包含负值；围绕有意义中心的偏差用发散色；比较图共享色域；缺失与零分开 | 基本热图支持；发散中心需原生适配 |
| 分类错在哪里 | 混淆矩阵 | 真实类别为行、预测为列；计数或行归一化明确说明；色标 0–1 时标比例；每类 n 可写图注 | 原始计数、行归一化、数值标注支持 |
| 多条曲线、多条件难以辨别 | 小多图 / 分面图 | 同一比较使用一致坐标范围；按实验逻辑排序；避免几十条线挤在一层 | 多图可分别生成；组合排版需适配 |
| 效应量与置信区间 / ROC / 生存过程 | 森林图 / ROC / 生存曲线 | 明确效应零点或比值 1；ROC 标轴和测试集；区间/风险集必须来自已有分析 | 需原生适配；不自动估计统计量 |
| 真正的三维空间、形貌或场分布 | 3D 面/空间图 | 只有第三维本身有科学含义才使用；不要给普通柱图添加透视厚度 | 需在 Origin 原生适配 |

这里的“支持”表示现有 `origin_plot.py` 能绘制已提供的数据，**不是能自动完成全部统计分析**。箱线、小提琴、ROC、森林图、分面、非对称误差棒和置信带尚无通用批量实现，不能用截图导入 Origin 充当原生图。

选图建议的主要依据：

- [Kick the bar chart habit](https://www.nature.com/articles/nmeth.2837) 与 [Show the dots in plots](https://www.nature.com/articles/s41551-017-0079)：计数可以用柱图；实验样本可行时应表达个体观测，避免仅靠均值隐藏分布。
- [Beyond Bar and Line Graphs](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002128)：小样本的原始点、配对关系与数据分布会改变读者对结果的理解。
- [SuperPlots](https://rupress.org/jcb/article/219/6/e202001064/151717/SuperPlots-Communicating-reproducibility-and)：同时呈现实验内变化和独立实验间变化；显示全部点也不能自动消除伪重复。
- [Error bars in experimental biology](https://rupress.org/jcb/article/177/1/7/34602/Error-bars-in-experimental-biology)：误差条必须说明 SD、SEM 或 CI，含义不能互换。
- [Bengio & Grandvalet：交叉验证方差](https://www.jmlr.org/papers/v5/grandvalet04a.html)：交叉验证各折因训练数据重叠而相关。折间 SD 可以描述离散程度，但不能直接把折数当作独立 n 来计算 SEM、CI 或显著性。

表中的具体布局和 Origin 适配判断是本项目的实施建议。ECDF、森林图等条目不是声称上述期刊逐项要求使用这些图型。

## 4. 在 Origin 里怎么落实风格？

### 颜色和线条

本项目建议以白背景、清楚的轴线、有限颜色开始。同一对象在整套图中保持同色；不要每页重新分配颜色。参考 [Okabe–Ito 的 Color Universal Design](https://jfly.uni-koeln.de/color/)，同时使用颜色与点形、线型或位置，避免识别完全依赖红/绿。

公开示例用蓝 `#0072B2`、橙 `#D55E00`、绿 `#009E73` 和灰色，并配不同点形。它们是工作配色，**不是期刊指定色板**；仍应检查最终尺寸、灰度效果和色觉可读性。热图需按数值语义选择顺序色或发散色，而不是默认彩虹色。

### 字体、边框和留白

- 先确定最终图宽，再确定字号。全文同类标签尽量统一，单位写在轴标题中；字、线和点在最终尺寸下均应可辨。
- 面板字母按具体期刊设置；Nature 的小写规则不能直接套到 Science 的大写规则。
- 曲线比较可保留四边细框，也可按要求仅显示左/下轴；不把“某一种边框”宣称为整个系列统一规定。减少没有信息作用的阴影、重复标签和密集网格。
- 长解释放图注；短条件说明可以放图内空处。删除顶部标题后，收紧 **Origin 原生页面或图层**，不要仅裁 PNG 而让 PDF 和工程仍保留大片白边。
- 比较性面板保持坐标尺度一致；使用对数轴时说明含义。缩小白边不能裁掉刻度、轴标题、误差棒或图例。

### 特别注意：宽度 5 cm 时字号会一起缩小

若一张导出宽度为 89 mm、字体 7 pt 的图被等比例缩到 50 mm，文字变为：

```text
最终字号 = 源字号 × 放置宽度 / 实际导出宽度
7 × 50 / 89 ≈ 3.93 pt
```

若确实需要在 50 mm 下读到 7 pt，89 mm 源图对应字号约为 `7 × 89 / 50 = 12.46 pt`，或者直接在目标尺寸下重排图层。不能只把所有图片宽度统一 5 cm，就认为字号也符合论文要求。

**计算用实际导出 PDF 宽度。** 当前 helper 的 `page_inches` 是初始画布；原生页面收紧后宽度会变化。请看核验报告的 `compact_page.page_after_inches` 与 `export_qa.pdf_page_inches`，不能把初始画布宽度当作最终图宽。

10×10 混淆矩阵的数字较多，可能需要更宽的面板或简化标注方式。优先检查阅读效果，不为了统一宽度把每格文字缩得难以辨认。

## 5. 矢量、位图和可编辑工程怎么交付？

| 内容 | 本项目工作建议 | 要核验什么 |
|---|---|---|
| 曲线、散点、柱、热图中的线和文字 | Origin 原生矢量 PDF；另外保存 OPJU | PDF 中有路径和可提取的文字；字体/字号正确；不能整图只有一张位图 |
| 照片、显微图、扫描图 | 保留原始像素，按具体刊物要求准备位图 | **最终尺寸**下的有效分辨率；比例尺和标注保持清楚 |
| 照片＋数据图的复合图 | 嵌入照片，保留矢量文字、线和数据图 | 链接图像嵌入；不能将整图栅格化后冒充可编辑复合图 |
| 组会与继续修改 | OPJU；需要时嵌入 Origin OLE 到 PPT | OLE 双击可回 Origin 与普通图片是两种交付；PPT 不是自动满足期刊提交格式 |

本工具的 **SVG 是由 PDF 转换得到，可能把字形变成路径**。它是矢量，但不等于可编辑文字；面对明确要求不转曲文字的投稿指南，不能仅凭 `.svg` 扩展名就认定合格。

位图像素计算：`像素数 = dpi × 最终宽度(mm) / 25.4`。例如 180 mm、300 dpi 至少需向上取整为 2126 像素。更改 DPI 标签或上采样不能补造原始细节。不同出版社对照片、混合图和黑白线稿的要求不同，见[来源记录](journal-sources.json)，不统一冒称“所有期刊 300 dpi 即可”。

OPJU 是本项目为继续编辑保留的工作文件，**不是这些出版社统一要求提交的文件格式**。

## 6. 四张公开示例：看图、下载、复现

![四类数据的 Origin 原生示例](journal-gallery/gallery.png)

从[示例目录](journal-gallery/README.md)下载各图的 PNG、原生 PDF、可编辑 OPJU 和核验摘要。全部数据和设置在 [figures.json](../examples/journal-gallery/figures.json) 中：时间响应、独立样本点图、配对观测、带未测试类别的混淆矩阵。

```powershell
# 在仓库根目录，先按首页安装 Python 依赖并确认 Origin 可调用
& ./.venv/Scripts/python.exe skills/origin-scientific-plotting/scripts/origin_plot.py `
  --spec examples/journal-gallery/figures.json --validate-only

& ./.venv/Scripts/python.exe skills/origin-scientific-plotting/scripts/origin_plot.py `
  --spec examples/journal-gallery/figures.json --output results-journal-gallery `
  --formats png,pdf,emf
```

输出目录必须新建或为空。这四张图用于展示选图关系与简洁排版，**不是任何刊物的已认证模板**。每次复现均应核对保存后数据、原生样式和实际导出尺寸，再根据目标期刊调整。

也可以直接给 Codex 这样的任务：

> 使用 `$origin-scientific-plotting`。这是六个独立样本的组间比较，请先保留全部点，再按 Nature Communications 当前官方指南和最终 88 mm 图宽设置字体、线宽与图例。不要自动拟合或生成统计显著性。导出 OPJU 和可编辑文字的原生 PDF，列出核验到的要求与尚未确认项。

## 7. 使用与更新

本页总结、Skill 和原创示例均公开在本仓库，可按 [MIT 许可](../LICENSE) 使用。出版社原文、商标和链接项目仍按各自许可使用；本仓库不是 Nature、AAAS、Cell Press、Elsevier 或 OriginLab 官方产品。

发现期刊指南更新或本文记录有误，欢迎提交带有**官方链接、刊名、文章类型与阶段**的 Issue / PR。可以更新已核验规则，但不能把未知值悄悄补成“官方要求”。
