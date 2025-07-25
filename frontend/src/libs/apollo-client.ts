import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";

const graphqlUrl =
  import.meta.env.VITE_GRAPHQL_URL || "http://localhost:8005/graphql";

const httpLink = createHttpLink({
  uri: graphqlUrl,
  credentials: "same-origin",
});

export const apolloClient = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          investors: {
            keyArgs: ["page", "size"],
            merge(_, incoming) {
              return incoming;
            },
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: "cache-and-network",
    },
  },
});
