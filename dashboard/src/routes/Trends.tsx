import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useQueryStates } from 'nuqs';
import { useData } from '../context/DataContext';
import { Sparkline } from '../components/Sparkline';
import { themeColor } from '../components/ThemeCard';
import { trendsParsers } from '../lib/filters';
import { findLatestDate, weeklyBuckets } from '../lib/aggregations';
import { formatCount, formatDate, formatPct } from '../lib/format';
import { buildThemeToSlug } from '../lib/slug';
import { format, subDays } from 'date-fns';

const RANGE_TO_DAYS: Record<string, number | null> = {
  '30d': 30,
  '90d': 90,
  '1y': 365,
  all: null,
};

export default function Trends() {
  const { aggregates, taxonomy } = useData();
  const [state, setState] = useQueryStates(trendsParsers);
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const themeToSlug = useMemo(() => buildThemeToSlug(taxonomy), [taxonomy]);

  const days = RANGE_TO_DAYS[state.range];
  const end = useMemo(() => findLatestDate(aggregates.themesByDay) ?? new Date(), [aggregates]);
  const start = useMemo(() => {
    if (!days) return null;
    return subDays(end, days);
  }, [end, days]);

  // Build a single dataset keyed by date with each theme as a column
  const data = useMemo(() => {
    const dateSet = new Set<string>();
    for (const theme of taxonomy.themes) {
      const map = aggregates.themesByDay[theme] ?? {};
      for (const d of Object.keys(map)) dateSet.add(d);
    }
    const dates = Array.from(dateSet).sort();
    const filteredDates = dates.filter((d) => {
      if (!start) return true;
      return d >= format(start, 'yyyy-MM-dd');
    });
    return filteredDates.map((date) => {
      const row: Record<string, string | number> = { date };
      for (const theme of taxonomy.themes) {
        row[theme] = aggregates.themesByDay[theme]?.[date] ?? 0;
      }
      return row;
    });
  }, [aggregates, taxonomy, start]);

  const velocityRows = useMemo(() => {
    return taxonomy.themes
      .map((theme) => {
        const buckets = weeklyBuckets(aggregates.themesByDay, theme, 4, end);
        const w = buckets.map((b) => b.count);
        const prev = w[2] ?? 0;
        const curr = w[3] ?? 0;
        const pct = prev === 0 ? (curr === 0 ? 0 : 100) : ((curr - prev) / prev) * 100;
        const direction: 'up' | 'down' | 'flat' =
          Math.abs(pct) <= 5 ? 'flat' : pct > 0 ? 'up' : 'down';
        return { theme, weeks: w, pct, direction, spark: buckets.map((b) => ({ date: b.weekStart, count: b.count })) };
      })
      .sort((a, b) => (b.weeks[3] ?? 0) - (a.weeks[3] ?? 0));
  }, [aggregates, taxonomy, end]);

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-h1 text-neutral-900">Trends</h1>
          <p className="text-body text-neutral-500">Volume over time, by theme</p>
        </div>
        <div className="flex items-center gap-2">
          {(['30d', '90d', '1y', 'all'] as const).map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setState({ range: r })}
              className={`rounded-full px-3 py-1 text-caption ${
                state.range === r
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              }`}
            >
              {r === 'all' ? 'All time' : r}
            </button>
          ))}
        </div>
      </div>

      <section className="rounded-xl bg-white p-4 shadow-card">
        <div className="h-[400px]">
          <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#e2e8f0" />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => formatDate(String(v))}
                tick={{ fontSize: 12, fill: '#475569' }}
                minTickGap={32}
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
              <Legend
                onClick={(o) => {
                  const k = String(o.value);
                  setHidden((prev) => {
                    const next = new Set(prev);
                    if (next.has(k)) next.delete(k);
                    else next.add(k);
                    return next;
                  });
                }}
                wrapperStyle={{ fontSize: 12 }}
              />
              {taxonomy.themes.map((theme) => (
                <Line
                  key={theme}
                  type="monotone"
                  dataKey={theme}
                  stroke={themeColor(theme)}
                  strokeWidth={hidden.has(theme) ? 0 : 2}
                  dot={false}
                  isAnimationActive={false}
                  hide={hidden.has(theme)}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="rounded-xl bg-white p-4 shadow-card">
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-h2 text-neutral-900">Weekly velocity</h2>
          <span className="text-caption text-neutral-500">↑ Up · → Flat · ↓ Down</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-body">
            <thead>
              <tr className="text-caption uppercase tracking-wide text-neutral-500">
                <th className="px-2 py-2 text-left">Theme</th>
                <th className="px-2 py-2 text-right">W-3</th>
                <th className="px-2 py-2 text-right">W-2</th>
                <th className="px-2 py-2 text-right">W-1</th>
                <th className="px-2 py-2 text-right">This week</th>
                <th className="px-2 py-2 text-right">WoW</th>
                <th className="px-2 py-2 text-right w-[100px]">Trend</th>
              </tr>
            </thead>
            <tbody>
              {velocityRows.map((row) => {
                const arrow =
                  row.direction === 'up' ? '↑' : row.direction === 'down' ? '↓' : '→';
                const dColor =
                  row.direction === 'up'
                    ? 'text-success-700'
                    : row.direction === 'down'
                    ? 'text-danger-600'
                    : 'text-neutral-500';
                return (
                  <tr key={row.theme} className="border-t border-neutral-100 hover:bg-neutral-50">
                    <td className="px-2 py-2">
                      <Link
                        to={`/theme/${themeToSlug[row.theme]}`}
                        className="font-semibold hover:text-primary-600"
                        style={{ color: themeColor(row.theme) }}
                      >
                        {row.theme}
                      </Link>
                    </td>
                    {row.weeks.map((c, i) => (
                      <td key={i} className="px-2 py-2 text-right font-mono text-neutral-700">
                        {formatCount(c)}
                      </td>
                    ))}
                    <td className={`px-2 py-2 text-right font-semibold ${dColor}`}>
                      {arrow} {formatPct(row.pct)}
                    </td>
                    <td className="px-2 py-2">
                      <Sparkline data={row.spark} color={themeColor(row.theme)} height={32} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
