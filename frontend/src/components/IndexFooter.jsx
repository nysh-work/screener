import { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { getIndexData, refreshIndexData } from '../services/indexApi';

const IndexFooter = () => {
  const [indexData, setIndexData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  const fetchIndexData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getIndexData();
      setIndexData(response.indices);
      setLastUpdated(new Date(response.timestamp));
    } catch (err) {
      console.error('Error fetching index data:', err);
      setError('Failed to fetch index data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      await refreshIndexData();
      await fetchIndexData();
    } catch (err) {
      console.error('Error refreshing index data:', err);
      setError('Failed to refresh index data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndexData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchIndexData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    if (num >= 10000000) return (num / 10000000).toFixed(2) + ' Cr';
    if (num >= 100000) return (num / 100000).toFixed(2) + ' L';
    if (num >= 1000) return (num / 1000).toFixed(2) + ' K';
    return num.toFixed(2);
  };

  const formatPercent = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return num.toFixed(2) + '%';
  };

  const getTrendIcon = (current, ema20) => {
    if (current > ema20) return <TrendingUp className="w-3 h-3 text-green-500" />;
    if (current < ema20) return <TrendingDown className="w-3 h-3 text-red-500" />;
    return <Minus className="w-3 h-3 text-gray-500" />;
  };

  const indexConfig = [
    { key: 'nifty_50', name: 'NIFTY 50', shortName: 'N50' },
    { key: 'nifty_500', name: 'NIFTY 500', shortName: 'N500' },
    { key: 'nifty_bank', name: 'NIFTY Bank', shortName: 'BANK' },
    { key: 'nifty_it', name: 'NIFTY IT', shortName: 'IT' },
    { key: 'nifty_auto', name: 'NIFTY Auto', shortName: 'AUTO' }
  ];

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900 border-t border-red-200 dark:border-red-700 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center px-3 py-1 text-sm bg-red-100 dark:bg-red-800 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading && !indexData) {
    return (
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <div className="flex items-center text-gray-500 dark:text-gray-400">
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            Loading index data...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Index Data
          </div>
          <div className="flex items-center space-x-2">
            {lastUpdated && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {indexConfig.map(({ key, name, shortName }) => {
            const data = indexData?.[key];
            if (!data) return null;

            return (
              <div key={key} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-300">
                    {shortName}
                  </span>
                  {getTrendIcon(data.current_price, data.ema_20)}
                </div>
                
                <div className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">
                  {formatNumber(data.current_price)}
                </div>
                
                <div className="grid grid-cols-2 gap-1 text-xs text-gray-500 dark:text-gray-400">
                  <div>
                    <span className="block">14D High:</span>
                    <span className="font-medium">{formatNumber(data.high_14d)}</span>
                  </div>
                  <div>
                    <span className="block">14D Low:</span>
                    <span className="font-medium">{formatNumber(data.low_14d)}</span>
                  </div>
                  <div>
                    <span className="block">EMA20:</span>
                    <span className="font-medium">{formatNumber(data.ema_20)}</span>
                  </div>
                  <div>
                    <span className="block">EMA50:</span>
                    <span className="font-medium">{formatNumber(data.ema_50)}</span>
                  </div>
                  <div>
                    <span className="block">MACD:</span>
                    <span className={`font-medium ${data.macd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatNumber(data.macd)}
                    </span>
                  </div>
                  <div>
                    <span className="block">Chop:</span>
                    <span className="font-medium">{formatPercent(data.choppiness_index)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default IndexFooter;