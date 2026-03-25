from pydantic import BaseModel, Field
from typing import List, Optional 

class LineItem(BaseModel):
    description: str
    amount: float

class ReceiptData(BaseModel):
    merchant_name: str = Field(description="Name of the store or service")
    date: str = Field(description="Date of the transaction in YYYY-MM-DD format")
    total_amount: float = Field(description="Total amount charged")
    currency: str = Field(description="Currency code, e.g., USD, EUR, INR")
    line_items: List[LineItem] = Field(description="List of individual items purchased")
    
    
    original_language: str = Field(description="The primary language detected on the receipt")
    needs_translation: bool = Field(description="True if the receipt was not in English")