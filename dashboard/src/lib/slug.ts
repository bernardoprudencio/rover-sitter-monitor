import type { Taxonomy } from '../types';

export function slugify(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function buildSlugToTheme(taxonomy: Taxonomy): Record<string, string> {
  const map: Record<string, string> = {};
  for (const t of taxonomy.themes) map[slugify(t)] = t;
  return map;
}

export function buildThemeToSlug(taxonomy: Taxonomy): Record<string, string> {
  const map: Record<string, string> = {};
  for (const t of taxonomy.themes) map[t] = slugify(t);
  return map;
}
