import {
  BookOpen,
  TrendingUp,
  Calculator,
  Shield,
  BarChart3,
  Lightbulb,
  AlertTriangle,
  Target,
} from 'lucide-react';

export default function Learn() {
  const sections = [
    {
      title: 'Investing is NOT Gambling',
      icon: Shield,
      color: 'red',
      content: [
        {
          subtitle: 'Key Differences',
          points: [
            'Gambling is based on luck and chance with negative expected returns',
            'Investing is based on research, analysis, and company fundamentals',
            'Investing in quality companies creates long-term wealth',
            'Gambling creates entertainment with the house having an edge',
          ],
        },
        {
          subtitle: 'The Danger of Treating Stocks Like a Casino',
          points: [
            'Day trading without research is speculation, not investing',
            "Chasing 'hot tips' or meme stocks is gambling behavior",
            "Over-leveraging or using money you can't afford to lose",
            "Not understanding what you're buying is a recipe for disaster",
          ],
        },
      ],
    },
    {
      title: 'Fundamental Analysis Basics',
      icon: Calculator,
      color: 'blue',
      content: [
        {
          subtitle: 'Valuation Metrics',
          points: [
            '<strong>P/E Ratio (Price-to-Earnings):</strong> Shows how much you pay for each rupee of earnings. Lower is generally better, but compare within industries.',
            '<strong>P/B Ratio (Price-to-Book):</strong> Compares stock price to book value per share. Value investors look for P/B < 1.',
            '<strong>EV/EBITDA:</strong> Enterprise Value to EBITDA. Useful for comparing companies with different debt levels.',
            '<strong>Dividend Yield:</strong> Annual dividends as a percentage of stock price. Higher yield can indicate value or distress.',
          ],
        },
        {
          subtitle: 'Profitability Metrics',
          points: [
            '<strong>ROE (Return on Equity):</strong> Net profit as % of shareholder equity. Aim for 15%+. Shows how efficiently capital is used.',
            '<strong>ROCE (Return on Capital Employed):</strong> Profit before tax as % of capital employed. Good companies have ROCE > 15-20%.',
            '<strong>OPM (Operating Profit Margin):</strong> Operating profit as % of sales. Shows operational efficiency.',
            '<strong>NPM (Net Profit Margin):</strong> Net profit as % of sales. Higher margins = better pricing power.',
          ],
        },
        {
          subtitle: 'Growth Metrics',
          points: [
            '<strong>Sales CAGR:</strong> Compound Annual Growth Rate of revenue. Look for consistent 10-15%+ growth.',
            '<strong>Profit CAGR:</strong> Growth in profits. Should match or exceed sales growth.',
            '<strong>EPS Growth:</strong> Earnings Per Share growth. Quality companies grow EPS consistently.',
          ],
        },
        {
          subtitle: 'Quality Indicators',
          points: [
            '<strong>Debt-to-Equity:</strong> Total debt divided by equity. Lower is better. < 1 is generally safe.',
            '<strong>Current Ratio:</strong> Current assets / current liabilities. Should be > 1.5 for safety.',
            '<strong>Promoter Holding:</strong> Percentage owned by founders. Higher = better skin in the game.',
            '<strong>Piotroski Score:</strong> 0-9 score measuring financial strength. 7+ indicates strong fundamentals.',
          ],
        },
      ],
    },
    {
      title: 'Technical Analysis Basics',
      icon: TrendingUp,
      color: 'green',
      content: [
        {
          subtitle: 'Moving Averages',
          points: [
            '<strong>EMA 20/50:</strong> Exponential Moving Averages smooth price data. Price above EMA = uptrend.',
            '<strong>Golden Cross:</strong> When short-term MA crosses above long-term MA = bullish signal.',
            '<strong>Death Cross:</strong> When short-term MA crosses below long-term MA = bearish signal.',
          ],
        },
        {
          subtitle: 'Momentum Indicators',
          points: [
            '<strong>RSI (Relative Strength Index):</strong> 0-100 scale. > 70 = overbought, < 30 = oversold.',
            '<strong>MACD:</strong> Moving Average Convergence Divergence. Shows momentum shifts and trend changes.',
            '<strong>Choppiness Index:</strong> Measures market chop. Low values = trending, high values = choppy/ranging.',
          ],
        },
        {
          subtitle: 'Important Disclaimer',
          points: [
            'Technical analysis shows what traders are doing, not company fundamentals',
            "Past chart patterns don't predict future movements with certainty",
            'Use technical analysis as ONE tool, not the only tool',
            'Combine with fundamental analysis for best results',
          ],
        },
      ],
    },
    {
      title: 'How to Use This Screener Responsibly',
      icon: Target,
      color: 'purple',
      content: [
        {
          subtitle: 'Step 1: Screen for Ideas',
          points: [
            'Use screening strategies to generate a list of potential companies',
            'Screening is the FIRST step, not the last step',
            'Look for companies that meet your criteria (value, growth, quality, etc.)',
          ],
        },
        {
          subtitle: 'Step 2: Research Deeply',
          points: [
            "Read the company's annual reports and investor presentations",
            'Understand the business model: How does it make money?',
            'Study the industry and competitive landscape',
            'Check management quality and track record',
            'Look at the balance sheet for hidden risks',
          ],
        },
        {
          subtitle: 'Step 3: Validate With Multiple Metrics',
          points: [
            "Don't rely on just one metric (e.g., low P/E)",
            'Check profitability, growth, quality, and valuation together',
            'Compare the company with peers in the same sector',
            'Look at 3-5 year trends, not just current numbers',
          ],
        },
        {
          subtitle: 'Step 4: Understand Risk',
          points: [
            "Every investment carries risk - even the 'safest' ones",
            'Diversify across sectors and companies',
            'Never invest borrowed money or emergency funds',
            "Set a maximum loss you're willing to accept before investing",
          ],
        },
      ],
    },
    {
      title: 'Common Mistakes to Avoid',
      icon: AlertTriangle,
      color: 'amber',
      content: [
        {
          subtitle: 'Behavioral Mistakes',
          points: [
            "❌ FOMO (Fear of Missing Out): Chasing stocks after they've run up",
            '❌ Panic Selling: Selling at the bottom during corrections',
            '❌ Overconfidence: Thinking a few wins make you an expert',
            '❌ Confirmation Bias: Only looking for information that supports your view',
            '❌ Anchoring: Fixating on purchase price instead of current value',
          ],
        },
        {
          subtitle: 'Analysis Mistakes',
          points: [
            '❌ Ignoring debt levels while focusing only on P/E ratio',
            '❌ Not reading financial statements and relying only on screeners',
            '❌ Buying based on tips from friends or social media',
            '❌ Neglecting to understand the business model',
            '❌ Comparing metrics across different industries without context',
          ],
        },
        {
          subtitle: 'Risk Management Mistakes',
          points: [
            '❌ Putting all your money in one stock',
            '❌ Investing money you need in the short term',
            '❌ Not having a plan or exit strategy',
            '❌ Over-trading and racking up fees',
            '❌ Ignoring position sizing (bet sizing)',
          ],
        },
      ],
    },
    {
      title: 'Recommended Learning Path',
      icon: BookOpen,
      color: 'indigo',
      content: [
        {
          subtitle: 'Essential Reading',
          points: [
            "📚 'The Intelligent Investor' by Benjamin Graham",
            "📚 'One Up On Wall Street' by Peter Lynch",
            "📚 'Common Stocks and Uncommon Profits' by Philip Fisher",
            "📚 'Coffee Can Investing' by Saurabh Mukherjea (India-focused)",
          ],
        },
        {
          subtitle: 'Online Resources',
          points: [
            '🌐 Screener.in - Detailed financial data and screening',
            '🌐 Moneycontrol - News and market updates',
            '🌐 NSE/BSE websites - Official market data',
            '🌐 Annual reports - Available on company websites',
          ],
        },
        {
          subtitle: 'Practice & Learn',
          points: [
            'Start with paper trading (virtual portfolio) before using real money',
            'Track your decisions and learn from mistakes',
            "Study successful investors' strategies",
            'Join investing communities, but think independently',
            'Continuously educate yourself - markets evolve',
          ],
        },
      ],
    },
  ];

  const getColorClasses = (color) => {
    const colors = {
      red: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 border-red-200 dark:border-red-700',
      blue: 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-700',
      green:
        'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 border-green-200 dark:border-green-700',
      purple:
        'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-700',
      amber:
        'bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-700',
      indigo:
        'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-700',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-8 text-white shadow-lg">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white bg-opacity-20 rounded-lg">
            <Lightbulb className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Learn to Invest Wisely</h1>
            <p className="text-primary-100 mt-1">
              Education is your best investment. Understand before you invest.
            </p>
          </div>
        </div>
      </div>

      {/* Sections */}
      {sections.map((section, index) => {
        const Icon = section.icon;
        return (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden"
          >
            <div className={`p-6 border-l-4 ${getColorClasses(section.color)}`}>
              <div className="flex items-center gap-3 mb-4">
                <Icon className="w-6 h-6" />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {section.title}
                </h2>
              </div>

              <div className="space-y-6">
                {section.content.map((subsection, subIndex) => (
                  <div key={subIndex}>
                    {subsection.subtitle && (
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                        {subsection.subtitle}
                      </h3>
                    )}
                    <ul className="space-y-2 ml-4">
                      {subsection.points.map((point, pointIndex) => (
                        <li
                          key={pointIndex}
                          className="text-gray-700 dark:text-gray-300 leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: `• ${point}` }}
                        />
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}

      {/* Final Warning */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900 dark:to-orange-900 border-2 border-red-200 dark:border-red-700 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-red-900 dark:text-red-100 mb-2">
              Final Reminder: This is Your Hard-Earned Money
            </h3>
            <p className="text-red-800 dark:text-red-200 leading-relaxed">
              Remember why you built this tool: to <strong>learn</strong> and
              make <strong>informed decisions</strong> - not to gamble. If you
              find yourself making impulsive decisions, chasing quick profits,
              or investing money you can't afford to lose, <strong>STOP</strong>
              . Take a break. Go back to learning. The stock market will always
              be there tomorrow. Your capital, once lost, may not be.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
