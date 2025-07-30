import { DataTable } from "@/components/ui/data-table";
import { TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";

import { useGetCommitmentBreakdownQuery } from "@/graphql/generated/graphql";
import { formatCurrency } from "@/libs/utils";
import styles from "./commitment-widget.module.css";
import { HeaderRight } from "./header/header-right";
import { columns } from "./libs/column-definition";

interface CommitmentWidgetProps {
  investorId: string | undefined;
}

export const CommitmentWidget = ({ investorId = "" }: CommitmentWidgetProps) => {
  const [selectedAsset, setSelectedAsset] = useState<string>("all");

  const { data } = useGetCommitmentBreakdownQuery({
    variables: {
      investorId,
      assetClassId: selectedAsset === "all" ? "" : selectedAsset,
    },
    skip: !investorId,
  });

  useEffect(() => {
    setSelectedAsset("all");
  }, [investorId]);

  if (!data?.commitmentBreakdown?.commitments.length) {
    return (
      <DataTable
        title="Commitment Breakdown"
        columns={[]}
        data={[]}
        getRowKey={() => "empty"}
        emptyState={
          <div className={styles.emptyState}>
            <TrendingUp className={styles.emptyIcon} />
            <h3 className={styles.emptyTitle}>Select an investor</h3>
            <p className={styles.emptyText}>
              Choose an investor from the table above to view their commitment breakdown
            </p>
          </div>
        }
      />
    );
  }

  const {
    commitmentBreakdown: { investorName, totalCommitmentAmount, assets },
  } = data;

  const commitments =
    selectedAsset === "all"
      ? data.commitmentBreakdown.commitments
      : data.commitmentBreakdown.commitments.filter((commitment) => commitment.assetClassId === selectedAsset);

  const totalAmount =
    selectedAsset === "all"
      ? totalCommitmentAmount
      : assets.find((asset) => asset.id === selectedAsset)?.totalCommitmentAmount;

  return (
    <DataTable
      title={investorName}
      subtitle="Commitment Breakdown"
      headerRight={
        <HeaderRight
          totalAmount={formatCurrency(totalAmount || 0)}
          assets={assets}
          selectedAsset={selectedAsset}
          onSelectAsset={setSelectedAsset}
        />
      }
      columns={columns}
      data={commitments}
      getRowKey={(row) => row.id}
      className={styles.CommitmentWidget}
    />
  );
};
