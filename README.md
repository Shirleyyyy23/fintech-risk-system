# 金融风控智能决策系统（fintech-risk-system）

> 一个"贷前信用评分 + 贷中/贷后反洗钱监控"双引擎的银行智能风控系统。
> 独立完成《智能决策综合实践》实验；目标：跑通 6 大模块 + AI 模块、学到东西、产出求职作品。
> 数据来源：Hugging Face（2026-01 后合规）；满足"≥1万条/≥8字段/含时间维度/多源集成"。

## 项目结构
```
fintech-risk-system/
├── README.md               # 本文件
├── requirements.txt        # Python 依赖
├── .gitignore
├── data/                   # 数据层（raw 不入库，processed 可入库）
│   ├── raw/                # 原始下载（HF 两个数据集）
│   ├── processed/          # 清洗后宽表
│   └── external/           # 自造维度（时间/节假日、客户桥接维）
├── sql/                    # 数仓建表与 OLAP 查询
├── notebooks/              # 探索与建模笔记本
├── src/                    # 可复用脚本（采集/预处理/建模/可视/AI）
├── models/                 # 训练好的模型与适配器
├── dashboard/              # BI 看板文件（Power BI / Tableau）
├── ai_assets/             # AI 模块素材（知识库/微调数据/提示词）
├── reports/               # 分析/设计文档（Markdown）
├── docs/                  # 环境配置与运行说明、方法日志
└── outputs/               # 图表、录屏等产出物
```

## 环境搭建（详见 docs/环境配置.md）
- Python 3.11+，虚拟环境 `venv`；依赖见 `requirements.txt`
- 数据库：本地 MySQL 8.0，库名 `fintech_risk`（Navicat 管理）
- IDE：VSCode；版本管理：GitHub

## 运行步骤（详见 docs/运行说明.md）
1. `python -m venv venv && source venv/bin/activate`（Win：`venv\Scripts\activate`）
2. `pip install -r requirements.txt`
3. 下载数据：`python src/ingestion/download_datasets.py`
4. 预处理 → 数仓 → 建模 → 可视化 → AI 模块（见 notebooks / src）

## 当前进度
- [x] Day 0：环境搭建与项目骨架
- [ ] W1：数据采集 + 预处理
- [ ] W2：数仓 + OLAP + 描述/诊断分析
- [ ] W3：预测建模 + 可视化
- [ ] W4：AI 智能模块 + 整合
- [ ] W5：buffer（作品精修/博客）

## 核心亮点（作品差异化）
- 信用评分 XGBoost + **SHAP 可解释性**（面试官最爱问"为什么这么判"）
- 反洗钱 Isolation Forest / 分类（±GNN 图神经网络）
- 统一 BI 看板（双 Tab）+ Streamlit 交互应用
- AI 助手：中文信用风控 LoRA 微调 + 洗钱手法 RAG 问答
