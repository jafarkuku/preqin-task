import { Select } from "@/components/ui/select";
import styles from "./header-right.module.css";

interface HeaderRightProps {
  totalAmount: string;
  assets: {
    id: string;
    name: string;
  }[];
  selectedAsset: string;
  onSelectAsset: (value: string) => void;
}

export const HeaderRight = ({
  totalAmount,
  assets,
  selectedAsset,
  onSelectAsset,
}: HeaderRightProps) => {
  const assetClassOptions = [
    { label: "All Asset Classes", value: "all" },
    ...assets.map(({ id, name }) => ({
      label: name,
      value: id,
    })),
  ];

  return (
    <div className={styles.headerRight}>
      <Select
        value={selectedAsset}
        onChange={(value) => onSelectAsset(value)}
        options={assetClassOptions}
        placeholder="Filter by asset class"
      />
      <div className={styles.totalSection}>
        <h1 className={styles.totalAmount}>{totalAmount}</h1>
        <p className={styles.totalLabel}>Total Commitments</p>
      </div>
    </div>
  );
};
