-- ========================================
-- COMPLETE PRODUCTION DATABASE SETUP
-- Generated for: sumo-rest.co.il
-- Date: November 11, 2025
-- ========================================
-- This script includes:
-- ✓ Site Settings (logo, about, colors)
-- ✓ Branches (Karmiel, Ramah)
-- ✓ Reservation Settings
-- ✓ Admin User
-- ✓ Menu Categories (10)
-- ✓ Menu Items (50+)
-- ✓ Gallery Photos (17)
-- ✓ Catering Gallery (5)
-- ========================================

-- Clear existing data
TRUNCATE TABLE site_settings, branches, reservation_settings, admin_users, menu_settings, roles, menu_categories, menu_items, gallery_photos, catering_gallery_images RESTART IDENTITY CASCADE;

-- ========================================
-- 1. SITE SETTINGS
-- ========================================
INSERT INTO site_settings (
    id, site_name_he, site_name_en, hero_title_he, hero_title_en,
    hero_subtitle_he, hero_subtitle_en, about_title_he, about_title_en,
    about_content_he, about_content_en, facebook_url, instagram_url,
    enable_online_ordering, enable_menu_display, enable_contact_form,
    enable_table_reservations, enable_app_download, enable_catering_section,
    enable_careers_section, hero_desktop_image, logo_image,
    primary_color, accent_color, app_store_url, google_play_url,
    catering_title_he, catering_title_en, catering_subtitle_he, catering_subtitle_en,
    careers_title_he, careers_title_en, careers_subtitle_he, careers_subtitle_en,
    catering_page_hero_title_he, catering_page_hero_subtitle_he,
    careers_page_hero_title_he, careers_page_hero_subtitle_he,
    enable_gallery, enable_catering_page, show_app_banner
) VALUES (
    1, 'Sumo Asian Kitchen', 'Sumo Asian Kitchen', 'סומו', 'SUMO',
    'Feel lucky in every bite', 'Feel lucky in every bite',
    'אודותינו', 'About Us',
    'רשת סומו – החוויה האסייתית המודרנית.
כל מנה טרייה, מוקפדת ומוכנה מול העיניים – סושי ומנות ווק צבעוניות שמביאים את הטעמים והאנרגיה של המזרח הרחוק.
בין אם במסעדות או במשלוחים – אצלנו כל ביקור או הזמנה הם רגע של כיף, טעמים עשירים ואווירה צעירה, קלילה וכיפית.
בדיוק כמו שהסלוגן שלנו אומר: Feel lucky in every bite.',
    'About Sumo
Welcome to Sumo, an Asian restaurant that blends flavors from the Far East with a modern and elegant touch.
At Sumo, we take pride in using only the freshest and highest-quality ingredients to ensure an unforgettable dining experience every time.

Our menu features a fine selection of crafted sushi and flavorful wok dishes, inspired by the cuisines of Japan and Thailand.
Everything is served with careful attention to detail, design, and presentation — creating a harmony of taste, aroma, and atmosphere.',
    'https://facebook.com', 'https://www.instagram.com/sumo.karmiel',
    false, true, true, true, true, true, true,
    'hero_desktop_20251101_191518_95.jpg', 'sumo_logo_final.png',
    '#1a3a6e', '#dc3545',
    'https://apps.apple.com/app/sumo-kitchen',
    'https://play.google.com/store/apps/details?id=com.sumo.kitchen',
    'קייטרינג ואירועים מיוחדים', 'Premium Catering Services',
    'הביאו את הטעמים האסיאתיים האותנטיים לחגיגה הבאה שלכם. אנו מציעים תפריטי קייטרינג מותאמים אישית לחתונות, ימי הולדת ואירועי חברה.',
    'Let us make your special event unforgettable with our authentic Asian cuisine',
    'הצטרפו לצוות שלנו', 'Join Our Team',
    'מחפשים אנשי מקצוע מוכשרים להצטרף למשפחת סומו. גלו הזדמנויות קריירה מרגשות במטבח האסייתי המוביל.',
    'Looking for talented professionals to join the SUMO family. Discover exciting career opportunities at the leading Asian kitchen.',
    'קייטרינג ואירועים מיוחדים', 'הפכו את האירוע שלכם לבלתי נשכח עם המטבח האסייתי האותנטי שלנו',
    'הצטרפו לצוות שלנו', 'בואו להיות חלק ממשפחת סומו - מקום שבו כישרון פוגש תשוקה',
    false, true, true
);

