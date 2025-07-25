import { useMemo, useState } from "react";
import { DataTable } from "@/components/ui/data-table";
import type { InvestorFromQuery } from "@/libs/types";
import styles from "./investor-widget.module.css";
import { columns } from "./libs/column-definitions";

interface InvestorWidgetProps {
  investors: InvestorFromQuery[];
  selectedInvestor: InvestorFromQuery | null;
  onInvestorSelect: (investor: InvestorFromQuery) => void;
}

export const InvestorWidget = ({
  investors,
  selectedInvestor,
  onInvestorSelect,
}: InvestorWidgetProps) => {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredInvestors = useMemo(() => {
    return investors.filter(
      (investor) =>
        investor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        investor.investorType
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        investor.country.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [investors, searchTerm]);

  return (
    <DataTable
      title="Investors"
      searchConfig={{
        value: searchTerm,
        onChange: setSearchTerm,
        placeholder: "Search investors...",
      }}
      columns={columns}
      data={filteredInvestors || []}
      onRowClick={onInvestorSelect}
      selectedRowId={selectedInvestor?.id}
      getRowKey={(investor) => investor.id}
      className={styles.investorTable}
      paginate
      paginationConfig={{ itemsPerPage: 5 }}
    />
  );
};
