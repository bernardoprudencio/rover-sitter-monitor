import { addDays, format, parseISO, startOfWeek, subDays } from 'date-fns';
import type { Aggregates, Post, Taxonomy } from '../types';

export interface DayCount {
  date: string;
  count: number;
}

export function lastNDays(
  themesByDay: Record<string, Record<string, number>>,
  theme: string,
  n: number,
  endDate?: Date,
): DayCount[] {
  const themeMap = themesByDay[theme] ?? {};
  const end = endDate ?? findLatestDate(themesByDay) ?? new Date();
  const out: DayCount[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = subDays(end, i);
    const key = format(d, 'yyyy-MM-dd');
    out.push({ date: key, count: themeMap[key] ?? 0 });
  }
  return out;
}

export interface WoWDelta {
  pct: number;
  direction: 'up' | 'down' | 'flat';
  current: number;
  previous: number;
}

export function weekOverWeekDelta(
  themesByDay: Record<string, Record<string, number>>,
  theme: string,
  endDate?: Date,
): WoWDelta {
  const themeMap = themesByDay[theme] ?? {};
  const end = endDate ?? findLatestDate(themesByDay) ?? new Date();
  let current = 0;
  let previous = 0;
  for (let i = 0; i < 7; i++) {
    const d = subDays(end, i);
    current += themeMap[format(d, 'yyyy-MM-dd')] ?? 0;
  }
  for (let i = 7; i < 14; i++) {
    const d = subDays(end, i);
    previous += themeMap[format(d, 'yyyy-MM-dd')] ?? 0;
  }
  if (previous === 0 && current === 0) return { pct: 0, direction: 'flat', current, previous };
  if (previous === 0) return { pct: 100, direction: 'up', current, previous };
  const pct = ((current - previous) / previous) * 100;
  let direction: 'up' | 'down' | 'flat' = 'flat';
  if (Math.abs(pct) > 5) direction = pct > 0 ? 'up' : 'down';
  return { pct, direction, current, previous };
}

export interface WeekBucket {
  weekStart: string;
  count: number;
}

export function weeklyBuckets(
  themesByDay: Record<string, Record<string, number>>,
  theme: string,
  weeks: number,
  endDate?: Date,
): WeekBucket[] {
  const themeMap = themesByDay[theme] ?? {};
  const end = endDate ?? findLatestDate(themesByDay) ?? new Date();
  const buckets: WeekBucket[] = [];
  for (let w = weeks - 1; w >= 0; w--) {
    const weekEnd = subDays(end, w * 7);
    const ws = startOfWeek(weekEnd, { weekStartsOn: 1 });
    let count = 0;
    for (let i = 0; i < 7; i++) {
      const d = addDays(ws, i);
      count += themeMap[format(d, 'yyyy-MM-dd')] ?? 0;
    }
    buckets.push({ weekStart: format(ws, 'yyyy-MM-dd'), count });
  }
  return buckets;
}

export interface PostFilters {
  themes?: string[];
  problems?: string[];
  from?: string | null;
  to?: string | null;
  q?: string;
}

export function filterPosts(posts: Post[], f: PostFilters): Post[] {
  const q = (f.q ?? '').trim().toLowerCase();
  const themes = f.themes && f.themes.length ? new Set(f.themes) : null;
  const problems = f.problems && f.problems.length ? new Set(f.problems) : null;
  const from = f.from ? f.from : null;
  const to = f.to ? f.to : null;
  return posts.filter((p) => {
    if (themes && !p.themes.some((t) => themes.has(t))) return false;
    if (problems && !p.problems.some((pr) => problems.has(pr))) return false;
    if (from && p.date < from) return false;
    if (to && p.date > to) return false;
    if (q) {
      const hay = `${p.title} ${p.preview}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

export function topProblemsForTheme(
  _themeCounts: Record<string, number>,
  problemCounts: Record<string, number>,
  taxonomy: Taxonomy,
  theme: string,
  n = 3,
): Array<{ problem: string; count: number }> {
  const problems = Object.entries(taxonomy.problems)
    .filter(([_, meta]) => meta.theme === theme)
    .map(([name]) => ({ problem: name, count: problemCounts[name] ?? 0 }))
    .sort((a, b) => b.count - a.count);
  return problems.slice(0, n);
}

export function findLatestDate(
  themesByDay: Record<string, Record<string, number>>,
): Date | null {
  let latest: string | null = null;
  for (const map of Object.values(themesByDay)) {
    for (const date of Object.keys(map)) {
      if (!latest || date > latest) latest = date;
    }
  }
  return latest ? parseISO(latest) : null;
}

export function distinctPostsForTheme(
  posts: Post[],
  theme: string,
): Post[] {
  return posts.filter((p) => p.themes.includes(theme));
}

export function themeShare(theme: string, agg: Aggregates): number {
  if (agg.totalTaggedPosts === 0) return 0;
  return ((agg.themeCounts[theme] ?? 0) / agg.totalTaggedPosts) * 100;
}
