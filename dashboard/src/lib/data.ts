import type { Aggregates, Meta, Post, Taxonomy } from '../types';

const DATA_BASE = `${import.meta.env.BASE_URL}data/`;

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return (await res.json()) as T;
}

export async function fetchMeta(): Promise<Meta> {
  return fetchJson<Meta>(`${DATA_BASE}meta.json?t=${Date.now()}`);
}

export async function fetchTaxonomy(): Promise<Taxonomy> {
  return fetchJson<Taxonomy>(`${DATA_BASE}taxonomy.json`);
}

export async function fetchAggregates(meta: Meta): Promise<Aggregates> {
  return fetchJson<Aggregates>(`${DATA_BASE}${meta.aggregates_file}`);
}

const postsCache = new Map<string, Promise<Post[]>>();

export function loadPosts(meta: Meta): Promise<Post[]> {
  const key = meta.posts_file;
  const existing = postsCache.get(key);
  if (existing) return existing;
  const p = fetchJson<Post[]>(`${DATA_BASE}${meta.posts_file}`);
  postsCache.set(key, p);
  return p;
}
