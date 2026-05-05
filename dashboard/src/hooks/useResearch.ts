import { useEffect, useState } from 'react';
import type { ResearchDoc } from '../types';
import { loadResearch } from '../lib/data';
import { useData } from '../context/DataContext';

export function useResearch(): {
  research: ResearchDoc[];
  loading: boolean;
  error: string | null;
} {
  const { meta } = useData();
  const [research, setResearch] = useState<ResearchDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadResearch(meta)
      .then((r) => {
        if (!cancelled) {
          setResearch(r);
          setLoading(false);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [meta]);

  return { research, loading, error };
}
