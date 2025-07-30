# 高级人才流动科研项目：流体模块

## 项目概述

本模块作为"高级人才流动"科研项目的核心组成部分，基于热力学扩散理论构建流体模型，用于预测全球顶尖科学家的职业流动概率。模型将科学家的职业选择视为粒子在势能场中的扩散过程，通过量化影响因子（如学术影响力、自立性、协作程度等）来预测五种流动方向的概率分布。

### 核心特性

- **数据驱动**: 基于斯坦福/Elsevier全球顶尖2%科学家排名数据（~220,000条记录）
- **物理模型**: 采用热力学扩散方程，结合势能场理论
- **多维预测**: 输出5种职业流动方向的概率分布
- **高效处理**: 支持批量分析和并行计算
- **可扩展性**: 模块化设计，易于集成到更大的人才流动网络模型中

## 安装依赖

```bash
pip install numpy pandas scipy matplotlib pathlib tqdm
```

## 快速开始

```python
from scientist_mobility_enhanced import EnhancedScientistMobilityAnalyzer

# 初始化分析器
analyzer = EnhancedScientistMobilityAnalyzer("path/to/data")

# 运行完整分析
results = analyzer.run_enhanced_analysis(n_samples=100, detailed_analysis_count=5)

# 分析单个科学家
single_result = analyzer.analyze_single_scientist(author_idx=0)
print(f"预测结果: {single_result['final_probs']}")
```

## 数据源与结构

### 数据来源

本模块使用斯坦福大学与Elsevier合作发布的"全球顶尖2%科学家"排名数据，基于Scopus数据库构建，覆盖约200,000名科学家（占全球科学家总数的2%）。

数据包含三个主要表格：

1. **Table_1 (Authors career/singleyr)**: 个体科学家的职业生涯和年度指标
2. **Table_2 (Thresholds career/singleyr)**: 各领域/子领域的阈值统计
3. **Table_3 (Maxlog career/singleyr)**: 最大值日志，用于标准化

### 数据表结构

#### Table_1: 个体科学家指标
- `authfull`: 科学家全名
- `h23 (ns)`: 排除自引的h-index (2023)
- `nc9623 (ns)`: 1996-2023年排除自引的引用数
- `self%`: 自引百分比
- `rank (ns)`: 排除自引的排名
- `sm-field-frac`: 子领域出版物分数
- `firstyr/lastyr`: 首次/最后出版年份
- `ncsfl (ns)`: 场调整排除自引引用分数
- `cself`: 自引用数

#### Table_2: 领域阈值
- `top-list cprat@99 (ns)`: 99百分位复合排名（排除自引）
- `Cites@95`: 95百分位引用阈值
- `top-list self%@99`: 99百分位自引百分比

#### Table_3: 最大值标准化
- `max_h23 (ns)`: h-index最大值
- `max_nc9623 (ns)`: 引用数最大值
- `max_ncsfl (ns)`: 场调整引用分数最大值

## 变量选取与处理

### 38个原始变量

从数百个可用字段中，基于文献研究和逻辑分析，选取了38个与科学家流动显著相关的变量：

#### Table_1 变量（18个）
**Career指标 (9个)**:
1. `h23 (ns)` - 排除自引h-index
2. `nc9623 (ns)` - 长期引用数
3. `self%` - 自引百分比
4. `rank (ns)` - 排除自引排名
5. `sm-field-frac` - 子领域专注度
6. `firstyr` - 职业开始年份
7. `lastyr` - 最近活跃年份
8. `ncsfl (ns)` - 场调整引用分数
9. `cself` - 自引用总数

**Single-year指标 (9个)**:
1. `h23 (ns)` - 年度h-index
2. `nc2323 (ns)` - 年度引用数
3. `self%` - 年度自引百分比
4. `rank (ns)` - 年度排名
5. `sm-field-frac` - 年度子领域分数
6. `ncsfl (ns)` - 年度场调整分数
7. `cself` - 年度自引数
8. `nps` - 年度论文数
9. `cprat (ns)` - 年度复合排名

#### Table_2 变量（10个）
**Career阈值 (5个)**:
1. `top-list cprat@99 (ns)` - 复合排名99%阈值
2. `Cites@95` - 引用95%阈值
3. `top-list self%@99` - 自引99%阈值
4. `nc6023 (ns)` - 长期引用阈值
5. `h23 (ns)` - h-index阈值

