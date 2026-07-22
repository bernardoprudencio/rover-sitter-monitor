import { useMemo } from 'react';
import {
  Area,
  AreaChart,
  Cell,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useData } from '../context/DataContext';
import { lastNDays, weeklyBuckets } from '../lib/aggregations';
import { formatCount, formatDate } from '../lib/format';
import { StatTile } from '../components/StatTile';
import { starSitterReport } from '../content/starSitter';
import type { ResearchSummary, SentimentBreakdown, VoCTheme } from '../types';

const SENTIMENT_META: Array<{
  key: keyof SentimentBreakdown;
  label: string;
  color: string;
}> = [
  { key: 'negative', label: 'Negative', color: '#db2777' },
  { key: 'mixed', label: 'Mixed', color: '#ca8a04' },
  { key: 'neutral', label: 'Neutral', color: '#94a3b8' },
  { key: 'positive', label: 'Positive', color: '#059669' },
];

const PRIMARY = '#2563eb'; // Business theme color — Star Sitter lives here.

function sentimentTotal(s: SentimentBreakdown): number {
  return s.positive + s.negative + s.mixed + s.neutral;
}

function SentimentBar({ sentiment }: { sentiment: SentimentBreakdown }) {
  const total = sentimentTotal(sentiment) || 1;
  return (
    <div className="flex h-2 w-full overflow-hidden rounded-full bg-neutral-100">
      {SENTIMENT_META.map(({ key, color, label }) => {
        const pct = (sentiment[key] / total) * 100;
        if (pct <= 0) return null;
        return (
          <div
            key={key}
            title={`${label}: ${sentiment[key]}`}
            style={{ width: `${pct}%`, backgroundColor: color }}
          />
        );
      })}
    </div>
  );
}

function QuoteCard({
  text,
  url,
  meta,
}: {
  text: string;
  url?: string;
  meta?: string;
}) {
  const body = (
    <blockquote className="rounded-lg border-l-4 border-primary-200 bg-neutral-50 p-3">
      <p className="text-body italic text-neutral-700">“{text}”</p>
      {meta && <cite className="mt-1 block text-caption not-italic text-neutral-400">{meta}</cite>}
    </blockquote>
  );
  if (!url) return body;
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="block transition hover:opacity-80"
    >
      {body}
    </a>
  );
}

function VoCThemeSection({ theme }: { theme: VoCTheme }) {
  return (
    <section className="rounded-xl bg-white p-5 shadow-card">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="text-h2 text-neutral-900">{theme.label}</h3>
        <span className="shrink-0 text-caption font-mono text-neutral-500">
          {formatCount(theme.count)} post{theme.count === 1 ? '' : 's'}
        </span>
      </div>
      <div className="mt-2">
        <SentimentBar sentiment={theme.sentiment} />
      </div>
      <p className="mt-3 text-body text-neutral-600">{theme.summary}</p>
      {theme.quotes.length > 0 && (
        <div className="mt-4 space-y-2">
          {theme.quotes.map((q, i) => (
            <QuoteCard
              key={i}
              text={q.text}
              url={q.url}
              meta={[q.author ? `u/${q.author}` : null, q.date ? formatDate(q.date, 'MMM d, yyyy') : null]
                .filter(Boolean)
                .join(' · ')}
            />
          ))}
        </div>
      )}
      {theme.implication && (
        <p className="mt-4 rounded-lg bg-primary-50 p-3 text-body text-primary-800">
          <span className="font-semibold">Implication: </span>
          {theme.implication}
        </p>
      )}
    </section>
  );
}

