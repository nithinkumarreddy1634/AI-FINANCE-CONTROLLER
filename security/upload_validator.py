"""
Secure CSV Upload Validator
Validates file extension, size, column headers, and row limits before processing CSV files.
"""

import io
from typing import Tuple, List, Optional
import pandas as pd

class SecureUploadValidator:
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
    MAX_ROWS = 5000

    REQUIRED_HEADERS = {
        "orders": ["order_id", "customer_id", "order_date", "expected_amount"],
        "payments": ["payment_id", "order_id", "paid_amount"],
        "bank": ["bank_transaction_id", "received_amount"]
    }

    @classmethod
    def validate_csv_content(cls, file_bytes: bytes, file_type: str) -> Tuple[bool, Optional[str], Optional[pd.DataFrame]]:
        if len(file_bytes) > cls.MAX_FILE_SIZE_BYTES:
            return False, f"File size exceeds maximum allowed limit of 5MB ({len(file_bytes)} bytes).", None

        try:
            stream = io.BytesIO(file_bytes)
            df = pd.read_csv(stream)
        except Exception as e:
            return False, f"Unable to parse CSV file: {str(e)}", None

        if len(df) > cls.MAX_ROWS:
            return False, f"CSV contains {len(df)} rows, exceeding maximum limit of {cls.MAX_ROWS} rows.", None

        if file_type in cls.REQUIRED_HEADERS:
            missing = [h for h in cls.REQUIRED_HEADERS[file_type] if h not in df.columns]
            if missing:
                return False, f"Required column(s) missing for {file_type} CSV: {', '.join(missing)}.", None

        return True, None, df

