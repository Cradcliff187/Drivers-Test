import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ReviewCard from '../components/ReviewCard';

export default function ReviewPage() {
  const { state } = useLocation() as any;
  const navigate = useNavigate();
  if (!state) return <p className="p-4">No data.</p>;
  const { questions, answers } = state;
  const [idx, setIdx] = useState(0);

  const next = () => setIdx((i: number) => Math.min(i + 1, questions.length - 1));
  const prev = () => setIdx((i: number) => Math.max(i - 1, 0));

  return (
    <main className="max-w-sm mx-auto p-4 space-y-4">
      <ReviewCard q={questions[idx]} userChoice={answers[idx]} />
      <div className="flex justify-between">
        <button disabled={idx===0} onClick={prev} className="px-3 py-1 bg-gray-200 rounded disabled:opacity-30">Prev</button>
        <span>{idx+1} / {questions.length}</span>
        <button disabled={idx===questions.length-1} onClick={next} className="px-3 py-1 bg-gray-200 rounded disabled:opacity-30">Next</button>
      </div>
      {idx===questions.length-1 && (
        <button className="w-full bg-blue-600 text-white py-2 rounded" onClick={()=>navigate('/')}>Done</button>
      )}
    </main>
  );
} 