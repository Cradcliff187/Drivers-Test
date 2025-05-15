import React, { useState } from 'react';

type Choice = { label: string; text: string };
interface Props {
  question: { questionText: string; choices: Choice[] };
  onSelect: (label: string) => void;
}

export default function QuestionCard({ question, onSelect }: Props) {
  const [selected, setSelected] = useState<string>('');
  const choose = (label: string) => {
    setSelected(label);
    onSelect(label);
  };

  return (
    <div className="space-y-4">
      <p className="font-medium">{question.questionText}</p>
      <ul className="space-y-2">
        {question.choices.map((c) => (
          <li key={c.label}>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="choice"
                value={c.label}
                checked={selected === c.label}
                onChange={() => choose(c.label)}
                className="h-4 w-4"
              />
              <span>{c.text}</span>
            </label>
          </li>
        ))}
      </ul>
    </div>
  );
} 