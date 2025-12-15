import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, LayoutGrid, List, PieChart, Eye, History, Database, Menu, X, AlertCircle, Globe } from 'lucide-react';
import ScreenFilters from './components/ScreenFilters';
import ResultsTable from './components/ResultsTable';
import StockDetail from './components/StockDetail';
import Portfolio from './components/Portfolio';
import Watchlist from './components/Watchlist';
import CustomScreener from './components/CustomScreener';
import Backtest from './components/Backtest';
import DataManagement from './components/DataManagement';
import Universe from './components/Universe';
import IndexFooter from './components/IndexFooter';
import { runScreen, healthCheck } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('screener');
  const [screenResults, setScreenResults] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [screenInfo, setScreenInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  const renderContent = () => {
    switch (activeTab) {
      case 'screener':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <ScreenFilters onRunScreen={handleRunScreen} />
            </div>
            <div className="lg:col-span-2">
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
              <ResultsTable
                results={screenResults}
                onSelectStock={handleSelectStock}
              />
            </div>
          </div>
        );
      case 'custom':
        return <CustomScreener />;
      case 'portfolio':
        return <Portfolio />;
      case 'watchlist':
        return <Watchlist />;
      case 'backtest':
        return <Backtest />;
      case 'data':
        return <DataManagement />;
      case 'universe':
        return <Universe />;
      default:
        return <div>Select a tab</div>;
    }
  };

  const NavItem = ({ id, icon: Icon, label }) => (
    <button
      onClick={() => { setActiveTab(id); setMobileMenuOpen(false); }}
      className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${activeTab === id
          ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-100'
          : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
        }`}
    >
      <Icon className="w-4 h-4 mr-2" />
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-primary-600 dark:text-primary-400 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 hidden sm:block">
                  Nishanth's Screener
                </h1>
              </div>
            </div>

            {/* Desktop Nav */}
            <nav className="hidden md:flex space-x-1">
              <NavItem id="screener" icon={LayoutGrid} label="Scanner" />
              <NavItem id="custom" icon={List} label="Custom" />
              <NavItem id="portfolio" icon={PieChart} label="Portfolio" />
              <NavItem id="watchlist" icon={Eye} label="Watchlist" />
              <NavItem id="universe" icon={Globe} label="Universe" />
              <NavItem id="backtest" icon={History} label="Backtest" />
              <NavItem id="data" icon={Database} label="Data" />
            </nav>

            <div className="flex items-center">
              <div className={`flex items-center px-3 py-1 rounded-full text-xs sm:text-sm ${apiStatus === 'healthy'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : apiStatus === 'error'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${apiStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                <span className="hidden sm:inline">{apiStatus === 'healthy' ? 'API Connected' : apiStatus === 'error' ? 'API Error' : 'Checking...'}</span>
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden ml-4 p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-2 pt-2 pb-3 space-y-1">
            <NavItem id="screener" icon={LayoutGrid} label="Scanner" />
            <NavItem id="custom" icon={List} label="Custom" />
            <NavItem id="portfolio" icon={PieChart} label="Portfolio" />
            <NavItem id="watchlist" icon={Eye} label="Watchlist" />
            <NavItem id="universe" icon={Globe} label="Universe" />
            <NavItem id="backtest" icon={History} label="Backtest" />
            <NavItem id="data" icon={Database} label="Data" />
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {apiStatus === 'error' && (
          <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertCircle className="h-5 w-5 text-red-400" />
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

        {renderContent()}
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetail
          ticker={selectedStock}
          onClose={handleCloseStockDetail}
        />
      )}

      {/* Index Data Footer */}
      <IndexFooter />

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            <strong>Disclaimer:</strong> Nishanth, please remember the lessons you have learnt from the past! This is being made to ensure that you do not loose your head and like you did previously.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
