export default function Logo({ className = 'w-8 h-8', variant = 'color' }) {
  const colors =
    variant === 'color'
      ? {
          primary: '#16a34a',
          secondary: '#22c55e',
          accent: '#4ade80',
          bg: 'white',
        }
      : {
          primary: 'currentColor',
          secondary: 'currentColor',
          accent: 'currentColor',
          bg: 'transparent',
        };

  return (
    <svg
      className={className}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background Circle */}
      <circle
        cx="50"
        cy="50"
        r="48"
        fill={colors.bg}
        stroke={colors.primary}
        strokeWidth="2"
      />

      {/* Chart Bars - Rising trend */}
      <rect
        x="20"
        y="60"
        width="8"
        height="20"
        rx="2"
        fill={colors.primary}
        opacity="0.8"
      />
      <rect
        x="33"
        y="50"
        width="8"
        height="30"
        rx="2"
        fill={colors.secondary}
        opacity="0.9"
      />
      <rect x="46" y="40" width="8" height="40" rx="2" fill={colors.accent} />
      <rect
        x="59"
        y="30"
        width="8"
        height="50"
        rx="2"
        fill={colors.secondary}
        opacity="0.9"
      />
      <rect
        x="72"
        y="20"
        width="8"
        height="60"
        rx="2"
        fill={colors.primary}
        opacity="0.8"
      />

      {/* Trend Line */}
      <path
        d="M 22 65 L 37 55 L 50 45 L 63 35 L 76 25"
        stroke={colors.primary}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />

      {/* Sparkle/Star accent (education element) */}
      <circle cx="78" cy="23" r="3" fill="#fbbf24" />
      <path
        d="M 78 18 L 78 28 M 73 23 L 83 23"
        stroke="#fbbf24"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
