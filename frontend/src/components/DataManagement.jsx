import { useState } from 'react';
import { updateUniverse } from '../services/api';
import { RefreshCw, Database, AlertCircle } from 'lucide-react';

export default function DataManagement() {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null); // { message, success, errors }

    const handleUpdate = async (universe) => {
        if (!confirm(`This will fetch data for all ${universe} stocks. It may take a while. Continue?`)) return;

        setLoading(true);
        setStatus(null);
        try {
            const response = await updateUniverse({ universe });
            setStatus(response.data);
        } catch (error) {
            console.error(error);
            setStatus({ error: 'Update failed. Check backend logs.' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-8">
            <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
                <div className="flex items-center mb-6">
                    <Database className="w-8 h-8 text-primary-600 mr-3" />
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Data Management</h2>
                </div>

                <p className="text-gray-600 dark:text-gray-400 mb-8">
                    Update your local database with fresh data from Yahoo Finance.
                    This process fetches the latest prices, fundamentals, and calculates metrics.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-750 transition">
                        <h3 className="text-lg font-semibold mb-2 dark:text-gray-100">NIFTY 50</h3>
                        <p className="text-sm text-gray-500 mb-4">Top 50 Blue Chip Companies</p>
                        <button
                            onClick={() => handleUpdate('nifty50')}
                            disabled={loading}
                            className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? 'Updating...' : 'Update Nifty 50'}
                        </button>
                    </div>

                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-750 transition">
                        <h3 className="text-lg font-semibold mb-2 dark:text-gray-100">NIFTY 100</h3>
                        <p className="text-sm text-gray-500 mb-4">Top 100 Large Cap Companies</p>
                        <button
                            onClick={() => handleUpdate('nifty100')}
                            disabled={loading}
                            className="w-full py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                        >
                            {loading ? 'Updating...' : 'Update Nifty 100'}
                        </button>
                    </div>

                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-750 transition">
                        <h3 className="text-lg font-semibold mb-2 dark:text-gray-100">NIFTY 500</h3>
                        <p className="text-sm text-gray-500 mb-4">Broad Market Coverage</p>
                        <button
                            onClick={() => handleUpdate('nifty500')}
                            disabled={loading}
                            className="w-full py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
                        >
                            {loading ? 'Updating...' : 'Update Nifty 500'}
                        </button>
                    </div>
                </div>

                {status && (
                    <div className={`mt-8 p-4 rounded-lg flex items-start ${status.error ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'}`}>
                        {status.error ? <AlertCircle className="w-5 h-5 mr-2 mt-0.5" /> : <RefreshCw className="w-5 h-5 mr-2 mt-0.5" />}
                        <div>
                            {status.error ? (
                                <p>{status.error}</p>
                            ) : (
                                <>
                                    <p className="font-semibold">{status.message}</p>
                                    <p className="text-sm mt-1">
                                        Successfully updated: {status.success} stocks.
                                        Errors: {status.errors}.
                                    </p>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
