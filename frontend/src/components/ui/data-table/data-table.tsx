import { type ReactNode } from "react";
import clsx from "clsx";

import styles from "./data-table.module.css";
import { DataTableHeader } from "./header";
import type {
  DataTableColumn,
  DataTableSearchProps,
  PaginationConfig,
} from "./libs/types";
import { DataTableBody } from "./table-body";

interface DataTableProps<T> {
  title: string;
  subtitle?: string;
  headerRight?: ReactNode;
  searchConfig?: DataTableSearchProps;
  columns: DataTableColumn<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  selectedRowId?: string | number;
  getRowKey: (item: T) => string | number;
  emptyState?: ReactNode;
  className?: string;
  paginate?: boolean;
  paginationConfig?: PaginationConfig;
}

export function DataTable<T>({
  title,
  subtitle,
  headerRight,
  searchConfig,
  columns,
  data,
  onRowClick,
  selectedRowId,
  getRowKey,
  emptyState,
  className,
}: DataTableProps<T>) {
  return (
    <div className={clsx(styles.widget, className)}>
      <DataTableHeader
        title={title}
        subtitle={subtitle}
        headerRight={headerRight}
        searchConfig={searchConfig}
      />

      {!data.length && emptyState ? (
        emptyState
      ) : (
        <DataTableBody
          columns={columns}
          data={data}
          onRowClick={onRowClick}
          selectedRowId={selectedRowId}
          getRowKey={getRowKey}
        />
      )}
    </div>
  );
}
