import requests
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

def fetch_youbike_data() -> pd.DataFrame:
    # 台北市 YouBike 2.0 的 Web API 網址
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    # 使用 requests 套件裡面的 get 函式，執行後會傳出 Response 的實體
    response = requests.get(url)
    response.raise_for_status()
    data = response.json() # 使用 Response 實體的 json() 方法，會傳出 list 的資料結構
    return pd.DataFrame(data)


def dataframe_to_pdf(df: pd.DataFrame, filename: str, max_rows: int = 20) -> None:
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )

    styles = getSampleStyleSheet()
    story = [Paragraph("YouBike 即時資料報表", styles["Title"]), Spacer(1, 0.3 * cm)]

    rows = [list(df.columns)] + df.head(max_rows).astype(str).values.tolist()
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), # 註冊可顯示中文的字型（macOS / Linux 常可直接使用）
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )

    story.append(table)
    doc.build(story)


def main() -> None:
    try:
        df = fetch_youbike_data()
        print(df.head())
        output_file = "youbike_report.pdf"
        dataframe_to_pdf(df, output_file)
        print(f"已產生 PDF 檔案：{output_file}")
    except requests.RequestException:
        print("下載失敗，無法取得資料。")


if __name__ == '__main__':
    main()