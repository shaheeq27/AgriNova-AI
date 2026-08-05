'use client';
import React, { useEffect, useState } from 'react';

export interface MetricProps {
  value: string | number;
  unit?: string;
  animate?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Metric: React.FC<MetricProps> = ({
  value,
  unit,
  animate = true,
  className = '',
  style,
}) => {
  const [displayValue, setDisplayValue] = useState(animate && typeof value === 'number' ? 0 : value);

  useEffect(() => {
    if (animate && typeof value === 'number') {
      let start = 0;
      const duration = 1000;
      const increment = value / (duration / 16);
      
      const timer = setInterval(() => {
        start += increment;
        if (start >= value) {
          setDisplayValue(value);
          clearInterval(timer);
        } else {
          setDisplayValue(Math.floor(start));
        }
      }, 16);
      
      return () => clearInterval(timer);
    }
  }, [value, animate]);

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: '2rem',
    fontWeight: 700,
    lineHeight: 1.2,
    margin: 0,
    color: 'var(--text-primary)',
    ...style,
  };

  const unitStyle: React.CSSProperties = {
    fontSize: '1rem',
    fontWeight: 400,
    color: 'var(--text-secondary)',
    marginLeft: '4px',
  };

  return (
    <div style={baseStyle} className={className}>
      {displayValue}
      {unit && <span style={unitStyle}>{unit}</span>}
    </div>
  );
};

export default Metric;
