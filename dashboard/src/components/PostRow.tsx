import clsx from 'clsx';
import type { Post } from '../types';
import { formatDate } from '../lib/format';

export function PostRow({
  post,
  onProblemClick,
}: {
  post: Post;
  onProblemClick?: (problem: string) => void;
}) {
  const isRemoved =
    post.preview.startsWith('[removed]') || post.preview.startsWith('[deleted]');
  return (
    <article className="rounded-lg border border-neutral-100 bg-white p-3 hover:shadow-card transition">
      <a
        href={post.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-body font-semibold text-neutral-900 hover:text-primary-600"
      >
        {post.title}
      </a>
      <div className="mt-1 flex flex-wrap items-center gap-2 text-caption text-neutral-500">
        <span>{formatDate(post.date)}</span>
        <span>·</span>
        <span>u/{post.author}</span>
        {post.llmTagged && (
          <span
            title="Tagged by Claude (~92% accuracy)"
            className="rounded-full bg-primary-50 px-1.5 py-0.5 font-mono text-[10px] text-primary-700"
          >
            LLM
          </span>
        )}
        {post.problems
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
      <p
        className={clsx(
          'mt-2 line-clamp-2 text-body',
          isRemoved ? 'italic text-neutral-400' : 'text-neutral-600',
        )}
      >
        {post.preview || '—'}
      </p>
    </article>
  );
}
