from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Index
from app.db.database import Base

class StockBasic(Base):
    """
    Model for storing basic information of A-share stocks.
    """
    __tablename__ = 'stock_basic'

    code = Column(String(20), primary_key=True, index=True) # E.g., sh.600000
    code_name = Column(String(50)) # Stock name
    industry = Column(String(50)) # Industry
    area = Column(String(50)) # Geographic area
    market = Column(String(20)) # Main board, SME, ChiNext, etc.
    list_date = Column(Date) # Listing date
    delisted = Column(Boolean, default=False) # Delisted flag

class DailyData(Base):
    """
    Model for storing daily K-line data.
    """
    __tablename__ = 'daily_data'
    __table_args__ = (
        Index('idx_daily_code_date', 'code', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), index=True) # Stock code
    date = Column(Date, index=True) # Trading date
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    preclose = Column(Float)
    volume = Column(Float) # Trade volume
    amount = Column(Float) # Trade amount
    turn = Column(Float) # Turnover rate

    # Technical Indicators calculated on the fly or pre-calculated
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    kdj_k = Column(Float, nullable=True)
    kdj_d = Column(Float, nullable=True)
    kdj_j = Column(Float, nullable=True)

class WeeklyData(Base):
    """
    Model for storing weekly K-line data.
    """
    __tablename__ = 'weekly_data'
    __table_args__ = (
        Index('idx_weekly_code_date', 'code', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), index=True) # Stock code
    date = Column(Date, index=True) # Trading date
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float) # Trade volume
    amount = Column(Float) # Trade amount
    turn = Column(Float) # Turnover rate

    # Technical Indicators calculated on the fly or pre-calculated
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    kdj_k = Column(Float, nullable=True)
    kdj_d = Column(Float, nullable=True)
    kdj_j = Column(Float, nullable=True)

class MonthlyData(Base):
    """
    Model for storing monthly K-line data.
    """
    __tablename__ = 'monthly_data'
    __table_args__ = (
        Index('idx_monthly_code_date', 'code', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), index=True) # Stock code
    date = Column(Date, index=True) # Trading date
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float) # Trade volume
    amount = Column(Float) # Trade amount
    turn = Column(Float) # Turnover rate

    # Technical Indicators calculated on the fly or pre-calculated
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    kdj_k = Column(Float, nullable=True)
    kdj_d = Column(Float, nullable=True)
    kdj_j = Column(Float, nullable=True)


class Fundamentals(Base):
    """
    Model for storing fundamental data (quarterly).
    Includes:
    - 流通市值 (Circulating market cap)
    - 最新季报数据 (Latest quarterly report data)
    - 资产负债率 (Debt-to-asset ratio)
    - 经营活动现金流量 (Operating cash flow)
    """
    __tablename__ = 'fundamentals'
    __table_args__ = (
        Index('idx_fund_code_date', 'code', 'report_date', unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), index=True)
    report_date = Column(Date, index=True) # Report period ending date
    circulating_market_cap = Column(Float, nullable=True) # 流通市值
    debt_to_asset_ratio = Column(Float, nullable=True) # 资产负债率
    operating_cash_flow = Column(Float, nullable=True) # 经营活动现金流量净额
    net_profit = Column(Float, nullable=True) # 净利润 (part of 季报数据)
    eps = Column(Float, nullable=True) # 每股收益 (part of 季报数据)
    roe = Column(Float, nullable=True) # 净资产收益率 (part of 季报数据)
