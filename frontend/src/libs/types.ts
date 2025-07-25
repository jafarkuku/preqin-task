import { type GetInvestorsQuery } from "@/graphql/generated/graphql";

export type InvestorFromQuery =
  GetInvestorsQuery["investors"]["investors"][number];
