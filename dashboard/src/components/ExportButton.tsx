import Papa from 'papaparse';
import type { Post } from '../types';
import { formatCount } from '../lib/format';

export function ExportButton({
  posts,
  filenamePrefix = 'rover-posts',
}: {
  posts: Post[];
  filenamePrefix?: string;
}) {
  const handleClick = () => {
    const rows = posts.map((p) => ({
      date: p.date,
      title: p.title,
      url: p.url,
      author: p.author,
      themes: p.themes.join(', '),
      problems: p.problems.join(', '),
      preview: p.preview,
      subreddit: p.subreddit,
    }));
    const csv = Papa.unparse(rows);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const ts = new Date().toISOString().slice(0, 10);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filenamePrefix}-${ts}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={posts.length === 0}
      className="rounded-md bg-primary-500 px-4 py-2 text-white text-body font-semibold hover:bg-primary-600 disabled:bg-neutral-300 disabled:cursor-not-allowed"
    >
      Export filtered posts (CSV) · {formatCount(posts.length)}
    </button>
  );
}
