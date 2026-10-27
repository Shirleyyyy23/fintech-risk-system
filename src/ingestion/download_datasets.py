"""
W1 D1 - 数据采集：下载两个 HF 数据集并落盘到 data/raw/

数据集：
  1) 信用风险评估：Uris001/credit-risk-eda
     - 2026-03-29 发布，约 31,521 行 / 15 字段，MIT，raw 可解释（收入/利率/贷款比/信用历史/先前违约…）
     - 注意：该集是"申请人快照"，通常无显式时间列；时间主线由下方 AML 数据集承担。
  2) 反洗钱 AML：VynFi/aml-100k
     - 2026-04 发布，约 75 万笔交易，含时间戳/行为偏置，Apache 2.0。
     - 每笔交易带时间 → 满足老师"数据需有时间维度"的硬指标。

运行（在 D:\\fintech-risk-system 下、venv 激活）：
   python src/ingestion/download_datasets.py

中国大陆若直接连 huggingface.co 超时，脚本已自动把 HF_ENDPOINT 设为 hf-mirror.com 镜像。
如需换回官方源，把下方 HF_ENDPOINT 行注释掉即可。
"""

import os
from pathlib import Path

# 国内访问 Hugging Face 用镜像，避免超时（官方源可注释此行）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from datasets import load_dataset

# 项目根目录：本文件位于 src/ingestion/，向上两级即项目根
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# 每个数据集的校验要求（min_rows / min_cols 对应老师硬指标≥1万条、≥8字段）
DATASETS = {
    "credit_risk": {
        "hf_id": "Uris001/credit-risk-eda",
        "out": RAW / "credit_risk_eda.csv",
        "min_rows": 10000,
        "min_cols": 8,
        "require_time": False,   # 信用集本就无时间列，不强制
        "time_hints": ["date", "issue", "time", "month", "year"],
    },
    "aml": {
        "hf_id": "VynFi/aml-100k",
        "out": RAW / "aml_100k.csv",
        "min_rows": 10000,
        "min_cols": 8,
        "require_time": True,    # AML 必须含时间列（硬指标）
        "time_hints": ["timestamp", "time", "date", "txn_time", "transaction_time"],
    },
}


def _to_df(ds):
    """把 load_dataset 的返回统一转成 pandas DataFrame。"""
    # DatasetDict（多 split）→ 取 train，否则取第一个 split
    if hasattr(ds, "keys"):
        split = "train" if "train" in ds else list(ds.keys())[0]
        return ds[split].to_pandas()
    # 单 Dataset
    return ds.to_pandas()


def _find_time_col(columns, hints):
    cols = [c.lower() for c in columns]
    for h in hints:
        for c in cols:
            if h in c:
                # 返回原始大小写列名
                return columns[cols.index(c)]
    return None


def main():
    all_ok = True
    for key, cfg in DATASETS.items():
        print(f"\n=== 下载 [{key}] : {cfg['hf_id']} ===")
        try:
            ds = load_dataset(cfg["hf_id"])
        except Exception as e:
            print(f"  ✗ 下载失败：{e}")
            all_ok = False
            continue

        df = _to_df(ds)
        n_rows, n_cols = df.shape
        time_col = _find_time_col(list(df.columns), cfg["time_hints"])

        # 落盘
        df.to_csv(cfg["out"], index=False, encoding="utf-8")
        print(f"  ✓ 已保存：{cfg['out']}")
        print(f"    行数={n_rows:,}  列数={n_cols}")
        print(f"    字段：{list(df.columns)}")
        print(f"    时间列：{time_col if time_col else '（未检测到）'}")

        # 校验
        checks = []
        checks.append(("行数≥%d" % cfg["min_rows"], n_rows >= cfg["min_rows"]))
        checks.append(("字段≥%d" % cfg["min_cols"], n_cols >= cfg["min_cols"]))
        if cfg["require_time"]:
            checks.append(("存在时间列", time_col is not None))
        else:
            checks.append(("时间列(信息项)", True))  # 不强制

        print("    校验：")
        ok = True
        for name, passed in checks:
            mark = "✓" if passed else "✗"
            print(f"      [{mark}] {name}")
            ok = ok and passed
        all_ok = all_ok and ok
        if not ok:
            print(f"  ✗ [{key}] 未满足老师硬指标，请检查数据集或换源！")

    print("\n" + ("全部通过 ✓ 可以进入 EDA" if all_ok else "存在未通过项 ✗ 见上"))
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
