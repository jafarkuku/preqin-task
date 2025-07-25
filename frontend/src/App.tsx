import { ApolloProvider } from "@apollo/client";
import { apolloClient } from "./libs/apollo-client";
import { Dashboard } from "./pages/dashboard/dashboard";
import "./App.css";

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <Dashboard />
    </ApolloProvider>
  );
}

export default App;
