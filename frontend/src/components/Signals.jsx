import { useEffect, useState } from 'react';
import { getSignals, runSignalsBacktest, addToWatchlist } from '../services/api';
import { TrendingUp, TrendingDown, Eye, Plus } from 'lucide-react';

export default function Signals() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    ema: 'all',
    macd: 'all',
    trend: 'all',
    search: ''
  });
  const [backtestDays, setBacktestDays] = useState(30);
  const [backtest, setBacktest] = useState(null);
  const [running, setRunning] = useState(false);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (filters.search) params.search = filters.search;
      if (filters.ema === 'bullish') params.ema_bullish = true;
      if (filters.ema === 'bearish') params.ema_bearish = true;
      if (filters.macd === 'bullish') params.macd_bullish = true;
      if (filters.macd === 'bearish') params.macd_bearish = true;
      if (filters.trend === 'trending') params.trending = true;
      if (filters.trend === 'choppy') params.choppy = true;
      const resp = await getSignals(params);
      setSignals(resp.data.signals || []);
    } catch (e) {
      setError('Failed to load signals');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  const filtered = signals.filter(s => {
    const search = filters.search.trim().toLowerCase();
    if (search && !(s.ticker?.toLowerCase().includes(search) || s.company_name?.toLowerCase().includes(search))) return false;
    if (filters.ema === 'bullish' && !s.ema_bullish) return false;
    if (filters.ema === 'bearish' && !s.ema_bearish) return false;
    if (filters.macd === 'bullish' && !s.macd_bullish) return false;
    if (filters.macd === 'bearish' && !s.macd_bearish) return false;
    if (filters.trend === 'trending' && !s.trending) return false;
    if (filters.trend === 'choppy' && !s.choppy) return false;
    return true;
  });

  const format = n => n !== null && n !== undefined ? Number(n).toFixed(2) : '-';

  const handleAddWatchlist = async (ticker) => {
    try {
      await addToWatchlist({ ticker });
      alert(`Added ${ticker} to watchlist`);
    } catch {
      alert('Failed to add to watchlist');
    }
  };

  const handleRunBacktest = async () => {
    try {
      setRunning(true);
      setBacktest(null);
      const payload = {
        days: Number(backtestDays) || 30,
        search: filters.search || undefined,
        ema_bullish: filters.ema === 'bullish' ? true : undefined,
        ema_bearish: filters.ema === 'bearish' ? true : undefined,
        macd_bullish: filters.macd === 'bullish' ? true : undefined,
        macd_bearish: filters.macd === 'bearish' ? true : undefined,
        trending: filters.trend === 'trending' ? true : undefined,
        choppy: filters.trend === 'choppy' ? true : undefined,
        limit: 200
      };
      const resp = await runSignalsBacktest(payload);
      setBacktest(resp.data);
    } catch {
      alert('Failed to run backtest');
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading signals...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded p-4">
        <p className="text-red-700 dark:text-red-300">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Signals</h2>
        <button onClick={fetchSignals} className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">Refresh</button>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <input
            placeholder="Search ticker or company"
            value={filters.search}
            onChange={e => setFilters({ ...filters, search: e.target.value })}
            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <select value={filters.ema} onChange={e => setFilters({ ...filters, ema: e.target.value })} className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="all">EMA: All</option>
            <option value="bullish">EMA: Bullish</option>
            <option value="bearish">EMA: Bearish</option>
          </select>
          <select value={filters.macd} onChange={e => setFilters({ ...filters, macd: e.target.value })} className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="all">MACD: All</option>
            <option value="bullish">MACD: Bullish</option>
            <option value="bearish">MACD: Bearish</option>
          </select>
          <select value={filters.trend} onChange={e => setFilters({ ...filters, trend: e.target.value })} className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="all">Trend: All</option>
            <option value="trending">Trend: Trending</option>
            <option value="choppy">Trend: Choppy</option>
          </select>
          <div className="flex items-center space-x-2">
            <div className="flex items-center text-green-600"><TrendingUp className="w-4 h-4 mr-1" />Bullish</div>
            <div className="flex items-center text-red-600"><TrendingDown className="w-4 h-4 mr-1" />Bearish</div>
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-700 dark:text-gray-300">Light Backtest Days</label>
            <input
              type="number"
              min="2"
              max="365"
              value={backtestDays}
              onChange={e => setBacktestDays(e.target.value)}
              className="w-24 p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          <button
            onClick={handleRunBacktest}
            disabled={running}
            className={`px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 ${running ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {running ? 'Running...' : 'Run Light Backtest'}
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticker</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">EMA20</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">EMA50</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">MACD</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Chop</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {filtered.map(s => (
              <tr key={s.ticker}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">{s.ticker}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">{format(s.current_price)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">{format(s.ema_20)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">{format(s.ema_50)}</td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${s.macd >= 0 ? 'text-green-600' : 'text-red-600'}`}>{format(s.macd)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">{format(s.choppiness_index)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex items-center space-x-2">
                    {s.ema_bullish && <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">EMA Bullish</span>}
                    {s.ema_bearish && <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-700">EMA Bearish</span>}
                    {s.macd_bullish && <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">MACD+</span>}
                    {s.macd_bearish && <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-700">MACD-</span>}
                    {s.trending && <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700">Trending</span>}
                    {s.choppy && <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">Choppy</span>}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                  <button onClick={() => handleAddWatchlist(s.ticker)} className="inline-flex items-center px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700">
                    <Plus className="w-4 h-4 mr-1" /> Watchlist
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {backtest && (
        <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 p-4 rounded">
          <h3 className="text-lg font-semibold text-green-800 dark:text-green-100 mb-2">Backtest Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-green-700 dark:text-green-200">Tickers Tested</div>
              <div className="text-xl font-bold text-green-900 dark:text-green-100">{backtest.summary?.tickers_tested || 0}</div>
            </div>
            <div>
              <div className="text-sm text-green-700 dark:text-green-200">Avg Return %</div>
              <div className="text-xl font-bold text-green-900 dark:text-green-100">{Number(backtest.summary?.avg_return_pct || 0).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-green-700 dark:text-green-200">Median Return %</div>
              <div className="text-xl font-bold text-green-900 dark:text-green-100">{Number(backtest.summary?.median_return_pct || 0).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-green-700 dark:text-green-200">Win Rate %</div>
              <div className="text-xl font-bold text-green-900 dark:text-green-100">{Number(backtest.summary?.win_rate_pct || 0).toFixed(0)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
