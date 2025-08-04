"""
Bank Statement Routes - Processing endpoints for bank statements
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from src.api.controllers.bank_statement_controller import BankStatementController
from src.api.schemas.responses import APIResponse
from src.api.middleware.auth import verify_api_key

router = APIRouter(prefix="/api", tags=["Bank Statement"])

@router.post("/process", response_model=APIResponse)
async def process(
    file: UploadFile = File(...),
    customer_id: Optional[str] = Form(None),
    api_key: str = Depends(verify_api_key)
):
    return await BankStatementController.process_file_async(file, customer_id)
