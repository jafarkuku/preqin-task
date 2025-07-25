import { type ReactNode } from "react";
import { Search } from "lucide-react";
import styles from "../data-table.module.css";

interface DataTableSearchProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

interface DataTableHeaderProps {
  title: string;
  subtitle?: string;
  headerRight?: ReactNode;
  searchConfig?: DataTableSearchProps;
}

export function DataTableHeader({
  title,
  subtitle,
  headerRight,
  searchConfig,
}: DataTableHeaderProps) {
  return (
    <div className={styles.header}>
      <div className={styles.titleSection}>
        <div>
          <h2 className={styles.title}>{title}</h2>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      </div>
      {(headerRight || searchConfig) && (
        <div className={styles.headerRight}>
          {headerRight && (
            <div className={styles.headerRightContent}>{headerRight}</div>
          )}
          {searchConfig && (
            <div className={styles.searchContainer}>
              <Search className={styles.searchIcon} />
              <input
                type="text"
                placeholder={searchConfig.placeholder || "Search..."}
                value={searchConfig.value}
                onChange={(e) => searchConfig.onChange?.(e.target.value)}
                className={styles.searchInput}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
