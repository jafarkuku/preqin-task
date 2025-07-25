import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { GET_COMMITMENT_BREAKDOWN } from "@/graphql/queries";
import { createCommitmentBreakdownMock } from "@/test-utils/factory";
import { CommitmentWidget } from "../commitment-widget";

describe("CommitmentWidget", () => {
  it("renders empty state when no investor is selected", () => {
    render(
      <MockedProvider mocks={[]}>
        <CommitmentWidget investorId={undefined} />
      </MockedProvider>
    );

    expect(screen.getByText("Select an investor")).toBeInTheDocument();
  });

  it("renders commitment breakdown after loading", async () => {
    const mockData = createCommitmentBreakdownMock({
      investorName: "Alpha Capital",
      totalCommitmentAmount: 1_000_000,
    });

    const mocks = [
      {
        request: {
          query: GET_COMMITMENT_BREAKDOWN,
          variables: { investorId: "1" },
        },
        result: {
          data: {
            commitmentBreakdown: mockData,
          },
        },
      },
    ];

    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <CommitmentWidget investorId="1" />
      </MockedProvider>
    );

    expect(await screen.findByText("Alpha Capital")).toBeInTheDocument();

    expect(await screen.findByText("Real Estate")).toBeInTheDocument();

    expect(screen.getByText("Commitment Breakdown")).toBeInTheDocument();

    expect(screen.getByText("£1M")).toBeInTheDocument();
  });
});
