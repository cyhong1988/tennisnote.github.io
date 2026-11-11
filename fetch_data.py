import json
import os
from datetime import datetime
import urllib.request
import ssl

DATA_FILE = "data.json"

# 忽略 SSL 憑證問題
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 載入現有資料
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = {}
else:
    data = {}

def get_twse_prices():
    # TWSE 每日收盤 OpenAPI (從官方伺服器端抓取不會有 CORS 問題)
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        items = json.loads(res.read().decode("utf-8"))
        
    p0050 = None
    p00685L = None
    
    for row in items:
        code = row.get("Code")
        if code == "0050":
            try:
                p0050 = float(row.get("ClosingPrice", "").replace(",", ""))
            except ValueError:
                pass
        elif code == "00685L":
            try:
                p00685L = float(row.get("ClosingPrice", "").replace(",", ""))
            except ValueError:
                pass
                
    return p0050, p00685L

try:
    p0050, p00685L = get_twse_prices()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if p0050 is not None and p00685L is not None:
        data[today_str] = {
            "0050": p0050,
            "00685L": p00685L
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"成功更新 {today_str}: 0050={p0050}, 00685L={p00685L}")
    else:
        print("未取得完整收盤價（可能今日未開盤或資料尚未公佈）")
except Exception as e:
    print(f"抓取發生錯誤: {e}")
