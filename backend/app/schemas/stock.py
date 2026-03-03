from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StockBasicResponse(BaseModel):
    code: str
    code_name: Optional[str]

    class Config:
        from_attributes = True

class DailyDataResponse(BaseModel):
    date: date
    open: Optional[float] = 0.0
    high: Optional[float] = 0.0
    low: Optional[float] = 0.0
    close: Optional[float] = 0.0
    volume: Optional[float] = 0.0
    amount: Optional[float] = 0.0
    turn: Optional[float] = 0.0
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_hist: Optional[float]
    kdj_k: Optional[float]
    kdj_d: Optional[float]
    kdj_j: Optional[float]

    class Config:
        from_attributes = True

class WeeklyDataResponse(DailyDataResponse):
    pass

class MonthlyDataResponse(DailyDataResponse):
    pass

class FundamentalsResponse(BaseModel):
    report_date: date
    circulating_market_cap: Optional[float]
    debt_to_asset_ratio: Optional[float]
    operating_cash_flow: Optional[float]
    net_profit: Optional[float]
    eps: Optional[float]
    roe: Optional[float]

    class Config:
        from_attributes = True
