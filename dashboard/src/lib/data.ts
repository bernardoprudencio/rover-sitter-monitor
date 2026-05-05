import type {
  Aggregates,
  Meta,
  Post,
  ResearchAggregates,
  ResearchDoc,
  Taxonomy,
} from '../types';

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

export async function fetchResearchAggregates(
  meta: Meta,
): Promise<ResearchAggregates | null> {
  if (!meta.research_aggregates_file) return null;
  return fetchJson<ResearchAggregates>(`${DATA_BASE}${meta.research_aggregates_file}`);
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

const researchCache = new Map<string, Promise<ResearchDoc[]>>();

export function loadResearch(meta: Meta): Promise<ResearchDoc[]> {
  if (!meta.research_file) return Promise.resolve([]);
  const key = meta.research_file;
  const existing = researchCache.get(key);
  if (existing) return existing;
  const p = fetchJson<ResearchDoc[]>(`${DATA_BASE}${meta.research_file}`);
  researchCache.set(key, p);
  return p;
}
