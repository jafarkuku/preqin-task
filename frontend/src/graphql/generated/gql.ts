/* eslint-disable */
import * as types from "./graphql";
import { type TypedDocumentNode as DocumentNode } from "@graphql-typed-document-node/core";

/**
 * Map of all GraphQL operations in the project.
 *
 * This map has several performance disadvantages:
 * 1. It is not tree-shakeable, so it will include all operations in the project.
 * 2. It is not minifiable, so the string of a GraphQL query will be multiple times inside the bundle.
 * 3. It does not support dead code elimination, so it will add unused operations.
 *
 * Therefore it is highly recommended to use the babel or swc plugin for production.
 * Learn more about it here: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client#reducing-bundle-size
 */
type Documents = {
  "\n  fragment InvestorSummaryFields on InvestorSummary {\n    id\n    name\n    investorType\n    country\n    commitmentCount\n    totalCommitmentAmount\n  }\n": typeof types.InvestorSummaryFieldsFragmentDoc;
  "\n  fragment AssetClassBreakdownFields on AssetClassBreakdown {\n    id\n    name\n    totalAmount\n    currency\n    percentage\n    commitmentCount\n    commitments {\n      id\n      amount\n      currency\n      percentage\n      createdAt\n    }\n  }\n": typeof types.AssetClassBreakdownFieldsFragmentDoc;
  "\n  \n  query GetInvestors {\n    investors {\n      ...InvestorSummaryFields\n    }\n  }\n": typeof types.GetInvestorsDocument;
  "\n  \n  \n  query GetInvestorDetail($id: String!) {\n    investor(id: $id) {\n      id\n      name\n      investorType\n      country\n      dateAdded\n      commitmentCount\n      totalCommitmentAmount\n      assetClassBreakdown {\n        ...AssetClassBreakdownFields\n      }\n    }\n  }\n": typeof types.GetInvestorDetailDocument;
};
const documents: Documents = {
  "\n  fragment InvestorSummaryFields on InvestorSummary {\n    id\n    name\n    investorType\n    country\n    commitmentCount\n    totalCommitmentAmount\n  }\n":
    types.InvestorSummaryFieldsFragmentDoc,
  "\n  fragment AssetClassBreakdownFields on AssetClassBreakdown {\n    id\n    name\n    totalAmount\n    currency\n    percentage\n    commitmentCount\n    commitments {\n      id\n      amount\n      currency\n      percentage\n      createdAt\n    }\n  }\n":
    types.AssetClassBreakdownFieldsFragmentDoc,
  "\n  \n  query GetInvestors {\n    investors {\n      ...InvestorSummaryFields\n    }\n  }\n":
    types.GetInvestorsDocument,
  "\n  \n  \n  query GetInvestorDetail($id: String!) {\n    investor(id: $id) {\n      id\n      name\n      investorType\n      country\n      dateAdded\n      commitmentCount\n      totalCommitmentAmount\n      assetClassBreakdown {\n        ...AssetClassBreakdownFields\n      }\n    }\n  }\n":
    types.GetInvestorDetailDocument,
};

/**
 * The gql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 *
 *
 * @example
 * ```ts
 * const query = gql(`query GetUser($id: ID!) { user(id: $id) { name } }`);
 * ```
 *
 * The query argument is unknown!
 * Please regenerate the types.
 */
export function gql(source: string): unknown;

/**
 * The gql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function gql(
  source: "\n  fragment InvestorSummaryFields on InvestorSummary {\n    id\n    name\n    investorType\n    country\n    commitmentCount\n    totalCommitmentAmount\n  }\n"
): (typeof documents)["\n  fragment InvestorSummaryFields on InvestorSummary {\n    id\n    name\n    investorType\n    country\n    commitmentCount\n    totalCommitmentAmount\n  }\n"];
/**
 * The gql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function gql(
  source: "\n  fragment AssetClassBreakdownFields on AssetClassBreakdown {\n    id\n    name\n    totalAmount\n    currency\n    percentage\n    commitmentCount\n    commitments {\n      id\n      amount\n      currency\n      percentage\n      createdAt\n    }\n  }\n"
): (typeof documents)["\n  fragment AssetClassBreakdownFields on AssetClassBreakdown {\n    id\n    name\n    totalAmount\n    currency\n    percentage\n    commitmentCount\n    commitments {\n      id\n      amount\n      currency\n      percentage\n      createdAt\n    }\n  }\n"];
/**
 * The gql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function gql(
  source: "\n  \n  query GetInvestors {\n    investors {\n      ...InvestorSummaryFields\n    }\n  }\n"
): (typeof documents)["\n  \n  query GetInvestors {\n    investors {\n      ...InvestorSummaryFields\n    }\n  }\n"];
/**
 * The gql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function gql(
  source: "\n  \n  \n  query GetInvestorDetail($id: String!) {\n    investor(id: $id) {\n      id\n      name\n      investorType\n      country\n      dateAdded\n      commitmentCount\n      totalCommitmentAmount\n      assetClassBreakdown {\n        ...AssetClassBreakdownFields\n      }\n    }\n  }\n"
): (typeof documents)["\n  \n  \n  query GetInvestorDetail($id: String!) {\n    investor(id: $id) {\n      id\n      name\n      investorType\n      country\n      dateAdded\n      commitmentCount\n      totalCommitmentAmount\n      assetClassBreakdown {\n        ...AssetClassBreakdownFields\n      }\n    }\n  }\n"];

export function gql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> =
  TDocumentNode extends DocumentNode<infer TType, any> ? TType : never;
