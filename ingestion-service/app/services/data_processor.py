"""
Cleaned up batch processor for ingestion service.

Coordinates between specialized managers with minimal, focused logging.
"""

import logging
from typing import Any

import httpx
import pandas as pd

from app.config import settings

from .asset_class_manager import AssetClassManager
from .commitment_manager import CommitmentManager
from .csv_parser import CSVParser
from .investor_manager import InvestorManager

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes the data using specialized managers.
    """

    def __init__(self) -> None:
        """Initialize HTTP client and specialized managers."""
        self.client = httpx.AsyncClient(timeout=60.0)

        # Initialize specialized managers
        self.asset_class_manager = AssetClassManager(
            self.client, settings.asset_class_service_url)
        self.investor_manager = InvestorManager(
            self.client, settings.investor_service_url)
        self.commitment_manager = CommitmentManager(
            self.client, settings.commitment_service_url)

        self.parser = CSVParser()

    async def process_dataframe(self, df: pd.DataFrame, job_id: str) -> dict[str, Any]:
        """
        Process entire DataFrame efficiently using specialized managers.
        """
        try:
            logger.info("Processing job %s: %d rows", job_id, len(df))

            if not self.parser.validate_csv_structure(df):
                return self._error_result(job_id, len(df), "Invalid CSV structure")

            investors, asset_classes, commitments = self.parser.parse_csv_data(
                df)

            logger.info("Parsed: %d investors, %d asset classes, %d commitments",
                        len(investors), len(asset_classes), len(commitments))

            asset_class_mapping = await self.asset_class_manager.bulk_create_asset_classes(asset_classes)

            if len(asset_class_mapping) == 0 and len(asset_classes) > 0:
                return self._error_result(job_id, len(df), "Failed to create asset classes")

            investor_mapping = await self.investor_manager.bulk_create_investors(investors)

            if len(investor_mapping) == 0 and len(investors) > 0:
                return self._error_result(
                    job_id, len(df), "Failed to create investors",
                    asset_classes_created=len(asset_class_mapping)
                )

            valid_commitments = self._count_valid_commitments(
                commitments, investor_mapping, asset_class_mapping
            )

            if valid_commitments == 0:
                return self._error_result(
                    job_id, len(df),
                    "No valid commitments: missing dependencies",
                    asset_classes_created=len(asset_class_mapping),
                    investors_created=len(investor_mapping)
                )

            commitment_count = await self.commitment_manager.bulk_create_commitments(
                commitments, investor_mapping, asset_class_mapping
            )

            success_rate = (commitment_count / len(commitments)
                            * 100) if commitments else 0

            asset_class_rate = f"{len(asset_class_mapping)}/{len(asset_classes)} ({len(asset_class_mapping) / len(asset_classes) * 100:.1f}%)" if asset_classes else "N/A"
            investor_rate = f"{len(investor_mapping)}/{len(investors)} ({len(investor_mapping) / len(investors) * 100:.1f}%)" if investors else "N/A"
            commitment_rate = f"{commitment_count}/{len(commitments)} ({success_rate:.1f}%)" if commitments else "N/A"

            result = {
                'job_id': job_id,
                'status': 'completed',
                'asset_classes_created': len(asset_class_mapping),
                'investors_created': len(investor_mapping),
                'commitments_created': commitment_count,
                'total_rows_processed': len(df),
                'success_rates': {
                    'asset_classes': asset_class_rate,
                    'investors': investor_rate,
                    'commitments': commitment_rate
                },
                'summary': {
                    'unique_investors_in_csv': len(investors),
                    'unique_asset_classes_in_csv': len(asset_classes),
                    'total_commitment_rows_in_csv': len(commitments),
                    'dependencies_valid': valid_commitments,
                    'dependencies_invalid': len(commitments) - valid_commitments
                }
            }

            logger.info("Job %s completed: Asset Classes: %s, Investors: %s, Commitments: %s",
                        job_id, asset_class_rate, investor_rate, commitment_rate)

            return result

        except Exception as e:
            logger.error("Error processing job %s: %s", job_id, e)
            return self._error_result(job_id, len(df) if df is not None else 0, str(e))
        finally:
            await self.client.aclose()

    def _error_result(
        self,
        job_id: str,
        total_rows: int,
        error_msg: str,
        asset_classes_created: int = 0,
        investors_created: int = 0,
        commitments_created: int = 0
    ) -> dict[str, Any]:
        """Create standardized error result."""
        return {
            'job_id': job_id,
            'status': 'failed',
            'error': error_msg,
            'asset_classes_created': asset_classes_created,
            'investors_created': investors_created,
            'commitments_created': commitments_created,
            'total_rows_processed': total_rows
        }

    def _count_valid_commitments(
        self,
        commitments: list[dict[str, Any]],
        investor_mapping: dict[str, str],
        asset_class_mapping: dict[str, str]
    ) -> int:
        """Count how many commitments have valid dependencies."""
        valid_count = 0

        for commitment in commitments:
            investor_name = commitment['investor_name']
            asset_class_name = commitment['asset_class_name']

            has_investor = investor_name in investor_mapping
            has_asset_class = asset_class_name in asset_class_mapping

            if has_investor and has_asset_class:
                valid_count += 1

        return valid_count
