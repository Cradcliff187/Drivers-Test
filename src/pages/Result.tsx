import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ReviewRow from '../components/ReviewRow';

export default function Result() {
  const { state } = useLocation() as any;
  const navigate = useNavigate();
  if (!state) return <p className="p-4">No result data.</p>;
  const { answers, questions } = state;
  const correct = questions.reduce((acc: number, q: any, i: number) => {
    const chosen = answers[i];
    const right = q.choices.find((c: any) => c.isCorrect)?.label;
    return acc + (chosen === right ? 1 : 0);
  }, 0);
  const pct = Math.round((correct / questions.length) * 100);
  const share = () => {
    const text = `I scored ${pct}% on the KY Driver Practice Test!`;
    if (navigator.share) {
      navigator.share({ text, url: window.location.href });
    } else {
      navigator.clipboard.writeText(text + ' ' + window.location.href);
      alert('Link copied to clipboard');
    }
  };
  return (
    <main className="max-w-sm mx-auto p-4 space-y-4">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Your Score</h2>
        <p className="text-3xl">{pct}%</p>
        <button className="bg-blue-600 text-white py-1 px-3 rounded" onClick={share}>
          Share result
        </button>
      </div>

      <h3 className="font-semibold">Review Questions</h3>
      {questions.map((q: any, i: number) => (
        <ReviewRow key={i} q={q} userChoice={answers[i]} idx={i} />
      ))}

      <div className="text-center pt-4">
        <button
          className="bg-blue-600 text-white py-2 px-4 rounded"
          onClick={() => navigate('/')}
        >
          Retake
        </button>
      </div>

      <div className="text-center pt-4">
        <button
          className="bg-gray-200 py-1 px-3 rounded"
          onClick={() => navigate('/review', { state })}
        >
          Review questions one-by-one
        </button>
      </div>
    </main>
  );
} 