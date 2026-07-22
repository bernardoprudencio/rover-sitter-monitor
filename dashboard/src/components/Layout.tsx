import { NavLink, Outlet } from 'react-router-dom';
import clsx from 'clsx';
import { useData } from '../context/DataContext';
import { formatAbsolute, formatCount, formatRelative } from '../lib/format';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: '◧' },
  { to: '/trends', label: 'Trends', icon: '↗' },
  { to: '/research', label: 'Research', icon: '✎' },
  { to: '/star-sitter', label: 'Star Sitter', icon: '★' },
  { to: '/untagged', label: 'Untagged', icon: '?' },
  { to: '/how-it-works', label: 'How it works', icon: '✦' },
];

export function Layout() {
  const { meta } = useData();
  return (
    <div className="flex min-h-screen w-full bg-neutral-50">
      <aside className="sticky top-0 hidden h-screen w-56 shrink-0 border-r border-neutral-200 bg-white px-3 py-4 md:flex md:flex-col">
        <div className="mb-6 flex items-center gap-2 px-2">
          <span className="text-2xl">🐾</span>
          <div>
            <div className="text-h3 text-neutral-900">Rover Sitter</div>
            <div className="text-caption text-primary-600">Pulse</div>
          </div>
        </div>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-md border-l-2 px-3 py-2 text-body transition',
                  isActive
                    ? 'border-primary-500 bg-primary-50 text-primary-700 font-semibold'
                    : 'border-transparent text-neutral-700 hover:bg-neutral-100',
                )
              }
            >
              <span aria-hidden className="font-mono text-neutral-400">
                {item.icon}
              </span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto px-2 text-caption text-neutral-400">
          <a
            href="https://github.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-primary-700"
          >
            View source on GitHub ↗
          </a>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-neutral-200 bg-white px-6">
          <div className="flex items-center gap-3 md:hidden">
            <span className="text-xl">🐾</span>
            <span className="text-h3 text-neutral-900">Rover Sitter Pulse</span>
          </div>
          <div className="hidden md:block text-h3 text-neutral-900">
            {/* Page title rendered by route content */}
          </div>
          <div className="flex items-center gap-4 text-caption text-neutral-500">
            <span title={formatAbsolute(meta.generated_at)}>{formatRelative(meta.generated_at)}</span>
            <span>·</span>
            <span>{formatCount(meta.post_count)} posts</span>
            {meta.sheet_url && (
              <a
                href={meta.sheet_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700"
              >
                View source sheet ↗
              </a>
            )}
          </div>
        </header>
        <main className="min-w-0 flex-1 px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
