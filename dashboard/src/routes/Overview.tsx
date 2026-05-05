import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { ThemeCard } from '../components/ThemeCard';
import { lastNDays, topProblemsForTheme, weekOverWeekDelta } from '../lib/aggregations';
import { buildThemeToSlug } from '../lib/slug';
import { formatCount } from '../lib/format';

export default function Overview() {
  const { aggregates, taxonomy } = useData();
  const themeToSlug = useMemo(() => buildThemeToSlug(taxonomy), [taxonomy]);

  const cards = useMemo(() => {
    return taxonomy.themes.map((theme) => {
      const total = aggregates.themeCounts[theme] ?? 0;
      const spark = lastNDays(aggregates.themesByDay, theme, 84); // 12 weeks
      const delta = weekOverWeekDelta(aggregates.themesByDay, theme);
      const topProblems = topProblemsForTheme(
        aggregates.themeCounts,
        aggregates.problemCounts,
        taxonomy,
        theme,
        3,
      );
      return {
        theme,
        slug: themeToSlug[theme],
        total,
        spark,
        delta,
        topProblems,
      };
    });
  }, [aggregates, taxonomy, themeToSlug]);

  const untaggedPct =
    aggregates.totalPosts > 0
      ? Math.round((aggregates.untaggedCount / aggregates.totalPosts) * 100)
      : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-h1 text-neutral-900">Theme overview</h1>
        <p className="text-body text-neutral-500">
          13 themes from r/RoverPetSitting · last 90 days
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white p-4 shadow-card">
          <div className="text-caption uppercase tracking-wide text-neutral-500">
            Total tagged posts
          </div>
          <div className="mt-1 text-h1 text-neutral-900">
            {formatCount(aggregates.totalTaggedPosts)}
          </div>
        </div>
        <div className="rounded-xl bg-white p-4 shadow-card">
          <div className="text-caption uppercase tracking-wide text-neutral-500">All posts</div>
          <div className="mt-1 text-h1 text-neutral-900">{formatCount(aggregates.totalPosts)}</div>
        </div>
        <div className="rounded-xl bg-white p-4 shadow-card">
          <div className="text-caption uppercase tracking-wide text-neutral-500">Untagged</div>
          <div className="mt-1 text-h1 text-neutral-900">
            {formatCount(aggregates.untaggedCount)}{' '}
            <span className="text-body text-neutral-500">({untaggedPct}%)</span>
          </div>
        </div>
        <div
          className="rounded-xl bg-primary-50 p-4 shadow-card text-primary-800"
          title="Posts can match multiple themes, so theme totals can sum to more than the total post count."
        >
          <div className="text-caption uppercase tracking-wide text-primary-700">Heads up ⓘ</div>
          <div className="mt-1 text-body">
            Posts can match multiple themes, so theme totals can sum to more than the total post
            count.
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {cards.map((c) => (
          <ThemeCard
            key={c.theme}
            theme={c.theme}
            slug={c.slug}
            total={c.total}
            spark={c.spark}
            delta={c.delta}
            topProblems={c.topProblems}
          />
        ))}
        <Link
          to="/untagged"
          className="block rounded-xl border-2 border-dashed border-neutral-300 bg-white p-4 text-center text-neutral-500 hover:border-primary-300 hover:text-primary-700"
        >
          <div className="text-h3">Untagged</div>
          <div className="mt-1 text-h1 text-neutral-700">{formatCount(aggregates.untaggedCount)}</div>
          <div className="mt-1 text-caption">posts unmatched</div>
          <div className="mt-2 text-caption">Help us improve coverage →</div>
        </Link>
      </div>
    </div>
  );
}
