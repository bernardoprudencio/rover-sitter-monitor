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
  llmTagged?: boolean;
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
  research_file?: string;
  research_aggregates_file?: string;
  research_count?: number;
  sheet_url?: string;
}

export interface ResearchDoc {
  id: string;
  updated: string;
  date: string;
  space: string;
  title: string;
  url: string;
  author: string;
  excerpt: string;
  themes: string[];
  problems: string[];
  labels: string[];
  llmTagged?: boolean;
}

export interface ResearchAggregates {
  themeCounts: Record<string, number>;
  problemCounts: Record<string, number>;
  spaceCounts: Record<string, number>;
  untaggedCount: number;
  totalDocs: number;
}

export interface ThemeFilterState {
  problems: string[];
  from: string | null;
  to: string | null;
  q: string;
  granularity: 'daily' | 'weekly';
}

// ---------------------------------------------------------------------------
// Star Sitter VoC report (the /star-sitter deliverable). The narrative lives in
// a committed .ts content module (dashboard/src/content/starSitter.ts) because
// *.json is globally gitignored; charts still draw from the live aggregates.
// ---------------------------------------------------------------------------

export type Sentiment = 'positive' | 'negative' | 'mixed' | 'neutral';

export interface SentimentBreakdown {
  positive: number;
  negative: number;
  mixed: number;
  neutral: number;
}

/** A verbatim pull-quote sourced from a Reddit post. */
export interface VoCQuote {
  text: string;
  url: string;
  date?: string;
  author?: string;
}

/** One clustered Voice-of-Customer theme mined from the Reddit corpus. */
export interface VoCTheme {
  id: string;
  label: string;
  /** Number of core-corpus posts expressing this theme. */
  count: number;
  sentiment: SentimentBreakdown;
  /** 1–2 sentence synthesis of what sitters are saying. */
  summary: string;
  quotes: VoCQuote[];
  /** What this theme implies for the badge→tiers decision. */
  implication?: string;
}

/** A prior internal research study, summarized from the full Confluence page. */
export interface ResearchSummary {
  id: string;
  title: string;
  space: string;
  url: string;
  method?: string;
  /** The one-line headline takeaway. */
  takeaway: string;
  /** Verbatim participant quotes pulled from the study. */
  quotes: VoCQuote[];
  /** How the study bears on a tiered loyalty model. */
  relevanceToTiers?: string;
  /** Paths under /img/star-sitter/research/ for any captured figures. */
  figures?: Array<{ src: string; caption?: string }>;
}

/** A Reddit screenshot captured for the report. */
export interface ReportImage {
  src: string;
  caption: string;
  sourceUrl: string;
}

export interface HeadlineStat {
  label: string;
  value: string;
  hint?: string;
}

export interface StarSitterReport {
  /** Report title + framing shown in the hero. */
  title: string;
  subtitle: string;
  /** The decision this artifact is meant to inform. */
  decisionQuestion: string;
  /** Short paragraphs establishing why the team is revisiting Star Sitter. */
  framing: string[];
  /** Corpus provenance note (counts, date range, sourcing caveats). */
  corpusNote: string;
  /** The dashboard problem name whose aggregates drive the charts. */
  chartProblem: string;
  headlineStats: HeadlineStat[];
  /** Overall sentiment mix across the core corpus, for the donut. */
  overallSentiment: SentimentBreakdown;
  vocThemes: VoCTheme[];
  research: ResearchSummary[];
  images: ReportImage[];
  implications: {
    supports: string[];
    cautions: string[];
    openQuestions: string[];
  };
  /** ISO date the report content was last synthesized. */
  generatedAt: string;
}
