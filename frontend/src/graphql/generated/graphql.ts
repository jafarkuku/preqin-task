import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
import * as ApolloReactHooks from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type AssetSummary = {
  __typename?: 'AssetSummary';
  commitmentCount: Scalars['Int']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  percentageOfTotal: Scalars['Float']['output'];
  totalCommitmentAmount: Scalars['Float']['output'];
};

export type CommitmentBreakdown = {
  __typename?: 'CommitmentBreakdown';
  assets: Array<AssetSummary>;
  commitments: Array<CommitmentDetail>;
  investorId: Scalars['String']['output'];
  investorName: Scalars['String']['output'];
  totalCommitmentAmount: Scalars['Float']['output'];
};

export type CommitmentDetail = {
  __typename?: 'CommitmentDetail';
  amount: Scalars['Float']['output'];
  assetClassId: Scalars['String']['output'];
  createdAt: Scalars['String']['output'];
  currency: Scalars['String']['output'];
  id: Scalars['String']['output'];
  name: Scalars['String']['output'];
  percentage: Scalars['Float']['output'];
};

export type InvestorDetail = {
  __typename?: 'InvestorDetail';
  commitmentCount: Scalars['Int']['output'];
  country: Scalars['String']['output'];
  createdAt: Scalars['String']['output'];
  dateAdded: Scalars['String']['output'];
  id: Scalars['String']['output'];
  investorType: Scalars['String']['output'];
  name: Scalars['String']['output'];
  totalCommitmentAmount: Scalars['Float']['output'];
  updatedAt: Scalars['String']['output'];
};

export type InvestorList = {
  __typename?: 'InvestorList';
  investors: Array<InvestorDetail>;
  page: Scalars['Int']['output'];
  size: Scalars['Int']['output'];
  total: Scalars['Int']['output'];
  totalCommitmentAmount: Scalars['Float']['output'];
  totalPages: Scalars['Int']['output'];
};

export type Query = {
  __typename?: 'Query';
  commitmentBreakdown?: Maybe<CommitmentBreakdown>;
  investors: InvestorList;
};


export type QueryCommitmentBreakdownArgs = {
  assetClassId?: InputMaybe<Scalars['String']['input']>;
  investorId: Scalars['String']['input'];
};


export type QueryInvestorsArgs = {
  page?: Scalars['Int']['input'];
  size?: Scalars['Int']['input'];
};

export type GetInvestorsQueryVariables = Exact<{
  page?: InputMaybe<Scalars['Int']['input']>;
  size?: InputMaybe<Scalars['Int']['input']>;
}>;


export type GetInvestorsQuery = { __typename?: 'Query', investors: { __typename?: 'InvestorList', totalCommitmentAmount: number, total: number, page: number, size: number, totalPages: number, investors: Array<{ __typename?: 'InvestorDetail', id: string, name: string, investorType: string, country: string, dateAdded: string, commitmentCount: number, totalCommitmentAmount: number }> } };

export type GetCommitmentBreakdownQueryVariables = Exact<{
  investorId: Scalars['String']['input'];
  assetClassId?: InputMaybe<Scalars['String']['input']>;
}>;


export type GetCommitmentBreakdownQuery = { __typename?: 'Query', commitmentBreakdown?: { __typename?: 'CommitmentBreakdown', investorId: string, investorName: string, totalCommitmentAmount: number, commitments: Array<{ __typename?: 'CommitmentDetail', id: string, assetClassId: string, name: string, amount: number, currency: string, percentage: number, createdAt: string }>, assets: Array<{ __typename?: 'AssetSummary', id: string, name: string, totalCommitmentAmount: number }> } | null };


export const GetInvestorsDocument = gql`
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

/**
 * __useGetInvestorsQuery__
 *
 * To run a query within a React component, call `useGetInvestorsQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetInvestorsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetInvestorsQuery({
 *   variables: {
 *      page: // value for 'page'
 *      size: // value for 'size'
 *   },
 * });
 */
export function useGetInvestorsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<GetInvestorsQuery, GetInvestorsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return ApolloReactHooks.useQuery<GetInvestorsQuery, GetInvestorsQueryVariables>(GetInvestorsDocument, options);
      }
export function useGetInvestorsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<GetInvestorsQuery, GetInvestorsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return ApolloReactHooks.useLazyQuery<GetInvestorsQuery, GetInvestorsQueryVariables>(GetInvestorsDocument, options);
        }
export function useGetInvestorsSuspenseQuery(baseOptions?: ApolloReactHooks.SkipToken | ApolloReactHooks.SuspenseQueryHookOptions<GetInvestorsQuery, GetInvestorsQueryVariables>) {
          const options = baseOptions === ApolloReactHooks.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return ApolloReactHooks.useSuspenseQuery<GetInvestorsQuery, GetInvestorsQueryVariables>(GetInvestorsDocument, options);
        }
export type GetInvestorsQueryHookResult = ReturnType<typeof useGetInvestorsQuery>;
export type GetInvestorsLazyQueryHookResult = ReturnType<typeof useGetInvestorsLazyQuery>;
export type GetInvestorsSuspenseQueryHookResult = ReturnType<typeof useGetInvestorsSuspenseQuery>;
export type GetInvestorsQueryResult = Apollo.QueryResult<GetInvestorsQuery, GetInvestorsQueryVariables>;
export const GetCommitmentBreakdownDocument = gql`
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

/**
 * __useGetCommitmentBreakdownQuery__
 *
 * To run a query within a React component, call `useGetCommitmentBreakdownQuery` and pass it any options that fit your needs.
 * When your component renders, `useGetCommitmentBreakdownQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGetCommitmentBreakdownQuery({
 *   variables: {
 *      investorId: // value for 'investorId'
 *      assetClassId: // value for 'assetClassId'
 *   },
 * });
 */
export function useGetCommitmentBreakdownQuery(baseOptions: ApolloReactHooks.QueryHookOptions<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables> & ({ variables: GetCommitmentBreakdownQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return ApolloReactHooks.useQuery<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>(GetCommitmentBreakdownDocument, options);
      }
export function useGetCommitmentBreakdownLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return ApolloReactHooks.useLazyQuery<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>(GetCommitmentBreakdownDocument, options);
        }
export function useGetCommitmentBreakdownSuspenseQuery(baseOptions?: ApolloReactHooks.SkipToken | ApolloReactHooks.SuspenseQueryHookOptions<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>) {
          const options = baseOptions === ApolloReactHooks.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return ApolloReactHooks.useSuspenseQuery<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>(GetCommitmentBreakdownDocument, options);
        }
export type GetCommitmentBreakdownQueryHookResult = ReturnType<typeof useGetCommitmentBreakdownQuery>;
export type GetCommitmentBreakdownLazyQueryHookResult = ReturnType<typeof useGetCommitmentBreakdownLazyQuery>;
export type GetCommitmentBreakdownSuspenseQueryHookResult = ReturnType<typeof useGetCommitmentBreakdownSuspenseQuery>;
export type GetCommitmentBreakdownQueryResult = Apollo.QueryResult<GetCommitmentBreakdownQuery, GetCommitmentBreakdownQueryVariables>;