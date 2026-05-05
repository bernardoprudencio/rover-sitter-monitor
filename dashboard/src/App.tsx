import { lazy, Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { NuqsAdapter } from 'nuqs/adapters/react-router/v6';
import { DataProvider } from './context/DataContext';
import { Layout } from './components/Layout';
import { Skeleton } from './components/Skeleton';

const Overview = lazy(() => import('./routes/Overview'));
const ThemeDetail = lazy(() => import('./routes/ThemeDetail'));
const Trends = lazy(() => import('./routes/Trends'));
const Untagged = lazy(() => import('./routes/Untagged'));
const Research = lazy(() => import('./routes/Research'));

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <NuqsAdapter>
        <DataProvider>
          <Suspense fallback={<Skeleton fullPage />}>
            <Routes>
              <Route element={<Layout />}>
                <Route index element={<Overview />} />
                <Route path="theme/:slug" element={<ThemeDetail />} />
                <Route path="trends" element={<Trends />} />
                <Route path="untagged" element={<Untagged />} />
                <Route path="research" element={<Research />} />
                <Route
                  path="*"
                  element={
                    <div className="rounded-xl bg-white p-10 text-center">
                      <h1 className="text-h1">Not found</h1>
                    </div>
                  }
                />
              </Route>
            </Routes>
          </Suspense>
        </DataProvider>
      </NuqsAdapter>
    </BrowserRouter>
  );
}
