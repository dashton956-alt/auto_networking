import type { ReactNode } from "react";
import { Skeleton } from "./Skeleton";

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  width?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  loading?: boolean;
  emptyMessage?: string;
  caption?: string;
}

export function Table<T>({
  columns,
  rows,
  rowKey,
  loading = false,
  emptyMessage = "No data",
  caption,
}: TableProps<T>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-chrome-200">
      <table className="min-w-full divide-y divide-chrome-200 text-sm">
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead className="bg-chrome-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                style={col.width ? { width: col.width } : undefined}
                className="px-4 py-3 text-left text-xs font-semibold text-chrome-500 uppercase tracking-wide"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-chrome-100">
          {loading &&
            Array.from({ length: 5 }).map((_, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3">
                    <Skeleton className="h-4 w-full" aria-label="Loading row" />
                  </td>
                ))}
              </tr>
            ))}

          {!loading && rows.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-8 text-center text-chrome-500"
              >
                {emptyMessage}
              </td>
            </tr>
          )}

          {!loading &&
            rows.map((row) => (
              <tr
                key={rowKey(row)}
                className="hover:bg-chrome-50 transition-colors"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-chrome-700 whitespace-nowrap">
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
