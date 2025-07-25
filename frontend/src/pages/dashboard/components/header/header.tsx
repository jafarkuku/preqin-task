import { Building2 } from "lucide-react";
import { formatCurrency } from "@/libs/utils";
import styles from "./Header.module.css";

interface HeaderProps {
  totalInvestors: number;
  totalCommitments: number;
}

export const Header = ({ totalInvestors, totalCommitments }: HeaderProps) => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.content}>
          <div className={styles.logoSection}>
            <Building2 className={styles.logoIcon} />
            <div>
              <h1 className={styles.title}>Preqin</h1>
              <p className={styles.subtitle}>Investment Management Dashboard</p>
            </div>
          </div>
          <div className={styles.stats}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>
                {totalInvestors.toLocaleString()}
              </div>
              <div className={styles.statLabel}>Investors</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>
                {formatCurrency(totalCommitments)}
              </div>
              <div className={styles.statLabel}>Total Commitments</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
