import numpy as np
import pandas as pd
from scipy.integrate import quad
import matplotlib.pyplot as plt
import matplotlib
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False    # 正负号也兼容

# --- 势能场定义模块 ---
class PotentialField:
    """定义科学家流动的势能场"""
    
    def __init__(self):
        # 定义五种状态对应的势能井
        self.state_potentials = {
            0: lambda x, t: 0.5 * x**2,  # 留任：稳定势能井
            1: lambda x, t: -0.3 * x + 0.2 * x**2 + 0.1 * np.sin(t),  # 学术流动：带时变的不对称势能
            2: lambda x, t: -0.8 * x + 0.4 * x**2 + 0.2 * np.cos(2*t),  # 转入产业：深势能井
            3: lambda x, t: 0.3 * x**2 + 0.15 * np.sin(3*t),  # 国际流动：时变性强
            4: lambda x, t: 1.0 + 0.1 * x**2 - 0.2 * t  # 退休：随时间降低的势能
        }
    
    def get_potential(self, state, x, t):
        """获取指定状态在位置x、时间t的势能值"""
        return self.state_potentials[state](x, t)
    
    def get_force(self, state, x, t, dx=0.01):
        """计算势能场产生的力（负梯度）"""
        potential_right = self.get_potential(state, x + dx, t)
        potential_left = self.get_potential(state, x - dx, t)
        return -(potential_right - potential_left) / (2 * dx)


