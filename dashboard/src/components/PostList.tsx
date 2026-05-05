import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import type { Post } from '../types';
import { PostRow } from './PostRow';
import { EmptyState } from './EmptyState';

export function PostList({
  posts,
  onProblemClick,
  onReset,
  emptyMessage = 'No posts match these filters.',
  showResetAction = true,
  height = '70vh',
}: {
  posts: Post[];
  onProblemClick?: (problem: string) => void;
  onReset?: () => void;
  emptyMessage?: string;
  showResetAction?: boolean;
  height?: string;
}) {
  const parentRef = useRef<HTMLDivElement>(null);
  const v = useVirtualizer({
    count: posts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 88,
    overscan: 8,
  });

  if (posts.length === 0) {
    return (
      <EmptyState
        message={emptyMessage}
        action={
          showResetAction && onReset ? (
            <button
              type="button"
              onClick={onReset}
              className="rounded-md bg-primary-500 px-4 py-2 text-white text-body font-semibold hover:bg-primary-600"
            >
              Reset filters
            </button>
          ) : undefined
        }
      />
    );
  }

  return (
    <div
      ref={parentRef}
      className="overflow-auto rounded-xl border border-neutral-200 bg-neutral-50"
      style={{ height }}
    >
      <div
        style={{
          height: `${v.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {v.getVirtualItems().map((vi) => {
          const post = posts[vi.index];
          return (
            <div
              key={post.id}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${vi.start}px)`,
                padding: '4px 8px',
              }}
            >
              <PostRow post={post} onProblemClick={onProblemClick} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
