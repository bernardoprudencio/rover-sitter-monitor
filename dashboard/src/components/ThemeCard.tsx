import { Link } from 'react-router-dom';
import clsx from 'clsx';
import { Sparkline } from './Sparkline';
import { formatCount, formatPct } from '../lib/format';
import type { WoWDelta } from '../lib/aggregations';

export const THEME_COLORS: Record<string, string> = {
  Availability: '#ff6b00',
  Business: '#2563eb',
  Clients: '#7c3aed',
  Communication: '#0891b2',
  Diversion: '#ca8a04',
  Experience: '#059669',
  Payments: '#db2777',
  'Preferences and rates': '#9333ea',
  'Recurring billings': '#0d9488',
  Requests: '#4f46e5',
  'Rover Cards': '#ea580c',
  'Rover fees': '#65a30d',
  Taxes: '#0369a1',
  Untagged: '#94a3b8',
};

export function themeColor(theme: string): string {
  return THEME_COLORS[theme] ?? '#64748b';
}

export function ThemeCard({
  theme,
  slug,
  total,
  spark,
  delta,
  topProblems,
}: {
  theme: string;
  slug: string;
  total: number;
  spark: Array<{ date: string; count: number }>;
  delta: WoWDelta;
  topProblems: Array<{ problem: string; count: number }>;
}) {
  const color = themeColor(theme);
  const arrow = delta.direction === 'up' ? '↑' : delta.direction === 'down' ? '↓' : '→';
  const deltaColor =
    delta.direction === 'up'
      ? 'text-success-700'
      : delta.direction === 'down'
      ? 'text-danger-600'
      : 'text-neutral-500';
  return (
    <Link
      to={`/theme/${slug}`}
      className={clsx(
        'group block rounded-xl bg-white p-4 shadow-card transition',
        'hover:shadow-card-hover hover:outline hover:outline-2 hover:outline-primary-200 hover:-translate-y-px',
      )}
    >
      <div className="flex items-baseline justify-between">
        <h3 className="text-h3 text-neutral-900" style={{ color }}>
          {theme}
        </h3>
        <span className={clsx('text-caption font-semibold', deltaColor)}>
          {arrow} {formatPct(delta.pct)}
        </span>
      </div>
      <div className="mt-1 text-h1 text-neutral-900">{formatCount(total)}</div>
      <div className="mt-2">
        <Sparkline data={spark} color={color} height={48} />
      </div>
      <ul className="mt-3 space-y-1">
        {topProblems.length === 0 && (
          <li className="text-caption text-neutral-400">No sub-problems yet.</li>
        )}
        {topProblems.map((p) => (
          <li key={p.problem} className="flex justify-between text-caption text-neutral-600">
            <span className="truncate">• {p.problem}</span>
            <span className="ml-2 font-mono text-neutral-500">{formatCount(p.count)}</span>
          </li>
        ))}
      </ul>
    </Link>
  );
}
