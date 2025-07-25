import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import type { CommitmentDetail } from "@/graphql/generated/graphql";
import { formatCurrency } from "@/libs/utils";
import { columns } from "../column-definition";

const mockCommitment: CommitmentDetail = {
  __typename: "CommitmentDetail",
  id: "c-1",
  assetClassId: "asset-1",
  createdAt: "2025-07-28T12:00:00Z",
  currency: "USD",
  amount: 250000,
  name: "Real Estate",
  percentage: 40,
};

describe("Commitment Columns Renderers", () => {
  it("renders commitment ID", () => {
    const { container } = render(<>{columns[0].render(mockCommitment, 0)}</>);

    expect(container.textContent).toContain(`#${mockCommitment.id}`);
  });

  it("renders asset class name with correct color", () => {
    const { container } = render(<>{columns[1].render(mockCommitment, 0)}</>);

    expect(container.textContent).toContain("Real Estate");

    const colorIndicator = container.querySelector("div[style]");

    expect(colorIndicator?.getAttribute("style")).toContain(
      "var(--asset-class-real-estate)"
    );
  });

  it("renders currency", () => {
    const { container } = render(<>{columns[2].render(mockCommitment, 0)}</>);

    expect(container.textContent).toBe("USD");
  });

  it("renders amount formatted", () => {
    const { container } = render(<>{columns[3].render(mockCommitment, 0)}</>);

    expect(container.textContent).toBe(formatCurrency(mockCommitment.amount));
  });

  it("renders percentage and progress bar", () => {
    const { container } = render(<>{columns[4].render(mockCommitment, 0)}</>);

    expect(container.textContent).toContain("40%");

    const fill = container.querySelector("div[style]");

    expect(fill?.getAttribute("style")).toContain("width: 40%");
  });
});
