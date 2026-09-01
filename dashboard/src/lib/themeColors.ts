/**
 * Per-theme brand colors, shared by the theme cards, the trends charts and the
 * theme detail page. Kept out of ThemeCard.tsx so that component file exports
 * only components (react-refresh/only-export-components).
 */
export const THEME_COLORS: Record<string, string> = {
  Availability: '#ff6b00',
  Business: '#2563eb',
  Clients: '#7c3aed',
  Communication: '#0891b2',
  Diversion: '#ca8a04',
  Experience: '#059669',
  Payments: '#db2777',
  'Preferences and rates': '#9333ea',
  'Recurring billings': '#0d9488',
  Requests: '#4f46e5',
  'Rover Cards': '#ea580c',
  'Rover fees': '#65a30d',
  Taxes: '#0369a1',
  Untagged: '#94a3b8',
};

export function themeColor(theme: string): string {
  return THEME_COLORS[theme] ?? '#64748b';
}
