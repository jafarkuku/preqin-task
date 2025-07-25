import type { CommitmentBreakdown } from "@/graphql/generated/graphql";
import type { InvestorFromQuery } from "@/libs/types";
import { faker } from "@faker-js/faker";

export type PaginatedInvestors = {
  investors: InvestorFromQuery[];
  totalCommitmentAmount: number;
  total: number;
  page: number;
  size: number;
  totalPages: number;
};

export function createInvestor(
  overrides: Partial<InvestorFromQuery> = {}
): InvestorFromQuery {
  return {
    id: faker.string.uuid(),
    name: faker.company.name(),
    investorType: faker.helpers.arrayElement([
      "fund manager",
      "institutional",
      "private",
    ]),
    country: faker.location.country(),
    dateAdded: faker.date.past().toISOString(),
    commitmentCount: faker.number.int({ min: 0, max: 10 }),
    totalCommitmentAmount: parseFloat(
      faker.finance.amount({ min: 0, max: 10000000 })
    ),
    ...overrides,
  };
}

export function createPaginatedInvestors(
  count: number,
  page = 1,
  size = 10
): PaginatedInvestors {
  const investors = Array.from({ length: count }, () => createInvestor());
  const totalCommitmentAmount = investors.reduce(
    (sum, inv) => sum + inv.totalCommitmentAmount,
    0
  );

  return {
    investors,
    totalCommitmentAmount,
    total: count,
    page,
    size,
    totalPages: Math.ceil(count / size),
  };
}

export function createCommitmentBreakdownMock(
  overrides = {}
): CommitmentBreakdown {
  return {
    __typename: "CommitmentBreakdown",
    investorId: faker.string.uuid(),
    investorName: faker.company.name(),
    totalCommitmentAmount: faker.number.int({ min: 100_000, max: 5_000_000 }),
    commitments: [
      {
        id: faker.string.uuid(),
        assetClassId: "asset-1",
        name: "Real Estate",
        amount: 500_000,
        currency: "GBP",
        percentage: 50,
        createdAt: "2025-07-28T12:00:00Z",
      },
    ],
    assets: [
      {
        id: "asset-1",
        name: "Real Estate",
      },
    ],
    ...overrides,
  };
}
