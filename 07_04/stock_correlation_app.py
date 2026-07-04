import yfinance as yf
import argparse

tickers = {
    "台積電": "2330.TW",
    "聯電": "2303.TW",
    "聯發科": "2454.TW",
    "鴻海": "2317.TW",
}

def fetch_data(start="2026-01-01", interval="1d"):
    codes = list(tickers.values())
    data = yf.download(codes, start=start, interval=interval, auto_adjust=True, progress=False)
    close = data["Close"]
    code_to_name = {v: k for k, v in tickers.items()}
    close = close.rename(columns=code_to_name)
    return close

def compute_returns_and_corr(close):
    returns = close.pct_change().dropna()
    corr = returns.corr()
    return returns, corr

def show_summary(close, returns, corr):
    print("收盤價 (最後 5 筆)：")
    print(close.tail())
    print(f"\n共 {len(close)} 天收盤價資料")
    print(f"\n日報酬率相關係數：")
    print(corr.to_string())

def main():
    parser = argparse.ArgumentParser(description="台股相關性分析工具")
    parser.add_argument("--start", default="2026-01-01", help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--interval", default="1d", help="K 線週期 (1d, 1wk, 1mo)")
    args = parser.parse_args()

    close = fetch_data(start=args.start, interval=args.interval)
    returns, corr = compute_returns_and_corr(close)
    show_summary(close, returns, corr)

    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.rc("font", family="Microsoft JhengHei")
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".3f")
    plt.title("日報酬率相關係數矩陣")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
