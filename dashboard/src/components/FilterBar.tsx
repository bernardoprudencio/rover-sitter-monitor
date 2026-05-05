import clsx from 'clsx';
import { format, subDays } from 'date-fns';

interface PresetOption {
  label: string;
  days: number | 'all';
}

const PRESETS: PresetOption[] = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 },
  { label: '1y', days: 365 },
  { label: 'All', days: 'all' },
];

export function FilterBar({
  problemOptions,
  selectedProblems,
  onTogglProblem,
  onClearProblems,
  from,
  to,
  onFromChange,
  onToChange,
  onPresetClick,
  rightSlot,
}: {
  problemOptions: string[];
  selectedProblems: string[];
  onTogglProblem: (p: string) => void;
  onClearProblems: () => void;
  from: string | null;
  to: string | null;
  onFromChange: (v: string | null) => void;
  onToChange: (v: string | null) => void;
  onPresetClick: (days: number | 'all') => void;
  rightSlot?: React.ReactNode;
}) {
  return (
    <div className="space-y-3 rounded-xl bg-white p-4 shadow-card">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-caption font-semibold uppercase tracking-wide text-neutral-500">
          Sub-problem
        </span>
        {problemOptions.length === 0 && (
          <span className="text-caption text-neutral-400">No sub-problems available</span>
        )}
        {problemOptions.map((p) => {
          const active = selectedProblems.includes(p);
          return (
            <button
              key={p}
              type="button"
              aria-pressed={active}
              onClick={() => onTogglProblem(p)}
              className={clsx(
                'inline-flex items-center gap-1 rounded-full px-3 py-1 text-caption transition',
                active
                  ? 'bg-primary-500 text-white hover:bg-primary-600'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200',
              )}
            >
              <span>{p}</span>
              {active && <span aria-hidden>×</span>}
            </button>
          );
        })}
        {selectedProblems.length > 0 && (
          <button
            type="button"
            onClick={onClearProblems}
            className="ml-1 text-caption text-primary-700 underline-offset-2 hover:underline"
          >
            Clear
          </button>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-caption font-semibold uppercase tracking-wide text-neutral-500">
          Date range
        </span>
        {PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => onPresetClick(p.days)}
            className="rounded-full bg-neutral-100 px-3 py-1 text-caption text-neutral-700 hover:bg-primary-50 hover:text-primary-700"
          >
            {p.label}
          </button>
        ))}
        <input
          type="date"
          value={from ?? ''}
          onChange={(e) => onFromChange(e.target.value || null)}
          className="rounded-md border border-neutral-300 px-2 py-1 text-caption text-neutral-700"
        />
        <span className="text-neutral-400">→</span>
        <input
          type="date"
          value={to ?? ''}
          onChange={(e) => onToChange(e.target.value || null)}
          className="rounded-md border border-neutral-300 px-2 py-1 text-caption text-neutral-700"
        />
        <div className="ml-auto">{rightSlot}</div>
      </div>
    </div>
  );
}

export function presetToRange(days: number | 'all'): { from: string | null; to: string | null } {
  if (days === 'all') return { from: null, to: null };
  const today = new Date();
  return {
    from: format(subDays(today, days), 'yyyy-MM-dd'),
    to: format(today, 'yyyy-MM-dd'),
  };
}
