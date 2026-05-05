import type { ResearchDoc } from '../types';
import { ResearchRow } from './ResearchRow';
import { EmptyState } from './EmptyState';

export function ResearchList({
  docs,
  onProblemClick,
  onReset,
  emptyMessage = 'No research documents match these filters.',
  showResetAction = true,
  maxHeight,
}: {
  docs: ResearchDoc[];
  onProblemClick?: (problem: string) => void;
  onReset?: () => void;
  emptyMessage?: string;
  showResetAction?: boolean;
  maxHeight?: string;
}) {
  if (docs.length === 0) {
    return (
      <EmptyState
        message={emptyMessage}
        action={
          showResetAction && onReset ? (
            <button
              type="button"
              onClick={onReset}
              className="rounded-md bg-primary-500 px-4 py-2 text-white text-body font-semibold hover:bg-primary-600"
            >
              Reset filters
            </button>
          ) : undefined
        }
      />
    );
  }

  return (
    <div
      className="space-y-2 overflow-auto rounded-xl border border-neutral-200 bg-neutral-50 p-2"
      style={maxHeight ? { maxHeight } : undefined}
    >
      {docs.map((d) => (
        <ResearchRow key={d.id} doc={d} onProblemClick={onProblemClick} />
      ))}
    </div>
  );
}
