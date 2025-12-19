import { useState, useEffect } from 'react';
import {
  listCustomScreens,
  createCustomScreen,
  deleteCustomScreen,
  runCustomScreen,
} from '../services/api';
import { Plus, Trash2, Play, Save, X } from 'lucide-react';
import ResultsTable from './ResultsTable';

const AVAILABLE_FIELDS = [
  { group: 'Valuation', label: 'P/E Ratio', value: 'price_to_earnings' },
  { group: 'Valuation', label: 'P/B Ratio', value: 'price_to_book' },
  { group: 'Valuation', label: 'EV/EBITDA', value: 'ev_ebitda' },
  { group: 'Profitability', label: 'ROE %', value: 'roe' },
  { group: 'Profitability', label: 'ROCE %', value: 'roce' },
  { group: 'Profitability', label: 'OPM %', value: 'opm' },
  { group: 'Profitability', label: 'NPM %', value: 'npm' },
  { group: 'Leverage', label: 'Debt/Equity', value: 'debt_equity' },
  { group: 'Leverage', label: 'Current Ratio', value: 'current_ratio' },
  { group: 'Growth', label: 'Sales Growth (3Y)', value: 'revenue_cagr_3y' },
  { group: 'Growth', label: 'Profit Growth (3Y)', value: 'profit_cagr_3y' },
  { group: 'Quality', label: 'Promoter Holding', value: 'promoter_holding' },
  { group: 'Quality', label: 'Piotroski Score', value: 'piotroski_score' },
  { group: 'Technical', label: 'EMA 20', value: 'ema_20' },
  { group: 'Technical', label: 'RSI', value: 'rsi' }, // Backend might not support yet but valid field check will catch if strict
  { group: 'Other', label: 'Market Cap', value: 'market_cap' },
  { group: 'Other', label: 'Current Price', value: 'price' },
];

const OPERATORS = [
  { label: 'Greater than', value: '>' },
  { label: 'Less than', value: '<' },
  { label: 'Equals', value: '=' },
  { label: 'Greater or Equal', value: '>=' },
  { label: 'Less or Equal', value: '<=' },
];