function ResearchSection({ study }: { study: ResearchSummary }) {
  return (
    <article className="rounded-xl bg-white p-5 shadow-card">
      <div className="flex items-baseline justify-between gap-3">
        <a
          href={study.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-h3 text-neutral-900 hover:text-primary-600"
        >
          {study.title}
        </a>
        <span className="shrink-0 rounded-full bg-primary-50 px-2 py-0.5 font-mono text-caption text-primary-700">
          {study.space}
        </span>
      </div>
      {study.method && (
        <p className="mt-1 text-caption text-neutral-400">{study.method}</p>
      )}
      <p className="mt-2 text-body font-medium text-neutral-800">{study.takeaway}</p>
      {study.relevanceToTiers && (
        <p className="mt-2 text-body text-neutral-600">
          <span className="font-semibold text-neutral-700">For tiers: </span>
          {study.relevanceToTiers}
        </p>
      )}
      {study.quotes.length > 0 && (
        <div className="mt-3 space-y-2">
          {study.quotes.map((q, i) => (
            <QuoteCard key={i} text={q.text} meta={q.author} />
          ))}
        </div>
      )}
      {study.figures && study.figures.length > 0 && (
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {study.figures.map((f, i) => (
            <figure key={i} className="overflow-hidden rounded-lg border border-neutral-100">
              <img src={f.src} alt={f.caption ?? study.title} className="w-full" loading="lazy" />
              {f.caption && (
                <figcaption className="p-2 text-caption text-neutral-500">{f.caption}</figcaption>
              )}
            </figure>
          ))}
        </div>
      )}
    </article>
  );
}

export default function StarSitter() {
  const { aggregates } = useData();
  const report = starSitterReport;
  const problem = report.chartProblem;

  const total = aggregates.problemCounts[problem] ?? 0;

  const seriesWeekly = useMemo(
    () =>
      weeklyBuckets(aggregates.problemsByDay, problem, 26).map((b) => ({
        date: b.weekStart,
        count: b.count,
      })),
    [aggregates, problem],
  );

  const last90 = useMemo(
    () => lastNDays(aggregates.problemsByDay, problem, 90).reduce((s, d) => s + d.count, 0),
    [aggregates, problem],
  );

  const sentimentData = SENTIMENT_META.map(({ key, label, color }) => ({
    name: label,
    value: report.overallSentiment[key],
    color,
  })).filter((d) => d.value > 0);

  return (
    <div className="mx-auto max-w-5xl space-y-8 pb-12">
      {/* Hero / framing */}
      <header className="rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 p-8 text-white shadow-card">
        <div className="flex items-center gap-2 text-caption uppercase tracking-widest text-primary-100">
          <span aria-hidden>★</span> Voice of the Customer
        </div>
        <h1 className="mt-2 text-3xl font-bold leading-tight">{report.title}</h1>
        <p className="mt-2 max-w-3xl text-lg text-primary-50">{report.subtitle}</p>
        <div className="mt-5 rounded-xl bg-white/10 p-4 backdrop-blur">
          <div className="text-caption uppercase tracking-wide text-primary-100">
            Decision this informs
          </div>
          <p className="mt-1 text-body text-white">{report.decisionQuestion}</p>
        </div>
      </header>

      {report.framing.length > 0 && (
        <section className="space-y-3">
          {report.framing.map((p, i) => (
            <p key={i} className="text-body leading-relaxed text-neutral-700">
              {p}
            </p>
          ))}
          <p className="text-caption text-neutral-400">{report.corpusNote}</p>
        </section>
      )}

      {/* Headline stats */}
      {report.headlineStats.length > 0 && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {report.headlineStats.map((s) => (
            <StatTile key={s.label} label={s.label} value={s.value} hint={s.hint} />
          ))}
        </div>
      )}

      {/* Charts: volume + sentiment */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <section className="rounded-xl bg-white p-4 shadow-card lg:col-span-8">
          <div className="mb-2 flex items-baseline justify-between">
            <h2 className="text-h2 text-neutral-900">Star Sitter mentions over time</h2>
            <span className="text-caption text-neutral-500">
              {formatCount(total)} total · {formatCount(last90)} in last 90 days
            </span>
          </div>
          <div className="h-[280px]">
            <ResponsiveContainer>
              <AreaChart data={seriesWeekly} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <defs>
                  <linearGradient id="grad-star-sitter" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={PRIMARY} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={PRIMARY} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#e2e8f0" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(v) => formatDate(v)}
                  tick={{ fontSize: 12, fill: '#475569' }}
                />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#475569' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e2e8f0',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelFormatter={(v) => formatDate(String(v), 'MMM d, yyyy')}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke={PRIMARY}
                  strokeWidth={2}
                  fill="url(#grad-star-sitter)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-1 text-caption text-neutral-400">
            Weekly volume of Star Sitter–tagged posts, from the live dashboard aggregates.
          </p>
        </section>

        <section className="rounded-xl bg-white p-4 shadow-card lg:col-span-4">
          <h2 className="text-h2 text-neutral-900">Sentiment mix</h2>
          {sentimentData.length === 0 ? (
            <p className="mt-3 text-body text-neutral-500">No sentiment data yet.</p>
          ) : (
            <>
              <div className="h-[200px]">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      isAnimationActive={false}
                    >
                      {sentimentData.map((d) => (
                        <Cell key={d.name} fill={d.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: 8,
                        fontSize: 12,
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <ul className="mt-2 space-y-1">
                {sentimentData.map((d) => (
                  <li key={d.name} className="flex items-center justify-between text-caption">
                    <span className="flex items-center gap-2 text-neutral-600">
                      <span
                        className="inline-block h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: d.color }}
                      />
                      {d.name}
                    </span>
                    <span className="font-mono text-neutral-500">{d.value}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>

      {/* VoC themes */}
      {report.vocThemes.length > 0 && (
        <section className="space-y-4">
          <div>
            <h2 className="text-h1 text-neutral-900">What sitters are saying</h2>
            <p className="text-body text-neutral-500">
              Themes clustered from {formatCount(total)} Reddit posts about Star Sitter.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {report.vocThemes.map((t) => (
              <VoCThemeSection key={t.id} theme={t} />
            ))}
          </div>
        </section>
      )}

      {/* Reddit images */}
      {report.images.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-h1 text-neutral-900">From the community</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {report.images.map((img, i) => (
              <figure
                key={i}
                className="overflow-hidden rounded-xl border border-neutral-100 bg-white shadow-card"
              >
                <a href={img.sourceUrl} target="_blank" rel="noopener noreferrer">
                  <img src={img.src} alt={img.caption} className="w-full" loading="lazy" />
                </a>
                <figcaption className="p-3 text-caption text-neutral-500">{img.caption}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      {/* Prior research */}
      {report.research.length > 0 && (
        <section className="space-y-4">
          <div>
            <h2 className="text-h1 text-neutral-900">What prior research found</h2>
            <p className="text-body text-neutral-500">
              Rover's own studies on Star Sitter, sitter rewards, and provider performance.
            </p>
          </div>
          <div className="space-y-4">
            {report.research.map((s) => (
              <ResearchSection key={s.id} study={s} />
            ))}
          </div>
        </section>
      )}

      {/* Implications for tiered loyalty */}
      <section className="rounded-2xl border border-primary-100 bg-primary-50/50 p-6">
        <h2 className="text-h1 text-primary-900">Implications for a tiered loyalty model</h2>
        <div className="mt-4 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div>
            <h3 className="text-h3 text-success-700">Evidence supports</h3>
            <ul className="mt-2 space-y-2">
              {report.implications.supports.map((s, i) => (
                <li key={i} className="text-body text-neutral-700">
                  <span className="mr-1 text-success-600">✓</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-h3 text-danger-600">Proceed with caution</h3>
            <ul className="mt-2 space-y-2">
              {report.implications.cautions.map((s, i) => (
                <li key={i} className="text-body text-neutral-700">
                  <span className="mr-1 text-danger-500">!</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-h3 text-neutral-700">Open questions</h3>
            <ul className="mt-2 space-y-2">
              {report.implications.openQuestions.map((s, i) => (
                <li key={i} className="text-body text-neutral-700">
                  <span className="mr-1 text-neutral-400">?</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <footer className="text-center text-caption text-neutral-400">
        Synthesized {formatDate(report.generatedAt, 'MMMM d, yyyy')} from r/RoverPetSitting and
        internal Confluence research · Rover Sitter Pulse
      </footer>
    </div>
  );
}
