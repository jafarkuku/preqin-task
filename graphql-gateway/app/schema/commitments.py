"""
Updated GraphQL Schema with Commitment Breakdown Focus.
"""
import asyncio
import logging
from typing import List, Optional

import strawberry

from app.services import (get_asset_class_client, get_commitment_client,
                          get_investor_client)
from app.services.commitment_service import CommitmentData
from app.utils.validator import safe_response

logger = logging.getLogger(__name__)


@strawberry.type
class AssetSummary:
    """Summary of an asset class used in commitments."""
    id: str
    name: str
    total_commitment_amount: float
    commitment_count: int
    percentage_of_total: float


@strawberry.type
class CommitmentDetail:
    """Individual commitment with asset class details."""
    id: str
    asset_class_id: str
    name: str
    amount: float
    currency: str
    percentage: float
    created_at: str


@strawberry.type
class CommitmentBreakdown:
    """Complete commitment breakdown for an investor."""
    investor_id: str
    investor_name: str
    assets: List[AssetSummary]
    total_commitment_amount: float
    commitments: List[CommitmentDetail]


@strawberry.type
class CommitmentQueries:
    """Commitment-related GraphQL queries."""

    @strawberry.field
    async def commitment_breakdown(
        self,
        investor_id: str,
        asset_class_id: Optional[str] = None
    ) -> Optional[CommitmentBreakdown]:
        """
        Get detailed commitment breakdown for a specific investor.

        Now uses the optimized commitment service that includes asset breakdowns.
        Can optionally filter by asset class.

        Args:
            investor_id: Investor identifier
            asset_class_id: Optional asset class filter

        Returns:
            CommitmentBreakdown with detailed commitment list and asset summaries
        """
        try:
            logger.info(
                "Fetching commitment breakdown for investor: %s, asset_class: %s",
                investor_id, asset_class_id or "all"
            )

            commitment_client = get_commitment_client()
            asset_class_client = get_asset_class_client()
            investor_client = get_investor_client()

            commitment_params = {"investor_id": investor_id}
            if asset_class_id:
                commitment_params["asset_class_id"] = asset_class_id

            results = await asyncio.gather(
                commitment_client.get_commitments(**commitment_params),
                investor_client.get_investor(investor_id),
                return_exceptions=True
            )

            commitments_result, investor_result = results

            commitments_response = safe_response(
                commitments_result, "commitment", None)
            investor_data = safe_response(investor_result, "investor", None)

            if not investor_data:
                logger.warning("Investor not found: %s", investor_id)
                return None

            if commitments_response is None:
                logger.info(
                    "No commitments found for investor: %s", investor_id)
                return CommitmentBreakdown(
                    investor_id=investor_id,
                    investor_name=investor_data['name'],
                    total_commitment_amount=0.0,
                    commitments=[],
                    assets=[]
                )

            commitments_data: List[CommitmentData] = commitments_response.get(
                "commitments", [])
            asset_breakdowns_data = commitments_response.get(
                "asset_breakdowns", [])
            total_amount = commitments_response.get("total_amount", 0.0)

            if not commitments_data:
                logger.info(
                    "No commitments found for investor: %s", investor_id)
                return CommitmentBreakdown(
                    investor_id=investor_id,
                    investor_name=investor_data['name'],
                    total_commitment_amount=0.0,
                    commitments=[],
                    assets=[]
                )

            asset_class_result = await asset_class_client.get_all_asset_classes()

            asset_class_names = {
                ac["id"]: ac["name"] for ac in asset_class_result
            }

            commitment_details = []
            for commitment in commitments_data:
                asset_class_name = asset_class_names.get(
                    commitment["asset_class_id"],
                    f"Unknown Asset Class ({commitment['asset_class_id']})"
                )

                percentage = (
                    commitment["amount"] / total_amount * 100) if total_amount > 0 else 0

                detail = CommitmentDetail(
                    id=commitment["id"],
                    asset_class_id=commitment["asset_class_id"],
                    name=asset_class_name,
                    amount=commitment["amount"],
                    currency=commitment["currency"],
                    percentage=round(percentage, 2),
                    created_at=commitment["created_at"]
                )
                commitment_details.append(detail)

            commitment_details.sort(key=lambda x: x.amount, reverse=True)

            enhanced_assets = []
            for asset_breakdown in asset_breakdowns_data:
                asset_name = asset_class_names.get(
                    asset_breakdown["asset_class_id"],
                    f"Unknown Asset Class ({asset_breakdown['asset_class_id']})"
                )

                asset_summary = AssetSummary(
                    id=asset_breakdown["asset_class_id"],
                    name=asset_name,
                    total_commitment_amount=asset_breakdown["total_amount"],
                    commitment_count=asset_breakdown["commitment_count"],
                    percentage_of_total=asset_breakdown["percentage_of_total"]
                )
                enhanced_assets.append(asset_summary)

            breakdown = CommitmentBreakdown(
                investor_id=investor_id,
                investor_name=investor_data["name"],
                total_commitment_amount=total_amount,
                commitments=commitment_details,
                assets=enhanced_assets
            )

            logger.info(
                "Successfully created commitment breakdown for %s with %d commitments (total: %.2f) across %d assets",
                investor_data["name"], len(
                    commitment_details), total_amount, len(enhanced_assets)
            )

            return breakdown

        except Exception as e:
            logger.error(
                "Error fetching commitment breakdown for investor %s: %s", investor_id, e)
            return None
