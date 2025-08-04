"""
Request models define what data Laravel needs to send to our API
These use Pydantic for automatic validation
"""
from pydantic import BaseModel, Field
from typing import Optional

class ProcessBankStatementRequest(BaseModel):
    """
    When Laravel wants to process a bank statement, it can send this data
    """
    # Optional: if Laravel wants to send text directly instead of a file
    text_content: Optional[str] = Field(None, description="Raw text content of the bank statement")
    
    # Optional: metadata Laravel might want to include
    customer_id: Optional[str] = Field(None, description="Customer identifier from Laravel")
    statement_type: Optional[str] = Field(None, description="Type of statement being processed")
    
    class Config:
        # Example of what Laravel would send
        schema_extra = {
            "example": {
                "text_content": "BANK STATEMENT\nDate: 01/01/2024...",
                "customer_id": "CUST123",
                "statement_type": "monthly"
            }
        }
