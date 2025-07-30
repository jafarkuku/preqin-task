import clsx from "clsx";
import { memo, useCallback, useMemo } from "react";
import type { DataTableColumn } from "../../libs/types";
import styles from "../table-body.module.css";

interface TableCellProps<T> {
  column: DataTableColumn<T>;
  item: T;
  index: number;
}

interface TableRowProps<T> {
  item: T;
  index: number;
  columns: DataTableColumn<T>[];
  onRowClick?: (item: T) => void;
  isSelected: boolean;
  rowKey: string | number;
}

function TableCellComponent<T>({ column, item, index }: TableCellProps<T>) {
  return <td className={styles.cell}>{column.render(item, index)}</td>;
}

const MemoizedTableCell = memo(TableCellComponent) as typeof TableCellComponent;

function TableRowComponent<T>(props: TableRowProps<T>) {
  const { item, index, columns, onRowClick, isSelected } = props;

  const handleClick = useCallback(() => {
    if (onRowClick) onRowClick(item);
  }, [onRowClick, item]);

  const rowClasses = useMemo(() => {
    return clsx(styles.row, isSelected && styles.selectedRow, onRowClick && styles.clickableRow);
  }, [isSelected, onRowClick]);

  return (
    <tr className={rowClasses} onClick={onRowClick ? handleClick : undefined}>
      {columns.map((column) => (
        <MemoizedTableCell key={column.key} column={column} item={item} index={index} />
      ))}
    </tr>
  );
}

export const TableRow = memo(TableRowComponent) as typeof TableRowComponent;
