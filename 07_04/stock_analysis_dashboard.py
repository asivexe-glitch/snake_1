import yfinance as yf
import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime, timedelta

tickers = {
    "台積電": "2330.TW",
    "聯電": "2303.TW",
    "聯發科": "2454.TW",
    "鴻海": "2317.TW",
    "台達電": "2308.TW",
    "廣達": "2382.TW",
    "日月光投控": "3711.TW",
    "中華電": "2412.TW",
}

TWII = "^TWII"
REPORT_DIR = "reports"

def ensure_report_dir():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

def fetch_data(start, end=None, interval="1d"):
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    codes = list(tickers.values())
    data = yf.download(codes + [TWII], start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    close = data["Close"]
    code_to_name = {v: k for k, v in tickers.items()}
    code_to_name[TWII] = "加權指數"
    close = close.rename(columns=code_to_name)
    volume = data.get("Volume", None)
    if volume is not None:
        volume = volume.rename(columns=code_to_name)
    return close, volume

def compute_returns(close):
    return close.pct_change().dropna()

def compute_log_returns(close):
    return np.log(close / close.shift(1)).dropna()

def rolling_correlation(returns, window=30):
    stock_names = list(tickers.keys())
    return returns[stock_names].rolling(window=window).corr(
        returns["加權指數"] if "加權指數" in returns.columns else returns.iloc[:, 0]
    )

def risk_metrics(returns, risk_free=0.015):
    metrics = {}
    for col in returns.columns:
        r = returns[col]
        metrics[col] = {
            "總報酬率(%)": round((1 + r).prod() * 100 - 100, 2),
            "年化報酬率(%)": round(((1 + r).prod()) ** (252 / len(r)) * 100 - 100, 2),
            "年化波動率(%)": round(r.std() * np.sqrt(252) * 100, 2),
            "夏普比率": round((r.mean() * 252 - risk_free) / (r.std() * np.sqrt(252)), 3),
            "最大回撤(%)": round(max_drawdown((1 + r).cumprod()) * 100, 2),
            "正報酬比率(%)": round((r > 0).sum() / len(r) * 100, 2),
            "日報酬率均值(%)": round(r.mean() * 100, 4),
            "日報酬率標準差(%)": round(r.std() * 100, 4),
            "偏態": round(r.skew(), 4),
            "峰態": round(r.kurtosis(), 4),
            "VaR_95(%)": round(r.quantile(0.05) * 100, 4),
            "CVaR_95(%)": round(r[r <= r.quantile(0.05)].mean() * 100, 4),
        }
    return pd.DataFrame(metrics).T

def max_drawdown(cumulative):
    return (cumulative / cumulative.cummax() - 1).min()

def equal_weight_portfolio(returns):
    n = len([c for c in returns.columns if c != "加權指數"])
    weights = np.ones(n) / n
    port_returns = returns[[c for c in returns.columns if c != "加權指數"]].dot(weights)
    cum = (1 + port_returns).cumprod()
    return port_returns, cum

def generate_charts(close, returns, corr, log_returns, rr):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns

    plt.rc("font", family="Microsoft JhengHei")
    plt.rc("axes", unicode_minus=False)
    stocks = [c for c in close.columns if c != "加權指數"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Chart 1: Price & MA ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    for i, stock in enumerate(stocks[:4]):
        ax = axes[i]
        price = close[stock]
        price.plot(ax=ax, color="steelblue", linewidth=1.5, label="收盤價")
        price.rolling(20).mean().plot(ax=ax, color="orange", linewidth=1, linestyle="--", label="MA20")
        price.rolling(60).mean().plot(ax=ax, color="red", linewidth=1, linestyle="--", label="MA60")
        if i == 0:
            ax.legend(fontsize=9)
        ax.set_title(f"{stock} 股價走勢", fontsize=12)
        ax.set_ylabel("價格")
        ax.grid(True, alpha=0.3)
    fig.suptitle("股價與移動平均線", fontsize=14, y=1.02)
    plt.tight_layout()
    p1 = os.path.join(REPORT_DIR, f"price_ma_{timestamp}.png")
    fig.savefig(p1, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 2: Normalized Price (Base=100) ---
    fig, ax = plt.subplots(figsize=(12, 6))
    norm = close[stocks].div(close[stocks].iloc[0]) * 100
    norm.plot(ax=ax, linewidth=1.5)
    ax.set_title("標準化股價比較 (基準日 = 100)", fontsize=13)
    ax.set_ylabel("標準化價格")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    p2 = os.path.join(REPORT_DIR, f"normalized_price_{timestamp}.png")
    fig.savefig(p2, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 3: Correlation Heatmap ---
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    cmap = sns.diverging_palette(250, 10, as_cmap=True)
    sns.heatmap(corr, mask=mask, annot=True, cmap=cmap, center=0,
                fmt=".3f", linewidths=0.5, ax=ax, square=True,
                cbar_kws={"shrink": 0.75})
    ax.set_title("日報酬率相關係數矩陣", fontsize=14)
    plt.tight_layout()
    p3 = os.path.join(REPORT_DIR, f"corr_heatmap_{timestamp}.png")
    fig.savefig(p3, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 4: Rolling Correlation vs Market ---
    fig, ax = plt.subplots(figsize=(12, 6))
    rolling_corr = rolling_correlation(returns, window=30)
    for col in rolling_corr.columns:
        ax.plot(rolling_corr.index, rolling_corr[col], label=col, linewidth=1)
    ax.set_title("30 日滾動相關係數 (vs 加權指數)", fontsize=13)
    ax.set_ylabel("相關係數")
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.5)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    p4 = os.path.join(REPORT_DIR, f"rolling_corr_{timestamp}.png")
    fig.savefig(p4, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 5: Cumulative Return ---
    fig, ax = plt.subplots(figsize=(12, 6))
    cum_returns = (1 + returns[stocks]).cumprod()
    cum_returns.plot(ax=ax, linewidth=1.5)
    ax.set_title("累積報酬率", fontsize=13)
    ax.set_ylabel("累積報酬率")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.2f}x"))
    plt.tight_layout()
    p5 = os.path.join(REPORT_DIR, f"cumulative_return_{timestamp}.png")
    fig.savefig(p5, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 6: Equal-Weight Portfolio ---
    port_ret, port_cum = equal_weight_portfolio(returns)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    port_cum.plot(ax=axes[0], color="darkgreen", linewidth=2)
    axes[0].set_title("等權重投資組合累積報酬", fontsize=12)
    axes[0].set_ylabel("累積報酬率")
    axes[0].grid(True, alpha=0.3)
    port_ret.hist(ax=axes[1], bins=60, color="steelblue", edgecolor="white", alpha=0.8)
    axes[1].set_title("投資組合日報酬率分布", fontsize=12)
    axes[1].set_xlabel("日報酬率")
    axes[1].set_ylabel("次數")
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    p6 = os.path.join(REPORT_DIR, f"portfolio_{timestamp}.png")
    fig.savefig(p6, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Chart 7: Return Histogram Grid ---
    n = len(stocks)
    cols = 2
    rows = (n + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    axes = axes.flatten()
    for i, stock in enumerate(stocks):
        ax = axes[i]
        ax.hist(returns[stock], bins=60, color="steelblue", edgecolor="white", alpha=0.8)
        ax.axvline(0, color="red", linestyle="--", linewidth=1)
        ax.set_title(f"{stock}\n均值={returns[stock].mean():.4%}  std={returns[stock].std():.4%}", fontsize=10)
        ax.set_xlabel("日報酬率")
        ax.set_ylabel("次數")
        ax.grid(True, alpha=0.3)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    fig.suptitle("個股日報酬率分布", fontsize=14)
    plt.tight_layout()
    p7 = os.path.join(REPORT_DIR, f"return_hist_{timestamp}.png")
    fig.savefig(p7, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return [p1, p2, p3, p4, p5, p6, p7]

def export_csv(close, returns, log_returns, rr, corr):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    close.to_csv(os.path.join(REPORT_DIR, f"close_price_{timestamp}.csv"), encoding="utf-8-sig")
    returns.to_csv(os.path.join(REPORT_DIR, f"daily_returns_{timestamp}.csv"), encoding="utf-8-sig")
    rr.to_csv(os.path.join(REPORT_DIR, f"risk_metrics_{timestamp}.csv"), encoding="utf-8-sig")
    corr.to_csv(os.path.join(REPORT_DIR, f"correlation_{timestamp}.csv"), encoding="utf-8-sig")

def show_summary(close, returns, log_returns, corr, rr):
    stocks = [c for c in close.columns if c != "加權指數"]
    print("=" * 65)
    print("  台股分析儀表板 — 報表摘要")
    print("=" * 65)
    print(f"分析期間: {close.index[0].date()} ~ {close.index[-1].date()}")
    print(f"交易日數: {len(close)} 天")
    print(f"標的數量: {len(stocks)} 檔個股 + 加權指數")
    print()

    print("收盤價 (最後 5 筆)：")
    print(close.tail().to_string())
    print()

    print("=" * 65)
    print("  日報酬率相關係數")
    print("=" * 65)
    print(corr.to_string())
    print()

    print("=" * 65)
    print("  風險與績效指標")
    print("=" * 65)
    pd.set_option("display.width", 120)
    print(rr.to_string())
    pd.reset_option("display.width")

    print()
    print(f"所有報表與圖表已儲存至「{REPORT_DIR}/」目錄。")

def main():
    parser = argparse.ArgumentParser(description="台股分析儀表板 — 多維度股票分析工具")
    parser.add_argument("--start", default="2026-01-01", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="結束日期 (YYYY-MM-DD)，預設為今天")
    parser.add_argument("--interval", default="1d", help="K 線週期 (1d, 1wk, 1mo)")
    parser.add_argument("--no-charts", action="store_true", help="略過圖表生成")
    parser.add_argument("--no-csv", action="store_true", help="略過 CSV 匯出")
    args = parser.parse_args()

    ensure_report_dir()
    print("正在下載資料...")
    close, volume = fetch_data(start=args.start, end=args.end, interval=args.interval)

    if close.empty:
        print("錯誤：無法取得股價資料。請檢查網路或日期範圍。")
        return

    returns = compute_returns(close)
    log_returns = compute_log_returns(close)
    corr = returns.corr()
    rr = risk_metrics(returns)

    show_summary(close, returns, log_returns, corr, rr)

    if not args.no_csv:
        export_csv(close, returns, log_returns, rr, corr)
        print("CSV 匯出完成。")

    if not args.no_charts:
        print("正在生成圖表...")
        charts = generate_charts(close, returns, corr, log_returns, rr)
        print(f"圖表已生成 ({len(charts)} 張)：")
        for c in charts:
            print(f"  └─ {c}")

if __name__ == "__main__":
    main()
