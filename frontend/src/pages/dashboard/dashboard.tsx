import { useState } from "react";
import { Header } from "./components/header/header";
import styles from "./dashboard.module.css";
import { InvestorWidget } from "./components/investor-widget";
import { CommitmentWidget } from "./components/commitment-widget";
import { useGetInvestorsQuery } from "@/graphql/generated/graphql";
import type { InvestorFromQuery } from "@/libs/types";

export const Dashboard = () => {
  const { data, loading, error } = useGetInvestorsQuery();
  const [selectedInvestor, setSelectedInvestor] =
    useState<InvestorFromQuery | null>(null);

  if (loading) {
    return <p>"Loading"</p>;
  }

  if (error || !data) {
    return <p>"Somethign went Wrong"</p>;
  }

  return (
    <div className={styles.container}>
      <Header
        totalInvestors={data.investors.total}
        totalCommitments={data.investors.totalCommitmentAmount}
      />

      <InvestorWidget
        investors={data.investors.investors}
        selectedInvestor={selectedInvestor}
        onInvestorSelect={setSelectedInvestor}
      />

      <CommitmentWidget investorId={selectedInvestor?.id} />
    </div>
  );
};
