import { useState, useEffect } from 'react';
import { getUniverseData } from '../services/api';
import { ArrowUpDown, Search, Filter, Download, RefreshCw, AlertCircle } from 'lucide-react';

export default function Universe() {
  const [universeData, setUniverseData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('ticker');
  const [sortDirection, setSortDirection] = useState('asc');
  const [filters, setFilters] = useState({
    minMarketCap: '',
    maxMarketCap: '',
    minPE: '',
    maxPE: '',
    minPB: '',
    maxPB: '',
    minROE: '',
    maxROE: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);

  const columns = [
    { key: 'ticker', label: 'Ticker', sortable: true },
    { key: 'name', label: 'Company Name', sortable: true },
    { key: 'current_price', label: 'Current Price', sortable: true, format: 'currency' },
    { key: 'market_cap', label: 'Market Cap', sortable: true, format: 'currency' },
    { key: 'pe_ratio', label: 'P/E Ratio', sortable: true, format: 'number' },
    { key: 'pb_ratio', label: 'P/B Ratio', sortable: true, format: 'number' },
    { key: 'debt_to_equity', label: 'Debt/Equity', sortable: true, format: 'number' },
    { key: 'current_ratio', label: 'Current Ratio', sortable: true, format: 'number' },
    { key: 'roe', label: 'ROE %', sortable: true, format: 'percentage' },
    { key: 'operating_margin', label: 'Operating Margin %', sortable: true, format: 'percentage' }
  ];

  useEffect(() => {
    fetchUniverseData();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [filters, searchTerm, sortField, sortDirection]);

  const fetchUniverseData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getUniverseData({ limit: 500 }); // Get up to 500 stocks
      
      // Handle different API response formats
      let stocks = [];
      if (response.data && response.data.stocks) {
        stocks = response.data.stocks;
      } else if (Array.isArray(response.data)) {
        stocks = response.data;
      } else {
        throw new Error('Invalid data format from API');
      }
      
      // Map and normalize the data with better error handling
      const stocksWithMetrics = stocks.map(stock => ({
        ticker: stock.ticker || stock.symbol || 'N/A',
        name: stock.company_name || stock.name || 'Unknown Company',
        current_price: stock.current_price || stock.price || 0,
        market_cap: stock.market_cap || 0,
        pe_ratio: stock.pe_ratio || 0,
        pb_ratio: stock.pb_ratio || 0,
        debt_to_equity: stock.debt_to_equity || stock.debt_equity_ratio || 0,
        current_ratio: stock.current_ratio || 0,
        operating_margin: stock.operating_margin || stock.opm || stock.operating_profit_margin || 0,
        roe: stock.roe || stock.return_on_equity || 0
      }));
      
      setUniverseData(stocksWithMetrics);
    } catch (error) {
      console.error('Error fetching universe data:', error);
      setError(`Failed to load universe data: ${error.message}. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const formatValue = (value, format) => {
    if (value === null || value === undefined || value === '' || value === 0) {
      return format === 'currency' ? '₹0' : 'N/A';
    }
    
    try {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          }).format(value);
        case 'percentage':
          return `${parseFloat(value).toFixed(2)}%`;
        case 'number':
          return parseFloat(value).toFixed(2);
        default:
          return value;
      }
    } catch (error) {
      return 'N/A';
    }
  };

  const filteredAndSortedData = universeData
    .filter(stock => {
      // Search filter
      const matchesSearch = stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           stock.name.toLowerCase().includes(searchTerm.toLowerCase());
      
      if (!matchesSearch) return false;

      // Numeric filters
      if (filters.minMarketCap && stock.market_cap < parseFloat(filters.minMarketCap)) return false;
      if (filters.maxMarketCap && stock.market_cap > parseFloat(filters.maxMarketCap)) return false;
      if (filters.minPE && stock.pe_ratio < parseFloat(filters.minPE)) return false;
      if (filters.maxPE && stock.pe_ratio > parseFloat(filters.maxPE)) return false;
      if (filters.minPB && stock.pb_ratio < parseFloat(filters.minPB)) return false;
      if (filters.maxPB && stock.pb_ratio > parseFloat(filters.maxPB)) return false;
      if (filters.minROE && stock.roe < parseFloat(filters.minROE)) return false;
      if (filters.maxROE && stock.roe > parseFloat(filters.maxROE)) return false;

      return true;
    })
    .sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      
      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  // Pagination logic
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredAndSortedData.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const exportToCSV = () => {
    const csvContent = [
      columns.map(col => col.label).join(','),
      ...filteredAndSortedData.map(stock => 
        columns.map(col => {
          const value = stock[col.key];
          return value === null || value === undefined ? '' : value;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'universe_data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
          <div className="flex items-center justify-center">
            <RefreshCw className="w-8 h-8 text-primary-600 animate-spin mr-3" />
            <span className="text-lg">Loading universe data...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-6">
          <div className="flex items-center mb-3">
            <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
            <span className="text-red-800 dark:text-red-200 font-medium">Unable to Load Stock Universe</span>
          </div>
          <p className="text-red-700 dark:text-red-300 text-sm mb-4">
            We're having trouble connecting to the server. The backend API might be temporarily unavailable or experiencing issues.
          </p>
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchUniverseData}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Retry Connection
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Stock Universe</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Comprehensive data for all stocks in the database ({filteredAndSortedData.length} stocks)
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={exportToCSV}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
            <button
              onClick={fetchUniverseData}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* Search and Filter Controls */}
        <div className="mb-6 space-y-4">
          <div className="flex items-center space-x-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by ticker or company name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center px-4 py-2 rounded-lg ${showFilters ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Market Cap Min</label>
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minMarketCap}
                    onChange={(e) => setFilters({...filters, minMarketCap: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Market Cap Max</label>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxMarketCap}
                    onChange={(e) => setFilters({...filters, maxMarketCap: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">P/E Min</label>
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minPE}
                    onChange={(e) => setFilters({...filters, minPE: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">P/E Max</label>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxPE}
                    onChange={(e) => setFilters({...filters, maxPE: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">P/B Min</label>
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minPB}
                    onChange={(e) => setFilters({...filters, minPB: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">P/B Max</label>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxPB}
                    onChange={(e) => setFilters({...filters, maxPB: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ROE Min %</label>
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.minROE}
                    onChange={(e) => setFilters({...filters, minROE: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ROE Max %</label>
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.maxROE}
                    onChange={(e) => setFilters({...filters, maxROE: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-600 dark:border-gray-500"
                  />
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setFilters({
                    minMarketCap: '',
                    maxMarketCap: '',
                    minPE: '',
                    maxPE: '',
                    minPB: '',
                    maxPB: '',
                    minROE: '',
                    maxROE: ''
                  })}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto max-h-[600px] relative border border-gray-200 dark:border-gray-700 rounded-lg">
          <table className="w-full table-auto">
            <thead className="sticky top-0 z-10">
              <tr className="bg-gray-50 dark:bg-gray-700 shadow-sm">
                {columns.map(column => (
                  <th
                    key={column.key}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 bg-gray-50 dark:bg-gray-700"
                    onClick={() => column.sortable && handleSort(column.key)}
                  >
                    <div className="flex items-center">
                      {column.label}
                      {column.sortable && (
                        <ArrowUpDown className={`w-4 h-4 ml-1 ${sortField === column.key ? 'text-primary-600' : 'text-gray-400'}`} />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {paginatedData.map((stock, index) => (
                <tr key={stock.ticker} className={index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'}>
                  {columns.map(column => (
                    <td key={column.key} className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                      {formatValue(stock[column.key], column.format)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {filteredAndSortedData.length > 0 && (
          <div className="flex items-center justify-between mt-4 px-4">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, filteredAndSortedData.length)} of {filteredAndSortedData.length} entries
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`px-3 py-1 rounded ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'}`}
              >
                Previous
              </button>
              <div className="flex space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                        pageNum = i + 1;
                    } else if (currentPage <= 3) {
                        pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                    } else {
                        pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                        <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            className={`px-3 py-1 rounded ${currentPage === pageNum ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'}`}
                        >
                            {pageNum}
                        </button>
                    );
                })}
              </div>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`px-3 py-1 rounded ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'}`}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {filteredAndSortedData.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No stocks match your search criteria.
          </div>
        )}
      </div>
    </div>
  );
}