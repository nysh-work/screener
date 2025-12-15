import { useState, useEffect } from 'react';
import { getPortfolio, addToPortfolio, removeFromPortfolio } from '../services/api';
import { Plus, Trash2, TrendingUp, TrendingDown } from 'lucide-react';

export default function Portfolio() {
    const [portfolio, setPortfolio] = useState({ holdings: [], summary: {} });
    const [loading, setLoading] = useState(true);
    const [newHolding, setNewHolding] = useState({ ticker: '', quantity: '', price: '', date: '', notes: '' });
    const [showAddForm, setShowAddForm] = useState(false);

    useEffect(() => {
        fetchPortfolio();
    }, []);

    const fetchPortfolio = async () => {
        try {
            setLoading(true);
            const response = await getPortfolio();
            setPortfolio(response.data);
        } catch (error) {
            console.error('Error fetching portfolio:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddHolding = async (e) => {
        e.preventDefault();
        try {
            await addToPortfolio({
                ...newHolding,
                quantity: parseFloat(newHolding.quantity),
                price: parseFloat(newHolding.price)
            });
            setNewHolding({ ticker: '', quantity: '', price: '', date: '', notes: '' });
            setShowAddForm(false);
            fetchPortfolio();
        } catch (error) {
            alert('Failed to add holding');
            console.error(error);
        }
    };

    const handleRemove = async (id) => {
        if (confirm('Are you sure you want to remove this holding?')) {
            try {
                await removeFromPortfolio(id);
                fetchPortfolio();
            } catch (error) {
                console.error('Error removing holding:', error);
            }
        }
    };

    const formatCurrency = (num) => `₹${num?.toFixed(2)}`;

    if (loading) return <div className="text-center py-8">Loading portfolio...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Portfolio</h2>
                <button
                    onClick={() => setShowAddForm(!showAddForm)}
                    className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                    <Plus className="w-4 h-4 mr-2" /> Add Holding
                </button>
            </div>

            {portfolio.summary && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Total Invested</p>
                        <p className="text-xl font-bold dark:text-gray-100">{formatCurrency(portfolio.summary.total_invested)}</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Current Value</p>
                        <p className="text-xl font-bold dark:text-gray-100">{formatCurrency(portfolio.summary.current_value)}</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Total P&L</p>
                        <div className={`flex items-center text-xl font-bold ${portfolio.summary.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {portfolio.summary.total_pnl >= 0 ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
                            {formatCurrency(portfolio.summary.total_pnl)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Return %</p>
                        <p className={`text-xl font-bold ${portfolio.summary.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {portfolio.summary.total_return_pct?.toFixed(2)}%
                        </p>
                    </div>
                </div>
            )}

            {showAddForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold mb-4 dark:text-gray-100">Add New Holding</h3>
                    <form onSubmit={handleAddHolding} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                            type="text"
                            placeholder="Ticker (e.g. RELIANCE)"
                            value={newHolding.ticker}
                            onChange={(e) => setNewHolding({ ...newHolding, ticker: e.target.value.toUpperCase() })}
                            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            required
                        />
                        <input
                            type="date"
                            value={newHolding.date}
                            onChange={(e) => setNewHolding({ ...newHolding, date: e.target.value })}
                            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                        <input
                            type="number"
                            placeholder="Quantity"
                            value={newHolding.quantity}
                            onChange={(e) => setNewHolding({ ...newHolding, quantity: e.target.value })}
                            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Price per share"
                            step="0.01"
                            value={newHolding.price}
                            onChange={(e) => setNewHolding({ ...newHolding, price: e.target.value })}
                            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            required
                        />
                        <input
                            type="text"
                            placeholder="Notes (optional)"
                            value={newHolding.notes}
                            onChange={(e) => setNewHolding({ ...newHolding, notes: e.target.value })}
                            className="p-2 border rounded md:col-span-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        />
                        <div className="md:col-span-2 flex justify-end space-x-2">
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
                                Save Holding
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticker</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Price</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cur Price</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {portfolio.holdings.map((holding) => (
                            <tr key={holding.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium dark:text-gray-100">{holding.ticker}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right dark:text-gray-300">{holding.quantity}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right dark:text-gray-300">{formatCurrency(holding.purchase_price)}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-right dark:text-gray-300">{formatCurrency(holding.current_price)}</td>
                                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${holding.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {formatCurrency(holding.unrealized_pnl)} ({holding.return_pct?.toFixed(2)}%)
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button onClick={() => handleRemove(holding.id)} className="text-red-600 hover:text-red-900">
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {portfolio.holdings.length === 0 && (
                            <tr>
                                <td colSpan="6" className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                    No holdings found. Add stocks to start tracking.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
