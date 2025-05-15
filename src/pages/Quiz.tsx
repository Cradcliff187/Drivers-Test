import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import QuestionCard from '../components/QuestionCard';
import ProgressBar from '../components/ProgressBar';

export default function Quiz() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const count = Number(params.get('count') || 10);
  const difficulty = params.get('difficulty') || 'all';
  const [questions, setQuestions] = useState<any[]>([]);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number,string>>({});

  useEffect(() => {
    fetch(`/api/random?count=${count}`)
      .then(r=>r.json())
      .then(setQuestions);
  },[]);

  const next = ()=>{
    if(index+1 >= questions.length){
      navigate('/result', {state:{answers, questions}});
    } else {
      setIndex(i=>i+1);
    }
  };

  if(!questions.length) return <p className="p-4">Loading…</p>;

  return (
    <main className="max-w-sm mx-auto p-4">
      <ProgressBar value={index+1} max={questions.length} />
      <QuestionCard question={questions[index]} onSelect={(choice)=>setAnswers({...answers, [index]: choice})} />
      <button onClick={next} className="mt-4 bg-blue-600 text-white w-full py-2 rounded">
        {index+1===questions.length ? 'Finish' : 'Next'}
      </button>
    </main>
  );
} 