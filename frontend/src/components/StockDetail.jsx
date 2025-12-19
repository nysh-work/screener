import { useState, useEffect } from 'react';
import {
  X,
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import { getStockInfo } from '../services/api';

export default function StockDetail({ ticker, onClose }) {
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStockData();
  }, [ticker]);

  const loadStockData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getStockInfo(ticker);
      setStockData(response.data);
    } catch (err) {
      setError('Failed to load stock details');
      console.error('Error loading stock data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return typeof num === 'number' ? num.toFixed(2) : num;
  };

  const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    if (num >= 10000) return `₹${(num / 10000).toFixed(2)}Cr`;
    return `₹${num.toFixed(2)}`;
  };

  const MetricCard = ({ icon: Icon, label, value, trend }) => (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400 mr-2" />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {label}
          </span>
        </div>
        {trend && (
          <span
            className={`text-xs ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}
          >
            {trend > 0 ? '+' : ''}
            {trend}%
          </span>
        )}
      </div>
      <div className="text-xl font-bold text-gray-900 dark:text-gray-100">
        {value}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-4xl w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-4xl w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Error
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!stockData) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-6xl w-full my-8">
        {/* Header */}
        <div className="flex justify-between items-start p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100">
              {stockData.company_name}
            </h2>
            <div className="flex items-center mt-2">
              <span className="text-lg font-medium text-primary-600 dark:text-primary-400 mr-4">
                {stockData.ticker}
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {stockData.sector} • {stockData.industry}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Price Section */}
          <div className="mb-6">
            <div className="flex items-baseline mb-4">
              <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">
                {formatCurrency(stockData.price)}
              </span>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard
              icon={DollarSign}
              label="Market Cap"
              value={formatCurrency(stockData.market_cap)}
            />
            <MetricCard
              icon={BarChart3}
              label="P/E Ratio"
              value={formatNumber(stockData.price_to_earnings)}
            />
            <MetricCard
              icon={BarChart3}
              label="P/B Ratio"
              value={formatNumber(stockData.price_to_book)}
            />
            <MetricCard
              icon={TrendingUp}
              label="ROE"
              value={`${formatNumber(stockData.roe)}%`}
            />
          </div>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Valuation Metrics */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                Valuation Metrics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    P/E Ratio
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.price_to_earnings)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    P/B Ratio
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.price_to_book)}
                  </span>
                </div>
              </div>
            </div>

            {/* Profitability Metrics */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                Profitability Metrics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">ROE</span>
                  <span
                    className={`font-medium ${
                      stockData.roe > 15
                        ? 'text-green-600'
                        : 'text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    {formatNumber(stockData.roe)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">ROCE</span>
                  <span
                    className={`font-medium ${
                      stockData.roce > 15
                        ? 'text-green-600'
                        : 'text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    {formatNumber(stockData.roce)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Operating Margin
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.opm)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Financial Health */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                Financial Health
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Debt/Equity
                  </span>
                  <span
                    className={`font-medium ${
                      stockData.debt_equity < 1
                        ? 'text-green-600'
                        : 'text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    {formatNumber(stockData.debt_equity)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Current Ratio
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.current_ratio)}
                  </span>
                </div>
              </div>
            </div>

            {/* Growth Metrics */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                Growth Metrics
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Revenue Growth (3Y CAGR)
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.revenue_cagr_3y)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">
                    Profit Growth (3Y CAGR)
                  </span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {formatNumber(stockData.profit_cagr_3y)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
