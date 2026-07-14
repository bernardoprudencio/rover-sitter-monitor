import clsx from 'clsx';

export type TagSource = 'all' | 'llm' | 'keyword';

const OPTIONS: { value: TagSource; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'llm', label: 'LLM' },
  { value: 'keyword', label: 'Keyword' },
];

export function TagSourceToggle({
  value,
  onChange,
  showLabel = true,
}: {
  value: TagSource;
  onChange: (v: TagSource) => void;
  showLabel?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      {showLabel && (
        <span className="text-caption font-semibold uppercase tracking-wide text-neutral-500">
          Tag source
        </span>
      )}
      <div className="flex flex-wrap items-center gap-1">
        {OPTIONS.map((o) => (
          <button
            key={o.value}
            type="button"
            aria-pressed={value === o.value}
            onClick={() => onChange(o.value)}
            className={clsx(
              'rounded-full px-3 py-1 text-caption transition',
              value === o.value
                ? 'bg-primary-500 text-white'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200',
            )}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}
