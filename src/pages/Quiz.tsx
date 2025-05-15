import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import QuestionCard from '../components/QuestionCard';
import ScoreBar from '../components/ScoreBar';
import { useQuiz } from '../hooks/useQuiz';

export default function Quiz() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const count = Number(params.get('count') || 10);
  const difficulty = params.get('difficulty') || 'all';
  const quiz = useQuiz();

  useEffect(() => {
    if (!quiz.questions.length) {
      fetch(`/api/random?count=${count}`)
        .then((r) => r.json())
        .then((qs) => quiz.loadQuestions(qs));
    }
  }, []);

  const next = () => {
    if (quiz.index + 1 >= quiz.questions.length) {
      navigate('/result', { state: { answers: quiz.answers, questions: quiz.questions } });
    } else {
      quiz.next();
    }
  };

  if (!quiz.questions.length) return <p className="p-4">Loading…</p>;

  return (
    <main className="max-w-sm mx-auto p-4">
      <ScoreBar correct={quiz.correctCount} total={quiz.questions.length} />
      <QuestionCard
        question={quiz.questions[quiz.index]}
        onSelect={(choice) => quiz.selectAnswer(choice)}
      />
      <button
        disabled={quiz.answers[quiz.index] === undefined}
        onClick={next}
        className="mt-4 bg-blue-600 text-white w-full py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {quiz.index + 1 === quiz.questions.length ? 'Finish' : 'Next'}
      </button>
    </main>
  );
} 