export interface Topic {
  id: number;
  name: string;
}

export type Difficulty = "easy" | "medium" | "hard";
export type ProblemStatus = "todo" | "attempted" | "solved";

export interface Problem {
  id: number;
  title: string;
  url: string;
  difficulty: Difficulty;
  source: string;
  topics: Topic[];
  created_at: string;
  status: ProblemStatus | null;
}

export interface SheetProblem {
  id: number;
  problem: Problem;
  order: number;
}

export interface Sheet {
  id: number;
  name: string;
  is_public: boolean;
  created_at: string;
  sheet_problems: SheetProblem[];
}

export interface Stats {
  by_status: Record<string, number>;
  by_difficulty: Record<string, number>;
  by_topic: { problem__topics__name: string | null; count: number }[];
  total_solved: number;
}
