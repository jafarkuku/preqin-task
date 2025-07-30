import { useMemo } from "react";
import { type DataTableColumn } from "../libs/types";
import styles from "./table-body.module.css";
import { TableRow } from "./table-row/table-row";

interface DataTableBodyProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  selectedRowId?: string | number;
  getRowKey: (item: T) => string | number;
}

export function DataTableBody<T>({
  columns,
  data,
  onRowClick,
  selectedRowId,
  getRowKey,
}: DataTableBodyProps<T>) {
  const headerRow = useMemo(
    () => (
      <tr className={styles.headerRow}>
        {columns.map((column) => (
          <th key={column.key} className={styles.headerCell}>
            {column.header}
          </th>
        ))}
      </tr>
    ),
    [columns]
  );

  const rows = useMemo(() => {
    return data.map((item, index) => {
      const rowKey = getRowKey(item);
      return {
        item,
        index,
        rowKey,
        isSelected: selectedRowId === rowKey,
      };
    });
  }, [data, selectedRowId, getRowKey]);

  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>{headerRow}</thead>
        <tbody>
          {rows.map(({ item, index, rowKey, isSelected }) => (
            <TableRow
              key={rowKey}
              item={item}
              index={index}
              columns={columns}
              onRowClick={onRowClick}
              isSelected={isSelected}
              rowKey={rowKey}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
