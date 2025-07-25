import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { columns } from "../column-definitions";
import type { InvestorFromQuery } from "@/libs/types";
import { createInvestor } from "@/test-utils/factory";

export const mockInvestor: InvestorFromQuery = createInvestor({
  id: "inv-123",
  name: "Alpha Capital",
  investorType: "Fund Manager",
  country: "UK",
  dateAdded: "2025-07-27T00:00:00Z",
  commitmentCount: 3,
  totalCommitmentAmount: 250_000,
});

describe("Investor Widget Columns", () => {
  it("renders investor name", () => {
    render(<>{columns[0].render(mockInvestor, 0)}</>);
    expect(screen.getByText("Alpha Capital")).toBeInTheDocument();
  });

  it("renders investor type with icon", () => {
    render(<>{columns[1].render(mockInvestor, 0)}</>);
    expect(screen.getByText("Fund Manager")).toBeInTheDocument();
  });

  it("renders investor country with icon", () => {
    render(<>{columns[2].render(mockInvestor, 0)}</>);
    expect(screen.getByText("UK")).toBeInTheDocument();
  });

  it("renders commitment count with badge", () => {
    render(<>{columns[3].render(mockInvestor, 0)}</>);
    expect(screen.getByText("3 commitments")).toBeInTheDocument();
  });

  it("renders total commitment amount formatted", () => {
    render(<>{columns[4].render(mockInvestor, 0)}</>);
    expect(screen.getByText("£250K")).toBeInTheDocument();
  });

  it("renders date added in readable format", () => {
    render(<>{columns[5].render(mockInvestor, 0)}</>);
    expect(screen.getByText("27/07/2025")).toBeInTheDocument(); // May vary based on locale
  });
});
