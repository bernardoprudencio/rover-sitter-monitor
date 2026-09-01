import { createContext, useContext } from 'react';
import type { Aggregates, Meta, ResearchAggregates, Taxonomy } from '../types';

export interface DataContextValue {
  meta: Meta;
  taxonomy: Taxonomy;
  aggregates: Aggregates;
  researchAggregates: ResearchAggregates | null;
}

export const DataContext = createContext<DataContextValue | null>(null);

export function useData(): DataContextValue {
  const v = useContext(DataContext);
  if (!v) throw new Error('useData must be used within DataProvider');
  return v;
}
