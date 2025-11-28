export interface CommentData {
  id: string;
  imageSource: string;
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  topic: string;
  theme: string;
}

export interface AnalysisStats {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
  themes: Record<string, number>;
  topics: Record<string, number>;
}

export type AppState = 'idle' | 'analyzing' | 'complete' | 'error';

export interface FileWithPreview extends File {
  preview: string;
}