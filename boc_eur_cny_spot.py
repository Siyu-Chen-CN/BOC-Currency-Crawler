import argparse
import os
from datetime import datetime
from io import StringIO

import requests
import pandas as pd
import matplotlib.pyplot as plt

BOC_URL = "https://www.boc.cn/sourcedb/whpj/"
DEFAULT_TXT = "boc_eur_spot.txt"


def fetch_eur_spot_sell():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(BOC_URL, headers=headers, timeout=15)
    r.raise_for_status()

    r.encoding = "utf-8"
    dfs = pd.read_html(StringIO(r.text), attrs={"id": "priceTable"})
    if not dfs:
        raise RuntimeError("没解析到 priceTable, 可能网页结构变了")

    df = dfs[0]  # 外汇牌价表

    # 表头顺序：
    # 0货币名称 1现汇买入价 2现钞买入价 3现汇卖出价 4现钞卖出价 5中行折算价 6发布日期 7发布时间
    eur = df[df.iloc[:, 0].astype(str).str.contains("欧元", na=False)]
    if eur.empty:
        raise RuntimeError("表格里没找到“欧元”这一行")

    row = eur.iloc[0]
    spot_sell_100 = float(str(row.iloc[3]).strip())  # 现汇卖出价（每100欧元）

    boc_date_raw = str(row.iloc[6]).strip() if len(row) > 6 else ""
    boc_time = str(row.iloc[7]).strip() if len(row) > 7 else ""

    # 只保留日期部分
    boc_date = boc_date_raw[:10] if len(boc_date_raw) >= 10 else boc_date_raw

    return {
        "local_time": datetime.now().isoformat(timespec="seconds"),
        "boc_date": boc_date,               # YYYY/MM/DD
        "boc_time": boc_time,
        "spot_sell_100": spot_sell_100,     # 100 EUR -> CNY
        "spot_sell_1": spot_sell_100 / 100.0,  # 1 EUR -> CNY
    }


def already_recorded_today(path: str, boc_date: str) -> bool:
    """检查 txt 里是否已经记录过同一个 boc_date(同一天)"""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    try:
        df = pd.read_csv(path, sep="\t", dtype=str)
        if "boc_date" not in df.columns:
            return False
        # 兼容历史数据里可能带时间的情况：统一取前10位再比较
        existing = df["boc_date"].astype(str).str.slice(0, 10)
        return (existing == boc_date[:10]).any()
    except Exception:
        # 如果文件格式被手动改坏了，就不拦截
        return False


def append_txt(path: str, data: dict, force: bool = False):
    header = "\t".join(["local_time", "boc_date", "boc_time", "spot_sell_100", "spot_sell_1"])

    if (not force) and already_recorded_today(path, data["boc_date"]):
        print(f"SKIP  今天（{data['boc_date']}）已经记录过了，未重复写入。")
        return

    line = "\t".join([
        data["local_time"],
        data["boc_date"],
        data["boc_time"],
        f'{data["spot_sell_100"]:.4f}',
        f'{data["spot_sell_1"]:.6f}',
    ])

    need_header = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", encoding="utf-8") as f:
        if need_header:
            f.write(header + "\n")
        f.write(line + "\n")

    print(f"APPEND  已写入：{data['boc_date']}  卖出价(1EUR)={data['spot_sell_1']:.6f}")


def plot_txt(path: str, out_png: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file unfound:{path}(run fetch cmd first)")

    df = pd.read_csv(path, sep="\t")
    df["local_time"] = pd.to_datetime(df["local_time"], errors="coerce")
    df = df.dropna(subset=["local_time"]).sort_values("local_time")

    plt.figure()
    plt.plot(df["local_time"], df["spot_sell_1"], marker="o", label="Spot selling price (CNY / 1 EUR)")
    plt.xlabel("Time (Day)")
    plt.ylabel("Currency")
    plt.title("BOC EUR to CNY")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="欧元现汇卖出价 -> txt; 可画趋势")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="抓取一次并追加写入txt(同日默认不重复写)")
    p_fetch.add_argument("--file", default=DEFAULT_TXT)
    p_fetch.add_argument("--force", action="store_true", help="强制写入(即使同一天已记录)")

    p_plot = sub.add_parser("plot", help="读取txt并画趋势")
    p_plot.add_argument("--file", default=DEFAULT_TXT)
    p_plot.add_argument("--out", default="eur_spot_trend.png")

    args = parser.parse_args()

    if args.cmd == "fetch":
        data = fetch_eur_spot_sell()
        append_txt(args.file, data, force=args.force)
        print(f"INFO  local={data['local_time']}  boc={data['boc_date']} {data['boc_time']}")
    else:
        plot_txt(args.file, args.out)


if __name__ == "__main__":
    main()