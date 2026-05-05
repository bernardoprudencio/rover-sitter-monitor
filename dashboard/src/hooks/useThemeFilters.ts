import { useQueryStates } from 'nuqs';
import { themeDetailParsers } from '../lib/filters';

export function useThemeFilters() {
  return useQueryStates(themeDetailParsers);
}
