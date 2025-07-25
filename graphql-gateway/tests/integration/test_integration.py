from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestGraphQLIntegration:
    """Integration tests for GraphQL endpoint."""

    def test_health_check(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "GraphQL Gateway"

    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "GraphQL Gateway"
        assert "/graphql" in data["graphql_endpoint"]
        assert len(data["queries"]) > 0

    @pytest.mark.asyncio
    async def test_graphql_investors_query(self, mock_investor_client):
        """Test GraphQL investors query."""
        with patch('app.schema.investors.get_investor_client', return_value=mock_investor_client):
            client = TestClient(app)

            query = """
            query {
                investors(page: 1, size: 20) {
                    investors {
                        id
                        name
                        investorType
                        country
                        commitmentCount
                        totalCommitmentAmount
                    }
                    totalCommitmentAmount
                    total
                    page
                    size
                }
            }
            """

            response = client.post("/graphql", json={"query": query})
            assert response.status_code == 200

            data = response.json()["data"]["investors"]

            expected_amount = sum(i["total_commitment_amount"]
                                  for i in mock_investor_client.get_all_investors.return_value["investors"])
            assert len(data["investors"]) == 2
            assert data["totalCommitmentAmount"] == expected_amount

    @pytest.mark.asyncio
    async def test_graphql_commitment_breakdown_query(self, mock_investor_client, mock_commitment_client, mock_asset_class_client):
        """Test GraphQL commitment breakdown query."""
        with patch('app.schema.commitments.get_investor_client', return_value=mock_investor_client), \
                patch('app.schema.commitments.get_commitment_client', return_value=mock_commitment_client), \
                patch('app.schema.commitments.get_asset_class_client', return_value=mock_asset_class_client):

            client = TestClient(app)

            query = """
            query {
                commitmentBreakdown(investorId: "inv-1") {
                    investorId
                    investorName
                    totalCommitmentAmount
                    commitments {
                        id
                        name
                        amount
                        percentage
                    }
                    assets {
                        id
                        name
                    }
                }
            }
            """

            response = client.post("/graphql", json={"query": query})
            assert response.status_code == 200

            data = response.json()["data"]["commitmentBreakdown"]
            assert data["investorId"] == "inv-1"
            assert data["totalCommitmentAmount"] == 1500000.0
            assert len(data["commitments"]) == 2
            assert len(data["assets"]) == 2
