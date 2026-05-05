import { parseAsArrayOf, parseAsString, parseAsStringEnum } from 'nuqs';

export const themeDetailParsers = {
  problems: parseAsArrayOf(parseAsString).withDefault([]),
  from: parseAsString,
  to: parseAsString,
  q: parseAsString.withDefault(''),
  granularity: parseAsStringEnum(['daily', 'weekly'] as const).withDefault('weekly'),
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
};
