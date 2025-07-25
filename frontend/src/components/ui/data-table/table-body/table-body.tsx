import { type DataTableColumn } from "../libs/types";
import styles from "./table-body.module.css";
import clsx from "clsx";

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
  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr className={styles.headerRow}>
            {columns.map((column) => (
              <th key={column.key} className={styles.headerCell}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => {
            const rowKey = getRowKey(item);
            const isSelected = selectedRowId === rowKey;

            return (
              <tr
                key={rowKey}
                className={clsx(
                  styles.row,
                  isSelected && styles.selectedRow,
                  onRowClick && styles.clickableRow
                )}
                onClick={() => onRowClick?.(item)}
              >
                {columns.map((column) => (
                  <td key={column.key} className={styles.cell}>
                    {column.render(item, index)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
