import { format, subDays } from 'date-fns';
import { parseAsArrayOf, parseAsString, parseAsStringEnum } from 'nuqs';

export const themeDetailParsers = {
  problems: parseAsArrayOf(parseAsString).withDefault([]),
  from: parseAsString,
  to: parseAsString,
  q: parseAsString.withDefault(''),
  granularity: parseAsStringEnum(['daily', 'weekly'] as const).withDefault('weekly'),
  tag: parseAsStringEnum(['all', 'llm', 'keyword'] as const).withDefault('all'),
};

export const triageParsers = {
  themes: parseAsArrayOf(parseAsString).withDefault([]),
  problems: parseAsArrayOf(parseAsString).withDefault([]),
  q: parseAsString.withDefault(''),
};

export const trendsParsers = {
  range: parseAsStringEnum(['30d', '90d', '1y', 'all'] as const).withDefault('90d'),
  themes: parseAsArrayOf(parseAsString).withDefault([]),
};

export const untaggedParsers = {
  q: parseAsString.withDefault(''),
};

export const researchParsers = {
  themes: parseAsArrayOf(parseAsString).withDefault([]),
  problems: parseAsArrayOf(parseAsString).withDefault([]),
  spaces: parseAsArrayOf(parseAsString).withDefault([]),
  q: parseAsString.withDefault(''),
  tag: parseAsStringEnum(['all', 'llm', 'keyword'] as const).withDefault('all'),
};

/**
 * Turn a date-range preset (7d / 30d / 90d / 1y / All) into concrete from/to
 * filter values. Lives here rather than in FilterBar.tsx so that component
 * file exports only components (react-refresh/only-export-components).
 */
export function presetToRange(days: number | 'all'): { from: string | null; to: string | null } {
  if (days === 'all') return { from: null, to: null };
  const today = new Date();
  return {
    from: format(subDays(today, days), 'yyyy-MM-dd'),
    to: format(today, 'yyyy-MM-dd'),
  };
}