export default function CustomScreener() {
  const [screens, setScreens] = useState([]);
  const [view, setView] = useState('list'); // list, create, results
  const [loading, setLoading] = useState(false);

  // Create Form State
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    logic: 'AND',
    criteria: [{ field: 'roe', operator: '>', value: '' }],
  });

  // Results State
  const [results, setResults] = useState(null);
  const [activeScreenName, setActiveScreenName] = useState('');

  useEffect(() => {
    fetchScreens();
  }, []);

  const fetchScreens = async () => {
    try {
      const response = await listCustomScreens();
      setScreens(response.data.screens);
    } catch (error) {
      console.error('Error fetching screens:', error);
    }
  };

  const handleAddCriterion = () => {
    setFormData({
      ...formData,
      criteria: [
        ...formData.criteria,
        { field: 'roe', operator: '>', value: '' },
      ],
    });
  };

  const handleRemoveCriterion = (index) => {
    const newCriteria = formData.criteria.filter((_, i) => i !== index);
    setFormData({ ...formData, criteria: newCriteria });
  };

  const handleCriterionChange = (index, key, value) => {
    const newCriteria = [...formData.criteria];
    newCriteria[index][key] = value;
    setFormData({ ...formData, criteria: newCriteria });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      // Transform criteria array to object format expected by backend
      const criteriaObj = {};
      formData.criteria.forEach((c) => {
        criteriaObj[c.field] = {
          operator: c.operator,
          value: parseFloat(c.value),
        };
      });

      await createCustomScreen({
        name: formData.name,
        description: formData.description,
        logic: formData.logic,
        criteria: criteriaObj,
      });

      alert('Screen created successfully!');
      setView('list');
      fetchScreens();
      setFormData({
        name: '',
        description: '',
        logic: 'AND',
        criteria: [{ field: 'roe', operator: '>', value: '' }],
      });
    } catch (error) {
      console.error('Error creating screen:', error);
      alert('Failed to create screen. Check inputs.');
    }
  };

  const handleDelete = async (name) => {
    if (confirm(`Delete screen "${name}"?`)) {
      try {
        await deleteCustomScreen(name);
        fetchScreens();
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleRun = async (name) => {
    try {
      setLoading(true);
      setActiveScreenName(name);
      setView('results');
      const response = await runCustomScreen({ name, limit: 100 });
      setResults(response.data.results);
    } catch (error) {
      console.error(error);
      alert('Failed to run screen');
      setView('list');
    } finally {
      setLoading(false);
    }
  };

  if (view === 'results') {
    return (
      <div className="space-y-4">
        <button
          onClick={() => setView('list')}
          className="text-primary-600 hover:underline mb-4"
        >
          &larr; Back to Custom Screens
        </button>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-4">
          Results: {activeScreenName}
        </h2>
        {loading ? (
          <div className="text-center py-8">Running screen...</div>
        ) : (
          <ResultsTable results={results} onSelectStock={() => {}} />
        )}
      </div>
    );
  }

  if (view === 'create') {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold dark:text-gray-100">
            Create New Screen
          </h2>
          <button
            onClick={() => setView('list')}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Screen Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="e.g. High Growth Clean"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Logic
              </label>
              <select
                value={formData.logic}
                onChange={(e) =>
                  setFormData({ ...formData, logic: e.target.value })
                }
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="AND">Match ALL conditions (AND)</option>
                <option value="OR">Match ANY condition (OR)</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <input
                type="text"
                required
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Describe what this screen does..."
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-medium text-gray-900 dark:text-gray-200">
              Criteria
            </h3>
            {formData.criteria.map((criterion, index) => (
              <div
                key={index}
                className="flex flex-wrap md:flex-nowrap gap-4 items-end bg-gray-50 dark:bg-gray-750 p-3 rounded"
              >
                <div className="flex-1 min-w-[200px]">
                  <label className="text-xs text-gray-500 mb-1 block">
                    Metric
                  </label>
                  <select
                    value={criterion.field}
                    onChange={(e) =>
                      handleCriterionChange(index, 'field', e.target.value)
                    }
                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    {AVAILABLE_FIELDS.map((f) => (
                      <option key={f.value} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="w-32">
                  <label className="text-xs text-gray-500 mb-1 block">
                    Operator
                  </label>
                  <select
                    value={criterion.operator}
                    onChange={(e) =>
                      handleCriterionChange(index, 'operator', e.target.value)
                    }
                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    {OPERATORS.map((op) => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex-1 min-w-[150px]">
                  <label className="text-xs text-gray-500 mb-1 block">
                    Value
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={criterion.value}
                    onChange={(e) =>
                      handleCriterionChange(index, 'value', e.target.value)
                    }
                    className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Value"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveCriterion(index)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                  disabled={formData.criteria.length === 1}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={handleAddCriterion}
              className="flex items-center text-primary-600 text-sm font-medium hover:text-primary-700"
            >
              <Plus className="w-4 h-4 mr-1" /> Add Condition
            </button>
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="submit"
              className="flex items-center px-6 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            >
              <Save className="w-4 h-4 mr-2" /> Save Screen
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
            Custom Screens
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Build and run your own screening strategies
          </p>
        </div>
        <button
          onClick={() => setView('create')}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          <Plus className="w-4 h-4 mr-2" /> Create New
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {screens.map((screen) => (
          <div
            key={screen.name}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md flex justify-between items-center"
          >
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {screen.name}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                {screen.description}
              </p>
              <div className="mt-2 text-xs text-gray-500">
                {/* Try to parse criteria to show summary if it's a string, else show length */}
                Criteria:{' '}
                {typeof screen.criteria === 'string'
                  ? JSON.parse(screen.criteria).length
                  : Object.keys(screen.criteria || {}).length}{' '}
                conditions
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => handleRun(screen.name)}
                className="flex items-center px-3 py-1.5 bg-green-100 text-green-700 rounded hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
              >
                <Play className="w-4 h-4 mr-1" /> Run
              </button>
              <button
                onClick={() => handleDelete(screen.name)}
                className="p-2 text-gray-400 hover:text-red-600"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}

        {screens.length === 0 && (
          <div className="text-center py-10 bg-white dark:bg-gray-800 rounded-lg shadow">
            <p className="text-gray-500 dark:text-gray-400">
              No custom screens found.
            </p>
            <button
              onClick={() => setView('create')}
              className="text-primary-600 hover:underline mt-2"
            >
              Create your first screen
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
