import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Aggregates, Meta, ResearchAggregates, Taxonomy } from '../types';
import {
  fetchAggregates,
  fetchMeta,
  fetchResearchAggregates,
  fetchTaxonomy,
} from '../lib/data';
import { Skeleton } from '../components/Skeleton';

interface DataContextValue {
  meta: Meta;
  taxonomy: Taxonomy;
  aggregates: Aggregates;
  researchAggregates: ResearchAggregates | null;
}

const DataContext = createContext<DataContextValue | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const [value, setValue] = useState<DataContextValue | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const meta = await fetchMeta();
        const [taxonomy, aggregates, researchAggregates] = await Promise.all([
          fetchTaxonomy(),
          fetchAggregates(meta),
          fetchResearchAggregates(meta),
        ]);
        if (!cancelled) setValue({ meta, taxonomy, aggregates, researchAggregates });
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center p-8">
        <div className="rounded-xl bg-white p-6 shadow-card max-w-md text-center">
          <h2 className="text-h2 mb-2 text-danger-700">Couldn't load data.</h2>
          <p className="text-body text-neutral-500 mb-4 break-words">{error}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-md bg-primary-500 px-4 py-2 text-white text-body font-semibold hover:bg-primary-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!value) return <Skeleton fullPage />;

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData(): DataContextValue {
  const v = useContext(DataContext);
  if (!v) throw new Error('useData must be used within DataProvider');
  return v;
}