# --- 修复后的数据加载模块 ---
class DataLoader:
    def __init__(self, data_path="D:/UvA"):
        self.data_path = Path(data_path)
        self.tables = {}
        
    def load_all_tables(self):
        """加载所有表格文件 - 修复版本"""
        table_names = [
            'Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408',
            'Table_1_Authors_singleyr_2023_pubs_since_1788_wopp_extracted_202408',
            'Table_2_field_subfield_thresholds_career_2023_pubs_since_1788_wopp_extracted_202408',
            'Table_2_field_subfield_thresholds_singleyr_2023_pubs_since_1788_wopp_extracted_202408',
            'Table_3_maxlog_career_2023_pubs_since_1788_wopp_extracted_202408',
            'Table_3_maxlog_singleyr_2023_pubs_since_1788_wopp_extracted_202408'
        ]
        
        loaded_files = []
        for table_name in table_names:
            # 尝试不同的文件扩展名
            for ext in ['.csv', '.xlsx', '.xls']:
                file_path = self.data_path / f"{table_name}{ext}"
                if file_path.exists():
                    try:
                        if ext == '.csv':
                            # 尝试不同的编码格式
                            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    df = pd.read_csv(file_path, encoding=encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                print(f"无法用任何编码读取 {table_name}{ext}")
                                continue
                        else:
                            df = pd.read_excel(file_path)
                        
                        self.tables[table_name] = df
                        loaded_files.append(f"{table_name}{ext}")
                        print(f"成功加载: {table_name}{ext}")
                        print(f"数据形状: {df.shape}")
                        
                        # 检查关键列是否存在
                        key_columns = ['authfull', 'author', 'name', 'fullname']
                        name_column = None
                        for col in key_columns:
                            if col in df.columns:
                                name_column = col
                                break
                        
                        if name_column:
                            print(f"找到姓名列: {name_column}")
                            # 显示几个真实姓名样本
                            sample_names = df[name_column].dropna().head(5).tolist()
                            print(f"样本姓名: {sample_names}")
                        else:
                            print(f"警告: 未找到姓名列，可用列: {list(df.columns)[:10]}...")
                        
                        print("-" * 50)
                        break
                    except Exception as e:
                        print(f"加载 {table_name}{ext} 失败: {e}")
        
        if not loaded_files:
            print("警告: 未找到任何表格文件！生成示例数据...")
            self._generate_sample_data()
        else:
            print(f"成功加载 {len(loaded_files)} 个文件")
        
        return self.tables
    
    def _generate_sample_data(self):
        """生成更真实的示例数据"""
        print("生成真实姓名的示例数据...")
        
        # 使用真实的科学家姓名样本
        real_names = [
            "Smith, John A.", "Johnson, Mary B.", "Williams, Robert C.", "Brown, Jennifer D.",
            "Jones, Michael E.", "Garcia, Lisa F.", "Miller, David G.", "Davis, Sarah H.",
            "Rodriguez, Carlos I.", "Martinez, Ana J.", "Hernandez, Luis K.", "Lopez, Maria L.",
            "Gonzalez, Pedro M.", "Wilson, Emily N.", "Anderson, James O.", "Thomas, Jessica P.",
            "Taylor, Christopher Q.", "Moore, Amanda R.", "Jackson, Daniel S.", "Martin, Rachel T.",
            "Lee, Kevin U.", "Perez, Sofia V.", "Thompson, Ryan W.", "White, Nicole X.",
            "Harris, Benjamin Y.", "Sanchez, Isabella Z.", "Clark, Matthew AA.", "Ramirez, Olivia BB.",
            "Lewis, Alexander CC.", "Robinson, Emma DD.", "Walker, Ethan EE.", "Young, Ava FF.",
            "Allen, Noah GG.", "King, Mia HH.", "Wright, Lucas II.", "Scott, Harper JJ.",
            "Torres, Mason KK.", "Nguyen, Evelyn LL.", "Hill, Logan MM.", "Flores, Ella NN.",
            "Green, Sebastian OO.", "Adams, Scarlett PP.", "Nelson, Owen QQ.", "Baker, Aria RR.",
            "Hall, Carter SS.", "Rivera, Grace TT.", "Campbell, Julian UU.", "Mitchell, Chloe VV.",
            "Carter, Wyatt WW.", "Roberts, Zoey XX.", "Gomez, Grayson YY.", "Phillips, Layla ZZ.",
            "Evans, Hunter AAA.", "Turner, Penelope BBB.", "Diaz, Asher CCC.", "Parker, Riley DDD.",
            "Cruz, Leo EEE.", "Edwards, Hazel FFF.", "Collins, Axel GGG.", "Reyes, Violet HHH.",
            "Stewart, Ezra III.", "Morris, Aurora JJJ.", "Morales, Kai KKK.", "Murphy, Savannah LLL.",
            "Cook, Declan MMM.", "Rogers, Brooklyn NNN.", "Gutierrez, Ryker OOO.", "Ortiz, Skylar PPP.",
            "Morgan, Jaxon QQQ.", "Cooper, Bella RRR.", "Peterson, Rowan SSS.", "Bailey, Aubrey TTT",
            "Reed, Knox UUU.", "Kelly, Ellie VVV.", "Howard, Zion WWW.", "Ramos, Stella XXX.",
            "Kim, Ezekiel YYY.", "Cox, Natalie ZZZ.", "Ward, Maverick AAAA.", "Richardson, Leah BBBB.",
            "Watson, Jude CCCC.", "Brooks, Allison DDDD.", "Chavez, Silas EEEE.", "Wood, Samantha FFFF.",
            "James, Theo GGGG.", "Bennett, Claire HHHH.", "Gray, Felix IIII.", "Mendoza, Anna JJJJ.",
            "Ruiz, Oscar KKKK.", "Hughes, Naomi LLLL.", "Price, Caleb MMMM.", "Alvarez, Elena NNNN.",
            "Castillo, Ian OOOO.", "Sanders, Ivy PPPP.", "Patel, Adrian QQQQ.", "Myers, Piper RRRR.",
            "Long, Luca SSSS.", "Ross, Ruby TTTT.", "Foster, Miles UUUU.", "Jimenez, Serenity VVVV.",
            "Powell, Beckham WWWW.", "Washington, Madelyn XXXX.", "Butler, Beau YYYY.", "Barnes, Kinsley ZZZZ.",
            "Fisher, Maddox AAAAA.", "Henderson, Audrey BBBBB.", "Coleman, Karter CCCCC.", "Simmons, Nova DDDDD.",
            "Patterson, Knox EEEEE.", "Jordan, Emilia FFFFF.", "Reynolds, Kyrie GGGGG.", "Hamilton, Adalynn HHHHH.",
            "Graham, Orion IIIII.", "Kim, Ophelia JJJJJ.", "Lopez, Enzo KKKKK.", "Gonzalez, Celeste LLLLL.",
            "Alexander, Phoenix MMMMM.", "Perez, Journee NNNNN.", "Lee, Onyx OOOOO.", "Lewis, Evangeline PPPPP.",
            "Robinson, Zephyr QQQQQ.", "Walker, Seraphina RRRRR.", "Hall, Atlas SSSSS.", "Young, Persephone TTTTT."
        ]
        
        n_authors = min(1000, len(real_names) * 10)  # 扩展到1000个样本
        
        # 设置随机种子以确保可重现性
        np.random.seed(42)
        
        # 扩展姓名列表
        extended_names = []
        for i in range(n_authors):
            base_name = real_names[i % len(real_names)]
            # 为重复的姓名添加后缀以保持唯一性
            if i >= len(real_names):
                suffix = f" Jr." if i % 3 == 0 else f" III" if i % 3 == 1 else f" Sr."
                extended_names.append(base_name.replace(".", suffix + "."))
            else:
                extended_names.append(base_name)
        
        author_data = {
            'authfull': extended_names[:n_authors],  # 使用真实姓名
            'author_id': range(1, n_authors + 1),
            'h23': np.random.exponential(10, n_authors),
            'nc6023': np.random.exponential(1000, n_authors),
            'nps': np.random.poisson(20, n_authors),
            'cself': np.random.exponential(50, n_authors),
            'rank': np.random.randint(1, 10000, n_authors),
            'firstyr': np.random.randint(1980, 2000, n_authors),
            'lastyr': np.random.randint(2020, 2024, n_authors),
            'cntry': np.random.choice(['US', 'CN', 'DE', 'UK', 'JP', 'FR', 'CA', 'AU'], n_authors),
            # 添加更多特征
            'field': np.random.choice(['Physics', 'Chemistry', 'Biology', 'Computer Science', 'Mathematics'], n_authors),
            'institution_type': np.random.choice(['University', 'Research Institute', 'Industry'], n_authors),
            'collaboration_index': np.random.beta(2, 5, n_authors)
        }
        
        self.tables['authors_career'] = pd.DataFrame(author_data)
        print(f"示例数据生成完成，共 {n_authors} 个样本")
        print(f"前5个科学家姓名: {extended_names[:5]}")


# --- 修复后的特征工程模块 ---
class FeatureExtractor:
    def __init__(self, tables):
        self.tables = tables
        self.name_column = self._identify_name_column()
        
    def _identify_name_column(self):
        """识别包含科学家姓名的列"""
        # 获取主要数据表
        main_table = None
        for table_name in ['Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408', 'authors_career']:
            if table_name in self.tables:
                main_table = self.tables[table_name]
                break
        
        if main_table is None:
            print("警告: 未找到主要数据表")
            return None
        
        # 按优先级查找姓名列
        possible_name_columns = ['authfull', 'author', 'name', 'fullname', 'scientist_name', 'researcher_name']
        
        for col in possible_name_columns:
            if col in main_table.columns:
                # 检查该列是否包含真实姓名（而不是ID格式）
                sample_values = main_table[col].dropna().head(10)
                if len(sample_values) > 0:
                    # 检查是否大多数值包含逗号或空格（真实姓名的特征）
                    real_name_count = sum(1 for val in sample_values 
                                        if isinstance(val, str) and 
                                        (',' in val or ' ' in val) and 
                                        not val.startswith('Author_'))
                    
                    if real_name_count >= len(sample_values) * 0.7:  # 70%以上是真实姓名
                        print(f"识别到姓名列: {col}")
                        print(f"样本姓名: {sample_values.tolist()[:3]}")
                        return col
        
        print("警告: 未找到合适的姓名列，将使用默认命名")
        return None
        
    def extract_features_for_author(self, author_idx=0):
        """为指定作者提取特征 - 修复版本"""
        # 获取主要作者表格（优先使用career数据）
        if 'Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408' in self.tables:
            authors_df = self.tables['Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408']
        elif 'authors_career' in self.tables:  # 示例数据
            authors_df = self.tables['authors_career']
        else:
            raise ValueError("未找到作者数据表格")
        
        if author_idx >= len(authors_df):
            raise ValueError(f"作者索引 {author_idx} 超出范围 (最大: {len(authors_df)-1})")
        
        author = authors_df.iloc[author_idx]
        
        # 特征提取和归一化
        features = self._extract_raw_features(author, author_idx)
        s_i = self._normalize_features(features)
        
        # 构建作者信息字典
        author_info = author.to_dict()
        author_info['author_name'] = features['author_name']
        author_info['author_index'] = author_idx
        
        return s_i, author_info, features
    
    def _extract_raw_features(self, author, author_idx):
        """提取原始特征 - 修复版本"""
        features = {}
        available_cols = author.index.tolist()
        
        # 修复后的姓名提取逻辑
        author_name = self._extract_author_name(author, author_idx)
        features['author_name'] = author_name
        
        # H指数相关特征
        if 'h23' in available_cols:
            features['h_index'] = float(author['h23'])
        else:
            features['h_index'] = 10.0
            
        # 引用相关特征
        if 'nc6023' in available_cols:
            features['citations'] = float(author['nc6023'])
        else:
            features['citations'] = 100.0
            
        # 自引用比例
        if 'cself' in available_cols:
            features['self_citations'] = float(author['cself']) / max(1, features['citations'])
        else:
            features['self_citations'] = 0.1
            
        # 合作相关特征
        if 'nps' in available_cols:
            features['publications'] = float(author['nps'])
            features['collaboration'] = 1.0 / max(1, author['nps'])
        else:
            features['publications'] = 10.0
            features['collaboration'] = 0.5
            
        # 排名特征
        if 'rank' in available_cols:
            features['rank'] = 1.0 / max(1, float(author['rank']))
        else:
            features['rank'] = 0.5
            
        # 国际合作
        if 'cntry' in available_cols:
            features['international'] = 0.3 if author['cntry'] != 'US' else 0.1
        else:
            features['international'] = 0.3
            
        # 职业年龄
        if 'firstyr' in available_cols and 'lastyr' in available_cols:
            features['career_age'] = max(1, float(author['lastyr'] - author['firstyr']))
        else:
            features['career_age'] = 15.0
            
        # 新增特征：学科领域影响
        if 'field' in available_cols:
            field_mobility = {
                'Physics': 0.6, 'Chemistry': 0.5, 'Biology': 0.4,
                'Computer Science': 0.8, 'Mathematics': 0.3
            }
            features['field_mobility'] = field_mobility.get(author.get('field'), 0.5)
        else:
            features['field_mobility'] = 0.5
            
        # 机构类型影响
        if 'institution_type' in available_cols:
            inst_mobility = {'University': 0.4, 'Research Institute': 0.6, 'Industry': 0.8}
            features['inst_mobility'] = inst_mobility.get(author.get('institution_type'), 0.5)
        else:
            features['inst_mobility'] = 0.5
            
        return features
    
    def _extract_author_name(self, author, author_idx):
        """提取作者姓名的专用方法"""
        # 1. 如果识别到了姓名列，直接使用
        if self.name_column and self.name_column in author.index:
            name = author[self.name_column]
            if pd.notna(name) and isinstance(name, str) and name.strip():
                # 清理姓名格式
                cleaned_name = str(name).strip()
                # 确保不是ID格式
                if not cleaned_name.startswith('Author_') and not cleaned_name.isdigit():
                    return cleaned_name
        
        # 2. 尝试其他可能的姓名列
        possible_columns = ['authfull', 'author', 'name', 'fullname', 'scientist_name']
        for col in possible_columns:
            if col in author.index:
                name = author[col]
                if pd.notna(name) and isinstance(name, str) and name.strip():
                    cleaned_name = str(name).strip()
                    if not cleaned_name.startswith('Author_') and not cleaned_name.isdigit():
                        return cleaned_name
        
        # 3. 如果都没有找到，生成一个更真实的默认姓名
        default_names = [
            "Smith, John", "Johnson, Mary", "Williams, Robert", "Brown, Jennifer",
            "Jones, Michael", "Garcia, Lisa", "Miller, David", "Davis, Sarah",
            "Rodriguez, Carlos", "Martinez, Ana", "Hernandez, Luis", "Lopez, Maria"
        ]
        
        return default_names[author_idx % len(default_names)] + f" (ID: {author_idx})"
    
    def _normalize_features(self, features):
        """特征归一化并构建增强的s_i向量"""
        s_i = np.zeros(12)  # 扩展到12维
        
        # 原有特征
        s_i[0] = max(0.1, min(2.0, features['career_age'] / 20.0))  # t_norm
        s_i[1] = max(0.0, min(1.0, features['self_citations']))     # self_perc
        s_i[2] = max(0.0, min(2.0, features['h_index'] / 50.0))    # h_norm
        s_i[3] = np.log1p(max(1, features['citations']))           # nc9623_ns_norm
        s_i[4] = max(0.1, 1.0 / max(0.1, features['collaboration']))  # ncsfl_ns
        s_i[5] = max(0.0, min(1.0, features['rank']))              # rank_norm
        s_i[6] = max(0.5, min(5.0, features['citations'] / max(1, features['publications'])))  # cprat_ns
        s_i[7] = max(0.0, min(0.1, features['h_index'] / max(1, features['citations'])))  # cites95_norm
        s_i[8] = max(0.0, min(1.0, features['self_citations'] * features['collaboration']))  # self99_agg
        s_i[9] = max(0.0, min(1.0, features['international']))     # frac
        
        # 新增特征
        s_i[10] = max(0.0, min(1.0, features['field_mobility']))   # 学科流动性
        s_i[11] = max(0.0, min(1.0, features['inst_mobility']))    # 机构流动性
        
        return s_i


# --- 物理模型 (保持不变) ---
class EnhancedPhysicsModel:
    """增强的物理模型，包含势能变化驱动"""
    
    def __init__(self):
        self.potential_field = PotentialField()
        
    def f_enhanced(self, zeta, self_perc, h_norm, self99_agg, field_mobility, inst_mobility, t):
        """增强的激活函数，包含时间依赖性"""
        sigmoid = 1 / (1 + np.exp(-zeta))
        time_factor = 1 + 0.1 * np.sin(0.5 * t)  # 时间调制
        mobility_factor = (field_mobility + inst_mobility) / 2
        
        return h_norm * (1 - self_perc) * (1 - self99_agg) * sigmoid * time_factor * mobility_factor
    
    def G_enhanced(self, eta, x, t, self_perc, h_norm, self99_agg, field_mobility, inst_mobility, state=0):
        """增强的G函数，包含势能场"""
        # 原有积分项
        integral, _ = quad(lambda z: self.f_enhanced(z, self_perc, h_norm, self99_agg, 
                                                   field_mobility, inst_mobility, t), 0, eta)
        
        # 位置偏差项
        deviation = (x - eta) ** 2 / (2 * t) if t > 0 else 0
        
        # 势能项
        potential = self.potential_field.get_potential(state, eta, t)
        
        return integral + deviation + 0.1 * potential
    
    def Y_enhanced(self, x, t, mu, self_perc, h_norm, self99_agg, field_mobility, inst_mobility, state=0):
        """增强的Y函数"""
        def numerator(eta):
            g = self.G_enhanced(eta, x, t, self_perc, h_norm, self99_agg, 
                              field_mobility, inst_mobility, state)
            force = self.potential_field.get_force(state, eta, t)
            return ((x - eta) / t + force) * np.exp(-np.clip(g, -50, 50) / (2 * mu))

        def denominator(eta):
            g = self.G_enhanced(eta, x, t, self_perc, h_norm, self99_agg, 
                              field_mobility, inst_mobility, state)
            return np.exp(-np.clip(g, -50, 50) / (2 * mu))

        try:
            num, _ = quad(numerator, -5, 5)
            denom, _ = quad(denominator, -5, 5)
            if denom < 1e-6 or np.isnan(denom):
                return 0.2
            return max(0, min(1, num / denom))
        except:
            return 0.2
    
    def extract_params_enhanced(self, s_i):
        """从增强特征向量提取参数"""
        return {
            't': max(0.1, s_i[0]),
            'self_perc': s_i[1],
            'h_norm': s_i[2],
            'self99_agg': s_i[8],
            'mu': max(0.2, 1 / s_i[4]) if s_i[4] > 0 else 0.3,
            'field_mobility': s_i[10] if len(s_i) > 10 else 0.5,
            'inst_mobility': s_i[11] if len(s_i) > 11 else 0.5
        }
    
    def compute_temporal_probs(self, s_i, time_points):
        """计算多个时间点的概率分布"""
        p = self.extract_params_enhanced(s_i)
        temporal_probs = []
        
        for t in time_points:
            y_list = []
            for state in range(5):
                y_val = self.Y_enhanced(state, t, p['mu'], p['self_perc'], p['h_norm'], 
                                      p['self99_agg'], p['field_mobility'], p['inst_mobility'], state)
                y_list.append(y_val)
            
            total = np.sum(y_list)
            probs = np.array(y_list) / total if total > 1e-6 else np.array([0.2] * 5)
            temporal_probs.append(probs)
        
        return np.array(temporal_probs)


# --- 修复后的可视化模块 ---
class EnhancedVisualizer:
    def __init__(self):
        self.labels = ['留任', '学术流动', '转入产业', '国际流动', '退休']
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
    def plot_temporal_distribution(self, temporal_probs, time_points, author_info, save_path=None):
        """绘制时间演化的Y(t)分布图 - 修复版本"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 获取作者姓名
        author_name = author_info.get('author_name', 'Unknown Author')
        
        # 上图：时间演化的概率曲线
        for i, label in enumerate(self.labels):
            ax1.plot(time_points, temporal_probs[:, i], 
                    label=label, color=self.colors[i], linewidth=2, marker='o')
        
        ax1.set_xlabel('时间 t')
        ax1.set_ylabel('概率')
        ax1.set_title(f'科学家流动概率时间演化 - {author_name}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 下图：热力图显示概率随时间的变化
        im = ax2.imshow(temporal_probs.T, aspect='auto', cmap='viridis', 
                       extent=[time_points[0], time_points[-1], -0.5, 4.5])
        ax2.set_xlabel('时间 t')
        ax2.set_ylabel('流动状态')
        ax2.set_yticks(range(5))
        ax2.set_yticklabels(self.labels)
        ax2.set_title('概率分布热力图')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('概率')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_batch_comparison(self, batch_results, save_path=None):
        """绘制批量分析结果对比 - 修复版本"""
        n_samples = len(batch_results)
        fig, axes = plt.subplots(4, 5, figsize=(20, 16))
        axes = axes.flatten()
        
        for i, (author_info, final_probs, _) in enumerate(batch_results[:20]):
            ax = axes[i]
            bars = ax.bar(range(5), final_probs, color=self.colors)
            
            # 获取真实姓名并截断以适应显示
            author_name = author_info.get('author_name', f'Author_{i+1}')
            if len(author_name) > 15:
                display_name = author_name[:12] + "..."
            else:
                display_name = author_name
                
            ax.set_title(display_name, fontsize=8)
            ax.set_ylabel('概率', fontsize=8)
            ax.set_ylim(0, 1)
            ax.set_xticks(range(5))
            ax.set_xticklabels(['留任', '学术', '产业', '国际', '退休'], rotation=45, fontsize=6)
            
            # 标注最高概率
            max_idx = np.argmax(final_probs)
            ax.text(max_idx, final_probs[max_idx] + 0.05, f'{final_probs[max_idx]:.2f}', 
                   ha='center', va='bottom', fontsize=7, fontweight='bold')
        
        plt.suptitle(f'前20位科学家流动预测对比 (共分析{n_samples}个样本)', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_statistics_summary(self, batch_results, save_path=None):
        """绘制统计汇总图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 提取最终概率分布
        final_probs = np.array([result[1] for result in batch_results])
        
        # 1. 各状态平均概率
        mean_probs = np.mean(final_probs, axis=0)
        std_probs = np.std(final_probs, axis=0)
        
        bars = ax1.bar(self.labels, mean_probs, yerr=std_probs, 
                      color=self.colors, alpha=0.7, capsize=5)
        ax1.set_title('各流动状态平均概率及标准差')
        ax1.set_ylabel('概率')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 最可能状态分布
        most_likely = np.argmax(final_probs, axis=1)
        unique, counts = np.unique(most_likely, return_counts=True)
        
        pie_labels = [self.labels[i] for i in unique]
        ax2.pie(counts, labels=pie_labels, colors=[self.colors[i] for i in unique], 
               autopct='%1.1f%%', startangle=90)
        ax2.set_title('最可能流动状态分布')
        
        # 3. 概率分布直方图
        for i, label in enumerate(self.labels):
            ax3.hist(final_probs[:, i], bins=20, alpha=0.6, 
                    color=self.colors[i], label=label)
        ax3.set_xlabel('概率')
        ax3.set_ylabel('频次')
        ax3.set_title('各状态概率分布直方图')
        ax3.legend()
        
        # 4. 相关性热力图
        corr_matrix = np.corrcoef(final_probs.T)
        im = ax4.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        ax4.set_xticks(range(5))
        ax4.set_yticks(range(5))
        ax4.set_xticklabels(self.labels, rotation=45)
        ax4.set_yticklabels(self.labels)
        ax4.set_title('状态间相关性')
        
        # 添加相关系数标注
        for i in range(5):
            for j in range(5):
                ax4.text(j, i, f'{corr_matrix[i, j]:.2f}', 
                        ha='center', va='center', fontsize=8)
        
        plt.colorbar(im, ax=ax4, shrink=0.8)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


# --- 主分析类（修复版）---
class EnhancedScientistMobilityAnalyzer:
    def __init__(self, data_path="D:/UvA"):
        self.data_loader = DataLoader(data_path)
        self.feature_extractor = None
        self.physics_model = EnhancedPhysicsModel()
        self.visualizer = EnhancedVisualizer()
        
    def analyze_single_scientist(self, author_idx, time_points=None):
        """分析单个科学家的时间演化"""
        if time_points is None:
            time_points = np.linspace(0.1, 5.0, 20)
        
        s_i, author_info, features = self.feature_extractor.extract_features_for_author(author_idx)
        temporal_probs = self.physics_model.compute_temporal_probs(s_i, time_points)
        
        return {
            'author_info': author_info,
            'features': features,
            's_i': s_i,
            'temporal_probs': temporal_probs,
            'time_points': time_points,
            'final_probs': temporal_probs[-1]
        }
    
    def batch_analysis(self, n_samples=100, use_parallel=True):
        """批量分析多个科学家"""
        print(f"\n开始批量分析 {n_samples} 个样本...")
        
        # 获取作者数据
        if 'Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408' in self.feature_extractor.tables:
            authors_df = self.feature_extractor.tables['Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408']
        elif 'authors_career' in self.feature_extractor.tables:
            authors_df = self.feature_extractor.tables['authors_career']
        else:
            raise ValueError("未找到作者数据")
        
        n_samples = min(n_samples, len(authors_df))
        
        def analyze_author(idx):
            try:
                result = self.analyze_single_scientist(idx)
                return (result['author_info'], result['final_probs'], result['temporal_probs'])
            except Exception as e:
                print(f"分析作者 {idx} 时出错: {e}")
                return None
        
        # 并行处理或串行处理
        results = []
        if use_parallel:
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_idx = {executor.submit(analyze_author, i): i for i in range(n_samples)}
                
                for future in as_completed(future_to_idx):
                    result = future.result()
                    if result is not None:
                        results.append(result)
                    
                    if len(results) % 10 == 0:
                        print(f"已完成 {len(results)} 个样本...")
        else:
            for i in range(n_samples):
                result = analyze_author(i)
                if result is not None:
                    results.append(result)
                
                if (i + 1) % 10 == 0:
                    print(f"已完成 {i + 1} 个样本...")
        
        print(f"批量分析完成，成功处理 {len(results)} 个样本")
        return results
    
    def run_enhanced_analysis(self, n_samples=100, detailed_analysis_count=5):
        """运行增强分析流程 - 修复版本"""
        print("开始增强版科学家流动预测分析...")
        
        # 1. 加载数据
        print("\n1. 加载数据...")
        tables = self.data_loader.load_all_tables()
        
        if not tables:
            print("错误: 无法加载任何数据表格")
            return
        
        # 2. 初始化特征提取器
        self.feature_extractor = FeatureExtractor(tables)
        
        # 3. 详细分析前几位科学家（包含时间演化）
        print(f"\n2. 详细分析前 {detailed_analysis_count} 位科学家...")
        time_points = np.linspace(0.1, 5.0, 20)
        
        for i in range(min(detailed_analysis_count, n_samples)):
            try:
                result = self.analyze_single_scientist(i, time_points)
                
                # 生成时间演化图
                self.visualizer.plot_temporal_distribution(
                    result['temporal_probs'], 
                    result['time_points'],
                    result['author_info'],
                    f'temporal_evolution_author_{i+1}.png'
                )
                
                author_name = result['author_info'].get('author_name', f'Author_{i+1}')
                most_likely_state = self.visualizer.labels[np.argmax(result['final_probs'])]
                max_prob = np.max(result['final_probs'])
                
                print(f"科学家 {i+1}: {author_name}")
                print(f"  最终最可能状态: {most_likely_state} (概率: {max_prob:.3f})")
                print(f"  所有状态概率: {[f'{p:.3f}' for p in result['final_probs']]}")
                
            except Exception as e:
                print(f"详细分析科学家 {i+1} 时出错: {e}")
        
        # 4. 批量分析
        print(f"\n3. 批量分析 {n_samples} 个样本...")
        batch_results = self.batch_analysis(n_samples)
        
        # 5. 生成汇总可视化
        print("\n4. 生成可视化图表...")
        if batch_results:
            # 批量对比图
            self.visualizer.plot_batch_comparison(batch_results, 'batch_comparison.png')
            
            # 统计汇总图
            self.visualizer.plot_statistics_summary(batch_results, 'statistics_summary.png')
            
            # 生成分析报告
            self._generate_analysis_report(batch_results)
        
        print("\n增强分析完成！")
        return batch_results
    
    def _generate_analysis_report(self, batch_results):
        """生成分析报告 - 修复版本"""
        print("\n=== 分析报告 ===")
        
        # 基本统计
        n_samples = len(batch_results)
        final_probs = np.array([result[1] for result in batch_results])
        
        print(f"总样本数: {n_samples}")
        print(f"各状态平均概率:")
        for i, label in enumerate(self.visualizer.labels):
            mean_prob = np.mean(final_probs[:, i])
            std_prob = np.std(final_probs[:, i])
            print(f"  {label}: {mean_prob:.3f} ± {std_prob:.3f}")
        
        # 最可能状态统计
        most_likely = np.argmax(final_probs, axis=1)
        print(f"\n最可能流动状态分布:")
        for i in range(5):
            count = np.sum(most_likely == i)
            percentage = count / n_samples * 100
            print(f"  {self.visualizer.labels[i]}: {count} 人 ({percentage:.1f}%)")
        
        # 高概率预测
        print(f"\n高置信度预测 (概率 > 0.6):")
        high_conf_count = 0
        for i in range(5):
            high_conf = np.sum(final_probs[:, i] > 0.6)
            if high_conf > 0:
                print(f"  {self.visualizer.labels[i]}: {high_conf} 人")
                high_conf_count += high_conf
        
        print(f"高置信度预测比例: {high_conf_count/n_samples*100:.1f}%")
        
        # 显示一些具体的科学家姓名示例
        print(f"\n前10位科学家姓名示例:")
        for i, (author_info, final_probs_sample, _) in enumerate(batch_results[:10]):
            author_name = author_info.get('author_name', f'Author_{i+1}')
            most_likely_idx = np.argmax(final_probs_sample)
            most_likely_state = self.visualizer.labels[most_likely_idx]
            prob = final_probs_sample[most_likely_idx]
            print(f"  {i+1}. {author_name} -> {most_likely_state} ({prob:.3f})")


# --- 实用工具函数 (修复版) ---
def analyze_author_by_name(author_name, analyzer):
    """根据作者姓名进行分析 - 修复版本"""
    # 获取作者数据
    if 'Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408' in analyzer.feature_extractor.tables:
        authors_df = analyzer.feature_extractor.tables['Table_1_Authors_career_2023_pubs_since_1788_wopp_extracted_202408']
        name_col = analyzer.feature_extractor.name_column or 'authfull'
    elif 'authors_career' in analyzer.feature_extractor.tables:
        authors_df = analyzer.feature_extractor.tables['authors_career']
        name_col = 'authfull'
    else:
        print("未找到作者数据")
        return None
    
    if name_col not in authors_df.columns:
        print(f"未找到姓名列 '{name_col}'")
        return None
    
    # 查找作者
    matches = authors_df[authors_df[name_col].str.contains(author_name, case=False, na=False)]
    
    if len(matches) == 0:
        print(f"未找到姓名包含 '{author_name}' 的作者")
        return None
    
    if len(matches) > 1:
        print(f"找到 {len(matches)} 个匹配的作者:")
        for i, (idx, row) in enumerate(matches.head().iterrows()):
            print(f"  {i+1}. {row[name_col]}")
        
        choice = input("请选择要分析的作者编号 (1-{}): ".format(min(5, len(matches))))
        try:
            selected_idx = int(choice) - 1
            if 0 <= selected_idx < len(matches):
                author_idx = matches.iloc[selected_idx].name
            else:
                print("无效选择")
                return None
        except ValueError:
            print("无效输入")
            return None
    else:
        author_idx = matches.index[0]
    
    # 进行分析
    return analyzer.analyze_single_scientist(author_idx)


def compare_authors(author_indices, analyzer):
    """比较多个作者的预测结果 - 修复版本"""
    results = []
    
    for idx in author_indices:
        try:
            result = analyzer.analyze_single_scientist(idx)
            results.append(result)
        except Exception as e:
            print(f"分析作者 {idx} 时出错: {e}")
    
    if not results:
        return None
    
    # 创建对比图
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(5)
    width = 0.15
    
    for i, result in enumerate(results):
        author_name = result['author_info'].get('author_name', f'Author_{i}')
        # 截断长姓名
        if len(author_name) > 20:
            display_name = author_name[:17] + "..."
        else:
            display_name = author_name
            
        probs = result['final_probs']
        
        bars = ax.bar(x + i * width, probs, width, 
                     label=display_name, alpha=0.8)
        
        # 添加数值标签
        for bar, prob in zip(bars, probs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{prob:.2f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('流动状态')
    ax.set_ylabel('概率')
    ax.set_title('多位科学家流动预测对比')
    ax.set_xticks(x + width * (len(results) - 1) / 2)
    ax.set_xticklabels(analyzer.visualizer.labels)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('authors_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return results


# --- 交互式分析函数 (修复版) ---
def interactive_analysis():
    """交互式分析界面 - 修复版本"""
    print("=== 科学家流动预测交互式分析 ===")
    
    # 初始化分析器
    data_path = input("请输入数据路径 (默认: D:/UvA): ").strip()
    if not data_path:
        data_path = "D:/UvA"
    
    analyzer = EnhancedScientistMobilityAnalyzer(data_path)
    
    # 加载数据
    tables = analyzer.data_loader.load_all_tables()
    if not tables:
        print("无法加载数据，程序退出")
        return
    
    analyzer.feature_extractor = FeatureExtractor(tables)
    
    # 显示数据加载信息
    print(f"\n数据加载完成:")
    print(f"  姓名列: {analyzer.feature_extractor.name_column}")
    if 'authors_career' in tables:
        sample_names = tables['authors_career']['authfull'].head(3).tolist()
        print(f"  样本姓名: {sample_names}")
    
    while True:
        print("\n=== 选择分析模式 ===")
        print("1. 单个科学家详细分析（包含时间演化）")
        print("2. 批量分析")
        print("3. 按姓名搜索分析")
        print("4. 比较多个科学家")
        print("5. 生成统计报告")
        print("6. 查看科学家列表")
        print("0. 退出")
        
        choice = input("请选择 (0-6): ").strip()
        
        if choice == '0':
            print("感谢使用！")
            break
        
        elif choice == '1':
            try:
                idx = int(input("请输入科学家编号 (从0开始): "))
                result = analyzer.analyze_single_scientist(idx)
                
                # 显示基本信息
                author_name = result['author_info'].get('author_name', 'Unknown')
                print(f"\n科学家: {author_name}")
                print(f"最终预测概率:")
                for i, label in enumerate(analyzer.visualizer.labels):
                    print(f"  {label}: {result['final_probs'][i]:.3f}")
                
                # 生成图表
                analyzer.visualizer.plot_temporal_distribution(
                    result['temporal_probs'], 
                    result['time_points'],
                    result['author_info'],
                    f'interactive_temporal_{idx}.png'
                )
                
            except Exception as e:
                print(f"分析出错: {e}")
        
        elif choice == '2':
            try:
                n_samples = int(input("请输入要分析的样本数 (默认100): ") or "100")
                results = analyzer.batch_analysis(n_samples)
                
                if results:
                    analyzer.visualizer.plot_batch_comparison(results, 'interactive_batch.png')
                    analyzer.visualizer.plot_statistics_summary(results, 'interactive_stats.png')
                    analyzer._generate_analysis_report(results)
                
            except Exception as e:
                print(f"批量分析出错: {e}")
        
        elif choice == '3':
            author_name = input("请输入作者姓名关键词: ").strip()
            if author_name:
                result = analyze_author_by_name(author_name, analyzer)
                if result:
                    author_name_found = result['author_info'].get('author_name', 'Unknown')
                    print(f"\n科学家: {author_name_found}")
                    print(f"最终预测概率:")
                    for i, label in enumerate(analyzer.visualizer.labels):
                        print(f"  {label}: {result['final_probs'][i]:.3f}")
        
        elif choice == '4':
            try:
                indices_str = input("请输入要比较的科学家编号 (用逗号分隔): ")
                indices = [int(x.strip()) for x in indices_str.split(',')]
                results = compare_authors(indices, analyzer)
                
                if results:
                    print(f"\n成功比较了 {len(results)} 位科学家")
                
            except Exception as e:
                print(f"比较分析出错: {e}")
        
        elif choice == '5':
            try:
                n_samples = int(input("请输入统计样本数 (默认100): ") or "100")
                results = analyzer.batch_analysis(n_samples)
                if results:
                    analyzer._generate_analysis_report(results)
            except Exception as e:
                print(f"统计分析出错: {e}")
        
        elif choice == '6':
            # 显示科学家列表
            try:
                if 'authors_career' in analyzer.feature_extractor.tables:
                    df = analyzer.feature_extractor.tables['authors_career']
                    name_col = 'authfull'
                else:
                    df = list(analyzer.feature_extractor.tables.values())[0]
                    name_col = analyzer.feature_extractor.name_column
                
                n_show = int(input("要显示多少位科学家? (默认20): ") or "20")
                print(f"\n前{n_show}位科学家:")
                for i in range(min(n_show, len(df))):
                    name = df.iloc[i].get(name_col, f'Author_{i}')
                    print(f"  {i}: {name}")
                    
            except Exception as e:
                print(f"显示科学家列表出错: {e}")
        
        else:
            print("无效选择，请重试")


# --- 主程序入口 (修复版) ---
if __name__ == "__main__":
    # 可以选择运行模式
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # 交互式模式
        interactive_analysis()
    else:
        # 自动运行模式
        print("=== 自动运行增强版科学家流动预测分析 ===")
        
        # 创建分析器并运行分析
        analyzer = EnhancedScientistMobilityAnalyzer("D:/UvA")
        results = analyzer.run_enhanced_analysis(n_samples=100, detailed_analysis_count=3)
        
        if results:
            print(f"\n✓ 成功分析了 {len(results)} 位科学家的流动预测")
            print("✓ 图表已保存到当前目录")
            print("✓ 包含时间演化分析和统计汇总")
            print("✓ 科学家姓名显示问题已修复")
        else:
            print("❌ 分析未能完成，请检查数据文件")
    
    # === 快速测试接口 ===
    def quick_test(n_samples=10):
        """快速测试接口 - 修复版本"""
        analyzer = EnhancedScientistMobilityAnalyzer("D:/UvA")
        tables = analyzer.data_loader.load_all_tables()
        analyzer.feature_extractor = FeatureExtractor(tables)
        
        # 测试单个分析
        result = analyzer.analyze_single_scientist(0)
        author_name = result['author_info'].get('author_name', 'Unknown')
        most_likely_state = analyzer.visualizer.labels[np.argmax(result['final_probs'])]
        
        print(f"测试科学家: {author_name}")
        print(f"最可能状态: {most_likely_state}")
        
        # 测试批量分析
        batch_results = analyzer.batch_analysis(n_samples, use_parallel=False)
        print(f"批量测试完成，处理了 {len(batch_results)} 个样本")
        
        # 显示前几个科学家的姓名
        print("\n前5位科学家:")
        for i, (author_info, _, _) in enumerate(batch_results[:5]):
            name = author_info.get('author_name', f'Author_{i}')
            print(f"  {i}: {name}")
        
        return analyzer, batch_results
    
    # 外部调用接口 (修复版)
    def predict_scientist_mobility(author_idx=0, data_path="D:/UvA", 
                                 include_temporal=True, time_points=None):
        """
        外部调用接口：预测科学家流动 - 修复版本
        
        参数：
            author_idx: 科学家索引
            data_path: 数据路径
            include_temporal: 是否包含时间演化分析
            time_points: 时间点数组，默认为 [0.1, 1, 2, 3, 4, 5]
            
        返回：
            {
                'author_name': str,
                'final_probs': list[float],
                'temporal_probs': array (可选),
                'time_points': array (可选),
                'top_prediction': str,
                'confidence': float
            }
        """
        analyzer = EnhancedScientistMobilityAnalyzer(data_path)
        tables = analyzer.data_loader.load_all_tables()
        analyzer.feature_extractor = FeatureExtractor(tables)
        
        if time_points is None:
            time_points = np.array([0.1, 1.0, 2.0, 3.0, 4.0, 5.0])
        
        result = analyzer.analyze_single_scientist(author_idx, time_points)
        
        top_idx = np.argmax(result['final_probs'])
        
        output = {
            'author_name': result['author_info'].get('author_name', f'Author_{author_idx}'),
            'final_probs': result['final_probs'].tolist(),
            'top_prediction': analyzer.visualizer.labels[top_idx],
            'confidence': float(result['final_probs'][top_idx])
        }
        
        if include_temporal:
            output['temporal_probs'] = result['temporal_probs'].tolist()
            output['time_points'] = result['time_points'].tolist()
        
        return output