**Single-year阈值 (5个)**:
1. `top-list cprat@99 (ns)` - 年度复合排名阈值
2. `Cites@95` - 年度引用阈值
3. `top-list self%@99` - 年度自引阈值
4. `nc2323 (ns)` - 年度引用阈值
5. `h23 (ns)` - 年度h-index阈值

#### Table_3 变量（10个）
**Career最大值 (5个)**:
1. `max_h23 (ns)` - h-index最大值
2. `max_nc9623 (ns)` - 引用数最大值
3. `max_ncsfl (ns)` - 场调整分数最大值
4. `max_cself` - 自引最大值
5. `max_cprat (ns)` - 复合排名最大值

**Single-year最大值 (5个)**:
1. `max_h23 (ns)` - 年度h-index最大值
2. `max_nc2323 (ns)` - 年度引用最大值
3. `max_ncsfl (ns)` - 年度场调整最大值
4. `max_cself` - 年度自引最大值
5. `max_cprat (ns)` - 年度复合排名最大值

### 降维处理：从38维到12维s_i向量

为避免高维灾难并提高计算效率，采用以下策略将38个变量精简为12维特征向量：

#### 降维策略

1. **平均合并**: 对career和single-year相同类型指标取平均值
2. **标准化**: 使用Table_3最大值进行归一化
3. **领域聚合**: 利用Table_2阈值进行领域调整
4. **对数变换**: 对大数值变量应用log1p变换防止溢出
5. **合并相似**: 将功能相似的指标合并为单一特征

#### 12维s_i向量定义

| 维度 | 变量名 | 含义 | 计算方式 |
|------|--------|------|----------|
| s_i[0] | t_norm | 职业长度标准化 | (lastyr - firstyr) / 60, 范围[0.1,1.0] |
| s_i[1] | self_perc | 自引百分比 | avg(career_self% + singleyr_self%) / 2 |
| s_i[2] | h_norm | 标准化h-index | avg(h23_career + h23_singleyr) / max_h23 |
| s_i[3] | nc9623_ns_norm | 标准化引用数 | log1p(avg(nc9623 + nc2323)) / log1p(max) |
| s_i[4] | ncsfl_ns | 场调整引用分数 | avg(ncsfl_career + ncsfl_singleyr) / max_ncsfl |
| s_i[5] | rank_norm | 标准化排名 | 1 / avg(rank_career + rank_singleyr) |
| s_i[6] | cprat_ns | 复合排名分数 | avg(cprat_career + cprat_singleyr) |
| s_i[7] | cites95_norm | 95%引用阈值 | avg(Cites@95_career + Cites@95_singleyr) / 12000 |
| s_i[8] | self99_agg | 99%自引聚合 | avg(self%@99_career + self%@99_singleyr) |
| s_i[9] | frac | 领域专注度 | sm-field-frac from career |
| s_i[10] | field_mobility | 学科流动性 | 基于领域的流动倾向系数 |
| s_i[11] | inst_mobility | 机构流动性 | 基于机构类型的流动系数 |

## 核心数学模型

### 物理学基础

模型基于热力学扩散理论，将科学家职业选择类比为粒子在势能场中的布朗运动。核心思想是科学家会倾向于向"吸引力"更强、"阻力"更小的职业方向流动。

### 势能场模型

#### 势能函数 G(η; x, t)

```math
G(\eta; x, t) = \int_{0}^{\eta} f(\zeta) \, d\zeta + \frac{(x - \eta)^2}{2t}
```

**输入变量**:
- `η` (eta): 潜在职业路径位置 [-5, 5]
- `x`: 目标流动方向 [0-4]
  - 0: 学术留任 (stay academic)
  - 1: 学术迁移 (academic move)
  - 2: 产业流动 (industry move)
  - 3: 国际迁移 (international move)
  - 4: 退休 (retirement)
- `t`: 扩散宽度参数，来自职业长度标准化

**输出值**: 势能值 G，数值越低表示流动"代价"越小

**物理意义**:
- 第一项: 累积吸引力，基于影响力、自立性等因素
- 第二项: 偏离惩罚，距离目标方向越远代价越高

#### 吸引力函数 f(ζ)

```math
f(\zeta) = h_{norm} \cdot (1 - self\_perc) \cdot (1 - self99\_agg) \cdot \frac{1}{1 + e^{-\zeta}}
```

