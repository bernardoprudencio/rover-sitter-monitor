import type { Aggregates } from '../types';
import { useData } from '../context/DataContext';

export function useAggregates(): Aggregates {
  return useData().aggregates;
}
