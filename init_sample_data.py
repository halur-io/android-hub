#!/usr/bin/env python3
"""
Script to initialize sample data for the SUMO restaurant website
Run this to populate the database with initial data
"""

from app import app
from database import db
from models import *
from datetime import datetime, date, time

def create_sample_data():
    with app.app_context():
        # Update site settings with more complete data
        settings = SiteSettings.query.first()
        if settings:
            settings.about_title_he = "סיפור סומו"
            settings.about_title_en = "The SUMO Story"
            settings.about_content_he = "סומו היא יותר ממסעדה - היא חוויה קולינרית שמשלבת את המיטב של המטבח האסייתי עם נגיעות מודרניות. משנת הקמתנו, אנו מחויבים להגיש את האוכל האסייתי האיכותי ביותר בצפון."
            settings.about_content_en = "SUMO is more than a restaurant - it's a culinary experience that combines the best of Asian cuisine with modern touches. Since our establishment, we are committed to serving the highest quality Asian food in the North."
            settings.facebook_url = "https://facebook.com/sumorestaurant"
            settings.instagram_url = "https://instagram.com/sumorestaurant"
            settings.whatsapp_number = "972501234567"
            db.session.commit()
            print("✓ Updated site settings")

        # Create branches
        rama_branch = Branch(
            name_he="סומו ראמה",
            name_en="SUMO Rama",
            address_he="כפר ראמה, רחוב ראשי 123",
            address_en="Rama Village, Main Street 123",
            phone="04-9581234",
            email="rama@sumo.co.il",
            waze_link="https://waze.com/ul/rama",
            google_maps_link="https://maps.google.com/rama",
            is_active=True,
            display_order=1
        )
        db.session.add(rama_branch)
        
        karmiel_branch = Branch(
            name_he="סומו כרמיאל",
            name_en="SUMO Karmiel",
            address_he="כרמיאל, מרכז העיר 45",
            address_en="Karmiel, City Center 45",
            phone="04-9087654",
            email="karmiel@sumo.co.il",
            waze_link="https://waze.com/ul/karmiel",
            google_maps_link="https://maps.google.com/karmiel",
            is_active=True,
            display_order=2
        )
        db.session.add(karmiel_branch)
        db.session.commit()
        print("✓ Created branches")

        # Add working hours for branches
        days_he = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        days_en = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for branch in [rama_branch, karmiel_branch]:
            for i, (day_he, day_en) in enumerate(zip(days_he, days_en)):
                if i == 6:  # Saturday - closed
                    wh = WorkingHours(
                        branch_id=branch.id,
                        day_of_week=i,
                        day_name_he=day_he,
                        day_name_en=day_en,
                        is_closed=True
                    )
                elif i == 5:  # Friday - shorter hours
                    wh = WorkingHours(
                        branch_id=branch.id,
                        day_of_week=i,
                        day_name_he=day_he,
                        day_name_en=day_en,
                        open_time="12:00",
                        close_time="22:00",
                        is_closed=False
                    )
                else:  # Regular days
                    wh = WorkingHours(
                        branch_id=branch.id,
                        day_of_week=i,
                        day_name_he=day_he,
                        day_name_en=day_en,
                        open_time="12:00",
                        close_time="23:00",
                        is_closed=False
                    )
                db.session.add(wh)
        db.session.commit()
        print("✓ Added working hours")

        # Create menu categories
        sushi_cat = MenuCategory(
            name_he="סושי ורולים",
            name_en="Sushi & Rolls",
            description_he="מבחר סושי טרי ורולים מיוחדים",
            description_en="Fresh sushi and special rolls selection",
            display_order=1,
            is_active=True
        )
        db.session.add(sushi_cat)
        
        noodles_cat = MenuCategory(
            name_he="נודלס ואורז",
            name_en="Noodles & Rice",
            description_he="מנות נודלס ואורז אסייתיות",
            description_en="Asian noodle and rice dishes",
            display_order=2,
            is_active=True
        )
        db.session.add(noodles_cat)
        
        appetizers_cat = MenuCategory(
            name_he="מנות ראשונות",
            name_en="Appetizers",
            description_he="מנות פתיחה מסורתיות",
            description_en="Traditional starter dishes",
            display_order=3,
            is_active=True
        )
        db.session.add(appetizers_cat)
        db.session.commit()
        print("✓ Created menu categories")

        # Add menu items
        items = [
            # Sushi items
            MenuItem(
                category_id=sushi_cat.id,
                name_he="סלמון רול",
                name_en="Salmon Roll",
                description_he="8 יחידות, סלמון טרי, אבוקדו ומלפפון",
                description_en="8 pieces, fresh salmon, avocado and cucumber",
                price=45,
                is_available=True,
                display_order=1
            ),
            MenuItem(
                category_id=sushi_cat.id,
                name_he="ספיישל רול",
                name_en="Special Roll",
                description_he="8 יחידות, טונה חריפה, טמפורה ובצל ירוק",
                description_en="8 pieces, spicy tuna, tempura and green onion",
                price=52,
                is_spicy=True,
                is_available=True,
                display_order=2
            ),
            # Noodles items
            MenuItem(
                category_id=noodles_cat.id,
                name_he="פאד תאי",
                name_en="Pad Thai",
                description_he="נודלס אורז מוקפץ עם ירקות, ביצה ובוטנים",
                description_en="Stir-fried rice noodles with vegetables, egg and peanuts",
                price=58,
                is_vegetarian=True,
                is_available=True,
                display_order=1
            ),
            MenuItem(
                category_id=noodles_cat.id,
                name_he="ראמן",
                name_en="Ramen",
                description_he="מרק נודלס יפני עשיר עם ביצה רכה",
                description_en="Rich Japanese noodle soup with soft egg",
                price=62,
                is_available=True,
                display_order=2
            ),
            # Appetizers
            MenuItem(
                category_id=appetizers_cat.id,
                name_he="אדממה",
                name_en="Edamame",
                description_he="פולי סויה מאודים עם מלח גס",
                description_en="Steamed soybeans with coarse salt",
                price=28,
                is_vegan=True,
                is_gluten_free=True,
                is_available=True,
                display_order=1
            ),
            MenuItem(
                category_id=appetizers_cat.id,
                name_he="גיוזה",
                name_en="Gyoza",
                description_he="כיסוני בצק יפניים במילוי עוף וירקות",
                description_en="Japanese dumplings filled with chicken and vegetables",
                price=38,
                is_available=True,
                display_order=2
            )
        ]
        
        for item in items:
            db.session.add(item)
        db.session.commit()
        print("✓ Added menu items")

        # Add sample gallery photos
        gallery_photos = [
            GalleryPhoto(
                file_path="/static/images/gallery1.jpg",
                caption_he="האווירה במסעדה",
                caption_en="Restaurant atmosphere",
                display_order=1,
                is_active=True
            ),
            GalleryPhoto(
                file_path="/static/images/gallery2.jpg",
                caption_he="מנות מיוחדות",
                caption_en="Special dishes",
                display_order=2,
                is_active=True
            )
        ]
        
        for photo in gallery_photos:
            db.session.add(photo)
        db.session.commit()
        print("✓ Added gallery photos")

        # Add sample contact message
        message = ContactMessage(
            name="דוד כהן",
            email="david@example.com",
            phone="050-1234567",
            message="המסעדה נראית מעולה! מתי אתם פותחים בכרמיאל?",
            is_read=False
        )
        db.session.add(message)
        
        # Add sample reservation
        reservation = Reservation(
            branch_id=rama_branch.id,
            customer_name="שרה לוי",
            phone="052-9876543",
            email="sarah@example.com",
            date=date.today(),
            time=time(19, 30),
            guests=4,
            special_requests="שולחן ליד החלון בבקשה",
            status="pending"
        )
        db.session.add(reservation)
        db.session.commit()
        print("✓ Added sample messages and reservations")

        print("\n✅ Sample data created successfully!")
        print("\nAdmin Login Details:")
        print("Username: admin")
        print("Password: admin123")
        print("\nAccess the admin panel at: /admin")

if __name__ == "__main__":
    create_sample_data()