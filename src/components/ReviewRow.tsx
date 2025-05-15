import React from 'react';
import { Question } from '../../types/Question';

interface Props {
  q: Question;
  userChoice: string;
  idx: number;
}

export default function ReviewRow({ q, userChoice, idx }: Props) {
  const correctLabel = q.choices.find((c) => c.isCorrect)?.label;
  return (
    <details className="border rounded mb-2" open={false}>
      <summary className="cursor-pointer p-2 select-none">
        Question {idx + 1}
      </summary>
      <div className="p-3 space-y-2">
        <p className="font-medium">{q.questionText}</p>
        <ul className="ml-4 list-disc space-y-1">
          {q.choices.map((c) => {
            const isUser = c.label === userChoice;
            const isCorrect = c.label === correctLabel;
            return (
              <li key={c.label} className="flex items-center gap-2">
                <span>{c.label}.</span>
                <span className={isCorrect ? 'text-green-700' : isUser && !isCorrect ? 'text-red-700' : ''}>
                  {c.text}
                </span>
                {isCorrect && <span>✅</span>}
                {isUser && !isCorrect && <span>❌</span>}
              </li>
            );
          })}
        </ul>
        {q.explanation && <p className="prose text-sm mt-2" dangerouslySetInnerHTML={{ __html: q.explanation }} />}
      </div>
    </details>
  );
} 