import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = () => api.get('/api/health');

// Screens
export const listScreens = () => api.get('/api/screens');
export const runScreen = (screenData) => api.post('/api/screens/run', screenData);

// Stocks
export const listStocks = (params) => api.get('/api/stocks', { params });
export const getStockInfo = (ticker) => api.get(`/api/stocks/${ticker}`);
export const updateStockData = (tickers) => api.post('/api/stocks/update', { tickers });
export const getUniverseData = (params) => api.get('/api/stocks', { params });

// Sectors
export const listSectors = () => api.get('/api/sectors');

// Portfolio
export const getPortfolio = () => api.get('/api/portfolio');
export const addToPortfolio = (data) => api.post('/api/portfolio', data);
export const removeFromPortfolio = (id) => api.delete(`/api/portfolio/${id}`);

// Watchlist
export const getWatchlist = () => api.get('/api/watchlist');
export const addToWatchlist = (data) => api.post('/api/watchlist', data);
export const removeFromWatchlist = (ticker) => api.delete(`/api/watchlist/${ticker}`);

export default api;

// Custom Screens
export const listCustomScreens = () => api.get('/api/custom-screens');
export const createCustomScreen = (data) => api.post('/api/custom-screens', data);
export const deleteCustomScreen = (name) => api.delete(`/api/custom-screens/${name}`);
export const runCustomScreen = (data) => api.post('/api/custom-screens/run', data);

// Backtesting
export const runBacktest = (data) => api.post('/api/backtest/run', data);
export const getBacktestHistory = (screenName) => api.get('/api/backtest/history', { params: { screen_name: screenName } });

// Database
export const updateUniverse = (data) => api.post('/api/stocks/update-universe', data);
export const addStock = (data) => api.post('/api/stocks', data);
export const addStocksFromCSV = (data) => api.post('/api/stocks/csv', data);
