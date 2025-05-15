import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export default function Result() {
  const { state } = useLocation() as any;
  const navigate = useNavigate();
  if (!state) return <p className="p-4">No result data.</p>;
  const { answers, questions } = state;
  const correct = questions.filter((_:any,i:number)=>{
    const chosen = answers[i];
    const right = questions[i].choices.find((c:any)=>c.isCorrect)?.label;
    return chosen === right;
  }).length;
  const pct = Math.round((correct/questions.length)*100);
  return (
    <main className="max-w-sm mx-auto p-4 text-center space-y-4">
      <h2 className="text-2xl font-bold">Your Score</h2>
      <p className="text-3xl">{pct}%</p>
      <button className="bg-blue-600 text-white py-2 px-4 rounded" onClick={()=>navigate('/')}>Retake</button>
    </main>
  );
} 