-- ========================================
-- 2. BRANCHES
-- ========================================
INSERT INTO branches (id, name_he, name_en, address_he, phone, email, is_active, display_order) VALUES
(2, 'כרמיאל', 'Karmiel', 'גן העיר', '0777392707', 'office@sumo-rest.co.il', true, 0),
(1, 'ראמה', 'Ramah', '', '0506088883', '', true, 1);

-- ========================================
-- 3. RESERVATION SETTINGS
-- ========================================
INSERT INTO reservation_settings (
    id, enable_reservations, reservation_system_url,
    reservation_button_text_he, reservation_button_text_en,
    show_on_homepage
) VALUES (
    1, true, 'https://tbit.be/BHWCPU',
    'הזמינו שולחן', 'Reserve a Table', true
);

-- ========================================
-- 4. ADMIN USER
-- ========================================
INSERT INTO admin_users (id, username, email, password_hash, is_active, is_superadmin) VALUES (
    1, 'khalilshiban', 'khalil@sumo.com',
    'scrypt:32768:8:1$mZLASnK16agbrOoN$60029896d6f0e210859fe740efa4d95d3a6f4242e1da3b5f717127e724d06afef743a939e9e215db6780537aa2c220c1923e1cb14c08247eda766247774626ee',
    true, true
);

-- ========================================
-- 5. MENU SETTINGS
-- ========================================
INSERT INTO menu_settings (id, setting_key, setting_value, description) VALUES
(1, 'show_images', 'false', 'Show Images');

-- ========================================
-- 6. ROLES
-- ========================================
INSERT INTO roles (id, name, display_name, description, is_active, is_system_role) VALUES
(1, 'superadmin', 'Super Administrator', 'Full system access with all permissions', true, true),
(2, 'admin', 'Administrator', 'Full administrative access to most features', true, true),
(3, 'manager', 'Manager', 'Management access to operations and reports', true, false),
(4, 'kitchen', 'Kitchen Staff', 'Kitchen operations and order management', true, false),
(5, 'delivery', 'Delivery Manager', 'Delivery and driver management', true, false),
(6, 'cashier', 'Cashier', 'Order taking and payment processing', true, false),
(7, 'viewer', 'Viewer', 'Read-only access to reports and data', true, false);

-- ========================================
-- 7. MENU CATEGORIES (10 categories)
-- ========================================
INSERT INTO menu_categories (id, name_he, name_en, display_order, is_active, show_in_menu, show_in_order) VALUES
(10, 'ראשונות', 'ראשונות', 1, true, true, true),
(12, 'יקיטורי', 'יקיטורי', 2, true, true, true),
(13, 'באנים', 'באנים', 3, true, true, true),
(14, 'ארוחות ילדים', 'ארוחות ילדים', 4, true, true, true),
(11, 'ווק', 'ווק', 5, true, true, true),
(15, 'סושי', 'סושי', 6, true, true, true),
(16, 'ניגירי', 'ניגירי', 7, true, true, true),
(17, 'סשימי', 'סשימי', 8, true, true, true),
(18, 'שתיה קלה', 'שתיה קלה', 9, true, true, true),
(19, 'שתיה חמה', 'שתיה חמה', 10, true, false, true);


