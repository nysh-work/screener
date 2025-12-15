# Stock Screener Web Application

A full-stack web application for screening Indian equity markets with React frontend and FastAPI backend.

## Architecture

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: SQLite (via existing backend)
- **Data Source**: Yahoo Finance (yfinance)

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Install Python dependencies** (from project root):
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database** (if not already done):
   ```bash
   python main.py init
   ```

3. **Load stock data**:
   ```bash
   # Fetch data for top 20 NSE stocks
   python main.py update

   # Or fetch more stocks
   python main.py update --limit 50 --universe nifty50
   ```

4. **Start the FastAPI server**:
   ```bash
   python -m uvicorn api.app:app --reload
   ```

   The API will be available at http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/health

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:5173

## Features

### Stock Screening Dashboard

- **Multiple Screening Strategies**:
  - Value investing (P/B < 5, ROE > 15%)
  - Growth stocks (Revenue CAGR > 20%)
  - Balanced approach
  - Quality businesses (ROE > 20%, ROCE > 20%)
  - Turnaround stories

- **Interactive Filters**:
  - Select screening strategy
  - Filter by sector
  - Set minimum market cap
  - Adjust result limits

- **Results Table**:
  - Sortable columns
  - Display key metrics (P/E, P/B, ROE, Market Cap)
  - Click to view detailed stock information

- **Stock Detail Modal**:
  - Comprehensive company information
  - Valuation metrics
  - Profitability ratios
  - Financial health indicators
  - Growth metrics

### API Endpoints

#### Screens
- `GET /api/screens` - List all available screening strategies
- `POST /api/screens/run` - Run a screening strategy

#### Stocks
- `GET /api/stocks` - List all stocks in database
- `GET /api/stocks/{ticker}` - Get detailed stock information
- `POST /api/stocks/update` - Update stock data from yfinance

#### Other
- `GET /api/health` - Health check
- `GET /api/sectors` - List all sectors
- `GET /api/portfolio` - Get portfolio holdings
- `GET /api/watchlist` - Get watchlist stocks

## Usage

1. **Start both servers**:
   - Backend: `python -m uvicorn api.app:app --reload` (from project root)
   - Frontend: `npm run dev` (from frontend directory)

2. **Access the application**:
   - Open http://localhost:5173 in your browser

3. **Run a screen**:
   - Select a screening strategy (Value, Growth, etc.)
   - Optionally filter by sector or market cap
   - Click "Run Screen" to see results

4. **View stock details**:
   - Click the info icon (ℹ️) in the results table
   - View comprehensive metrics in the modal

## Development

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ScreenFilters.jsx    # Screening filters sidebar
│   │   ├── ResultsTable.jsx     # Sortable results table
│   │   └── StockDetail.jsx      # Stock detail modal
│   ├── services/
│   │   └── api.js               # API service layer
│   ├── App.jsx                  # Main application component
│   ├── index.css                # Global styles with Tailwind
│   └── main.jsx                 # Entry point
├── .env                         # Environment variables
└── package.json
```

### Backend Structure

```
api/
└── app.py                       # FastAPI application with all endpoints
```

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
```

The build output will be in `frontend/dist/`

**Backend**:
```bash
# Run with production server
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### API Connection Issues

If you see "API Error" in the top right:
1. Make sure the FastAPI server is running on port 8000
2. Check that the database has data: `python main.py status`
3. Verify CORS settings in `api/app.py`

### No Results from Screen

If screens return no results:
1. Check that stock data is loaded: `python main.py status`
2. Try loading more stocks: `python main.py update --limit 100`
3. Adjust filter criteria (lower market cap requirement, fewer sector filters)

### Frontend Build Issues

If npm install fails:
1. Make sure Node.js version is 16 or higher
2. Delete `node_modules` and `package-lock.json`, then run `npm install` again
3. Try using `npm ci` for a clean install

## Technologies Used

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLite** - Database
- **yfinance** - Stock data fetching
- **pandas** - Data manipulation

## License

This project is for educational purposes only. Not investment advice.

## Disclaimer

**IMPORTANT**: This tool is for educational purposes only. Not investment advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
