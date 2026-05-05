export interface Post {
  id: string;
  date: string;
  title: string;
  url: string;
  author: string;
  preview: string;
  themes: string[];
  problems: string[];
  subreddit: string;
}

export interface Aggregates {
  themesByDay: Record<string, Record<string, number>>;
  problemsByDay: Record<string, Record<string, number>>;
  themeCounts: Record<string, number>;
  problemCounts: Record<string, number>;
  untaggedCount: number;
  untaggedKeywordFreq: Array<{ word: string; count: number }>;
  totalPosts: number;
  totalTaggedPosts: number;
}

export interface Taxonomy {
  schema_version: number;
  themes: string[];
  problems: Record<string, { theme: string; keywords: string[] }>;
}

export interface Meta {
  schema_version: number;
  generated_at: string;
  post_count: number;
  date_range: { start: string | null; end: string | null };
  posts_file: string;
  aggregates_file: string;
}

export interface ThemeFilterState {
  problems: string[];
  from: string | null;
  to: string | null;
  q: string;
  granularity: 'daily' | 'weekly';
}
