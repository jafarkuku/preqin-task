import { gql } from "@apollo/client";

export const GET_INVESTORS = gql`
  query GetInvestors($page: Int = 1, $size: Int = 20) {
    investors(page: $page, size: $size) {
      investors {
        id
        name
        investorType
        country
        dateAdded
        commitmentCount
        totalCommitmentAmount
      }
      totalCommitmentAmount
      total
      page
      size
      totalPages
    }
  }
`;

export const GET_COMMITMENT_BREAKDOWN = gql`
  query GetCommitmentBreakdown($investorId: String!, $assetClassId: String) {
    commitmentBreakdown(investorId: $investorId, assetClassId: $assetClassId) {
      investorId
      investorName
      totalCommitmentAmount
      commitments {
        id
        assetClassId
        name
        amount
        currency
        percentage
        createdAt
      }
      assets {
        id
        name
        totalCommitmentAmount
      }
    }
  }
`;
