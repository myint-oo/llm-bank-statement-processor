"""
Response models define what data our API sends back to Laravel
Laravel will receive these exact JSON structures
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransactionResponse(BaseModel):
    """
    Individual transaction data that Laravel will receive
    """
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    description: str = Field(..., description="Transaction description")
    debit: Optional[float] = Field(None, description="Debit amount (money withdrawn)")
    credit: Optional[float] = Field(None, description="Credit amount (money deposited)")
    balance: float = Field(..., description="Account balance after transaction")
    note: Optional[str] = Field(None, description="Additional notes")

class AccountResponse(BaseModel):
    """
    Account data with all transactions
    """
    account_number: str = Field(..., description="Bank account number")
    account_name: str = Field(..., description="Account holder name")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")
    opening_balance: float = Field(..., description="Opening balance for the period")
    closing_balance: float = Field(..., description="Closing balance for the period")
    transactions: List[TransactionResponse] = Field(..., description="List of all transactions")

class StatementPeriodResponse(BaseModel):
    """
    Statement period information
    """
    start_date: str = Field(..., description="Statement start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="Statement end date in YYYY-MM-DD format")

class BankStatementResponse(BaseModel):
    """
    Complete bank statement data that Laravel will receive
    This is the main response from our processing endpoint
    """
    bank_name: str = Field(..., description="Name of the bank")
    statement_period: StatementPeriodResponse = Field(..., description="Statement period")
    accounts: List[AccountResponse] = Field(..., description="List of accounts and transactions")
    
    # Metadata for Laravel
    processed_at: datetime = Field(default_factory=datetime.now, description="When processing completed")
    processing_time_seconds: Optional[float] = Field(None, description="How long processing took")

class APIResponse(BaseModel):
    """
    Standard API response wrapper
    All our endpoints will use this format so Laravel knows what to expect
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="The actual response data")
    error: Optional[str] = Field(None, description="Error message if success=false")

class HealthResponse(BaseModel):
    """
    Health check response for monitoring
    """
    status: str = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether AI model is ready")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """
    Error response format
    """
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
