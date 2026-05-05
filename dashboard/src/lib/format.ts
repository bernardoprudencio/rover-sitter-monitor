import { format, formatDistanceToNowStrict, parseISO } from 'date-fns';

export function formatDate(iso: string, fmt = 'MMM d'): string {
  try {
    return format(parseISO(iso), fmt);
  } catch {
    return iso;
  }
}

export function formatCount(n: number): string {
  return n.toLocaleString('en-US');
}

export function formatPct(pct: number): string {
  const sign = pct > 0 ? '+' : '';
  return `${sign}${Math.round(pct)}%`;
}

export function formatRelative(iso: string): string {
  try {
    return `Updated ${formatDistanceToNowStrict(parseISO(iso))} ago`;
  } catch {
    return 'Updated recently';
  }
}

export function formatAbsolute(iso: string): string {
  try {
    return format(parseISO(iso), "yyyy-MM-dd HH:mm 'UTC'");
  } catch {
    return iso;
  }
}
