"""
PII (Personally Identifiable Information) Masking
Detects and masks sensitive information in data
"""

import os
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Load environment variables
load_dotenv()


class PIIMasker:
    """PII Detection and Masking using Presidio"""

    def __init__(self):
        """Initialize PII analyzer and anonymizer"""
        self.enabled = os.getenv("PII_MASKING_ENABLED", "true").lower() == "true"
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Masking operators configuration
        self.operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "[PERSON_NAME]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CREDIT_CARD]"}),
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[IP_ADDRESS]"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "[ADDRESS]"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATE]"}),
        }

    def mask_text(self, text: str) -> str:
        """
        Detect and mask PII in text

        Args:
            text: Input text

        Returns:
            Masked text
        """
        if not self.enabled or not text:
            return text

        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text, entities=list(self.operators.keys()), language="en"
            )

            if not results:
                return text

            # Anonymize detected PII
            masked_text = self.anonymizer.anonymize(
                text=text, analyzer_results=results, operators=self.operators
            )

            return masked_text.text
        except Exception as e:
            print(f"Error in PII masking: {e}")
            return text

    def mask_dataframe(
        self, df, columns: Optional[List[str]] = None
    ):
        """
        Mask PII in pandas DataFrame

        Args:
            df: Input DataFrame
            columns: Specific columns to mask (if None, mask all object columns)

        Returns:
            DataFrame with masked PII
        """
        if not self.enabled or df is None or df.empty:
            return df

        import pandas as pd

        df_copy = df.copy()

        # Determine columns to mask
        if columns is None:
            columns = df_copy.select_dtypes(include=["object"]).columns.tolist()

        # Mask each column
        for col in columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(
                    lambda x: self.mask_text(str(x)) if pd.notna(x) else x
                )

        return df_copy

    def mask_dict(self, data: Dict) -> Dict:
        """
        Mask PII in dictionary

        Args:
            data: Input dictionary

        Returns:
            Dictionary with masked PII
        """
        if not self.enabled or not data:
            return data

        masked_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self.mask_text(value)
            else:
                masked_data[key] = value

        return masked_data

    def analyze_pii(self, text: str) -> List[Dict]:
        """
        Analyze text and return detected PII entities

        Args:
            text: Input text

        Returns:
            List of detected PII entities with details
        """
        if not text:
            return []

        try:
            results = self.analyzer.analyze(
                text=text, entities=list(self.operators.keys()), language="en"
            )

            detected_entities = []
            for result in results:
                detected_entities.append(
                    {
                        "entity_type": result.entity_type,
                        "start": result.start,
                        "end": result.end,
                        "text": text[result.start : result.end],
                        "score": result.score,
                    }
                )

            return detected_entities
        except Exception as e:
            print(f"Error in PII analysis: {e}")
            return []


# Global PII masker instance
_pii_masker: Optional[PIIMasker] = None


def get_pii_masker() -> PIIMasker:
    """Get or create the global PII masker instance"""
    global _pii_masker
    if _pii_masker is None:
        _pii_masker = PIIMasker()
    return _pii_masker
