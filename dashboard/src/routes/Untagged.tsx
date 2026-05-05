import { useMemo } from 'react';
import { useQueryStates } from 'nuqs';
import { useData } from '../context/DataContext';
import { usePosts } from '../hooks/usePosts';
import { PostList } from '../components/PostList';
import { Skeleton } from '../components/Skeleton';
import { untaggedParsers } from '../lib/filters';
import { formatCount } from '../lib/format';

export default function Untagged() {
  const { aggregates } = useData();
  const { posts, loading } = usePosts();
  const [state, setState] = useQueryStates(untaggedParsers);

  const untagged = useMemo(
    () =>
      posts
        .filter((p) => p.themes.length === 0 || (p.themes.length === 1 && p.themes[0] === 'Untagged'))
        .filter((p) => {
          if (!state.q) return true;
          const hay = `${p.title} ${p.preview}`.toLowerCase();
          return hay.includes(state.q.toLowerCase());
        })
        .sort((a, b) => b.date.localeCompare(a.date)),
    [posts, state.q],
  );

  const keywords = aggregates.untaggedKeywordFreq.slice(0, 50);

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-h1 text-neutral-900">Untagged</h1>
          <p className="text-body text-neutral-500">
            Posts that didn't match any taxonomy keyword · {formatCount(aggregates.untaggedCount)} total
          </p>
        </div>
        <a
          href="https://github.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-body text-primary-700 hover:underline"
        >
          Spot a missing tag? <strong>Suggest it on GitHub</strong> →
        </a>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[18rem_1fr]">
        <aside className="rounded-xl bg-white p-4 shadow-card">
          <h2 className="text-h3 text-neutral-900">Top keywords</h2>
          <p className="mt-1 text-caption text-neutral-500">Click to filter the post list</p>
          {state.q && (
            <button
              type="button"
              onClick={() => setState({ q: '' })}
              className="mt-2 inline-flex items-center gap-1 rounded-full bg-primary-500 px-3 py-1 text-caption text-white"
            >
              {state.q} <span aria-hidden>×</span>
            </button>
          )}
          <ul className="mt-3 max-h-[60vh] space-y-1 overflow-y-auto">
            {keywords.map((kw) => (
              <li key={kw.word}>
                <button
                  type="button"
                  onClick={() => setState({ q: kw.word })}
                  className={`flex w-full items-center justify-between rounded-md px-2 py-1 text-body hover:bg-primary-50 ${
                    state.q === kw.word ? 'bg-primary-100 text-primary-800' : 'text-neutral-700'
                  }`}
                >
                  <span className="truncate">{kw.word}</span>
                  <span className="font-mono text-caption text-neutral-500">{kw.count}</span>
                </button>
              </li>
            ))}
            {keywords.length === 0 && (
              <li className="text-caption text-neutral-400">No keywords yet.</li>
            )}
          </ul>
        </aside>
        <div className="min-w-0">
          {loading ? (
            <Skeleton rows={6} />
          ) : (
            <PostList
              posts={untagged}
              emptyMessage="No untagged posts in this range — taxonomy is doing its job."
              showResetAction={!!state.q}
              onReset={() => setState({ q: '' })}
            />
          )}
        </div>
      </div>
    </div>
  );
}
