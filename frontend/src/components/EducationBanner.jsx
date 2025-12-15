import { useState, useEffect } from 'react';
import { BookOpen, X, Lightbulb, TrendingUp, Shield } from 'lucide-react';

export default function EducationBanner() {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem('educationBannerDismissed');
    if (!dismissed) {
      setIsVisible(true);
    } else {
      setIsDismissed(true);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem('educationBannerDismissed', 'true');
    setIsVisible(false);
    setIsDismissed(true);
  };

  const handleReopen = () => {
    setIsVisible(true);
  };

  if (!isVisible && isDismissed) {
    return (
      <button
        onClick={handleReopen}
        className="mb-6 flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-200 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors text-sm"
      >
        <Lightbulb className="w-4 h-4" />
        <span>Show Educational Tips</span>
      </button>
    );
  }

  if (!isVisible) return null;

  return (
    <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 border-2 border-blue-200 dark:border-blue-700 rounded-xl p-6 shadow-lg animate-slideDown">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-500 rounded-lg">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Learn Before You Invest
            </h3>
          </div>

          <div className="space-y-3 text-gray-700 dark:text-gray-300">
            <p className="text-base leading-relaxed">
              Welcome to your stock screening tool! This is designed to help you <strong>learn</strong> and <strong>research</strong> - not to gamble with your money.
            </p>

            <div className="grid md:grid-cols-3 gap-4 mt-4">
              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                <Lightbulb className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm mb-1">Educate Yourself</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Understand financial metrics before making decisions. Visit the Learn tab.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm mb-1">Research Thoroughly</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Use screening as a starting point. Always do deeper research.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                <Shield className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm mb-1">Invest Responsibly</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Never invest money you can't afford to lose. This is not gambling.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-amber-100 dark:bg-amber-900 border border-amber-300 dark:border-amber-700 rounded-lg">
              <p className="text-sm text-amber-900 dark:text-amber-100">
                <strong>⚠️ Remember:</strong> Past performance doesn't guarantee future results.
                Markets are unpredictable. Learn the fundamentals, understand the risks, and never chase quick profits.
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleDismiss}
          className="ml-4 p-1 hover:bg-blue-200 dark:hover:bg-blue-800 rounded-lg transition-colors"
          aria-label="Dismiss banner"
        >
          <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>
    </div>
  );
}
