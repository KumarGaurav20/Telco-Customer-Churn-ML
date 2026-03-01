import pandas as pd
from typing import Tuple, List

# -----------------------------
# Helper validation functions
# -----------------------------
def column_exists(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns

def column_not_null(df: pd.DataFrame, col: str) -> bool:
    return df[col].notnull().all()

def values_in_set(df: pd.DataFrame, col: str, valid_set: list) -> bool:
    return df[col].isin(valid_set).all()

def values_between(df: pd.DataFrame, col: str, min_value=None, max_value=None) -> bool:
    s = df[col]
    if min_value is not None:
        s = s[s >= min_value]
    if max_value is not None:
        s = s[s <= max_value]
    return len(s) == len(df)

def column_pair_greater_equal(df: pd.DataFrame, col_A, col_B, mostly=1.0) -> bool:
    comparison = df[col_A] >= df[col_B]
    return comparison.mean() >= mostly

# -----------------------------
# Main validation function
# -----------------------------
def validate_telco_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Comprehensive data validation for Telco Customer Churn dataset.
    Implements schema, business logic, numeric range, and consistency checks.
    """
    print("🔍 Starting data validation...")

    failed_checks = []

    # -----------------------------
    # Convert numeric columns safely
    # -----------------------------
    for col in ["tenure", "MonthlyCharges", "TotalCharges"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill blank TotalCharges for new customers (tenure = 0)
    if "TotalCharges" in df.columns and "tenure" in df.columns:
        df.loc[df["tenure"] == 0, "TotalCharges"] = 0

    # === SCHEMA VALIDATION ===
    required_cols = [
        "customerID", "gender", "Partner", "Dependents",
        "PhoneService", "InternetService", "Contract",
        "tenure", "MonthlyCharges", "TotalCharges"
    ]
    for col in required_cols:
        if not column_exists(df, col):
            failed_checks.append(f"{col}_missing")
        elif not column_not_null(df, col):
            failed_checks.append(f"{col}_nulls")

    # === BUSINESS LOGIC VALIDATION ===
    if "gender" in df.columns and not values_in_set(df, "gender", ["Male", "Female"]):
        failed_checks.append("gender_invalid")
    
    for col in ["Partner", "Dependents", "PhoneService"]:
        if col in df.columns and not values_in_set(df, col, ["Yes", "No"]):
            failed_checks.append(f"{col}_invalid")

    if "Contract" in df.columns and not values_in_set(df, "Contract", ["Month-to-month", "One year", "Two year"]):
        failed_checks.append("Contract_invalid")

    if "InternetService" in df.columns and not values_in_set(df, "InternetService", ["DSL", "Fiber optic", "No"]):
        failed_checks.append("InternetService_invalid")

    # === NUMERIC RANGE VALIDATION ===
    numeric_checks = [
        ("tenure", 0, 120),
        ("MonthlyCharges", 0, 200),
        ("TotalCharges", 0, None)
    ]
    for col, min_val, max_val in numeric_checks:
        if col in df.columns and not values_between(df, col, min_val, max_val):
            failed_checks.append(f"{col}_out_of_range")

    # === DATA CONSISTENCY CHECKS ===
    if "TotalCharges" in df.columns and "MonthlyCharges" in df.columns:
        if not column_pair_greater_equal(df, "TotalCharges", "MonthlyCharges", mostly=0.95):
            failed_checks.append("TotalCharges_lt_MonthlyCharges")

    success = len(failed_checks) == 0

    if success:
        print(f"✅ Data validation PASSED")
    else:
        print(f"❌ Data validation FAILED, issues: {failed_checks}")

    return success, failed_checks