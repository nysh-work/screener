import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Index Data API functions
export const getIndexData = async () => {
  try {
    const response = await api.get('/api/index-data');
    return response.data;
  } catch (error) {
    console.error('Error fetching index data:', error);
    throw error;
  }
};

export const getSingleIndexData = async (indexKey) => {
  try {
    const response = await api.get(`/api/index-data/${indexKey}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${indexKey} data:`, error);
    throw error;
  }
};

export const refreshIndexData = async () => {
  try {
    const response = await api.post('/api/index-data/refresh');
    return response.data;
  } catch (error) {
    console.error('Error refreshing index data:', error);
    throw error;
  }
};

// Existing API functions
export const healthCheck = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export const listScreens = async () => {
  const response = await api.get('/api/screens');
  return response.data;
};

export const runScreen = async (screenData) => {
  const response = await api.post('/api/screens', screenData);
  return response.data;
};

export const listStocks = async (limit = 100, sector = null) => {
  const params = { limit };
  if (sector) params.sector = sector;
  const response = await api.get('/api/stocks', { params });
  return response.data;
};

export const getStockInfo = async (ticker) => {
  const response = await api.get(`/api/stocks/${ticker}`);
  return response.data;
};

export const listSectors = async () => {
  const response = await api.get('/api/sectors');
  return response.data;
};

export const getPortfolio = async () => {
  const response = await api.get('/api/portfolio');
  return response.data;
};

export const addToPortfolio = async (portfolioData) => {
  const response = await api.post('/api/portfolio', portfolioData);
  return response.data;
};

export const removeFromPortfolio = async (ticker) => {
  const response = await api.delete(`/api/portfolio/${ticker}`);
  return response.data;
};

export const getWatchlist = async () => {
  const response = await api.get('/api/watchlist');
  return response.data;
};

export const addToWatchlist = async (watchlistData) => {
  const response = await api.post('/api/watchlist', watchlistData);
  return response.data;
};

export const removeFromWatchlist = async (ticker) => {
  const response = await api.delete(`/api/watchlist/${ticker}`);
  return response.data;
};

export const updateStockData = async (tickers = null) => {
  const response = await api.post('/api/stocks/update', tickers);
  return response.data;
};

export const runBacktest = async (backtestData) => {
  const response = await api.post('/api/backtest', backtestData);
  return response.data;
};

export const listCustomScreens = async () => {
  const response = await api.get('/api/custom-screens');
  return response.data;
};

export const createCustomScreen = async (screenData) => {
  const response = await api.post('/api/custom-screens', screenData);
  return response.data;
};

export const deleteCustomScreen = async (name) => {
  const response = await api.delete(`/api/custom-screens/${name}`);
  return response.data;
};

export const runCustomScreen = async (screenData) => {
  const response = await api.post('/api/custom-screens/run', screenData);
  return response.data;
};

export const updateUniverse = async (universeData) => {
  const response = await api.post('/api/universe/update', universeData);
  return response.data;
};

export default api;