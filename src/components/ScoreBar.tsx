import React from 'react';

export default function ScoreBar({ correct, total }: { correct: number; total: number }) {
  const pct = total ? (correct / total) * 100 : 0;
  return (
    <div className="w-full sticky top-0 bg-white pt-2 z-10">
      <p className="text-sm text-center mb-1 font-medium">
        {correct} / {total} correct • {Math.round(pct)}%
      </p>
      <div className="w-full bg-gray-200 h-2">
        <div className="bg-green-600 h-2" style={{ width: pct + '%' }} />
      </div>
    </div>
  );
} 