**输入变量**:
- `ζ` (zeta): 路径变量
- `h_norm`: 标准化影响力 (s_i[2])
- `self_perc`: 自引百分比 (s_i[1])
- `self99_agg`: 聚合自引阈值 (s_i[8])

**输出值**: 吸引力强度，范围 [0, h_norm]

**物理意义**: 
- 使用Sigmoid函数模拟门槛效应
- 高影响力、低自引的科学家具有更强的流动吸引力
- ζ > 0时吸引力快速增长，模拟达到临界点后的加速流动

### 净流入强度模型

#### 核心扩散方程

```math
Y(x, t) = \frac{\int_{-\infty}^{\infty} \frac{x - \eta}{t} \cdot e^{- \frac{G(\eta; x, t)}{2\mu}} \, d\eta}{\int_{-\infty}^{\infty} e^{- \frac{G(\eta; x, t)}{2\mu}} \, d\eta}
```

**输入变量**:
- `x`: 流动方向 [0-4]
- `t`: 扩散宽度 (s_i[0])
- `μ` (mu): 不确定性参数，计算为 max(0.2, 1/s_i[4])
- 其他参数通过s_i向量传入

**输出值**: 方向x的净流入强度

**物理意义**:
- 分子: 加权导向因子 (x-η)/t，结合势能分布
- 分母: 归一化因子，确保概率密度一致
- μ控制随机性：μ大→分布平坦（更随机），μ小→分布尖锐（更确定）

### 参数映射关系

| 物理参数 | 数据映射 | 含义 |
|----------|----------|------|
| t | s_i[0] (t_norm) | 扩散宽度，长职业→大t→更不确定 |
| μ | max(0.2, 1/s_i[4]) | 不确定性，高协作→小μ→更确定 |
| h_norm | s_i[2] | 影响力，促进流动 |
| self_perc | s_i[1] | 自立性，高自引→倾向留任 |
| self99_agg | s_i[8] | 领域自引阈值 |

## 模块使用指南

### 基本用法

#### 1. 初始化分析器

```python
from scientist_mobility_enhanced import EnhancedScientistMobilityAnalyzer

# 指定数据路径
data_path = "path/to/stanford_elsevier_data"
analyzer = EnhancedScientistMobilityAnalyzer(data_path)
```

#### 2. 单个科学家分析

```python
# 分析编号为0的科学家
result = analyzer.analyze_single_scientist(author_idx=0)

print(f"科学家姓名: {result['author_info']['author_name']}")
print(f"最终概率分布: {result['final_probs']}")
print(f"最可能流向: {analyzer.visualizer.labels[np.argmax(result['final_probs'])]}")
```

#### 3. 批量分析

```python
# 分析前100个科学家
batch_results = analyzer.batch_analysis(n_samples=100)

# 生成统计报告
analyzer._generate_analysis_report(batch_results)
```

#### 4. 完整分析流程

```python
# 运行完整的增强分析
results = analyzer.run_enhanced_analysis(
    n_samples=1000,           # 批量分析样本数
    detailed_analysis_count=5  # 详细分析的科学家数量
)
```

### 高级用法

#### 1. 按姓名搜索分析

```python
# 搜索特定科学家
result = analyze_author_by_name("Einstein", analyzer)
if result:
    print(f"预测概率: {result['final_probs']}")
```

#### 2. 比较多个科学家

```python
# 比较编号为0,1,2的科学家
author_indices = [0, 1, 2]
comparison_results = compare_authors(author_indices, analyzer)
```

#### 3. 交互式分析

```python
# 启动交互式界面
interactive_analysis()
```

#### 4. 外部调用接口

```python
# 简化的预测接口
prediction = predict_scientist_mobility(
    author_idx=0,
    data_path="path/to/data",
    include_temporal=True
)

print(f"科学家: {prediction['author_name']}")
print(f"最可能方向: {prediction['top_prediction']}")
print(f"置信度: {prediction['confidence']:.3f}")
```

### 可视化功能

#### 1. 时间演化图

```python
# 绘制单个科学家的时间演化
analyzer.visualizer.plot_temporal_distribution(
    result['temporal_probs'], 
    result['time_points'],
    result['author_info']
)
```

#### 2. 批量对比图

