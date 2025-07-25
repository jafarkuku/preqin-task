import { Building2, MapPin, Calendar } from "lucide-react";

import { type DataTableColumn } from "@/components/ui/data-table";
import { formatCurrency } from "@/libs/utils";
import type { InvestorFromQuery } from "@/libs/types";

import styles from "../investor-widget.module.css";

export const columns: DataTableColumn<InvestorFromQuery>[] = [
  {
    key: "name",
    header: "Investor",
    render: (investor) => (
      <div className={styles.investorName}>{investor.name}</div>
    ),
  },
  {
    key: "type",
    header: "Type",
    render: (investor) => (
      <div className={styles.cellContent}>
        <Building2 className={styles.icon} />
        <span className={styles.capitalized}>{investor.investorType}</span>
      </div>
    ),
  },
  {
    key: "country",
    header: "Location",
    render: (investor) => (
      <div className={styles.cellContent}>
        <MapPin className={styles.icon} />
        <span>{investor.country}</span>
      </div>
    ),
  },
  {
    key: "commitments",
    header: "Commitments",
    render: ({ commitmentCount }) => (
      <span className={styles.badge}>
        {commitmentCount} commitment{commitmentCount > 1 ? "s" : ""}
      </span>
    ),
  },
  {
    key: "totalAmount",
    header: "Total Amount",
    render: ({ totalCommitmentAmount }) => (
      <span className={styles.amount}>
        {formatCurrency(totalCommitmentAmount)}
      </span>
    ),
  },
  {
    key: "dateAdded",
    header: "Date Added",
    render: ({ dateAdded }) => (
      <div className={styles.cellContent}>
        <Calendar className={styles.icon} />
        <span>{new Date(dateAdded).toLocaleDateString()}</span>
      </div>
    ),
  },
];
