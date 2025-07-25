import type { ReactNode } from "react";

export interface DataTableColumn<T> {
  key: string;
  header: string;
  render: (item: T, index: number) => ReactNode;
  rowSpan?: (item: T, index: number) => number;
}

export interface PaginationConfig {
  itemsPerPage?: number;
}

export interface DataTableSearchProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}
