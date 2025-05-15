import React from 'react';
import { Question } from '../../types/Question';

export default function ReviewCard({ q, userChoice }: { q: Question; userChoice: string }) {
  const correct = q.choices.find((c) => c.isCorrect)?.label;
  return (
    <div className="space-y-4">
      <p className="font-medium">{q.questionText}</p>
      <ul className="space-y-2">
        {q.choices.map((c) => {
          const isUser = c.label === userChoice;
          const isCorrect = c.label === correct;
          return (
            <li key={c.label} className="flex items-center gap-2">
              <span>{c.label}.</span>
              <span className={isCorrect ? 'text-green-700' : isUser && !isCorrect ? 'text-red-700' : ''}>{c.text}</span>
              {isCorrect && <span>✅</span>}
              {isUser && !isCorrect && <span>❌</span>}
            </li>
          );
        })}
      </ul>
      {q.explanation && <p className="prose text-sm" dangerouslySetInnerHTML={{ __html: q.explanation }} />}
    </div>
  );
} 