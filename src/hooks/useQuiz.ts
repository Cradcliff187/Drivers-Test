import { useState, useEffect } from 'react';
import { Question } from '../../types/Question';

interface QuizState {
  questions: Question[];
  index: number;
  answers: Record<number, string>; // index -> label
}

const KEY = 'ky-quiz-state';

export function useQuiz() {
  const [state, setState] = useState<QuizState>(() => {
    const saved = sessionStorage.getItem(KEY);
    if (saved) return JSON.parse(saved);
    return { questions: [], index: 0, answers: {} };
  });

  // persist
  useEffect(() => {
    sessionStorage.setItem(KEY, JSON.stringify(state));
  }, [state]);

  const selectAnswer = (label: string) => {
    setState((s) => ({ ...s, answers: { ...s.answers, [s.index]: label } }));
  };

  const next = () => {
    setState((s) => ({ ...s, index: Math.min(s.index + 1, s.questions.length - 1) }));
  };

  const reset = () => {
    sessionStorage.removeItem(KEY);
    setState({ questions: [], index: 0, answers: {} });
  };

  const loadQuestions = (qs: Question[]) => {
    setState({ questions: qs, index: 0, answers: {} });
  };

  const correctCount = state.questions.reduce((acc, q, i) => {
    const chosen = state.answers[i];
    const right = q.choices.find((c) => c.isCorrect)?.label;
    return acc + (chosen === right ? 1 : 0);
  }, 0);

  return { ...state, selectAnswer, next, reset, loadQuestions, correctCount } as const;
} 