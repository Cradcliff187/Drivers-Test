import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function Home() {
  const navigate = useNavigate();
  const [count, setCount] = useState(10);
  const [difficulty, setDifficulty] = useState<'easy'|'medium'|'hard'|'all'>('all');

  const startQuiz = () => {
    navigate(`/quiz?count=${count}&difficulty=${difficulty}`);
  };

  return (
    <main className="max-w-sm mx-auto p-4 flex flex-col gap-4 text-center">
      <h1 className="text-2xl font-bold">KY Driver Practice Test</h1>
      <div>
        <label className="block mb-1 font-medium">Number of Questions</label>
        <input
          type="range"
          min={5}
          max={50}
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
          className="w-full"
        />
        <span>{count}</span>
      </div>
      <div>
        <label className="block mb-1 font-medium">Difficulty</label>
        <select
          value={difficulty}
          onChange={(e)=>setDifficulty(e.target.value as any)}
          className="w-full border p-2 rounded"
        >
          <option value="all">All</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>
      <button onClick={startQuiz} className="bg-blue-600 text-white py-2 rounded">
        Start Test
      </button>
    </main>
  );
} 