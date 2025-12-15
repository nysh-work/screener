import { useState } from 'react';
import { updateUniverse, addStock, addStocksFromCSV } from '../services/api';
import { RefreshCw, Database, AlertCircle, Plus, Upload } from 'lucide-react';

export default function DataManagement() {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null); // { message, success, errors }
    const [showManualForm, setShowManualForm] = useState(false);
    const [showCSVUpload, setShowCSVUpload] = useState(false);
    const [manualStock, setManualStock] = useState({ ticker: '', name: '' });
    const [csvFile, setCsvFile] = useState(null);

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

    const handleManualStockSubmit = async (e) => {
        e.preventDefault();
        if (!manualStock.ticker || !manualStock.name) {
            setStatus({ error: 'Please fill in both ticker and name fields.' });
            return;
        }

        setLoading(true);
        setStatus(null);
        try {
            const response = await addStock(manualStock);
            setStatus({ message: `Stock ${manualStock.ticker} added successfully!`, success: 1, errors: 0 });
            setManualStock({ ticker: '', name: '' });
            setShowManualForm(false);
        } catch (error) {
            console.error(error);
            setStatus({ error: 'Failed to add stock. Please check if it already exists.' });
        } finally {
            setLoading(false);
        }
    };

    const handleCSVUpload = async (e) => {
        e.preventDefault();
        if (!csvFile) {
            setStatus({ error: 'Please select a CSV file.' });
            return;
        }

        setLoading(true);
        setStatus(null);
        
        const formData = new FormData();
        formData.append('file', csvFile);

        try {
            const response = await addStocksFromCSV(formData);
            setStatus({ 
                message: 'CSV upload completed!', 
                success: response.data.success || 0, 
                errors: response.data.errors || 0 
            });
            setCsvFile(null);
            setShowCSVUpload(false);
            e.target.reset();
        } catch (error) {
            console.error(error);
            setStatus({ error: 'Failed to upload CSV. Please check file format.' });
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file && file.type === 'text/csv') {
            setCsvFile(file);
        } else {
            setStatus({ error: 'Please select a valid CSV file.' });
            e.target.value = '';
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

                {/* Manual Stock Entry and CSV Upload Section */}
                <div className="mt-8 border-t border-gray-200 dark:border-gray-700 pt-8">
                    <h3 className="text-xl font-semibold mb-6 text-gray-800 dark:text-gray-100">Add Individual Stocks</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        {/* Manual Stock Entry */}
                        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                            <div className="flex items-center mb-4">
                                <Plus className="w-6 h-6 text-green-600 mr-2" />
                                <h4 className="text-lg font-semibold dark:text-gray-100">Add Stock Manually</h4>
                            </div>
                            <p className="text-sm text-gray-500 mb-4">Add individual stocks to your database</p>
                            
                            {!showManualForm ? (
                                <button
                                    onClick={() => setShowManualForm(true)}
                                    disabled={loading}
                                    className="w-full py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                >
                                    Add Manual Stock
                                </button>
                            ) : (
                                <form onSubmit={handleManualStockSubmit} className="space-y-3">
                                    <input
                                        type="text"
                                        placeholder="Stock Ticker (e.g., AAPL)"
                                        value={manualStock.ticker}
                                        onChange={(e) => setManualStock({...manualStock, ticker: e.target.value.toUpperCase()})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                                        required
                                    />
                                    <input
                                        type="text"
                                        placeholder="Company Name"
                                        value={manualStock.name}
                                        onChange={(e) => setManualStock({...manualStock, name: e.target.value})}
                                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                                        required
                                    />
                                    <div className="flex space-x-2">
                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="flex-1 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                                        >
                                            {loading ? 'Adding...' : 'Add Stock'}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setShowManualForm(false);
                                                setManualStock({ ticker: '', name: '' });
                                            }}
                                            disabled={loading}
                                            className="flex-1 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>

                        {/* CSV Upload */}
                        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                            <div className="flex items-center mb-4">
                                <Upload className="w-6 h-6 text-blue-600 mr-2" />
                                <h4 className="text-lg font-semibold dark:text-gray-100">Upload CSV File</h4>
                            </div>
                            <p className="text-sm text-gray-500 mb-4">Add multiple stocks from CSV file</p>
                            
                            {!showCSVUpload ? (
                                <button
                                    onClick={() => setShowCSVUpload(true)}
                                    disabled={loading}
                                    className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                                >
                                    Upload CSV File
                                </button>
                            ) : (
                                <form onSubmit={handleCSVUpload} className="space-y-3">
                                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                                        <input
                                            type="file"
                                            accept=".csv"
                                            onChange={handleFileChange}
                                            className="hidden"
                                            id="csv-file-input"
                                        />
                                        <label htmlFor="csv-file-input" className="cursor-pointer">
                                            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                                            <p className="text-sm text-gray-500">
                                                {csvFile ? csvFile.name : 'Click to select CSV file'}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-1">
                                                Format: ticker, name
                                            </p>
                                        </label>
                                    </div>
                                    <div className="flex space-x-2">
                                        <button
                                            type="submit"
                                            disabled={loading || !csvFile}
                                            className="flex-1 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                                        >
                                            {loading ? 'Uploading...' : 'Upload CSV'}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setShowCSVUpload(false);
                                                setCsvFile(null);
                                            }}
                                            disabled={loading}
                                            className="flex-1 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 disabled:opacity-50"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>
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
