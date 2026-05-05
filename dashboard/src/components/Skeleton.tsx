import clsx from 'clsx';

export function Skeleton({
  fullPage = false,
  rows = 6,
  className,
}: {
  fullPage?: boolean;
  rows?: number;
  className?: string;
}) {
  if (fullPage) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-neutral-50">
        <div className="w-full max-w-3xl space-y-3 p-8">
          {Array.from({ length: rows }).map((_, i) => (
            <div
              key={i}
              className="h-16 animate-pulse rounded-xl bg-neutral-200"
              style={{ animationDelay: `${i * 80}ms` }}
            />
          ))}
        </div>
      </div>
    );
  }
  return (
    <div className={clsx('space-y-3', className)}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-xl bg-neutral-200" />
      ))}
    </div>
  );
}
