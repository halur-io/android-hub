import re
import json
from datetime import datetime
from flask import current_app

class MenuParser:
    def __init__(self):
        # Extended and flexible category mapping
        self.categories_mapping = {
            'ראשונות': {'name_he': 'ראשונות', 'name_en': 'Appetizers', 'icon': 'fas fa-utensils', 'color': '#28a745'},
            'מנות ראשונות': {'name_he': 'מנות ראשונות', 'name_en': 'Appetizers', 'icon': 'fas fa-utensils', 'color': '#28a745'},
            'ווק': {'name_he': 'ווק', 'name_en': 'Wok Dishes', 'icon': 'fas fa-fire', 'color': '#dc3545'},
            'מוקפץ': {'name_he': 'מוקפץ', 'name_en': 'Wok Dishes', 'icon': 'fas fa-fire', 'color': '#dc3545'},
            'יקיטורי': {'name_he': 'יקיטורי', 'name_en': 'Yakitori', 'icon': 'fas fa-drumstick-bite', 'color': '#fd7e14'},
            'באנים': {'name_he': 'באנים', 'name_en': 'Buns', 'icon': 'fas fa-hamburger', 'color': '#6f42c1'},
            'לחמניות': {'name_he': 'לחמניות', 'name_en': 'Buns', 'icon': 'fas fa-hamburger', 'color': '#6f42c1'},
            'ארוחות ילדים': {'name_he': 'ארוחות ילדים', 'name_en': 'Kids Meals', 'icon': 'fas fa-child', 'color': '#20c997'},
            'ילדים': {'name_he': 'ילדים', 'name_en': 'Kids Meals', 'icon': 'fas fa-child', 'color': '#20c997'},
            'קינוחים': {'name_he': 'קינוחים', 'name_en': 'Desserts', 'icon': 'fas fa-ice-cream', 'color': '#e83e8c'},
            'מתוקים': {'name_he': 'מתוקים', 'name_en': 'Desserts', 'icon': 'fas fa-ice-cream', 'color': '#e83e8c'},
            'שתייה חמה': {'name_he': 'שתייה חמה', 'name_en': 'Hot Drinks', 'icon': 'fas fa-mug-hot', 'color': '#6c757d'},
            'חם': {'name_he': 'שתייה חמה', 'name_en': 'Hot Drinks', 'icon': 'fas fa-mug-hot', 'color': '#6c757d'},
            'שתייה קלה': {'name_he': 'שתייה קלה', 'name_en': 'Soft Drinks', 'icon': 'fas fa-glass', 'color': '#17a2b8'},
            'שתיה': {'name_he': 'שתיה', 'name_en': 'Drinks', 'icon': 'fas fa-glass', 'color': '#17a2b8'},
            'מנות עיקריות': {'name_he': 'מנות עיקריות', 'name_en': 'Main Dishes', 'icon': 'fas fa-utensils', 'color': '#fd7e14'},
            'עיקריות': {'name_he': 'עיקריות', 'name_en': 'Main Dishes', 'icon': 'fas fa-utensils', 'color': '#fd7e14'},
            'סושי': {'name_he': 'סושי', 'name_en': 'Sushi', 'icon': 'fas fa-fish', 'color': '#20c997'},
            'סלטים': {'name_he': 'סלטים', 'name_en': 'Salads', 'icon': 'fas fa-leaf', 'color': '#28a745'},
            'מרקים': {'name_he': 'מרקים', 'name_en': 'Soups', 'icon': 'fas fa-bowl', 'color': '#6c757d'},
            'צמחוני': {'name_he': 'צמחוני', 'name_en': 'Vegetarian', 'icon': 'fas fa-seedling', 'color': '#28a745'},
            'בשר': {'name_he': 'בשר', 'name_en': 'Meat', 'icon': 'fas fa-drumstick-bite', 'color': '#dc3545'},
            'עוף': {'name_he': 'עוף', 'name_en': 'Chicken', 'icon': 'fas fa-chicken', 'color': '#fd7e14'},
            'דגים': {'name_he': 'דגים', 'name_en': 'Fish', 'icon': 'fas fa-fish', 'color': '#17a2b8'},
            'פיצה': {'name_he': 'פיצה', 'name_en': 'Pizza', 'icon': 'fas fa-pizza-slice', 'color': '#dc3545'},
            'קריספי': {'name_he': 'קריספי', 'name_en': 'Crispy', 'icon': 'fas fa-fire', 'color': '#fd7e14'}
        }
        
        # Category detection keywords - for flexible matching
        self.category_keywords = list(self.categories_mapping.keys())
        
        # Debug mode
        self.debug = False  # Simplified parser doesn't need debug
    
    def parse_word_menu_simple(self, content):
        """Simple parser for user's specific format: Hebrew name + price"""
        try:
            # Find all potential menu items using simple pattern
            # Pattern: Hebrew text followed by 1-3 digits (price)
            pattern = r'([\u0590-\u05FF][\u0590-\u05FF\s\w\'"]+?)\s+(\d{1,3})(?=\s|$)'
            
            matches = re.findall(pattern, content)
            
            potential_items = []
            for match in matches:
                name = match[0].strip()
                price = int(match[1])
                
                # Filter reasonable menu items
                if (len(name) > 2 and 
                    10 <= price <= 300 and  # Reasonable price range
                    not any(bad in name.lower() for bad in ['תפטעמ', 'שגומ'])):
                    
                    potential_items.append({
                        'name_he': name,
                        'price': price,
                        'selected': False,  # User will choose
                        'category': '',     # User will assign
                        'order': len(potential_items)
                    })
            
            return {
                'potential_items': potential_items,
                'total_found': len(potential_items),
                'raw_matches': len(matches)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error parsing menu: {str(e)}")
            raise e
    
    def _detect_category(self, line):
        """Flexible category detection"""
        line_clean = line.strip()
        
        # Exact match first
        if line_clean in self.categories_mapping:
            return line_clean
        
        # Partial matches and common variations
        for category in self.category_keywords:
            if category in line_clean:
                return category
        
        # Check if line looks like a category header (Hebrew, short, caps-like)
        if len(line_clean) < 50 and any(c in line_clean for c in ['ראשונות', 'ווק', 'יקיטורי', 'באנים', 'ילדים', 'קינוחים', 'שתייה', 'עיקריות', 'סושי', 'סלטים']):
            # Create new category for unknown but likely categories
            new_category = line_clean
            if new_category not in self.categories_mapping:
                self.categories_mapping[new_category] = {
                    'name_he': new_category,
                    'name_en': new_category,
                    'icon': 'fas fa-utensils',
                    'color': '#6c757d'
                }
            return new_category
        
        return None
    
    def _looks_like_menu_item(self, line):
        """Check if line looks like a menu item"""
        line = line.strip()
        
        # Skip very short lines or lines with lots of symbols
        if len(line) < 3 or line.count('־') > 5 or line.count('_') > 5:
            return False
        
        # Look for Hebrew text (has Hebrew characters)
        has_hebrew = any('\u0590' <= c <= '\u05FF' for c in line)
        
        # Look for numbers (potential prices)
        has_numbers = any(c.isdigit() for c in line)
        
        # If it has both Hebrew and numbers, likely a menu item
        return has_hebrew and (has_numbers or len(line.strip()) > 5)
    
    def _parse_flexible_item(self, lines, start_index):
        """Parse menu item with flexible patterns"""
        if start_index >= len(lines):
            return None
        
        line = lines[start_index].strip()
        
        # Extract any numbers as potential prices
        prices = []
        dish_name = line
        
        # Look for price patterns anywhere in the line
        price_matches = re.findall(r'\b(\d{1,3})(?:₪|\s*שקל)?\b', line)
        if price_matches:
            prices = [int(p) for p in price_matches if 10 <= int(p) <= 200]  # Reasonable price range
            
            # Remove prices from dish name
            for price in price_matches:
                dish_name = re.sub(r'\b' + price + r'(?:₪|\s*שקל)?\b', '', dish_name)
        
        # Clean up dish name
        dish_name = re.sub(r'\s+', ' ', dish_name).strip()
        
        if not dish_name or len(dish_name) < 2:
            return None
        
        # Look for ingredients in next lines
        ingredients = ""
        next_index = start_index + 1
        
        while next_index < len(lines) and next_index < start_index + 3:  # Max 3 lines ahead
            next_line = lines[next_index].strip()
            
            # Stop if it looks like another item or category
            if self._looks_like_menu_item(next_line) or self._detect_category(next_line):
                break
            
            # Stop if line is decorative or empty
            if not next_line or next_line.count('־') > 3:
                next_index += 1
                break
            
            # Add as ingredient if it doesn't look like an item itself
            if not any(c.isdigit() for c in next_line):  # No numbers = likely ingredient
                if ingredients:
                    ingredients += " "
                ingredients += next_line
                next_index += 1
            else:
                break
        
        return {
            'name_he': dish_name,
            'name_en': self._transliterate_dish_name(dish_name),
            'prices': prices if prices else [0],  # Default price if none found
            'ingredients_he': ingredients,
            'ingredients_en': '',
            'next_index': next_index
        }
    
    def _parse_menu_item(self, lines, start_index):
        """Parse a single menu item starting from the given line index (enhanced)"""
        if start_index >= len(lines):
            return None
        
        line = lines[start_index].strip()
        
        # Multiple price patterns to try
        patterns = [
            r'^(\d+(?:/\d+)?)\s+(.+)$',  # Original: "56 Dish Name"
            r'^(.+?)\s+(\d+(?:/\d+)?)₪?$',  # End price: "Dish Name 56₪"
            r'^(.+?)\s+(\d+(?:/\d+)?)\s*שקל$',  # Hebrew currency: "Dish Name 56 שקל"
            r'^(\d+(?:/\d+)?)\.\s*(.+)$',  # Numbered: "1. Dish Name"
            r'^(.+?)[-־\s]+(\d+(?:/\d+)?)$'  # Dash separated: "Dish Name - 56"
        ]
        
        prices = []
        dish_name = ""
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if pattern.startswith(r'^(\d+'):  # Price first patterns
                    prices_str = match.group(1)
                    dish_name = match.group(2).strip()
                else:  # Price second patterns
                    dish_name = match.group(1).strip()
                    prices_str = match.group(2)
                
                # Parse prices
                try:
                    prices = [int(p.strip()) for p in prices_str.split('/')]
                    break
                except ValueError:
                    continue
        
        if not dish_name or not prices:
            return None
        
        # Look for ingredients/description in next line(s)
        ingredients = ""
        next_index = start_index + 1
        
        # Keep looking for ingredient lines until we hit another item or category
        while next_index < len(lines):
            next_line = lines[next_index].strip()
            
            # Stop if we hit another price pattern or category
            if any(re.match(p, next_line) for p in patterns) or self._detect_category(next_line):
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
    
    def process_selected_items(self, selected_items, branch_id, uploaded_by=None):
        """Process only user-selected items"""
        from database import db
        from models import MenuCategory, MenuItem, MenuItemPrice
        
        try:
            items_added = 0
            categories_used = set()
            
            for item in selected_items:
                if not item.get('selected', False):
                    continue
                    
                # Get or create category
                category_name = item.get('category', 'כללי')
                category = MenuCategory.query.filter_by(name_he=category_name).first()
                
                if not category:
                    category = MenuCategory(
                        name_he=category_name,
                        name_en=category_name,
                        icon='fas fa-utensils',
                        color='#007bff',
                        display_order=len(categories_used),
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.flush()
                    categories_used.add(category_name)
                
                # Create menu item
                menu_item = MenuItem(
                    category_id=category.id,
                    name_he=item['name_he'],
                    name_en=item.get('name_en', item['name_he']),
                    base_price=item['price'],
                    is_available=True,
                    display_order=item.get('order', items_added)
                )
                
                db.session.add(menu_item)
                items_added += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'items_added': items_added,
                'categories_used': len(categories_used)
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error storing selected items: {str(e)}")
            raise e