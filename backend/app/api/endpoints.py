from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.data_fetcher import get_stock_basics, download_daily_data, download_weekly_data, download_monthly_data, download_fundamentals
from app.models.stock import StockBasic, DailyData, WeeklyData, MonthlyData, Fundamentals
from app.schemas.stock import StockBasicResponse, DailyDataResponse, WeeklyDataResponse, MonthlyDataResponse, FundamentalsResponse
from app.services.strategy import run_strategy

router = APIRouter()

@router.get("/strategy/run")
def get_strategy_results(db: Session = Depends(get_db)):
    results = run_strategy(db)
    return {"status": "success", "data": results}

@router.get("/stocks", response_model=list[StockBasicResponse])
def get_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stocks = db.query(StockBasic).offset(skip).limit(limit).all()
    return stocks

@router.get("/daily/{code}", response_model=list[DailyDataResponse])
def get_daily_data(code: str, limit: int = 300, db: Session = Depends(get_db)):
    data = db.query(DailyData).filter(DailyData.code == code).order_by(DailyData.date.desc()).limit(limit).all()
    return data[::-1]

@router.get("/weekly/{code}", response_model=list[WeeklyDataResponse])
def get_weekly_data(code: str, limit: int = 300, db: Session = Depends(get_db)):
    data = db.query(WeeklyData).filter(WeeklyData.code == code).order_by(WeeklyData.date.desc()).limit(limit).all()
    return data[::-1]

@router.get("/monthly/{code}", response_model=list[MonthlyDataResponse])
def get_monthly_data(code: str, limit: int = 300, db: Session = Depends(get_db)):
    data = db.query(MonthlyData).filter(MonthlyData.code == code).order_by(MonthlyData.date.desc()).limit(limit).all()
    return data[::-1]

@router.get("/fundamentals/{code}", response_model=list[FundamentalsResponse])
def get_fundamental_data(code: str, limit: int = 4, db: Session = Depends(get_db)):
    data = db.query(Fundamentals).filter(Fundamentals.code == code).order_by(Fundamentals.report_date.desc()).limit(limit).all()
    return data

@router.post("/update/basics")
def update_basics(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(get_stock_basics, db)
    return {"status": "accepted", "message": "Stock basics update started in background."}

@router.post("/update/daily")
def update_daily(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(download_daily_data, db)
    background_tasks.add_task(download_weekly_data, db)
    background_tasks.add_task(download_monthly_data, db)
    return {"status": "accepted", "message": "Daily, weekly and monthly data download started in background."}

@router.post("/update/fundamentals")
def update_fundamentals(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(download_fundamentals, db)
    return {"status": "accepted", "message": "Fundamental data download started in background."}