```python
# 生成批量对比可视化
analyzer.visualizer.plot_batch_comparison(batch_results)
```

#### 3. 统计汇总图

```python
# 生成统计汇总可视化
analyzer.visualizer.plot_statistics_summary(batch_results)
```

## 输出结果解释

### 概率分布

每个科学家的分析结果包含5个方向的概率值，总和为1.0：

```python
final_probs = [0.15, 0.25, 0.35, 0.20, 0.05]
# 对应: [留任, 学术迁移, 产业流动, 国际迁移, 退休]
```

### 结果示例

```python
{
    'author_name': 'John Doe',
    'final_probs': [0.12, 0.28, 0.42, 0.15, 0.03],
    'top_prediction': '产业流动',
    'confidence': 0.42,
    'temporal_probs': [...],  # 时间演化数据
    'time_points': [0.1, 1.0, 2.0, ...]
}
```

### 解释指南

- **留任概率高** (>0.4): 科学家倾向于保持当前学术职位
- **产业流动概率高** (>0.3): 可能转向工业界或创业
- **国际迁移概率高** (>0.3): 倾向于跨国学术流动
- **学术迁移概率高** (>0.3): 倾向于换到其他学术机构
- **退休概率高** (>0.2): 接近职业生涯末期

## 性能优化

### 计算效率

1. **并行处理**: 使用ThreadPoolExecutor进行批量计算
2. **数值积分优化**: 限制积分区间为[-5,5]，减少计算时间
3. **内存管理**: 分块处理大数据集，避免内存溢出
4. **缓存机制**: 重复计算结果缓存

### 数值稳定性

1. **溢出防护**: 使用np.clip限制指数函数输入范围
2. **NaN处理**: 对异常值提供默认概率分布
3. **对数变换**: 对大数值使用log1p变换
4. **下界保护**: 为关键参数设置最小值

### 推荐配置

```python
# 小规模测试 (< 1000样本)
analyzer.batch_analysis(n_samples=100, use_parallel=False)

# 中等规模 (1000-10000样本)
analyzer.batch_analysis(n_samples=5000, use_parallel=True)

# 大规模处理 (> 10000样本)
# 建议分批处理，每批5000-10000样本
```

## 故障排除

### 常见问题

#### 1. 数据加载失败
```python
# 检查文件路径和格式
tables = analyzer.data_loader.load_all_tables()
if not tables:
    print("数据加载失败，请检查路径和文件格式")
```

#### 2. 计算溢出警告
```python
# 正常现象，模块内部已处理
# 如果持续出现，可调整缩放参数
```

#### 3. 概率分布异常
```python
# 检查输入数据质量
result = analyzer.analyze_single_scientist(0)
if np.any(np.isnan(result['final_probs'])):
    print("检测到NaN值，请检查输入数据")
```

### 调试模式

```python
# 启用详细输出
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试单个样本
test_result = analyzer.analyze_single_scientist(0)
print(f"调试信息: {test_result}")
```

## 模型限制与改进方向

### 当前限制

1. **假设简化**: 假设a_i=0（留任偏好），可能引入偏差
2. **外部因素**: 未考虑经济周期、政策变化等外部因素
3. **验证数据**: 缺乏真实流动结果验证模型准确性
4. **计算复杂度**: 数值积分对大规模数据处理效率有限

### 改进方向

1. **模型增强**:
   - 引入动态a_i估计
   - 添加外部环境变量
   - 实现Gaussian近似加速计算

2. **验证改进**:
   - 收集真实流动数据进行交叉验证
   - 实现时间序列预测验证
   - 添加准确率评估指标

3. **功能扩展**:
   - 支持实时数据更新
   - 添加Web API接口
   - 实现交互式可视化界面

## 引用与参考

### 数据源
- Stanford/Elsevier全球顶尖2%科学家排名
- Scopus数据库科学计量指标

### 理论基础
- 热力学扩散理论
- 布朗运动模型
- 统计物理学势能场理论

### 相关文献
- Ioannidis, J.P.A. et al. "Updated science-wide author databases of standardized citation indicators" (2023)
- 科学家流动模式相关研究文献

## 许可证

MIT License - 详见LICENSE文件

## 贡献指南

欢迎提交Issue和Pull Request来改进本模块。请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues页面
- 邮箱：[project-email@example.com]

---

*本文档持续更新中，最后更新时间：2024年*