"""
CSV parsing utilities for ingestion service.

Handles parsing CSV data and extracting unique entities.
"""

import logging
from typing import Dict, List, Tuple, TypedDict

import pandas as pd

logger = logging.getLogger(__name__)


class CommitmentData(TypedDict):
    """Shape of commitment data used for creating commitments."""
    investor_name: str
    asset_class_name: str
    amount: float
    currency: str


class CSVParser:
    """Handles parsing CSV data into structured entities."""

    @staticmethod
    def parse_csv_data(df: pd.DataFrame) -> Tuple[Dict, Dict, List]:
        """
        Parse CSV DataFrame and extract unique entities efficiently.

        Args:
            df: Pandas DataFrame from CSV

        Returns:
            Tuple of (unique_investors, unique_asset_classes, commitments_data)
        """
        logger.info("Parsing CSV data: %d rows", len(df))

        unique_investors = {}
        unique_asset_classes = {}
        commitments_data = []

        for _, row in df.iterrows():
            investor_name = row['Investor Name'].strip()
            if investor_name not in unique_investors:
                unique_investors[investor_name] = {
                    'name': investor_name,
                    'investor_type': row['Investory Type'].strip(),
                    'country': row['Investor Country'].strip(),
                    'date_added': row['Investor Date Added'].strip()
                }

            asset_class_name = row['Commitment Asset Class'].strip()
            if asset_class_name not in unique_asset_classes:
                unique_asset_classes[asset_class_name] = {
                    'name': asset_class_name,
                    'description': f"{asset_class_name} investment opportunities",
                    'status': 'active'
                }

            amount = float(row['Commitment Amount'])
            if amount > 0:
                commitments_data.append({
                    'investor_name': investor_name,
                    'asset_class_name': asset_class_name,
                    'amount': amount,
                    'currency': row['Commitment Currency'].strip()
                })
            else:
                logger.warning("Skipping commitment with zero/negative amount: %s -> %s, amount: %s",
                               investor_name, asset_class_name, amount)

        logger.info("Parsed: %d unique investors, %d unique asset classes, %d valid commitments",
                    len(unique_investors), len(unique_asset_classes), len(commitments_data))

        return unique_investors, unique_asset_classes, commitments_data

    @staticmethod
    def validate_csv_structure(df: pd.DataFrame) -> bool:
        """
        Validate that CSV has required columns.

        Args:
            df: Pandas DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        required_columns = [
            'Investor Name',
            'Investory Type',
            'Investor Country',
            'Investor Date Added',
            'Commitment Asset Class',
            'Commitment Amount',
            'Commitment Currency'
        ]

        missing_columns = [
            col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.error("CSV missing required columns: %s", missing_columns)
            return False

        logger.info("CSV structure validation passed")
        return True
