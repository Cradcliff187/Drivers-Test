export interface Choice {
  label: string;
  text: string;
  isCorrect?: boolean;
}

export interface Question {
  questionText: string;
  choices: Choice[];
  explanation?: string;
  pageRef?: number;
} 