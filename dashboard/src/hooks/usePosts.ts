import { useEffect, useState } from 'react';
import type { Post } from '../types';
import { loadPosts } from '../lib/data';
import { useData } from '../context/DataContext';

export function usePosts(): { posts: Post[]; loading: boolean; error: string | null } {
  const { meta } = useData();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadPosts(meta)
      .then((p) => {
        if (!cancelled) {
          setPosts(p);
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

  return { posts, loading, error };
}
