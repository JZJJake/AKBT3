import pandas as pd
from sqlalchemy.orm import Session
from app.models.stock import StockBasic, DailyData, Fundamentals
from datetime import date

def run_strategy(db: Session, target_date: date = None):
    """
    Runs the custom user strategy to select stocks.
    Strategy criteria translated to Python/Pandas logic:
    1. 市值 < 350 (Market Cap < 350)
    2. STRMID(CODE,1,2)<>"68" (Exclude Star Market codes starting with 'sh.68')
    3. JYJE > 0.1 (We'll assume Trade Amount > 0.1 billion or simply > 0 for now as proxy)
    4. A3 = CLOSE>OPEN AND M20>REF(M20,1) AND M20>MA(M20,5) AND DM205>REF(DM205,1)
            (where M20=MA(CLOSE,20), M205=MA(M20,5), DM205=M20-M205)
    5. KDJJ = REF(e,1)<30 AND e>REF(e,1) AND REF(e,1)<REF(e,2)
            (where e is KDJ_J value we calculated. We check previous day J < 30, and J has turned up: J_0 > J_1 and J_1 < J_2)
    """

    # 1 & 2: Get basic stock list excluding 'sh.68'
    stocks = db.query(StockBasic).filter(~StockBasic.code.like('sh.68%')).all()
    selected_stocks = []

    # In a real system, you'd calculate this via SQL or vectorizing a large dataframe.
    # For this terminal, we fetch the recent data per stock and evaluate.

    for stock in stocks:
        # Check fundamentals if market cap < 350 (assume the value is in 100millions,
        # but since we lack exact real-time API sync now, we use a placeholder check)
        # Assuming circulating_market_cap from our basic fetch is stored in some unit.
        fund = db.query(Fundamentals).filter(Fundamentals.code == stock.code).order_by(Fundamentals.report_date.desc()).first()
        if fund and fund.circulating_market_cap:
            # Simple check if it's over 350 (units vary by API, assuming standard AKShare 'yuan' and we need 350亿)
            if fund.circulating_market_cap > 350_000_000_000:
                continue # Skip if too large

        # Get recent 30 days of data to compute moving averages and evaluate
        recent_data = db.query(DailyData).filter(DailyData.code == stock.code).order_by(DailyData.date.desc()).limit(40).all()
        if len(recent_data) < 25:
            continue

        # Convert to pandas for easier calculation. Sort ascending for MA calculations
        df = pd.DataFrame([r.__dict__ for r in recent_data]).sort_values(by='date', ascending=True)

        # Calculate M20
        df['M20'] = df['close'].rolling(window=20).mean()
        # Calculate M205
        df['M205'] = df['M20'].rolling(window=5).mean()
        # Calculate DM205
        df['DM205'] = df['M20'] - df['M205']

        # We need the last 3 days to evaluate
        if len(df) < 3:
            continue

        d0 = df.iloc[-1]
        d1 = df.iloc[-2]
        d2 = df.iloc[-3]

        # Criteria A3
        is_close_gt_open = d0['close'] > d0['open']
        is_m20_rising = d0['M20'] > d1['M20']
        is_m20_gt_m205 = d0['M20'] > d0['M205']
        is_dm205_rising = d0['DM205'] > d1['DM205']

        A3 = is_close_gt_open and is_m20_rising and is_m20_gt_m205 and is_dm205_rising

        # Criteria KDJJ (J curve turning up from below 30)
        e0 = d0['kdj_j']
        e1 = d1['kdj_j']
        e2 = d2['kdj_j']

        if pd.isna(e0) or pd.isna(e1) or pd.isna(e2):
            continue

        KDJJ = (e1 < 30) and (e0 > e1) and (e1 < e2)

        # Amount check
        amount_ok = d0['amount'] > 0 # Placeholder for JYJE > 0.1

        if A3 and KDJJ and amount_ok:
            selected_stocks.append({
                "code": stock.code,
                "code_name": stock.code_name,
                "close": d0['close'],
                "date": str(d0['date'])
            })

    return selected_stocks
