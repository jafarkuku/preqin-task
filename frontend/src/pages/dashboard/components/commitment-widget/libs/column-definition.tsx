import type { DataTableColumn } from "@/components/ui/data-table";

import type { CommitmentDetail } from "@/graphql/generated/graphql";
import { formatCurrency } from "@/libs/utils";
import { PackageSearch } from "lucide-react";
import styles from "../commitment-widget.module.css";

export const columns: DataTableColumn<CommitmentDetail>[] = [
  {
    key: "id",
    header: "Id",
    render: (row) => <span className={styles.commitmentId}>#{row.id}</span>,
  },
  {
    key: "assetClass",
    header: "Asset Class",
    render: ({ name }) => (
      <div className={styles.assetClassCell}>
        <PackageSearch className={styles.icon} />
        <span className={styles.assetClassName}>{name}</span>
      </div>
    ),
  },
  {
    key: "currency",
    header: "Currency",
    render: (row) => <span className={styles.currency}>{row.currency}</span>,
  },
  {
    key: "amount",
    header: "Amount",
    render: (row) => <span className={styles.amount}>{formatCurrency(row.amount)}</span>,
  },
  {
    key: "percentage",
    header: "Percentage",
    render: ({ percentage }) => (
      <div className={styles.percentageCell}>
        <span className={styles.percentage}>{percentage}%</span>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${percentage}%` }} />
        </div>
      </div>
    ),
  },
];
