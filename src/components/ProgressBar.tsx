import React from 'react';

export default function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = (value / max) * 100;
  return (
    <div className="w-full bg-gray-200 rounded h-2 mb-4">
      <div className="bg-blue-600 h-2 rounded" style={{ width: pct + '%' }} />
    </div>
  );
} 