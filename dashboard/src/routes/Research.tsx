import { useMemo } from 'react';
import { useQueryStates } from 'nuqs';
import clsx from 'clsx';
import { useData } from '../context/DataContext';
import { useResearch } from '../hooks/useResearch';
import { ResearchList } from '../components/ResearchList';
import { TagSourceToggle } from '../components/TagSourceToggle';
import { Skeleton } from '../components/Skeleton';
import { researchParsers } from '../lib/filters';
import { formatCount } from '../lib/format';

export default function Research() {
  const { researchAggregates, taxonomy } = useData();
  const { research, loading } = useResearch();
  const [state, setState] = useQueryStates(researchParsers);

  const allSpaces = useMemo(() => {
    const set = new Set<string>();
    for (const d of research) if (d.space) set.add(d.space);
    return [...set].sort();
  }, [research]);

  const filtered = useMemo(() => {
    const q = state.q.trim().toLowerCase();
    return research.filter((d) => {
      if (state.themes.length && !d.themes.some((t) => state.themes.includes(t))) return false;
      if (state.problems.length && !d.problems.some((p) => state.problems.includes(p))) return false;
      if (state.spaces.length && !state.spaces.includes(d.space)) return false;
      if (state.tag === 'llm' && !d.llmTagged) return false;
      if (state.tag === 'keyword' && d.llmTagged) return false;
      if (q) {
        const hay = `${d.title} ${d.excerpt}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [research, state]);

  const totalDocs = researchAggregates?.totalDocs ?? research.length;
  const untaggedCount = researchAggregates?.untaggedCount ?? 0;

  const toggle = (key: 'themes' | 'problems' | 'spaces', value: string) => {
    const current = state[key];
    const has = current.includes(value);
    setState({ [key]: has ? current.filter((x) => x !== value) : [...current, value] } as any);
  };

  const reset = () =>
    setState({ themes: [], problems: [], spaces: [], q: '', tag: 'all' });

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-h1 text-neutral-900">Research</h1>
          <p className="text-body text-neutral-500">
            Internal Confluence pages tagged against the same taxonomy as Reddit ·{' '}
            {formatCount(totalDocs)} docs · {formatCount(untaggedCount)} untagged
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[18rem_1fr]">
        <aside className="space-y-4">
          <section className="rounded-xl bg-white p-4 shadow-card">
            <div className="flex items-center justify-between">
              <h2 className="text-h3 text-neutral-900">Search</h2>
              {state.q || state.themes.length || state.problems.length || state.spaces.length || state.tag !== 'all' ? (
                <button
                  type="button"
                  onClick={reset}
                  className="text-caption text-primary-700 hover:underline"
                >
                  Reset
                </button>
              ) : null}
            </div>
            <input
              type="search"
              value={state.q}
              onChange={(e) => setState({ q: e.target.value })}
              placeholder="Search title or excerpt"
              className="mt-2 w-full rounded-md border border-neutral-200 px-3 py-2 text-body focus:border-primary-500 focus:outline-none"
            />
          </section>

          <section className="rounded-xl bg-white p-4 shadow-card">
            <h2 className="text-h3 text-neutral-900">Spaces</h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {allSpaces.length === 0 && (
                <span className="text-caption text-neutral-400">No spaces yet.</span>
              )}
              {allSpaces.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggle('spaces', s)}
                  className={clsx(
                    'rounded-full px-3 py-1 text-caption transition',
                    state.spaces.includes(s)
                      ? 'bg-primary-500 text-white'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-primary-50',
                  )}
                >
                  {s}
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-xl bg-white p-4 shadow-card">
            <h2 className="text-h3 text-neutral-900">Themes</h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {taxonomy.themes.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => toggle('themes', t)}
                  className={clsx(
                    'rounded-full px-3 py-1 text-caption transition',
                    state.themes.includes(t)
                      ? 'bg-primary-500 text-white'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-primary-50',
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-xl bg-white p-4 shadow-card">
            <h2 className="text-h3 text-neutral-900">Tag source</h2>
            <div className="mt-2">
              <TagSourceToggle
                value={state.tag}
                onChange={(t) => setState({ tag: t })}
                showLabel={false}
              />
            </div>
          </section>
        </aside>

        <div className="min-w-0">
          <div className="mb-2 flex items-center justify-between text-caption text-neutral-500">
            <span>{formatCount(filtered.length)} matching</span>
            {state.problems.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {state.problems.map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => toggle('problems', p)}
                    className="rounded-full bg-primary-500 px-2 py-0.5 text-caption text-white"
                  >
                    {p} ×
                  </button>
                ))}
              </div>
            )}
          </div>
          {loading ? (
            <Skeleton rows={6} />
          ) : (
            <ResearchList
              docs={filtered}
              onProblemClick={(p) => toggle('problems', p)}
              onReset={reset}
              emptyMessage={
                research.length === 0
                  ? 'No research documents have been ingested yet. Run `make confluence-dump` once Confluence secrets are configured.'
                  : 'No research documents match these filters.'
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}
