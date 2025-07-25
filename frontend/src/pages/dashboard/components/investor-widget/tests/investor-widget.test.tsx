import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { InvestorWidget } from "../investor-widget";
import type { InvestorFromQuery } from "@/libs/types";
import { createInvestor } from "@/test-utils/factory";

const mockInvestors: InvestorFromQuery[] = [createInvestor(), createInvestor()];

describe("InvestorWidget", () => {
  it("renders the investor list", () => {
    render(
      <InvestorWidget
        investors={mockInvestors}
        selectedInvestor={null}
        onInvestorSelect={vi.fn()}
      />
    );

    expect(screen.getByText(mockInvestors[0].name)).toBeInTheDocument();
    expect(screen.getByText(mockInvestors[1].name)).toBeInTheDocument();
  });

  it("filters the list based on search", () => {
    render(
      <InvestorWidget
        investors={mockInvestors}
        selectedInvestor={null}
        onInvestorSelect={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText("Search investors...");

    fireEvent.change(searchInput, {
      target: {
        value: mockInvestors[0].name,
      },
    });

    expect(screen.getByText(mockInvestors[0].name)).toBeInTheDocument();
    expect(screen.queryByText(mockInvestors[1].name)).not.toBeInTheDocument();
  });
});
