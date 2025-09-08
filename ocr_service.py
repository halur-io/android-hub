"""
OCR Service for Receipt Processing
Handles image text extraction and receipt data parsing
"""

import os
import re
import json
from PIL import Image
import pytesseract
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

class ReceiptOCRService:
    """Service for processing receipt images and extracting structured data"""
    
    def __init__(self):
        # Configure tesseract for Hebrew and English
        self.config = '--oem 3 --psm 6 -l heb+eng'
        
        # Common receipt patterns (Hebrew and English)
        self.patterns = {
            'total_amount': [
                r'סה״כ\s*:?\s*(\d+\.?\d*)',
                r'סכום\s*:?\s*(\d+\.?\d*)',
                r'total\s*:?\s*(\d+\.?\d*)',
                r'sum\s*:?\s*(\d+\.?\d*)',
                r'₪\s*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*₪'
            ],
            'tax_amount': [
                r'מע״מ\s*:?\s*(\d+\.?\d*)',
                r'vat\s*:?\s*(\d+\.?\d*)',
                r'tax\s*:?\s*(\d+\.?\d*)'
            ],
            'receipt_number': [
                r'קבלה\s*#?\s*(\d+)',
                r'receipt\s*#?\s*(\d+)',
                r'inv\s*#?\s*(\d+)',
                r'מספר\s*:?\s*(\d+)'
            ],
            'date': [
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'(\d{1,2}\.\d{1,2}\.\d{2,4})',
                r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})'
            ],
            'phone': [
                r'(\d{2,3}[\-\s]?\d{7})',
                r'(\d{10})',
                r'0\d{1,2}[\-\s]?\d{7}'
            ]
        }
        
        # Common units in Hebrew and English
        self.units = ['יח', 'ק"ג', 'ליטר', 'גרם', 'pc', 'kg', 'liter', 'gram', 'pcs', 'unit']
        
        # Hebrew months mapping
        self.hebrew_months = {
            'ינואר': 1, 'פברואר': 2, 'מרץ': 3, 'אפריל': 4, 'מאי': 5, 'יוני': 6,
            'יולי': 7, 'אוגוסט': 8, 'ספטמבר': 9, 'אוקטובר': 10, 'נובמבר': 11, 'דצמבר': 12
        }

    def process_receipt_image(self, image_path: str) -> Dict:
        """
        Main function to process a receipt image and extract structured data
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            Dictionary containing extracted receipt data
        """
        try:
            # Load and preprocess image
            image = self._preprocess_image(image_path)
            
            # Extract text using OCR
            raw_text = pytesseract.image_to_string(image, config=self.config)
            
            # Clean and normalize text
            cleaned_text = self._clean_text(raw_text)
            
            # Extract structured data
            receipt_data = self._extract_receipt_data(cleaned_text)
            
            # Extract line items
            items = self._extract_line_items(cleaned_text)
            receipt_data['items'] = items
            
            # Calculate confidence score
            confidence = self._calculate_confidence(receipt_data, cleaned_text)
            receipt_data['confidence'] = confidence
            
            # Add raw OCR data for debugging
            receipt_data['raw_text'] = raw_text
            receipt_data['cleaned_text'] = cleaned_text
            
            return {
                'status': 'success',
                'data': receipt_data,
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'data': {},
                'confidence': 0.0
            }

    def _preprocess_image(self, image_path: str) -> Image.Image:
        """Preprocess image for better OCR results"""
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small
        width, height = image.size
        if width < 800 or height < 600:
            scale_factor = max(800/width, 600/height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image

    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might confuse parsing
        text = re.sub(r'[^\w\s\d\.\-\/\:₪,]', ' ', text)
        
        # Normalize common OCR mistakes
        replacements = {
            'o': '0',  # Common OCR mistake
            'O': '0',
            'l': '1',
            'I': '1'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()

    def _extract_receipt_data(self, text: str) -> Dict:
        """Extract structured data from receipt text"""
        data = {}
        
        # Extract total amount
        total = self._extract_by_patterns('total_amount', text)
        if total:
            data['total_amount'] = float(total)
        
        # Extract tax amount
        tax = self._extract_by_patterns('tax_amount', text)
        if tax:
            data['tax_amount'] = float(tax)
        
        # Extract receipt number
        receipt_num = self._extract_by_patterns('receipt_number', text)
        if receipt_num:
            data['receipt_number'] = receipt_num
        
        # Extract date
        date_str = self._extract_by_patterns('date', text)
        if date_str:
            parsed_date = self._parse_date(date_str)
            if parsed_date:
                data['receipt_date'] = parsed_date.isoformat()
        
        # Extract phone number (to help identify supplier)
        phone = self._extract_by_patterns('phone', text)
        if phone:
            data['supplier_phone'] = phone
        
        return data

    def _extract_by_patterns(self, pattern_type: str, text: str) -> Optional[str]:
        """Extract data using predefined patterns"""
        patterns = self.patterns.get(pattern_type, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse various date formats"""
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%d/%m/%y', '%d-%m-%y', '%d.%m.%y',
            '%Y/%m/%d', '%Y-%m-%d', '%Y.%m.%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None

    def _extract_line_items(self, text: str) -> List[Dict]:
        """Extract individual line items from receipt"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Look for lines with prices (containing numbers and currency)
            if re.search(r'\d+\.?\d*\s*₪|\d+\.?\d*$', line):
                item = self._parse_line_item(line)
                if item:
                    items.append(item)
        
        return items

    def _parse_line_item(self, line: str) -> Optional[Dict]:
        """Parse a single line item"""
        # Pattern to match: [description] [quantity] [unit] [price]
        # Example: "חלב תנובה 1 ליטר 6.50" or "Milk 1 liter 6.50₪"
        
        # Extract price (last number in the line)
        price_match = re.search(r'(\d+\.?\d*)\s*₪?$', line)
        if not price_match:
            return None
        
        price = float(price_match.group(1))
        
        # Remove price from line to get description and quantity
        description_part = line[:price_match.start()].strip()
        
        # Try to extract quantity and unit
        quantity = 1.0
        unit = 'יח'
        
        # Look for quantity pattern: number followed by unit
        qty_pattern = r'(\d+\.?\d*)\s*(' + '|'.join(self.units) + r')'
        qty_match = re.search(qty_pattern, description_part, re.IGNORECASE)
        
        if qty_match:
            quantity = float(qty_match.group(1))
            unit = qty_match.group(2)
            # Remove quantity and unit from description
            description_part = description_part[:qty_match.start()].strip()
        
        # Calculate unit price
        unit_price = price / quantity if quantity > 0 else price
        
        return {
            'description': description_part,
            'quantity': quantity,
            'unit': unit,
            'unit_price': unit_price,
            'total_price': price
        }

    def _calculate_confidence(self, data: Dict, text: str) -> float:
        """Calculate confidence score based on extracted data quality"""
        confidence = 0.0
        max_score = 100.0
        
        # Basic text quality (20 points)
        if len(text) > 50:
            confidence += 20
        elif len(text) > 20:
            confidence += 10
        
        # Total amount found (25 points)
        if 'total_amount' in data and data['total_amount'] > 0:
            confidence += 25
        
        # Receipt number found (15 points)
        if 'receipt_number' in data:
            confidence += 15
        
        # Date found (15 points)
        if 'receipt_date' in data:
            confidence += 15
        
        # Items found (25 points)
        items = data.get('items', [])
        if items:
            confidence += min(25, len(items) * 5)
        
        return min(confidence / max_score, 1.0)

    def match_items_to_stock(self, receipt_items: List[Dict], stock_items: List) -> List[Dict]:
        """
        Match receipt items to existing stock items using fuzzy matching
        
        Args:
            receipt_items: List of items extracted from receipt
            stock_items: List of stock items from database
            
        Returns:
            List of receipt items with stock item matches
        """
        matched_items = []
        
        for receipt_item in receipt_items:
            description = receipt_item['description'].lower()
            best_match = None
            best_score = 0.0
            
            for stock_item in stock_items:
                # Check Hebrew and English names
                names_to_check = [
                    stock_item.name_he.lower() if stock_item.name_he else '',
                    stock_item.name_en.lower() if stock_item.name_en else ''
                ]
                
                for name in names_to_check:
                    if name:
                        score = self._calculate_similarity(description, name)
                        if score > best_score and score > 0.6:  # Minimum similarity threshold
                            best_score = score
                            best_match = stock_item
            
            # Add match information to receipt item
            receipt_item['stock_match'] = {
                'stock_item_id': best_match.id if best_match else None,
                'stock_item_name': best_match.name_he if best_match else None,
                'confidence': best_score
            }
            
            matched_items.append(receipt_item)
        
        return matched_items

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word matching"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def create_stock_entries_from_receipt(self, receipt_items: List[Dict], branch_id: int, supplier_id: int = None) -> List[Dict]:
        """
        Create stock transaction entries from receipt items
        
        Args:
            receipt_items: List of matched receipt items
            branch_id: Branch ID for stock transactions
            supplier_id: Supplier ID if known
            
        Returns:
            List of stock transaction data ready for database insertion
        """
        transactions = []
        
        for item in receipt_items:
            stock_match = item.get('stock_match', {})
            stock_item_id = stock_match.get('stock_item_id')
            
            if stock_item_id and stock_match.get('confidence', 0) > 0.7:
                transaction = {
                    'stock_item_id': stock_item_id,
                    'branch_id': branch_id,
                    'transaction_type': 'stock_in',
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'total_price': item['total_price'],
                    'supplier_id': supplier_id,
                    'notes': f"Auto-imported from receipt: {item['description']}",
                    'confidence': stock_match['confidence']
                }
                transactions.append(transaction)
        
        return transactions