-- ========================================
-- 8. GALLERY PHOTOS (17 photos)
-- ========================================
INSERT INTO gallery_photos (id, file_path, display_order, is_active) VALUES
(1, '/static/uploads/gallery_20251030_231751_31.jpg', 0, true),
(2, '/static/uploads/gallery_20251030_233229_238394_52.jpg', 1, true),
(3, '/static/uploads/gallery_20251030_233247_334091_42.jpg', 2, true),
(4, '/static/uploads/gallery_20251030_233254_744270_32.jpg', 3, true),
(5, '/static/uploads/gallery_20251030_233309_417691_24.jpg', 4, true),
(6, '/static/uploads/gallery_20251030_233313_718631_75.jpg', 5, true),
(7, '/static/uploads/gallery_20251030_233327_843961_85.jpg', 6, true),
(8, '/static/uploads/gallery_20251030_233333_370363_90.jpg', 7, true),
(9, '/static/uploads/gallery_20251030_233353_707259_107.jpg', 8, true),
(10, '/static/uploads/gallery_20251030_233419_139106_148.jpg', 9, true),
(11, '/static/uploads/gallery_20251030_233432_156623_146.jpg', 10, true),
(12, '/static/uploads/gallery_20251030_233444_685074_142.jpg', 11, true),
(13, '/static/uploads/gallery_20251030_233453_686688_136.jpg', 12, true),
(14, '/static/uploads/gallery_20251030_233501_375953_142.jpg', 13, true),
(15, '/static/uploads/gallery_20251030_233509_436871_129.jpg', 14, true),
(16, '/static/uploads/gallery_20251030_233517_359730_144.jpg', 15, true),
(17, '/static/uploads/gallery_20251030_233525_435467_149.jpg', 16, true);

-- ========================================
-- 9. CATERING GALLERY (5 images)
-- ========================================
INSERT INTO catering_gallery_images (id, file_path, is_active, display_order) VALUES
(1, '/static/uploads/catering_20251106_142010_591990_45.jpg', true, 0),
(2, '/static/uploads/catering_20251106_142040_169207_74.jpg', true, 1),
(3, '/static/uploads/catering_20251106_142107_996143_88.jpg', true, 2),
(4, '/static/uploads/catering_20251106_142129_522915_66.jpg', true, 3),
(5, '/static/uploads/catering_20251106_142153_145035_10.jpg', true, 4);

