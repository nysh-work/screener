"""
FastAPI application for Stock Screener API.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from screener.engine import ScreeningEngine
from screener.criteria import list_available_screens, get_screen_config
from portfolio.tracker import PortfolioTracker
from data.fetcher import YFinanceFetcher

app = FastAPI(
    title="Stock Screener API",
    description="API for screening Indian equity markets",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()


# Pydantic models for request/response
class ScreenRequest(BaseModel):
    screen_type: str
    sectors: Optional[List[str]] = None
    min_market_cap: Optional[float] = None
    limit: int = 50


class PortfolioAddRequest(BaseModel):
    ticker: str
    quantity: float
    price: float
    date: Optional[str] = None
    notes: Optional[str] = None


class WatchlistAddRequest(BaseModel):
    ticker: str
    target_price: Optional[float] = None
    notes: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Stock Screener API",
        "version": "1.0.0",
        "endpoints": {
            "screens": "/api/screens",
            "stocks": "/api/stocks",
            "portfolio": "/api/portfolio",
            "watchlist": "/api/watchlist"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        tickers = db.get_all_tickers()
        return {
            "status": "healthy",
            "database": "connected",
            "stocks_count": len(tickers),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screens")
async def list_screens():
    """List all available screening strategies."""
    try:
        screens = list_available_screens()
        return {
            "screens": [
                {
                    "key": key,
                    "name": name,
                    "description": description
                }
                for key, name, description in screens
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/screens/run")
async def run_screen(request: ScreenRequest):
    """Run a screening strategy."""
    try:
        engine = ScreeningEngine(db)

        # Prepare filters
        additional_filters = {}
        if request.sectors:
            additional_filters['sector'] = request.sectors
        if request.min_market_cap:
            additional_filters['min_market_cap'] = request.min_market_cap

        # Run screen
        results = engine.run_predefined_screen(request.screen_type, additional_filters)

        # Get statistics
        stats = engine.get_screen_statistics(results)

        # Get screen config
        screen_config = get_screen_config(request.screen_type)

        # Convert to dict
        results_list = results.head(request.limit).to_dict(orient='records')

        return {
            "screen_name": screen_config['name'],
            "description": screen_config['description'],
            "criteria": screen_config['criteria'],
            "stats": stats,
            "results": results_list,
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks")
async def list_stocks(
    limit: int = Query(100, ge=1, le=500),
    sector: Optional[str] = None
):
    """List all stocks in database."""
    try:
        query = """
        SELECT
            c.ticker,
            c.company_name,
            c.sector,
            c.industry,
            f.market_cap,
            f.current_price,
            f.pe_ratio,
            f.pb_ratio,
            dm.roe,
            dm.roce
        FROM companies c
        LEFT JOIN fundamentals f ON c.ticker = f.ticker
        LEFT JOIN derived_metrics dm ON c.ticker = dm.ticker
        WHERE f.timestamp = (
            SELECT MAX(timestamp)
            FROM fundamentals
            WHERE ticker = c.ticker
        )
        """

        if sector:
            query += f" AND c.sector = '{sector}'"

        query += f" LIMIT {limit}"

        results = db.execute_query(query)

        return {
            "stocks": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{ticker}")
async def get_stock_info(ticker: str):
    """Get detailed information for a specific stock."""
    try:
        stock_data = db.get_latest_metrics(ticker.upper())

        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")

        return stock_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sectors")
async def list_sectors():
    """List all available sectors."""
    try:
        query = """
        SELECT DISTINCT sector
        FROM companies
        WHERE sector IS NOT NULL
        ORDER BY sector
        """
        results = db.execute_query(query)

        return {
            "sectors": [row['sector'] for row in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio holdings."""
    try:
        tracker = PortfolioTracker()
        holdings = tracker.get_portfolio()
        summary = tracker.get_portfolio_summary()

        return {
            "holdings": holdings.to_dict(orient='records') if not holdings.empty else [],
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/portfolio")
async def add_to_portfolio(request: PortfolioAddRequest):
    """Add a stock to portfolio."""
    try:
        tracker = PortfolioTracker()
        purchase_date = datetime.strptime(request.date, '%Y-%m-%d').date() if request.date else date.today()

        success = tracker.add_holding(
            request.ticker,
            request.quantity,
            request.price,
            purchase_date,
            request.notes
        )

        if success:
            return {"message": f"Added {request.ticker} to portfolio"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add to portfolio")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/portfolio/{portfolio_id}")
async def remove_from_portfolio(portfolio_id: int):
    """Remove a holding from portfolio."""
    try:
        tracker = PortfolioTracker()
        success = tracker.remove_holding(portfolio_id)

        if success:
            return {"message": f"Removed holding {portfolio_id} from portfolio"}
        else:
            raise HTTPException(status_code=404, detail="Holding not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchlist")
async def get_watchlist():
    """Get watchlist stocks."""
    try:
        tracker = PortfolioTracker()
        stocks = tracker.get_watchlist()

        return {
            "watchlist": stocks.to_dict(orient='records') if not stocks.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/watchlist")
async def add_to_watchlist(request: WatchlistAddRequest):
    """Add a stock to watchlist."""
    try:
        tracker = PortfolioTracker()
        success = tracker.add_to_watchlist(
            request.ticker,
            request.target_price,
            request.notes
        )

        if success:
            return {"message": f"Added {request.ticker} to watchlist"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add to watchlist")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/watchlist/{ticker}")
async def remove_from_watchlist(ticker: str):
    """Remove a stock from watchlist."""
    try:
        tracker = PortfolioTracker()
        success = tracker.remove_from_watchlist(ticker.upper())

        if success:
            return {"message": f"Removed {ticker} from watchlist"}
        else:
            raise HTTPException(status_code=404, detail="Stock not in watchlist")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stocks/update")
async def update_stock_data(tickers: Optional[List[str]] = None):
    """Update stock data from yfinance."""
    try:
        fetcher = YFinanceFetcher()

        if not tickers:
            # Default to top 20 stocks
            from data.fetcher import get_nse_top_stocks
            tickers = get_nse_top_stocks()[:20]

        success_count = 0
        error_count = 0

        for ticker in tickers:
            try:
                data = fetcher.fetch_all_data(ticker, include_history=False)

                if data:
                    db.add_company(data['company'])
                    db.add_fundamentals(data['fundamentals'])
                    db.add_derived_metrics(data['derived_metrics'])
                    db.add_growth_metrics(data['growth_metrics'])
                    db.add_quality_metrics(data['quality_metrics'])
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

        return {
            "message": "Data update completed",
            "success": success_count,
            "errors": error_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
