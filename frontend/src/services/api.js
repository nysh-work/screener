import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