-- ========================================
-- 10. MENU ITEMS (88 items)
-- ========================================
INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(25, 'סלט טרופי', 'סלט טרופי', 'מיקס חסה, בצל סגול, פרי טרופי, שירי צבעים, אבוקדו, קרוטונים אסייתים', 'מיקס חסה, בצל סגול, פרי טרופי, שירי צבעים, אבוקדו, קרוטונים אסייתים', 10, 0, '/static/uploads/menu_20251106_215149_JPG_cropped.png') ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(26, 'סלט ויאטנמי', 'סלט ויאטנמי', 'אטריות זכוכית, מלפפון, כרוב סגול, גזר, בצל ירוק,נבטים סינים ברוטב בוטנים ויאטנמי', 'אטריות זכוכית, מלפפון, כרוב סגול, גזר, בצל ירוק,נבטים סינים ברוטב בוטנים ויאטנמי', 10, 1, '/static/uploads/menu_20251107_004122_0H6A5284_cropped.png') ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(27, 'הקיסר האסייתי', 'הקיסר האסייתי', 'חסה ליטל ג''ם, תירס אומאמי, בצל סגול, צלפים ,קלמארי פריך / עוף צלוי', 'חסה ליטל ג''ם, תירס אומאמי, בצל סגול, צלפים ,קלמארי פריך / עוף צלוי', 10, 2, '/static/uploads/menu_20251110_180917_0H6A5234.JPG') ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(28, 'קריספי רייס', 'קריספי רייס', '4 יח'' קריספי מיני מאקי במילוי טרטר סלמון פיקנטי, שמנת, עירית.', '4 יח'' קריספי מיני מאקי במילוי טרטר סלמון פיקנטי, שמנת, עירית.', 10, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(29, 'נאמס ירקות/עוף', 'נאמס ירקות/עוף', '2 יח'' ספרינג רול וויאטנמי במילוי ירקות/עוף על מצע חסה אסייתית, צ''ילי חריף, נענע, כוסברה ומתבלים אסייתיים', '2 יח'' ספרינג רול וויאטנמי במילוי ירקות/עוף על מצע חסה אסייתית, צ''ילי חריף, נענע, כוסברה ומתבלים אסייתיים', 10, 4, '/static/uploads/menu_20251110_191751_0H6A5318_processed.png') ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(30, 'טטאקי סינטה כבושה', 'טטאקי סינטה כבושה', 'סינטה עגל בכבישה קרה, איולי כמהין ,איולי יוזו, עירית קצוצה וזסט לימון', 'סינטה עגל בכבישה קרה, איולי כמהין ,איולי יוזו, עירית קצוצה וזסט לימון', 10, 5, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(31, 'פופ שרימפס', 'פופ שרימפס', 'קוביות שרימפס בטמפורה עטופות באיולי יוזו, תבלין אומאמי ,עירית', 'קוביות שרימפס בטמפורה עטופות באיולי יוזו, תבלין אומאמי ,עירית', 10, 6, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(32, 'הביס היפני', 'הביס היפני', 'לחם חלב יפני מושחם, קרם אבוקדו, סביצ''ה דג לבן בתיבול יוזו, צילי חריף ,כוסברה ונענע', 'לחם חלב יפני מושחם, קרם אבוקדו, סביצ''ה דג לבן בתיבול יוזו, צילי חריף ,כוסברה ונענע', 10, 7, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(33, 'אגרול ירקות/עוף', 'אגרול ירקות/עוף', '2 יח'' אגרול ירקות/עוף - מוגש על מצע חסה אסייתית, צילי חריף, נענע, כוסברה ומתבלים אסייתיים', '2 יח'' אגרול ירקות/עוף - מוגש על מצע חסה אסייתית, צילי חריף, נענע, כוסברה ומתבלים אסייתיים', 10, 8, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(34, 'שרימפס פינגרז', 'שרימפס פינגרז', 'שרימפס פינגרז 4 יח'' עם רוטב טרטר ולימון', 'שרימפס פינגרז 4 יח'' עם רוטב טרטר ולימון', 10, 9, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(35, 'קלמארי פריך', 'קלמארי פריך', 'קלמרי מטוגן בציפוי פריך, מוגש עם רוטב חמוץ מתוק ו לימון', 'קלמרי מטוגן בציפוי פריך, מוגש עם רוטב חמוץ מתוק ו לימון', 10, 10, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(36, 'קימצ''י קוריאני', 'קימצ''י קוריאני', '', '', 10, 11, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(37, 'חמוצים יפנים', 'חמוצים יפנים', '', '', 10, 12, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(38, 'אדממה של סומו', 'אדממה של סומו', '', '', 10, 13, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(39, 'פאד תאי', 'פאד תאי', 'אטריות אורז, כרוב, גזר, בצל ירוק, נבטים סינים, שבבי בוטנים וכוסברה  - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12/ ביצה 5', 'אטריות אורז, כרוב, גזר, בצל ירוק, נבטים סינים, שבבי בוטנים וכוסברה  - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12/ ביצה 5', 11, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(40, 'ים השחור', 'ים השחור', 'אטריות שחורות, שרימפס, קלמארי, צילי קוריאני, שום וגנגר,בצל ירוק ונבטים סינים', 'אטריות שחורות, שרימפס, קלמארי, צילי קוריאני, שום וגנגר,בצל ירוק ונבטים סינים', 11, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(41, 'פרייד רייס', 'פרייד רייס', 'אורז מוקפץ עם גזר, בצל לבן, כרוב, גמבה ברוטב סויה כהה בתוספת ביצת עין מעל - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 'אורז מוקפץ עם גזר, בצל לבן, כרוב, גמבה ברוטב סויה כהה בתוספת ביצת עין מעל - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 11, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(42, 'החריפה', 'החריפה', 'אטריות ביצים, עוף, בצל לבן ופטריות מוקפצים ברוטב קארי אדום וחלב קוקוס מוגש עם שבבי בוטנים וקריספי בצל אסייתי', 'אטריות ביצים, עוף, בצל לבן ופטריות מוקפצים ברוטב קארי אדום וחלב קוקוס מוגש עם שבבי בוטנים וקריספי בצל אסייתי', 11, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(43, 'סמוקי', 'סמוקי', 'אטריות ביצים, כרוב לבן, גזר, פטריות, באק צ''וי, אווז מעושן, בצל קריספי ברוטב טריאקי מעושן - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 'אטריות ביצים, כרוב לבן, גזר, פטריות, באק צ''וי, אווז מעושן, בצל קריספי ברוטב טריאקי מעושן - תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 11, 4, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(44, 'תאילנד הירוקה', 'תאילנד הירוקה', 'אטריות תרד ירוקים, קוביות אננס, זוקיני, ברוקולי, באק צ''וי ובצל ירוק ברוטב קארי ירוק וחלב קוקוס – תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 'אטריות תרד ירוקים, קוביות אננס, זוקיני, ברוקולי, באק צ''וי ובצל ירוק ברוטב קארי ירוק וחלב קוקוס – תוספת עוף 12/ בקר 15/ שרימפס 20/ טופו 12', 11, 5, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(45, 'עוף קשיו', 'עוף קשיו', 'עוף בטמפורה מוקפץ עם קשיו, בצל לבן, גמבה וצ''ילי מוגש עם אורז מאודה', 'עוף בטמפורה מוקפץ עם קשיו, בצל לבן, גמבה וצ''ילי מוגש עם אורז מאודה', 11, 6, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(46, 'יקיטורי סלמון', 'יקיטורי סלמון', 'גלייז צילי מותסס, צ''ימיצ''ורי יפני, ירקות חרוכים', 'גלייז צילי מותסס, צ''ימיצ''ורי יפני, ירקות חרוכים', 12, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(47, 'יקיטורי שרימפס', 'יקיטורי שרימפס', 'יקיטורי שרימפס בתיבול ג''נג''ר שום, תבלינים יפנים ויוזו מוגש עם אבוקדו חרוך', 'יקיטורי שרימפס בתיבול ג''נג''ר שום, תבלינים יפנים ויוזו מוגש עם אבוקדו חרוך', 12, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(48, 'יקטורי דג לבן', 'יקטורי דג לבן', 'שיפוד של דג לבן במרינדה של קפיר ליים, ג''נג''ר ושום, מוגש עם רוטב קארי ירוק וחלב קוקוס בתוספת אורז מאודה', 'שיפוד של דג לבן במרינדה של קפיר ליים, ג''נג''ר ושום, מוגש עם רוטב קארי ירוק וחלב קוקוס בתוספת אורז מאודה', 12, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(49, 'יקיטורי עגל', 'יקיטורי עגל', 'לוליפופ עגל מוגש עם באק צ''וי ואורז מעושן', 'לוליפופ עגל מוגש עם באק צ''וי ואורז מעושן', 12, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(50, 'יקיטורי עוף', 'יקיטורי עוף', 'שיפודי עוף במרינדה אסייתית על הגריל, מיקס פטריות מוקפצות ברוטב חמאת בוטנים קוריאני', 'שיפודי עוף במרינדה אסייתית על הגריל, מיקס פטריות מוקפצות ברוטב חמאת בוטנים קוריאני', 12, 4, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(51, 'Infected mushrooms', 'Infected mushrooms', 'פטריות שינוגי פריכות, איולי קוג''י כמהין וסויט שימאגי', 'פטריות שינוגי פריכות, איולי קוג''י כמהין וסויט שימאגי', 13, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(52, 'סיי באן', 'סיי באן', 'דג לבן טמפורה, איולי מעושן, סלט כרוב סגול אסייתי', 'דג לבן טמפורה, איולי מעושן, סלט כרוב סגול אסייתי', 13, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(53, 'ביף באן', 'ביף באן', 'פרוסות עגל פלאנצ''ה, קרם אבוקדו, חסה, בצל סגול וצ''ילי חריף', 'פרוסות עגל פלאנצ''ה, קרם אבוקדו, חסה, בצל סגול וצ''ילי חריף', 13, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(54, 'קריספי שרימפס באן', 'קריספי שרימפס באן', 'קולסלואו אסייתי, בצל סגול, חסה ואיולי יוזו', 'קולסלואו אסייתי, בצל סגול, חסה ואיולי יוזו', 13, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(55, 'באן שניצל', 'באן שניצל', 'באן שניצל, ציפס ושתיה קלה', 'באן שניצל, ציפס ושתיה קלה', 14, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(56, 'הוט דוג קוריאני', 'הוט דוג קוריאני', '2 נקניקיות עוף קוריאני בציפוי דוריטוס/פנקו/טמפורה ושתיה קלה', '2 נקניקיות עוף קוריאני בציפוי דוריטוס/פנקו/טמפורה ושתיה קלה', 14, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(57, 'מוקפץ ילדים', 'מוקפץ ילדים', 'אטריות ביצים, עוף, טריאקי ושתיה קלה', 'אטריות ביצים, עוף, טריאקי ושתיה קלה', 14, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(58, 'קלאסיקו', 'קלאסיקו', 'סלמון, אבוקדו, גזר, מלפפון, במעטפת שומשום שחור', 'סלמון, אבוקדו, גזר, מלפפון, במעטפת שומשום שחור', 15, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(59, 'קינג סלמון', 'קינג סלמון', 'סלמון, גזר, קנפיו, אספרגוס, עטוף סלמון', 'סלמון, גזר, קנפיו, אספרגוס, עטוף סלמון', 15, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(60, 'יוזו רול', 'יוזו רול', 'אבוקדו,עירית, מלפפון, טוביקו, מעטפת דג ים לבן ויוזו קושו', 'אבוקדו,עירית, מלפפון, טוביקו, מעטפת דג ים לבן ויוזו קושו', 15, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(61, 'סטושי רול', 'סטושי רול', 'קנפיו,אבוקדו, מלפפון וטוביקו שחור, טופ של סביצ''ה דג לבן', 'קנפיו,אבוקדו, מלפפון וטוביקו שחור, טופ של סביצ''ה דג לבן', 15, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(62, 'ספייסי טונה רול', 'ספייסי טונה רול', 'אבוקדו, סורימי פנקו, עירית, שבבי טמפורה וטופ של ספייסי טונה', 'אבוקדו, סורימי פנקו, עירית, שבבי טמפורה וטופ של ספייסי טונה', 15, 4, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(63, 'ספייסי סורו', 'ספייסי סורו', 'סורימי , אבוקדו, מלפפון, עירית, ספייסי מיונז ושבבי בוטנים', 'סורימי , אבוקדו, מלפפון, עירית, ספייסי מיונז ושבבי בוטנים', 15, 5, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(64, 'קריספי רול', 'קריספי רול', 'סלמון, גזר, אבוקדו, גבינת גאודה, מטוגן בטמפורה', 'סלמון, גזר, אבוקדו, גבינת גאודה, מטוגן בטמפורה', 15, 6, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(65, 'קריספי שרימפס רול', 'קריספי שרימפס רול', 'שרימפס טמפורה, אבוקדו, בטטה', 'שרימפס טמפורה, אבוקדו, בטטה', 15, 7, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(66, 'קריספי סנדוויץ''', 'קריספי סנדוויץ''', 'סלמון, אבוקדו, בטטה, גבינת גאודה, טריאקי, מטוגן בטמפורה', 'סלמון, אבוקדו, בטטה, גבינת גאודה, טריאקי, מטוגן בטמפורה', 15, 8, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(67, 'גרין רול', 'גרין רול', 'זוקיני טמפורה, אבוקדו, אספרגוס, עירית במעטפת מלפפון', 'זוקיני טמפורה, אבוקדו, אספרגוס, עירית במעטפת מלפפון', 15, 9, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(68, 'שרימפס רול', 'שרימפס רול', 'שרימפס טמפורה, בטטה, מלפפון, עירית', 'שרימפס טמפורה, בטטה, מלפפון, עירית', 15, 10, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(69, 'קראב רול', 'קראב רול', 'סורימי טמפורה, מלפפון, עירית, קנפיו, ובטטה', 'סורימי טמפורה, מלפפון, עירית, קנפיו, ובטטה', 15, 11, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(70, 'אומגה', 'אומגה', 'סלמון צלוי, גבינת פילדלפיה, בצל ירוק, עירית, מלפפון, במעטפת אבוקדו וביצי טוביקו', 'סלמון צלוי, גבינת פילדלפיה, בצל ירוק, עירית, מלפפון, במעטפת אבוקדו וביצי טוביקו', 15, 12, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(71, 'יוקוזונה XL', 'יוקוזונה XL', 'סלמון, גבינת פילדלפיה, גזר, עירית, חסה סינית, במעטפת סלמון צרוב ואיולי סריראצ''ה', 'סלמון, גבינת פילדלפיה, גזר, עירית, חסה סינית, במעטפת סלמון צרוב ואיולי סריראצ''ה', 15, 13, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(72, 'מקסיקאנו', 'מקסיקאנו', 'טונה אדומה, בטטה, אבוקדו, עירית, מעטפת שומשום סויה וחלפיניו מעל', 'טונה אדומה, בטטה, אבוקדו, עירית, מעטפת שומשום סויה וחלפיניו מעל', 15, 14, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(73, 'קיו רול', 'קיו רול', 'ללא אורז עם דג לבן נא, אבוקדו, חסה סינית וקנפיו מוגש עם רוטב פונזו ג''נג''ר וטוביקו שחור', 'ללא אורז עם דג לבן נא, אבוקדו, חסה סינית וקנפיו מוגש עם רוטב פונזו ג''נג''ר וטוביקו שחור', 15, 15, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(74, 'פיש אנד צ''יפס רול', 'פיש אנד צ''יפס רול', 'דג לבן טמפורה, מקלות צ''יפס, במעטפת עירית איולי יוזו ונגיעת לימון', 'דג לבן טמפורה, מקלות צ''יפס, במעטפת עירית איולי יוזו ונגיעת לימון', 15, 16, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(75, 'סמוקי רול', 'סמוקי רול', 'מלפפון, עירית, גבינת פילדלפיה ואבוקדו במעטפת של סלמון מעושן וביצי טוביקו', 'מלפפון, עירית, גבינת פילדלפיה ואבוקדו במעטפת של סלמון מעושן וביצי טוביקו', 15, 17, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(76, 'טרמינל  3', 'טרמינל  3', 'שרימפס טמפורה, בטטה, גזר, במעטפת טונה אדומה וסלמון', 'שרימפס טמפורה, בטטה, גזר, במעטפת טונה אדומה וסלמון', 15, 18, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(77, 'בודה רול', 'בודה רול', 'מלפפון, גזר, קנפיו, גבינת פלדלפיה, אספרגוס , במעטפת בטטה', 'מלפפון, גזר, קנפיו, גבינת פלדלפיה, אספרגוס , במעטפת בטטה', 15, 19, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(78, 'סומו רול', 'סומו רול', 'שרימפס טמפורה, אבוקדו, גבינת שמנת כמהין, מעטפת אבוקדו ופנקו סגול', 'שרימפס טמפורה, אבוקדו, גבינת שמנת כמהין, מעטפת אבוקדו ופנקו סגול', 15, 20, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(79, 'אומאמי רול', 'אומאמי רול', 'שרימפס דוריטוס, אבוקדו, סרירצ''ה וטופ של סורימי קצוץ', 'שרימפס דוריטוס, אבוקדו, סרירצ''ה וטופ של סורימי קצוץ', 15, 21, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(80, 'טוקיו רול', 'טוקיו רול', 'שרימפס טמפורה, אושינקו, בטטה,עירית, מעטפת סלמון צרוב ואררה מסאגו', 'שרימפס טמפורה, אושינקו, בטטה,עירית, מעטפת סלמון צרוב ואררה מסאגו', 15, 22, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(81, 'וג''י רול', 'וג''י רול', 'טופו טמפורה, בטטה, אבוקדו, טריאקי שומשום וקריספי בטטה​', 'טופו טמפורה, בטטה, אבוקדו, טריאקי שומשום וקריספי בטטה​', 15, 23, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(82, 'דראגון רול', 'דראגון רול', 'שרימפס טמפורה, גזר, אבוקדו, עירית, במעטפת בטטה ובצל קריספי', 'שרימפס טמפורה, גזר, אבוקדו, עירית, במעטפת בטטה ובצל קריספי', 15, 24, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(83, 'סלמון 2 יח''', 'סלמון 2 יח''', '', '', 16, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(84, 'סלמון צרוב סויה קוג''י וגרידת לימון 2 יח''', 'סלמון צרוב סויה קוג''י וגרידת לימון 2 יח''', '', '', 16, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(85, 'טונה 2 יח''', 'טונה 2 יח''', '', '', 16, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(86, 'דג לבן יוזו קושו ופינגר ליים 2 יח''', 'דג לבן יוזו קושו ופינגר ליים 2 יח''', '', '', 16, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(87, 'ניגירי טונה ואיולי כמהין 2 יח''', 'ניגירי טונה ואיולי כמהין 2 יח''', '', '', 16, 4, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(88, 'אבוקדו 2 יח''', 'אבוקדו 2 יח''', '', '', 16, 5, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(89, 'בטטה 2 יח''', 'בטטה 2 יח''', '', '', 16, 6, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(90, 'פלטת ניגירי לבחירה 6 יח''', 'פלטת ניגירי לבחירה 6 יח''', '', '', 16, 7, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(91, 'טונה', 'טונה', '', '', 17, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(92, 'דג לבן', 'דג לבן', '', '', 17, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(93, 'סלמון', 'סלמון', '', '', 17, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(102, 'פיוז תה', 'פיוז תה', '', '', 18, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(103, 'לימונדה', 'לימונדה', '', '', 18, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(104, 'תפוזים', 'תפוזים', '', '', 18, 2, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(94, 'מים מינרלים 500 מ״ל', 'מים מינרלים 500 מ״ל', '', '', 18, 3, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(95, 'סודה', 'סודה', '', '', 18, 4, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(96, 'מים מוגזים 750 מ״ל', 'מים מוגזים 750 מ״ל', '', '', 18, 5, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(97, 'קוקה קולה', 'קוקה קולה', '', '', 18, 6, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(98, 'קולה זירו', 'קולה זירו', '', '', 18, 7, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(99, 'ספרייט', 'ספרייט', '', '', 18, 8, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(100, 'פאנטה', 'פאנטה', '', '', 18, 9, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(101, 'ענבים', 'ענבים', '', '', 18, 10, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(105, 'ג''ינג''ר אייל', 'ג''ינג''ר אייל', '', '', 18, 11, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(106, 'ספייסי ג''ינג''ר', 'ספייסי ג''ינג''ר', '', '', 18, 12, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(107, 'אשכוליות ורודה', 'אשכוליות ורודה', '', '', 18, 13, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(108, 'טוניק', 'טוניק', '', '', 18, 14, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(109, 'בירה שחורה', 'בירה שחורה', '', '', 18, 15, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(110, 'אספרסו קצר/ארוך', 'אספרסו קצר/ארוך', '', '', 19, 0, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(111, 'אספרסו כפול', 'אספרסו כפול', '', '', 19, 1, NULL) ON CONFLICT (id) DO NOTHING;

INSERT INTO menu_items (id, name_he, name_en, description_he, description_en, category_id, display_order, image_path) VALUES
(112, 'חליטת תה', 'חליטת תה', '', '', 19, 2, NULL) ON CONFLICT (id) DO NOTHING;


-- ========================================
-- RESET SEQUENCES
-- ========================================
SELECT setval('site_settings_id_seq', 1, true);
SELECT setval('branches_id_seq', 2, true);
SELECT setval('reservation_settings_id_seq', 1, true);
SELECT setval('admin_users_id_seq', 1, true);
SELECT setval('menu_settings_id_seq', 1, true);
SELECT setval('roles_id_seq', 7, true);
SELECT setval('menu_categories_id_seq', (SELECT MAX(id) FROM menu_categories), true);
SELECT setval('menu_items_id_seq', (SELECT MAX(id) FROM menu_items), true);
SELECT setval('gallery_photos_id_seq', 17, true);
SELECT setval('catering_gallery_images_id_seq', 5, true);

-- ========================================
-- ✅ PRODUCTION DATABASE SETUP COMPLETE!
-- ========================================
-- Your production site now has:
-- ✓ Logo & Hero Image
-- ✓ About Text (Hebrew & English)
-- ✓ Karmiel Branch Phone (0777392707)
-- ✓ Reservation Link (https://tbit.be/BHWCPU)
-- ✓ Admin Login (khalilshiban / Winston35!)
-- ✓ 10 Menu Categories
-- ✓ 88 Menu Items (Dishes)
-- ✓ 17 Gallery Photos
-- ✓ 5 Catering Images
-- ========================================
