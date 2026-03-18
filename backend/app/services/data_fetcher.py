import baostock as bs
import akshare as ak
import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.stock import StockBasic, DailyData, WeeklyData, MonthlyData, Fundamentals

def get_stock_basics(db: Session):
    try:
        stock_info_df = ak.stock_info_a_code_name()
        for _, row in stock_info_df.iterrows():
            code = str(row['code'])
            name = str(row['name'])
            bs_code = f"sh.{code}" if code.startswith(('6')) else f"sz.{code}" if code.startswith(('0', '3')) else f"bj.{code}"

            existing = db.query(StockBasic).filter(StockBasic.code == bs_code).first()
            if not existing:
                new_stock = StockBasic(code=bs_code, code_name=name)
                db.add(new_stock)
            else:
                existing.code_name = name
        db.commit()
        return {"status": "success", "message": "Stock basics updated successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    import ta
    if len(df) < 25:
        return df

    macd = ta.trend.MACD(df['close'], window_slow=25, window_fast=10, window_sign=7)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_hist'] = macd.macd_diff()

    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=9, smooth_window=3)
    df['kdj_k'] = stoch.stoch()
    df['kdj_d'] = stoch.stoch_signal()
    df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']

    df = df.fillna(0)
    return df

def download_kline_data(db: Session, frequency='d', model=DailyData, start_date='2020-01-01', end_date=None):
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    lg = bs.login()
    if lg.error_code != '0':
        return {"status": "error", "message": f"Baostock login failed: {lg.error_msg}"}

    stocks = db.query(StockBasic.code).all()
    fields = "date,code,open,high,low,close,volume,amount,turn" if frequency != 'd' else "date,code,open,high,low,close,preclose,volume,amount,turn"

    for (stock_code,) in stocks:
        last_record = db.query(model).filter(model.code == stock_code).order_by(model.date.desc()).first()
        fetch_start = start_date
        if last_record:
            fetch_start = (last_record.date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            if fetch_start > end_date:
                continue

        all_rs = bs.query_history_k_data_plus(
            stock_code, fields,
            start_date='2020-01-01', end_date=end_date, frequency=frequency, adjustflag="3"
        )
        all_data_list = []
        while (all_rs.error_code == '0') & all_rs.next():
             all_data_list.append(all_rs.get_row_data())

        if all_data_list:
            all_df = pd.DataFrame(all_data_list, columns=all_rs.fields)
            numeric_cols = [c for c in ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'turn'] if c in all_df.columns]
            all_df[numeric_cols] = all_df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
            all_df['date'] = pd.to_datetime(all_df['date'])
            all_df = calculate_indicators(all_df)

            new_df = all_df[all_df['date'] >= pd.to_datetime(fetch_start)]

            records_to_insert = []
            for _, row in new_df.iterrows():
                record = model(
                    code=stock_code,
                    date=row['date'].date(),
                    open=row['open'], high=row['high'], low=row['low'], close=row['close'],
                    volume=row.get('volume', 0), amount=row.get('amount', 0), turn=row.get('turn', 0),
                    macd=row.get('macd'), macd_signal=row.get('macd_signal'), macd_hist=row.get('macd_hist'),
                    kdj_k=row.get('kdj_k'), kdj_d=row.get('kdj_d'), kdj_j=row.get('kdj_j')
                )
                if frequency == 'd':
                    record.preclose = row.get('preclose', 0)
                records_to_insert.append(record)

            if records_to_insert:
                db.bulk_save_objects(records_to_insert)
                db.commit()

    bs.logout()
    return {"status": "success", "message": f"{frequency} data downloaded successfully"}

def download_daily_data(db: Session, start_date: str = '2020-01-01', end_date: str = None):
    return download_kline_data(db, frequency='d', model=DailyData, start_date=start_date, end_date=end_date)

def download_weekly_data(db: Session, start_date: str = '2020-01-01', end_date: str = None):
    return download_kline_data(db, frequency='w', model=WeeklyData, start_date=start_date, end_date=end_date)

def download_monthly_data(db: Session, start_date: str = '2020-01-01', end_date: str = None):
    return download_kline_data(db, frequency='m', model=MonthlyData, start_date=start_date, end_date=end_date)

def download_fundamentals(db: Session, date_str: str = None):
    try:
        spot_df = ak.stock_zh_a_spot_em()
        today = datetime.now().date()
        for _, row in spot_df.iterrows():
            code = str(row['代码'])
            bs_code = f"sh.{code}" if code.startswith(('6')) else f"sz.{code}" if code.startswith(('0', '3')) else f"bj.{code}"

            existing = db.query(Fundamentals).filter(
                Fundamentals.code == bs_code,
                Fundamentals.report_date == today
            ).first()

            if not existing:
                fund = Fundamentals(
                    code=bs_code,
                    report_date=today,
                    circulating_market_cap=row.get('流通市值', 0),
                )
                db.add(fund)
        db.commit()
        return {"status": "success", "message": "Fundamental data downloaded"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
