import { useState, useEffect } from 'react';
import {
  runBacktest,
  getBacktestHistory,
  listScreens,
  listCustomScreens,
} from '../services/api';
import { Play, Calendar, TrendingUp } from 'lucide-react';

export default function Backtest() {
  const [history, setHistory] = useState([]);
  const [predefinedScreens, setPredefinedScreens] = useState([]);
  const [customScreens, setCustomScreens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const [formData, setFormData] = useState({
    screenType: 'predefined', // predefined or custom
    screenName: '',
    startDate: '2023-01-01',
    endDate: new Date().toISOString().split('T')[0],
    holdingPeriod: 90,
  });

  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchHistory();
    fetchScreensList();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await getBacktestHistory();
      setHistory(response.data.history);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchScreensList = async () => {
    try {
      const [preRes, custRes] = await Promise.all([
        listScreens(),
        listCustomScreens(),
      ]);
      setPredefinedScreens(preRes.data.screens);
      setCustomScreens(custRes.data.screens);
      if (preRes.data.screens.length > 0) {
        setFormData((d) => ({ ...d, screenName: preRes.data.screens[0].key }));
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleRun = async (e) => {
    e.preventDefault();
    setRunning(true);
    setResult(null);
    try {
      const resp = await runBacktest({
        screen_name: formData.screenName,
        screen_type: formData.screenType,
        start_date: formData.startDate,
        end_date: formData.endDate,
        holding_period_days: parseInt(formData.holdingPeriod),
      });
      setResult(resp.data);
      fetchHistory();
    } catch (error) {
      console.error(error);
      alert('Backtest failed');
    } finally {
      setRunning(false);
    }
  };

  const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString();

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-6 dark:text-gray-100 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2" /> Run Backtest
        </h2>
        <form
          onSubmit={handleRun}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Strategy Type
            </label>
            <select
              value={formData.screenType}
              onChange={(e) => {
                const type = e.target.value;
                setFormData({
                  ...formData,
                  screenType: type,
                  screenName:
                    type === 'predefined'
                      ? predefinedScreens[0]?.key || ''
                      : customScreens[0]?.name || '',
                });
              }}
              className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="predefined">Predefined Screen</option>
              <option value="custom">Custom Screen</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Select Strategy
            </label>
            <select
              value={formData.screenName}
              onChange={(e) =>
                setFormData({ ...formData, screenName: e.target.value })
              }
              className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {formData.screenType === 'predefined'
                ? predefinedScreens.map((s) => (
                    <option key={s.key} value={s.key}>
                      {s.name}
                    </option>
                  ))
                : customScreens.map((s) => (
                    <option key={s.name} value={s.name}>
                      {s.name}
                    </option>
                  ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Start Date
            </label>
            <input
              type="date"
              required
              value={formData.startDate}
              onChange={(e) =>
                setFormData({ ...formData, startDate: e.target.value })
              }
              className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div className="md:col-span-3 flex justify-end">
            <button
              type="submit"
              disabled={running}
              className={`flex items-center px-6 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 ${running ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {running ? (
                'Running...'
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" /> Start Backtest
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {result && (
        <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 p-6 rounded-lg">
          <h3 className="text-lg font-bold text-green-800 dark:text-green-100 mb-4">
            Results Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-green-600 dark:text-green-300">
                Avg Return
              </p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {result.average_return?.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-green-600 dark:text-green-300">
                Win Rate
              </p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {result.winning_stocks !== undefined
                  ? (
                      (result.winning_stocks / result.stocks_passed) *
                      100
                    ).toFixed(0)
                  : 0}
                %
              </p>
            </div>
            <div>
              <p className="text-sm text-green-600 dark:text-green-300">
                Total Trades
              </p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {result.stocks_passed}
              </p>
            </div>
            <div>
              <p className="text-sm text-green-600 dark:text-green-300">
                Best Trade
              </p>
              <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                {result.best_performer}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Backtest History
          </h3>
        </div>
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Strategy
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Stocks
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Avg Return
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Period
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {history.map((item, idx) => (
              <tr key={idx}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {formatDate(item.backtest_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                  {item.screen_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                  {item.stocks_passed}
                </td>
                <td
                  className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${item.average_return > 0 ? 'text-green-600' : 'text-red-600'}`}
                >
                  {item.average_return?.toFixed(2)}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                  {item.start_date} to {item.end_date}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
