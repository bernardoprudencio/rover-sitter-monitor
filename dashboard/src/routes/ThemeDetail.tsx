import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useData } from '../context/DataContext';
import { usePosts } from '../hooks/usePosts';
import { useThemeFilters } from '../hooks/useThemeFilters';
import { buildSlugToTheme } from '../lib/slug';
import {
  filterPosts,
  lastNDays,
  themeShare,
  topProblemsForTheme,
  weekOverWeekDelta,
  weeklyBuckets,
} from '../lib/aggregations';
import { formatCount, formatDate, formatPct } from '../lib/format';
import { themeColor } from '../components/ThemeCard';
import { StatTile } from '../components/StatTile';
import { FilterBar, presetToRange } from '../components/FilterBar';
import { PostList } from '../components/PostList';
import { ExportButton } from '../components/ExportButton';
import { Skeleton } from '../components/Skeleton';

export default function ThemeDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { aggregates, taxonomy } = useData();
  const { posts, loading } = usePosts();
  const [filters, setFilters] = useThemeFilters();

  const slugToTheme = useMemo(() => buildSlugToTheme(taxonomy), [taxonomy]);
  const theme = slug ? slugToTheme[slug] : undefined;

  if (!theme) {
    return (
      <div className="rounded-xl bg-white p-10 text-center">
        <h1 className="text-h1 text-neutral-900">Theme not found</h1>
        <p className="mt-2 text-body text-neutral-500">
          The slug <code>{slug}</code> doesn't match any theme.
        </p>
        <Link to="/" className="mt-4 inline-block text-primary-700 hover:underline">
          ← Back to overview
        </Link>
      </div>
    );
  }

  const total = aggregates.themeCounts[theme] ?? 0;
  const last30 = lastNDays(aggregates.themesByDay, theme, 30).reduce(
    (s, d) => s + d.count,
    0,
  );
  const wow = weekOverWeekDelta(aggregates.themesByDay, theme);
  const share = themeShare(theme, aggregates);
  const subProblems = topProblemsForTheme(
    aggregates.themeCounts,
    aggregates.problemCounts,
    taxonomy,
    theme,
    20,
  );
  const allProblemNames = subProblems.map((p) => p.problem);

  const seriesDaily = useMemo(
    () => lastNDays(aggregates.themesByDay, theme, 90),
    [aggregates, theme],
  );
  const seriesWeekly = useMemo(
    () => weeklyBuckets(aggregates.themesByDay, theme, 13).map((b) => ({
      date: b.weekStart,
      count: b.count,
    })),
    [aggregates, theme],
  );
  const series = filters.granularity === 'weekly' ? seriesWeekly : seriesDaily;

  const filtered = useMemo(() => {
    if (loading) return [];
    return filterPosts(posts, {
      themes: [theme],
      problems: filters.problems.length ? filters.problems : undefined,
      from: filters.from ?? undefined,
      to: filters.to ?? undefined,
      q: filters.q,
    });
  }, [posts, theme, filters, loading]);

  const color = themeColor(theme);

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <Link to="/" className="text-caption text-primary-700 hover:underline">
            ‹ Overview
          </Link>
          <span className="text-caption text-neutral-400"> / </span>
          <span className="text-caption text-neutral-700">{theme}</span>
          <h1 className="mt-1 text-h1" style={{ color }}>
            {theme}
          </h1>
          <p className="text-body text-neutral-500">
            {formatCount(total)} posts
            {posts.length > 0 && filtered.length > 0 && ` · ${formatCount(filtered.length)} match filters`}
          </p>
        </div>
        <ExportButton posts={filtered} filenamePrefix={`rover-${slug}`} />
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Total" value={formatCount(total)} />
        <StatTile label="Last 30 days" value={formatCount(last30)} />
        <StatTile
          label="Week over week"
          value={formatPct(wow.pct)}
          direction={wow.direction}
          hint={`${wow.previous} → ${wow.current}`}
        />
        <StatTile label="Share of tagged" value={`${share.toFixed(1)}%`} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <section className="rounded-xl bg-white p-4 shadow-card lg:col-span-5">
          <h2 className="text-h2 text-neutral-900">Sub-problems</h2>
          {subProblems.filter((p) => p.count > 0).length === 0 ? (
            <p className="mt-3 text-body text-neutral-500">
              No matching sub-problems for this theme.
            </p>
          ) : (
            <div className="mt-3 h-[320px]">
              <ResponsiveContainer>
                <BarChart
                  data={subProblems.filter((p) => p.count > 0)}
                  layout="vertical"
                  margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
                >
                  <CartesianGrid stroke="#e2e8f0" horizontal={false} />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: '#475569' }} />
                  <YAxis
                    type="category"
                    dataKey="problem"
                    tick={{ fontSize: 12, fill: '#475569' }}
                    width={140}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e2e8f0',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="count" fill={color} radius={[0, 4, 4, 0]} isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>

        <section className="rounded-xl bg-white p-4 shadow-card lg:col-span-7">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-h2 text-neutral-900">Volume over time</h2>
            <div className="flex items-center gap-1 text-caption">
              <button
                type="button"
                onClick={() => setFilters({ granularity: 'daily' })}
                className={`rounded-full px-3 py-1 ${
                  filters.granularity === 'daily'
                    ? 'bg-primary-500 text-white'
                    : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                }`}
              >
                Daily
              </button>
              <button
                type="button"
                onClick={() => setFilters({ granularity: 'weekly' })}
                className={`rounded-full px-3 py-1 ${
                  filters.granularity === 'weekly'
                    ? 'bg-primary-500 text-white'
                    : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                }`}
              >
                Weekly
              </button>
            </div>
          </div>
          <div className="h-[320px]">
            <ResponsiveContainer>
              <AreaChart data={series} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <defs>
                  <linearGradient id={`grad-${slug}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={color} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={color} stopOpacity={0} />
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
                  stroke={color}
                  strokeWidth={2}
                  fill={`url(#grad-${slug})`}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <FilterBar
        problemOptions={allProblemNames}
        selectedProblems={filters.problems}
        onTogglProblem={(p) => {
          const has = filters.problems.includes(p);
          const next = has ? filters.problems.filter((x) => x !== p) : [...filters.problems, p];
          setFilters({ problems: next });
        }}
        onClearProblems={() => setFilters({ problems: [] })}
        from={filters.from}
        to={filters.to}
        onFromChange={(v) => setFilters({ from: v })}
        onToChange={(v) => setFilters({ to: v })}
        onPresetClick={(d) => {
          const r = presetToRange(d);
          setFilters({ from: r.from, to: r.to });
        }}
        rightSlot={
          <span className="text-caption text-neutral-500">
            {formatCount(filtered.length)} posts
          </span>
        }
      />

      {loading ? (
        <Skeleton rows={6} />
      ) : (
        <PostList
          posts={filtered}
          onProblemClick={(p) => {
            if (!filters.problems.includes(p)) {
              setFilters({ problems: [...filters.problems, p] });
            }
          }}
          onReset={() =>
            setFilters({ problems: [], from: null, to: null, q: '' })
          }
        />
      )}
    </div>
  );
}
