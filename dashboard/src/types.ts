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

// ---------------------------------------------------------------------------
// Plan cross-check. A VoC report is most useful when it is pointed at a
// specific proposal, so a report may optionally carry a verdict table checking
// an external product plan item-by-item against its own evidence. Kept
// optional: starSitter.ts / lockedRates.ts have no plan to check.
// ---------------------------------------------------------------------------

/**
 * How the corpus bears on one thing a plan proposes, prioritizes, or rejects.
 * `silent` is a first-class answer — the absence of evidence is reported, not
 * upgraded into a contradiction.
 */
export type CrossCheckVerdict = 'supported' | 'contradicted' | 'mixed' | 'silent';

export interface CrossCheckItem {
  id: string;
  /** The plan's item, in its own words where possible. */
  claim: string;
  /** Where it sits in the plan — "P0", "Cut line · No", "Motivation", … */
  planPosition: string;
  verdict: CrossCheckVerdict;
  /** One line naming the verdict, for scanning. */
  headline: string;
  /** The evidence and its counts, including what could not be checked. */
  evidence: string;
  quotes?: VoCQuote[];
}

/** A corpus cluster the plan does not mention at all. */
export interface CrossCheckBlindSpot {
  label: string;
  /** On-topic posts in this cluster. */
  count: number;
  note: string;
}

export interface PlanCrossCheck {
  title: string;
  /** The plan being checked. */
  source: {
    title: string;
    url: string;
    space: string;
    author: string;
    date: string;
    /** Evidence tier of the plan itself — it is not research. */
    docType: string;
  };
  /** Other pages found in the same space that the report's corpus missed. */
  alsoFound?: Array<{ title: string; url: string; note: string }>;
  framing: string[];
  items: CrossCheckItem[];
  blindSpots?: CrossCheckBlindSpot[];
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
  /**
   * Optional: chart a whole taxonomy THEME instead of a single problem. When
   * set, the route reads aggregates.themesByDay / themeCounts under this key
   * and `chartProblem` becomes the fallback. Needed for reports whose subject
   * has no single problem name — Inbox & Chat spans the seven-problem
   * `Communication` theme, and its largest single problem (Media uploads, 94
   * posts across 77 days) draws as a near-empty chart. Omitted by
   * starSitter.ts / lockedRates.ts, which chart one problem each.
   */
  chartTheme?: string;
  headlineStats: HeadlineStat[];
  /** Overall sentiment mix across the core corpus, for the donut. */
  overallSentiment: SentimentBreakdown;
  vocThemes: VoCTheme[];
  research: ResearchSummary[];
  images: ReportImage[];
  /** Optional item-by-item verdict on an external product plan. */
  crossCheck?: PlanCrossCheck;
  implications: {
    supports: string[];
    cautions: string[];
    openQuestions: string[];
  };
  /** ISO date the report content was last synthesized. */
  generatedAt: string;
}

// A VoC report is structurally identical across features (Star Sitter, Locked
// Rates, …). `VocReport` is the feature-neutral alias; `relevanceToTiers` is
// read generically as "relevance to the decision" per report. No shape change.
export type VocReport = StarSitterReport;
