import re

with open("backend/app/services/data_fetcher.py", "r") as f:
    content = f.read()

# Add Weekly and Monthly imports
content = content.replace("from app.models.stock import StockBasic, DailyData, Fundamentals", "from app.models.stock import StockBasic, DailyData, WeeklyData, MonthlyData, Fundamentals")

# Add weekly and monthly download functions
new_functions = """
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
"""

# Replace the existing `download_daily_data` function
content = re.sub(r'def download_daily_data\(.*?\n    return \{"status": "success", "message": "Daily data downloaded successfully"\}', new_functions.strip(), content, flags=re.DOTALL)

with open("backend/app/services/data_fetcher.py", "w") as f:
    f.write(content)
