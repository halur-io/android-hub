import re
import json
from datetime import datetime
from flask import current_app

class MenuParser:
    def __init__(self):
        self.categories_mapping = {
            'ראשונות': {'name_he': 'ראשונות', 'name_en': 'Appetizers', 'icon': 'fas fa-utensils', 'color': '#28a745'},
            'ווק': {'name_he': 'ווק', 'name_en': 'Wok Dishes', 'icon': 'fas fa-fire', 'color': '#dc3545'},
            'יקיטורי': {'name_he': 'יקיטורי', 'name_en': 'Yakitori', 'icon': 'fas fa-drumstick-bite', 'color': '#fd7e14'},
            'באנים': {'name_he': 'באנים', 'name_en': 'Buns', 'icon': 'fas fa-hamburger', 'color': '#6f42c1'},
            'ארוחות ילדים': {'name_he': 'ארוחות ילדים', 'name_en': 'Kids Meals', 'icon': 'fas fa-child', 'color': '#20c997'},
            'קינוחים': {'name_he': 'קינוחים', 'name_en': 'Desserts', 'icon': 'fas fa-ice-cream', 'color': '#e83e8c'},
            'שתייה חמה': {'name_he': 'שתייה חמה', 'name_en': 'Hot Drinks', 'icon': 'fas fa-mug-hot', 'color': '#6c757d'},
            'שתייה קלה': {'name_he': 'שתייה קלה', 'name_en': 'Soft Drinks', 'icon': 'fas fa-glass', 'color': '#17a2b8'}
        }
    
    def parse_word_menu(self, content, branch_id, uploaded_by=None):
        """Parse Word document menu content and return structured data"""
        try:
            # Split content into lines and clean up
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            categories = {}
            current_category = None
            current_items = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Check if this is a category header
                if line in self.categories_mapping:
                    # Save previous category if exists
                    if current_category and current_items:
                        categories[current_category] = current_items
                    
                    current_category = line
                    current_items = []
                    i += 1
                    continue
                
                # Skip empty lines and decorative lines
                if not line or line.count('־') > 5:
                    i += 1
                    continue
                
                # Try to parse menu item (price + name pattern)
                if current_category:
                    item_data = self._parse_menu_item(lines, i)
                    if item_data:
                        current_items.append(item_data)
                        i = item_data['next_index']
                        continue
                
                i += 1
            
            # Add final category
            if current_category and current_items:
                categories[current_category] = current_items
            
            return {
                'categories': categories,
                'total_items': sum(len(items) for items in categories.values()),
                'parsed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error parsing menu: {str(e)}")
            raise e
    
    def _parse_menu_item(self, lines, start_index):
        """Parse a single menu item starting from the given line index"""
        if start_index >= len(lines):
            return None
        
        line = lines[start_index].strip()
        
        # Look for price pattern at the beginning of the line
        # Pattern: number(s) followed by dish name
        price_pattern = r'^(\d+(?:/\d+)?)\s+(.+)$'
        match = re.match(price_pattern, line)
        
        if not match:
            return None
        
        prices_str = match.group(1)
        dish_name = match.group(2).strip()
        
        # Parse prices (could be single price or multiple like "56/62")
        prices = [int(p.strip()) for p in prices_str.split('/')]
        
        # Look for ingredients/description in next line(s)
        ingredients = ""
        next_index = start_index + 1
        
        # Keep looking for ingredient lines until we hit another item or category
        while next_index < len(lines):
            next_line = lines[next_index].strip()
            
            # Stop if we hit another price pattern or category
            if re.match(r'^\d+(?:/\d+)?\s+', next_line) or next_line in self.categories_mapping:
                break
            
            # Stop if line looks like section break or empty
            if not next_line or next_line.count('־') > 5:
                next_index += 1
                break
            
            # This looks like ingredients
            if ingredients:
                ingredients += " "
            ingredients += next_line
            next_index += 1
        
        return {
            'name_he': dish_name,
            'name_en': self._transliterate_dish_name(dish_name),
            'prices': prices,
            'ingredients_he': ingredients,
            'ingredients_en': '',  # Could add translation later
            'next_index': next_index
        }
    
    def _transliterate_dish_name(self, hebrew_name):
        """Simple transliteration helper - could be enhanced"""
        transliterations = {
            'הביס היפני': 'Japanese Hibis',
            'סלט טרופי': 'Tropical Salad',
            'קימצ\'י קוריאני': 'Korean Kimchi',
            'סלט ויאטנמי': 'Vietnamese Salad',
            'חמוצים יפנים': 'Japanese Pickles',
            'הקיסר האסייתי': 'Asian Caesar',
            'אדממה של סומו': 'Sumo Edamame',
            'קריספי רייס': 'Crispy Rice',
            'אגרול ירקות': 'Vegetable Spring Roll',
            'אגרול עוף': 'Chicken Spring Roll',
            'נאמס ירקות': 'Vegetable Nems',
            'נאמס עוף': 'Chicken Nems',
            'שרימפס פינגרז': 'Shrimp Fingers',
            'טטאקי סינטה כבושה': 'Pickled Cinta Tataki',
            'קלמארי פריך': 'Crispy Calamari',
            'פופ שרימפס': 'Pop Shrimp',
            'סמוקי': 'Smoky',
            'פאד תאי': 'Pad Thai',
            'תאילנד הירוקה': 'Green Thailand',
            'ים השחור': 'Black Sea',
            'עוף קשיו': 'Cashew Chicken',
            'פרייד רייס': 'Fried Rice',
            'החריפה': 'The Spicy One',
            'יקיטורי עגל': 'Beef Yakitori',
            'יקיטורי סלמון': 'Salmon Yakitori',
            'יקיטורי עוף': 'Chicken Yakitori',
            'יקיטורי שרימפס': 'Shrimp Yakitori',
            'יקטורי דג לבן': 'White Fish Yakitori',
            'ביף באן': 'Beef Bun',
            'קריספי שרימפס באן': 'Crispy Shrimp Bun',
            'סיי באן': 'Say Bun',
            'מוקפץ ילדים': 'Kids Stir Fry',
            'באן שניצל': 'Schnitzel Bun',
            'הוט דוג קוריאני': 'Korean Hot Dog'
        }
        
        return transliterations.get(hebrew_name, hebrew_name)
    
    def store_menu_items(self, parsed_data, branch_id, uploaded_by=None):
        """Store parsed menu items in the database"""
        from database import db
        from models import MenuCategory, MenuItem, MenuItemPrice
        
        try:
            items_added = 0
            categories_added = 0
            
            for category_name_he, items in parsed_data['categories'].items():
                # Get or create category
                category = MenuCategory.query.filter_by(name_he=category_name_he).first()
                if not category:
                    category_info = self.categories_mapping.get(category_name_he, {})
                    category = MenuCategory(
                        name_he=category_name_he,
                        name_en=category_info.get('name_en', category_name_he),
                        icon=category_info.get('icon', 'fas fa-utensils'),
                        color=category_info.get('color', '#007bff'),
                        display_order=categories_added,
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.flush()  # Get the ID
                    categories_added += 1
                
                # Add items to category
                for item_data in items:
                    # Check if item already exists
                    existing_item = MenuItem.query.filter_by(
                        name_he=item_data['name_he'],
                        category_id=category.id
                    ).first()
                    
                    if existing_item:
                        current_app.logger.info(f"Item already exists: {item_data['name_he']}")
                        continue
                    
                    # Create menu item
                    menu_item = MenuItem(
                        category_id=category.id,
                        name_he=item_data['name_he'],
                        name_en=item_data['name_en'],
                        ingredients_he=item_data['ingredients_he'],
                        ingredients_en=item_data['ingredients_en'],
                        base_price=item_data['prices'][0] if item_data['prices'] else 0,
                        is_available=True,
                        display_order=items_added
                    )
                    
                    db.session.add(menu_item)
                    db.session.flush()  # Get the ID
                    
                    # Add price options if multiple prices
                    if len(item_data['prices']) > 1:
                        size_names = ['קטן', 'רגיל', 'גדול', 'ענק']
                        size_names_en = ['Small', 'Regular', 'Large', 'Extra Large']
                        
                        for i, price in enumerate(item_data['prices']):
                            size_name_he = size_names[i] if i < len(size_names) else f'גודל {i+1}'
                            size_name_en = size_names_en[i] if i < len(size_names_en) else f'Size {i+1}'
                            
                            menu_price = MenuItemPrice(
                                menu_item_id=menu_item.id,
                                size_name_he=size_name_he,
                                size_name_en=size_name_en,
                                price=price,
                                is_default=(i == 0),
                                display_order=i
                            )
                            db.session.add(menu_price)
                    
                    items_added += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'items_added': items_added,
                'categories_added': categories_added
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error storing menu items: {str(e)}")
            raise e
    
    def process_word_menu(self, content, branch_id, uploaded_by=None):
        """Complete processing workflow for Word menu"""
        try:
            # Parse the content
            parsed_data = self.parse_word_menu(content, branch_id, uploaded_by)
            
            # Store in database
            result = self.store_menu_items(parsed_data, branch_id, uploaded_by)
            
            return {
                'success': True,
                'parsed_items': parsed_data['total_items'],
                'items_added': result['items_added'],
                'categories_added': result['categories_added'],
                'categories': list(parsed_data['categories'].keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }