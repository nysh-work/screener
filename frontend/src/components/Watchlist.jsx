import { useState, useEffect } from 'react';
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
} from '../services/api';
import { Plus, Trash2, TrendingUp, TrendingDown } from 'lucide-react';

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [shouldReload, setShouldReload] = useState(0);
  const [newItem, setNewItem] = useState({
    ticker: '',
    target_price: '',
    notes: '',
  });
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchWatchlist();
  }, [shouldReload]);

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const response = await getWatchlist();
      setWatchlist(response.data.watchlist);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await addToWatchlist({
        ...newItem,
        target_price: newItem.target_price
          ? parseFloat(newItem.target_price)
          : null,
      });
      setNewItem({ ticker: '', target_price: '', notes: '' });
      setShowAddForm(false);
      setShouldReload((p) => p + 1);
    } catch (error) {
      alert('Failed to add to watchlist');
      console.error(error);
    }
  };

  const handleRemove = async (ticker) => {
    if (confirm(`Remove ${ticker} from watchlist?`)) {
      try {
        await removeFromWatchlist(ticker);
        setShouldReload((p) => p + 1);
      } catch (error) {
        console.error('Error removing from watchlist:', error);
      }
    }
  };

  const formatCurrency = (num) => (num ? `₹${num.toFixed(2)}` : '-');
  const formatNumber = (num) => (num ? num.toFixed(2) : '-');

  if (loading && watchlist.length === 0)
    return <div className="text-center py-8">Loading watchlist...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          Watchlist
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          <Plus className="w-4 h-4 mr-2" /> Add Stock
        </button>
      </div>

      {showAddForm && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4 dark:text-gray-100">
            Add to Watchlist
          </h3>
          <form
            onSubmit={handleAdd}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <input
              type="text"
              placeholder="Ticker (e.g. TCS)"
              value={newItem.ticker}
              onChange={(e) =>
                setNewItem({ ...newItem, ticker: e.target.value.toUpperCase() })
              }
              className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              required
            />
            <input
              type="number"
              placeholder="Target Price (optional)"
              step="0.01"
              value={newItem.target_price}
              onChange={(e) =>
                setNewItem({ ...newItem, target_price: e.target.value })
              }
              className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <input
              type="text"
              placeholder="Notes (optional)"
              value={newItem.notes}
              onChange={(e) =>
                setNewItem({ ...newItem, notes: e.target.value })
              }
              className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
            <div className="md:col-span-3 flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {watchlist.map((stock) => {
          const hasTarget = stock.target_price && stock.current_price;
          const upside = hasTarget
            ? ((stock.target_price - stock.current_price) /
                stock.current_price) *
              100
            : null;
          const inBuyZone = hasTarget
            ? stock.current_price <= stock.target_price * 1.02
            : false;

          return (
            <div
              key={stock.ticker}
              className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 relative border ${inBuyZone ? 'border-green-500 ring-1 ring-green-200 dark:ring-green-700' : 'border-transparent'}`}
            >
              <button
                onClick={() => handleRemove(stock.ticker)}
                className="absolute top-4 right-4 text-gray-400 hover:text-red-500"
              >
                <Trash2 className="w-5 h-5" />
              </button>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {stock.ticker}
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Target: {formatCurrency(stock.target_price)}
                  </p>
                  {inBuyZone && (
                    <p className="mt-1 text-xs font-semibold text-green-600 dark:text-green-400">
                      In buy zone
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {formatCurrency(stock.current_price)}
                  </p>
                  {upside !== null && (
                    <p
                      className={`text-sm font-medium ${upside >= 0 ? 'text-green-600' : 'text-red-600'}`}
                    >
                      {upside >= 0 ? '+' : ''}
                      {upside.toFixed(2)}%
                    </p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    EV/EBITDA:
                  </span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.ev_ebitda)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">P/B:</span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.price_to_book)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    EMA 20:
                  </span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.ema_20)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    EMA 50:
                  </span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.ema_50)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    MACD:
                  </span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.macd)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">
                    Chop:
                  </span>
                  <span className="text-gray-900 dark:text-gray-100">
                    {formatNumber(stock.choppiness_index)}
                  </span>
                </div>
              </div>

              {stock.notes && (
                <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                    "{stock.notes}"
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {watchlist.length === 0 && !loading && (
        <div className="text-center py-10 bg-white dark:bg-gray-800 rounded-lg shadow">
          <p className="text-gray-500 dark:text-gray-400">
            Your watchlist is empty.
          </p>
        </div>
      )}
    </div>
  );
}
