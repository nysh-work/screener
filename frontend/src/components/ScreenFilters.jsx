import { useState, useEffect } from 'react';
import { listScreens, listSectors } from '../services/api';
import Tooltip from './Tooltip';

export default function ScreenFilters({ onRunScreen }) {
  const [screens, setScreens] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [sectorsLoading, setSectorsLoading] = useState(true);
  const [sectorsError, setSectorsError] = useState(false);
  const [selectedScreen, setSelectedScreen] = useState('value');
  const [selectedSectors, setSelectedSectors] = useState([]);
  const [minMarketCap, setMinMarketCap] = useState('');
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadScreens();
    loadSectors();
  }, []);

  const loadScreens = async () => {
    try {
      const response = await listScreens();
      setScreens(response.data.screens);
    } catch (error) {
      console.error('Error loading screens:', error);
    }
  };

  const loadSectors = async () => {
    setSectorsLoading(true);
    setSectorsError(false);
    try {
      const response = await listSectors();
      setSectors(response.data.sectors);
    } catch (error) {
      console.error('Error loading sectors:', error);
      setSectorsError(true);
      // Fallback to common sectors if API fails
      const fallbackSectors = [
        'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
        'Consumer Defensive', 'Energy', 'Utilities', 'Industrials',
        'Communication Services', 'Real Estate', 'Materials', 'Basic Materials'
      ];
      setSectors(fallbackSectors);
    } finally {
      setSectorsLoading(false);
    }
  };

  const handleSectorToggle = (sector) => {
    setSelectedSectors((prev) =>
      prev.includes(sector)
        ? prev.filter((s) => s !== sector)
        : [...prev, sector]
    );
  };

  const handleRunScreen = async () => {
    setLoading(true);
    try {
      const screenData = {
        screen_type: selectedScreen,
        sectors: selectedSectors.length > 0 ? selectedSectors : null,
        min_market_cap: minMarketCap ? parseFloat(minMarketCap) : null,
        limit: limit,
      };
      await onRunScreen(screenData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">
        Screen Filters
      </h2>

      <div className="space-y-6">
        {/* Screen Type Selection */}
        <div>
          <Tooltip content="Choose a pre-built screening strategy that filters stocks based on different investing philosophies. Each strategy uses proven fundamental metrics.">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Screening Strategy
            </label>
          </Tooltip>
          <select
            value={selectedScreen}
            onChange={(e) => setSelectedScreen(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            {screens.map((screen) => (
              <option key={screen.key} value={screen.key}>
                {screen.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {screens.find((s) => s.key === selectedScreen)?.description}
          </p>
        </div>

        {/* Market Cap Filter */}
        <div>
          <Tooltip content="Market capitalization is the total value of a company (share price × total shares). Larger companies are typically less volatile but may grow slower. Small caps can be riskier but offer higher growth potential.">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Minimum Market Cap (Crores)
            </label>
          </Tooltip>
          <input
            type="number"
            value={minMarketCap}
            onChange={(e) => setMinMarketCap(e.target.value)}
            placeholder="e.g., 1000"
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            💡 Tip: Large cap (&gt;20,000cr), Mid cap (5,000-20,000cr), Small cap (&lt;5,000cr)
          </p>
        </div>

        {/* Limit Filter */}
        <div>
          <Tooltip content="Limits the number of results returned. Start with fewer results for focused research, then expand as needed.">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Results: {limit}
            </label>
          </Tooltip>
          <input
            type="range"
            min="10"
            max="100"
            step="10"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Sector Filter */}
        <div>
          <Tooltip content="Filter by industry sector. Diversifying across sectors reduces risk. Each sector performs differently in various economic conditions.">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Sectors (Optional)
            </label>
          </Tooltip>
          {sectorsLoading ? (
            <div className="flex items-center justify-center p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-2"></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Loading sectors...</span>
            </div>
          ) : (
            <div className="max-h-40 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-gray-50 dark:bg-gray-700">
              {sectorsError && (
                <div className="mb-2 p-2 bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-600 rounded text-sm text-yellow-800 dark:text-yellow-200">
                  ⚠️ Using default sectors. Server connection issue.
                </div>
              )}
              {sectors.map((sector) => (
                <label key={sector} className="flex items-center mb-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 p-1 rounded">
                  <input
                    type="checkbox"
                    checked={selectedSectors.includes(sector)}
                    onChange={() => handleSectorToggle(sector)}
                    className="mr-2 h-4 w-4 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{sector}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Run Button */}
        <button
          onClick={handleRunScreen}
          disabled={loading}
          className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800'
          }`}
        >
          {loading ? 'Running Screen...' : 'Run Screen'}
        </button>
      </div>
    </div>
  );
}
