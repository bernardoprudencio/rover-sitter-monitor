import type { ResearchDoc } from '../types';
import { formatDate } from '../lib/format';

export function ResearchRow({
  doc,
  onProblemClick,
}: {
  doc: ResearchDoc;
  onProblemClick?: (problem: string) => void;
}) {
  const dateLabel = doc.date || (doc.updated ? doc.updated.slice(0, 10) : '');
  return (
    <article className="rounded-lg border border-neutral-100 bg-white p-3 hover:shadow-card transition">
      <a
        href={doc.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-body font-semibold text-neutral-900 hover:text-primary-600"
      >
        {doc.title}
      </a>
      <div className="mt-1 flex flex-wrap items-center gap-2 text-caption text-neutral-500">
        {dateLabel && <span>{formatDate(dateLabel)}</span>}
        {dateLabel && <span>·</span>}
        <span className="rounded-full bg-primary-50 px-2 py-0.5 font-mono text-caption text-primary-700">
          {doc.space}
        </span>
        {doc.author && <span>· {doc.author}</span>}
        {doc.problems
          .filter((p) => p !== 'Untagged')
          .map((p) => (
            <button
              key={p}
              type="button"
              onClick={(e) => {
                e.preventDefault();
                onProblemClick?.(p);
              }}
              className="rounded-full bg-neutral-100 px-2 py-0.5 text-caption text-neutral-700 hover:bg-primary-50 hover:text-primary-700"
            >
              {p}
            </button>
          ))}
      </div>
      {doc.excerpt && (
        <p className="mt-2 line-clamp-2 text-body text-neutral-600">{doc.excerpt}</p>
      )}
    </article>
  );
}
