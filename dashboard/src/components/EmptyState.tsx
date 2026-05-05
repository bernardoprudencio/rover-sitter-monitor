import type { ReactNode } from 'react';

export function EmptyState({
  message,
  action,
}: {
  message: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-dashed border-neutral-300 bg-white p-10 text-center">
      <p className="text-body text-neutral-500">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
