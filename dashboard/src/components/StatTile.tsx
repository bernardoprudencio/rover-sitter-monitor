import clsx from 'clsx';
import type { ReactNode } from 'react';

export function StatTile({
  label,
  value,
  delta,
  direction,
  hint,
}: {
  label: string;
  value: ReactNode;
  delta?: string;
  direction?: 'up' | 'down' | 'flat';
  hint?: string;
}) {
  const arrow = direction === 'up' ? '↑' : direction === 'down' ? '↓' : '→';
  const color =
    direction === 'up'
      ? 'text-success-700'
      : direction === 'down'
      ? 'text-danger-600'
      : 'text-neutral-500';
  return (
    <div className="rounded-xl bg-white p-4 shadow-card">
      <div className="text-caption uppercase tracking-wide text-neutral-500">{label}</div>
      <div className="mt-1 text-h1 text-neutral-900">{value}</div>
      {delta && (
        <div className={clsx('mt-1 text-body font-semibold', color)}>
          {arrow} {delta}
        </div>
      )}
      {hint && <div className="mt-1 text-caption text-neutral-400">{hint}</div>}
    </div>
  );
}
