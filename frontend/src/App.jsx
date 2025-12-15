import { useState, useEffect } from 'react';
import { BarChart3, Search, TrendingUp } from 'lucide-react';
import ScreenFilters from './components/ScreenFilters';
import ResultsTable from './components/ResultsTable';
import StockDetail from './components/StockDetail';
import { runScreen, healthCheck } from './services/api';

function App() {
  const [screenResults, setScreenResults] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [screenInfo, setScreenInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await healthCheck();
      setApiStatus('healthy');
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const handleRunScreen = async (screenData) => {
    try {
      const response = await runScreen(screenData);
      setScreenResults(response.data.results);
      setScreenInfo({
        name: response.data.screen_name,
        description: response.data.description,
        criteria: response.data.criteria,
        stats: response.data.stats,
      });
    } catch (error) {
      console.error('Error running screen:', error);
      alert('Failed to run screen. Make sure the backend is running and data is loaded.');
    }
  };

  const handleSelectStock = (ticker) => {
    setSelectedStock(ticker);
  };

  const handleCloseStockDetail = () => {
    setSelectedStock(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-primary-600 dark:text-primary-400 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                  Stock Screener
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Indian Equity Markets • NSE/BSE
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
                apiStatus === 'healthy'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : apiStatus === 'error'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  apiStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                {apiStatus === 'healthy' ? 'API Connected' : apiStatus === 'error' ? 'API Error' : 'Checking...'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {apiStatus === 'error' && (
          <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                  Backend API not available
                </h3>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  <p>
                    Make sure the FastAPI backend is running:
                    <code className="ml-2 px-2 py-1 bg-red-100 dark:bg-red-800 rounded">
                      python -m uvicorn api.app:app --reload
                    </code>
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Screen Info Banner */}
        {screenInfo && (
          <div className="bg-primary-50 dark:bg-primary-900 border border-primary-200 dark:border-primary-700 rounded-lg p-6 mb-6">
            <div className="flex items-start">
              <TrendingUp className="w-6 h-6 text-primary-600 dark:text-primary-400 mr-3 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-primary-900 dark:text-primary-100">
                  {screenInfo.name}
                </h3>
                <p className="text-sm text-primary-700 dark:text-primary-300 mt-1">
                  {screenInfo.description}
                </p>
                {screenInfo.stats && (
                  <div className="mt-3 flex flex-wrap gap-4 text-sm">
                    <span className="text-primary-800 dark:text-primary-200">
                      <strong>Stocks Found:</strong> {screenInfo.stats.total_stocks}
                    </span>
                    {screenInfo.stats.avg_pe && (
                      <span className="text-primary-800 dark:text-primary-200">
                        <strong>Avg P/E:</strong> {screenInfo.stats.avg_pe.toFixed(2)}
                      </span>
                    )}
                    {screenInfo.stats.avg_roe && (
                      <span className="text-primary-800 dark:text-primary-200">
                        <strong>Avg ROE:</strong> {screenInfo.stats.avg_roe.toFixed(2)}%
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <ScreenFilters onRunScreen={handleRunScreen} />
          </div>

          {/* Results Area */}
          <div className="lg:col-span-2">
            <ResultsTable
              results={screenResults}
              onSelectStock={handleSelectStock}
            />
          </div>
        </div>
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetail
          ticker={selectedStock}
          onClose={handleCloseStockDetail}
        />
      )}

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            <strong>Disclaimer:</strong> This tool is for educational purposes only. Not investment advice.
            Always conduct your own research.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
