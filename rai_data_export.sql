pg_dump: warning: there are circular foreign-key constraints on this table:
pg_dump: detail: cost_categories
pg_dump: hint: You might not be able to restore the dump without using --disable-triggers or temporarily dropping the constraints.
pg_dump: hint: Consider using a full dump instead of a --data-only dump to avoid this problem.
--
-- PostgreSQL database dump
--

-- Dumped from database version 16.11 (b740647)
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.admin_users VALUES (1, 'khalilshiban', 'khalil@sumo.com', 'scrypt:32768:8:1$mZLASnK16agbrOoN$60029896d6f0e210859fe740efa4d95d3a6f4242e1da3b5f717127e724d06afef743a939e9e215db6780537aa2c220c1923e1cb14c08247eda766247774626ee', true, true, '2025-09-05 09:09:36.651248', NULL);
INSERT INTO public.admin_users VALUES (3, 'Khalilshiban', 'admin@sumo.com', 'scrypt:32768:8:1$3hjtdtNdFgwGuu1R$4c1939074c1b18e2f85dca5c93e5b99caf43ec7d7f4cbad7eb0f35a82e119bc81a5bdec262b003192b4ea8ce3c42a5e780f49076c6dac51e8f439a83acaca48e', true, true, '2025-11-13 08:28:31.990557', NULL);
INSERT INTO public.admin_users VALUES (4, 'testuser123', 'testuser@example.com', 'scrypt:32768:8:1$pTL9M5RPl0WgfWyn$107ddb65afda630dbd31557fc557a4dbaf2cd2e06a99c613a34a83b0ef0102ebc91a17977f9e4ec9e905383445f6f29577abe658592e54df4c1813493d3a9746', true, false, '2025-11-15 11:17:34.966364', NULL);
INSERT INTO public.admin_users VALUES (5, 'testadmin', 'testadmin@example.com', 'scrypt:32768:8:1$sGAb6YlVyu4nULKv$fcd17a7f8b7e15a0025f8d2bff03000defbf5e49d37844052eed4d5a6f63614da248bb5b4c033736bae727ee16448b43a18921c2ae8b3de0c177ecfd9c81df77', true, true, NULL, NULL);
INSERT INTO public.admin_users VALUES (6, 'testuser', 'testuser@test.com', 'scrypt:32768:8:1$PCy1pErd1sCGKjna$6801eaa2000faa7ba123ad6c02b8b1289ca957db1ebfd71a2e9b025db4e3ea16057e26955692d26bed1f76c9d785665990b5e8f9a22c89ec5e9360f49f70312d', true, false, '2025-12-08 21:33:06.07349', NULL);


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.audit_logs VALUES (1, 'stock_item', 2, 'update', 3, '2025-11-13 13:20:20.395576', 'null', '{"source": "web", "ip_address": "172.31.96.194", "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36", "method": "POST", "endpoint": "admin.edit_stock_item"}');
INSERT INTO public.audit_logs VALUES (2, 'stock_item', 2, 'update', 3, '2025-11-13 13:23:00.702504', 'null', '{"source": "web", "ip_address": "172.31.96.194", "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36", "method": "POST", "endpoint": "admin.edit_stock_item"}');
INSERT INTO public.audit_logs VALUES (3, 'stock_item', 2, 'update', 3, '2025-11-13 13:26:48.224079', 'null', '{"source": "web", "ip_address": "172.31.96.194", "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36", "method": "POST", "endpoint": "admin.edit_stock_item"}');


--
-- Data for Name: branches; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.branches VALUES (1, 'ראמה', 'Ramah', '', '', '0506088883', '', 'https://waze.com/ul/hsvc5ksnm1', '', true, 1, NULL);
INSERT INTO public.branches VALUES (2, 'כרמיאל', 'Karmiel', 'גן העיר', '', '0777392707', 'office@sumo-rest.co.il', '', '', true, 0, NULL);


--
-- Data for Name: branch_config; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: career_positions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.career_positions VALUES (1, 'שף מנוסה', 'Experienced Chef', 'מחפשים שף מנוסה למטבח אסייתי', 'Looking for an experienced chef for Asian kitchen', 'ניסיון של 3 שנים, יכולת עבודה בצוות', '3 years experience, team player', 'כרמיאל', 'Karmiel', 'משרה מלאה', 'Full Time', true, 0, '2025-11-05 22:15:19.284105', '2025-11-05 22:15:19.284109');


--
-- Data for Name: career_contacts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.career_contacts VALUES (1, 'חליל שיבאן', 'khalilshiban@gmail.com', '0526647778', 1, NULL, 'dfdfdfdf', NULL, true, '2025-11-11 13:29:06.643506');
INSERT INTO public.career_contacts VALUES (2, 'חליל שיבאן', 'khalilshiban@gmail.com', '0526647778', 1, NULL, 'erdrxfdf', NULL, false, '2025-11-21 11:36:40.282917');
INSERT INTO public.career_contacts VALUES (3, 'חליל שיבאן', 'khalilshiban@gmail.com', '0526647778', 1, NULL, 'sdfsdfsdfsdfsdf', NULL, false, '2025-11-21 11:39:44.810743');


--
-- Data for Name: catering_contacts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catering_contacts VALUES (1, 'חליל שיבאן', 'khalilshiban@gmail.com', '0526647778', NULL, 'wedding', NULL, 'sdfsfsdfsdfsfsdfsdf', false, '2025-11-21 11:40:04.197146');


--
-- Data for Name: catering_gallery_images; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catering_gallery_images VALUES (7, '/static/uploads/catering_20251203_222600_211738_image00027.jpg', '', '', 'אירוע פרטי במסעדת ראי - אולם אירועים מיוחד', 'Private event at Rai Restaurant - Special event hall', true, 0, '2025-12-03 22:26:00.928442');
INSERT INTO public.catering_gallery_images VALUES (8, '/static/uploads/catering_20251203_222648_202046_image00064.jpg', '', '', 'ארוחת ערב עסקית בחדר פרטי עם מסך וטלוויזיה', 'Business dinner in private room with screen and TV', true, 1, '2025-12-03 22:26:48.56317');
INSERT INTO public.catering_gallery_images VALUES (9, '/static/uploads/catering_20251203_222735_531263_WhatsApp_Image_2021-12-01_at_10.37.40.jpg', '', '', 'חתונה קטנה באווירה אינטימית במסעדת ראי', 'Intimate small wedding at Rai Restaurant', true, 2, '2025-12-03 22:27:35.796342');
INSERT INTO public.catering_gallery_images VALUES (10, '/static/uploads/catering_20251203_222825_317666_Rai_IMG_8714.jpg', '', '', 'אירוע אירוסין ומסיבת שמחה במסעדה', 'Engagement party and celebration event at restaurant', true, 3, '2025-12-03 22:28:26.103182');
INSERT INTO public.catering_gallery_images VALUES (11, '/static/uploads/catering_20251203_222855_820633_Rai_IMG_8914.jpg', '', '', 'עריכת שולחנות לאירוע פרטי במסעדת ראי', 'Table setup for private event at Rai Restaurant', true, 4, '2025-12-03 22:28:56.54178');
INSERT INTO public.catering_gallery_images VALUES (12, '/static/uploads/catering_20251203_222924_410606_Rai_IMG_9019.jpg', '', '', 'אווירה רומנטית לאירועים מיוחדים', 'Romantic atmosphere for special events', true, 5, '2025-12-03 22:29:25.077323');
INSERT INTO public.catering_gallery_images VALUES (13, '/static/uploads/catering_20251203_223005_015486_image00057.jpg', '', '', 'מנות גורמה לאירועים וחגיגות', 'Gourmet dishes for events and celebrations', true, 6, '2025-12-03 22:30:05.414003');


--
-- Data for Name: catering_highlights; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catering_highlights VALUES (1, 'תפריטים מותאמים אישית', 'Custom Menus', 'נעצב תפריט מושלם במיוחד עבור האירוע שלכם, עם מגוון רחב של מנות אסייתיות אותנטיות', 'We design the perfect menu specifically for your event, with a wide variety of authentic Asian dishes', 'fa-utensils', true, 1, NULL, NULL);
INSERT INTO public.catering_highlights VALUES (2, 'שירות מקצועי', 'Professional Service', 'צוות מנוסה ומקצועי שידאג לכל פרט כדי להפוך את האירוע שלכם למושלם', 'Experienced professional team that takes care of every detail to make your event perfect', 'fa-star', true, 2, NULL, NULL);
INSERT INTO public.catering_highlights VALUES (3, 'איכות ללא פשרות', 'Uncompromising Quality', 'משתמשים רק במרכיבים הטריים והטובים ביותר לכל מנה', 'Using only the freshest and finest ingredients for every dish', 'fa-medal', true, 3, NULL, NULL);
INSERT INTO public.catering_highlights VALUES (4, 'גמישות מלאה', 'Full Flexibility', 'מתאימים את עצמנו לצרכים שלכם - כמות, זמן ומיקום', 'We adapt to your needs - quantity, timing and location', 'fa-clock', true, 4, NULL, NULL);
INSERT INTO public.catering_highlights VALUES (5, 'מחירים תחרותיים', 'Competitive Pricing', 'מחירים הוגנים וללא עלויות נסתרות', 'Fair prices with no hidden costs', 'fa-tags', true, 5, NULL, NULL);
INSERT INTO public.catering_highlights VALUES (6, 'ניסיון עשיר', 'Rich Experience', 'מעל 10 שנות ניסיון באספקת קייטרינג לאירועים מכל הסוגים', 'Over 10 years of experience providing catering for all types of events', 'fa-award', true, 6, NULL, NULL);


--
-- Data for Name: catering_packages; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catering_packages VALUES (1, 'חבילת כסף', 'Silver Package', 'חבילה מושלמת לאירועים קטנים ואינטימיים. כוללת מגוון מנות אסייתיות קלאסיות', 'Perfect package for small intimate events. Includes a variety of classic Asian dishes', '₪120-150 לאורח', '₪120-150 per person', 20, 50, '3 מנות ראשונות
5 מנות עיקריות
2 קינוחים
שתייה חמה', '3 appetizers
5 main courses
2 desserts
Hot beverages', NULL, true, false, 1, NULL, NULL);
INSERT INTO public.catering_packages VALUES (2, 'חבילת זהב', 'Gold Package', 'החבילה המומלצת שלנו לאירועים בינוניים. כוללת מבחר עשיר של המנות הטובות ביותר שלנו', 'Our recommended package for medium-sized events. Includes a rich selection of our best dishes', '₪180-220 לאורח', '₪180-220 per person', 30, 100, '5 מנות ראשונות
8 מנות עיקריות
3 קינוחים
שתייה חמה וקרה
קישוטי שולחן', '5 appetizers
8 main courses
3 desserts
Hot and cold beverages
Table decorations', NULL, true, true, 2, NULL, NULL);
INSERT INTO public.catering_packages VALUES (3, 'חבילת פלטינום', 'Platinum Package', 'החבילה היוקרתית ביותר שלנו. חוויה קולינרית מושלמת עם כל המנות המיוחדות והאקסקלוסיביות שלנו', 'Our most luxurious package. A perfect culinary experience with all our special and exclusive dishes', '₪250-300 לאורח', '₪250-300 per person', 50, 200, '7 מנות ראשונות
12 מנות עיקריות מובחרות
4 קינוחים יוקרתיים
בר משקאות מלא
תחנת סושי חיה
שירות מלצרים מלא
קישוטי שולחן יוקרתיים', '7 appetizers
12 premium main courses
4 luxury desserts
Full beverage bar
Live sushi station
Full waiter service
Luxury table decorations', NULL, true, false, 3, NULL, NULL);


--
-- Data for Name: task_groups; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.task_groups VALUES (1, 'באנים', 'באנים', 'morning', 'kitchen', '#dc3545', true, 0, '2025-09-05 12:01:36.582099', '2025-09-05 12:01:36.582103');
INSERT INTO public.task_groups VALUES (2, 'הכנות ווק נודלס', 'הכנת לכל סוגי הווק', 'morning', 'kitchen', '#6f42c1', true, 0, '2025-09-05 12:12:21.675656', '2025-09-05 12:12:21.675659');
INSERT INTO public.task_groups VALUES (3, 'הכנות ווק ירקות', 'הכנות ירקות לכל סוגי הווק', 'morning', 'kitchen', '#007bff', true, 0, '2025-09-05 12:14:16.593484', '2025-09-05 12:14:16.593487');
INSERT INTO public.task_groups VALUES (4, 'הכנות ווק יבשים + חלבונים + רטבים לווק', 'הכנות ווק יבשים + חלבונים + רטבים לווק', 'morning', 'kitchen', '#ffc107', true, 0, '2025-09-05 12:17:46.045789', '2025-09-05 12:17:46.045793');
INSERT INTO public.task_groups VALUES (5, 'הכנות סושי ירקות', 'הכנת ירקות לסושי', 'morning', 'kitchen', '#fd7e14', true, 0, '2025-09-09 16:32:59.458373', '2025-09-09 16:32:59.458376');
INSERT INTO public.task_groups VALUES (6, 'הכנות סושי יבשים', 'הכנות סושי יבשים', 'morning', 'kitchen', '#28a745', true, 0, '2025-09-09 16:35:06.205999', '2025-09-09 16:35:06.206003');
INSERT INTO public.task_groups VALUES (7, 'הכנות סושי חלבון', 'הכנות סושי חלבון', 'morning', 'kitchen', '#20c997', true, 0, '2025-09-09 16:37:35.862998', '2025-09-09 16:37:35.863002');
INSERT INTO public.task_groups VALUES (8, 'הכנות סושי רטבים', 'הכנות סושי רטבים', 'morning', 'kitchen', '#28a745', true, 0, '2025-09-09 16:40:56.270215', '2025-09-09 16:40:56.270218');


--
-- Data for Name: checklist_tasks; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.checklist_tasks VALUES (1, 'בצל סגול טבעות', 'באנים - בצל סגול טבעות', 'morning', 'kitchen', 'high', 'daily', true, 0, 1, '2025-09-05 12:01:36.663793', '2025-09-05 12:01:36.663797');
INSERT INTO public.checklist_tasks VALUES (2, 'חסה מסולסלת', 'באנים - חסה מסולסלת', 'morning', 'kitchen', 'high', 'daily', true, 0, 1, '2025-09-05 12:01:36.663798', '2025-09-05 12:01:36.663799');
INSERT INTO public.checklist_tasks VALUES (3, 'שמאגי מבושל', 'באנים - שמאגי מבושל', 'morning', 'kitchen', 'high', 'daily', true, 0, 1, '2025-09-05 12:01:36.6638', '2025-09-05 12:01:36.6638');
INSERT INTO public.checklist_tasks VALUES (4, 'צילי חריף', 'באנים - צילי חריף', 'morning', 'kitchen', 'high', 'daily', true, 0, 1, '2025-09-05 12:01:36.663801', '2025-09-05 12:01:36.663802');
INSERT INTO public.checklist_tasks VALUES (5, 'קולסאלי פיקנטי', 'באנים - קולסאלי פיקנטי', 'morning', 'kitchen', 'high', 'daily', true, 0, 1, '2025-09-05 12:01:36.663803', '2025-09-05 12:01:36.663803');
INSERT INTO public.checklist_tasks VALUES (6, 'אטריות ביצים', 'הכנת לכל סוגי הווק - אטריות ביצים', 'morning', 'kitchen', 'high', 'daily', true, 0, 2, '2025-09-05 12:12:21.753616', '2025-09-05 12:12:21.753619');
INSERT INTO public.checklist_tasks VALUES (7, 'איטריות שחורות', 'הכנת לכל סוגי הווק - איטריות שחורות', 'morning', 'kitchen', 'high', 'daily', true, 0, 2, '2025-09-05 12:12:21.75362', '2025-09-05 12:12:21.75362');
INSERT INTO public.checklist_tasks VALUES (8, 'אטריות תרד', 'הכנת לכל סוגי הווק - אטריות תרד', 'morning', 'kitchen', 'high', 'daily', true, 0, 2, '2025-09-05 12:12:21.753621', '2025-09-05 12:12:21.753621');
INSERT INTO public.checklist_tasks VALUES (9, 'אטריות אורז', 'הכנת לכל סוגי הווק - אטריות אורז', 'morning', 'kitchen', 'high', 'daily', true, 0, 2, '2025-09-05 12:12:21.753622', '2025-09-05 12:12:21.753622');
INSERT INTO public.checklist_tasks VALUES (10, 'אורז לבן/מאודה', 'הכנת לכל סוגי הווק - אורז לבן/מאודה', 'morning', 'kitchen', 'high', 'daily', true, 0, 2, '2025-09-05 12:12:21.753623', '2025-09-05 12:12:21.753623');
INSERT INTO public.checklist_tasks VALUES (11, 'כרוב', 'הכנות ירקות לכל סוגי הווק - כרוב', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673957', '2025-09-05 12:14:16.673961');
INSERT INTO public.checklist_tasks VALUES (12, 'גזר', 'הכנות ירקות לכל סוגי הווק - גזר', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673962', '2025-09-05 12:14:16.673963');
INSERT INTO public.checklist_tasks VALUES (13, 'בצל ירוק', 'הכנות ירקות לכל סוגי הווק - בצל ירוק', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673964', '2025-09-05 12:14:16.673965');
INSERT INTO public.checklist_tasks VALUES (14, 'בצל לבן', 'הכנות ירקות לכל סוגי הווק - בצל לבן', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673965', '2025-09-05 12:14:16.673966');
INSERT INTO public.checklist_tasks VALUES (15, 'נבטים', 'הכנות ירקות לכל סוגי הווק - נבטים', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673967', '2025-09-05 12:14:16.673967');
INSERT INTO public.checklist_tasks VALUES (16, 'פלפל גמבה אדום', 'הכנות ירקות לכל סוגי הווק - פלפל גמבה אדום', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673968', '2025-09-05 12:14:16.673968');
INSERT INTO public.checklist_tasks VALUES (17, 'פטריות פורטבלו', 'הכנות ירקות לכל סוגי הווק - פטריות פורטבלו', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673969', '2025-09-05 12:14:16.67397');
INSERT INTO public.checklist_tasks VALUES (18, 'באק צוי', 'הכנות ירקות לכל סוגי הווק - באק צוי', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673971', '2025-09-05 12:14:16.673971');
INSERT INTO public.checklist_tasks VALUES (19, 'זוקיני', 'הכנות ירקות לכל סוגי הווק - זוקיני', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673972', '2025-09-05 12:14:16.673973');
INSERT INTO public.checklist_tasks VALUES (20, 'ברוקולי', 'הכנות ירקות לכל סוגי הווק - ברוקולי', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673974', '2025-09-05 12:14:16.673974');
INSERT INTO public.checklist_tasks VALUES (21, 'אננס', 'הכנות ירקות לכל סוגי הווק - אננס', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673975', '2025-09-05 12:14:16.673975');
INSERT INTO public.checklist_tasks VALUES (22, 'בזיליקום', 'הכנות ירקות לכל סוגי הווק - בזיליקום', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673976', '2025-09-05 12:14:16.673977');
INSERT INTO public.checklist_tasks VALUES (23, 'כוסברה', 'הכנות ירקות לכל סוגי הווק - כוסברה', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673977', '2025-09-05 12:14:16.673978');
INSERT INTO public.checklist_tasks VALUES (24, 'שום', 'הכנות ירקות לכל סוגי הווק - שום', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.673979', '2025-09-05 12:14:16.673979');
INSERT INTO public.checklist_tasks VALUES (25, 'ג׳ינג׳ר', 'הכנות ירקות לכל סוגי הווק - ג׳ינג׳ר', 'morning', 'kitchen', 'high', 'daily', true, 0, 3, '2025-09-05 12:14:16.67398', '2025-09-05 12:14:16.673981');
INSERT INTO public.checklist_tasks VALUES (26, 'קשיו', 'הכנות ווק יבשים + חלבונים + רטבים לווק - קשיו', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127043', '2025-09-05 12:17:46.127047');
INSERT INTO public.checklist_tasks VALUES (27, 'צילי שטה', 'הכנות ווק יבשים + חלבונים + רטבים לווק - צילי שטה', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127048', '2025-09-05 12:17:46.127048');
INSERT INTO public.checklist_tasks VALUES (28, 'בצל קריספי', 'הכנות ווק יבשים + חלבונים + רטבים לווק - בצל קריספי', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127049', '2025-09-05 12:17:46.127049');
INSERT INTO public.checklist_tasks VALUES (29, 'בשר פרוס', 'הכנות ווק יבשים + חלבונים + רטבים לווק - בשר פרוס', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.12705', '2025-09-05 12:17:46.12705');
INSERT INTO public.checklist_tasks VALUES (30, 'עוף פרוס', 'הכנות ווק יבשים + חלבונים + רטבים לווק - עוף פרוס', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127051', '2025-09-05 12:17:46.127051');
INSERT INTO public.checklist_tasks VALUES (31, 'שרימפס', 'הכנות ווק יבשים + חלבונים + רטבים לווק - שרימפס', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127052', '2025-09-05 12:17:46.127052');
INSERT INTO public.checklist_tasks VALUES (32, 'קלמרי', 'הכנות ווק יבשים + חלבונים + רטבים לווק - קלמרי', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127053', '2025-09-05 12:17:46.127053');
INSERT INTO public.checklist_tasks VALUES (33, 'עוף טמפורה', 'הכנות ווק יבשים + חלבונים + רטבים לווק - עוף טמפורה', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127054', '2025-09-05 12:17:46.127054');
INSERT INTO public.checklist_tasks VALUES (34, 'טופו', 'הכנות ווק יבשים + חלבונים + רטבים לווק - טופו', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127054', '2025-09-05 12:17:46.127055');
INSERT INTO public.checklist_tasks VALUES (35, 'ביצים', 'הכנות ווק יבשים + חלבונים + רטבים לווק - ביצים', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127055', '2025-09-05 12:17:46.127055');
INSERT INTO public.checklist_tasks VALUES (36, 'ציר בקר', 'הכנות ווק יבשים + חלבונים + רטבים לווק - ציר בקר', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127056', '2025-09-05 12:17:46.127056');
INSERT INTO public.checklist_tasks VALUES (37, 'ציר עוף', 'הכנות ווק יבשים + חלבונים + רטבים לווק - ציר עוף', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127057', '2025-09-05 12:17:46.127057');
INSERT INTO public.checklist_tasks VALUES (38, 'סויה', 'הכנות ווק יבשים + חלבונים + רטבים לווק - סויה', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127057', '2025-09-05 12:17:46.127058');
INSERT INTO public.checklist_tasks VALUES (39, 'טריאקי', 'הכנות ווק יבשים + חלבונים + רטבים לווק - טריאקי', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127058', '2025-09-05 12:17:46.127059');
INSERT INTO public.checklist_tasks VALUES (40, 'קארי ירוק', 'הכנות ווק יבשים + חלבונים + רטבים לווק - קארי ירוק', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127059', '2025-09-05 12:17:46.127059');
INSERT INTO public.checklist_tasks VALUES (41, 'קארי אדום', 'הכנות ווק יבשים + חלבונים + רטבים לווק - קארי אדום', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.12706', '2025-09-05 12:17:46.12706');
INSERT INTO public.checklist_tasks VALUES (42, 'חלב קוקוס', 'הכנות ווק יבשים + חלבונים + רטבים לווק - חלב קוקוס', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127061', '2025-09-05 12:17:46.127061');
INSERT INTO public.checklist_tasks VALUES (43, 'תמצית עישון', 'הכנות ווק יבשים + חלבונים + רטבים לווק - תמצית עישון', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127062', '2025-09-05 12:17:46.127063');
INSERT INTO public.checklist_tasks VALUES (44, 'צילי קוריאני', 'הכנות ווק יבשים + חלבונים + רטבים לווק - צילי קוריאני', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127064', '2025-09-05 12:17:46.127064');
INSERT INTO public.checklist_tasks VALUES (45, 'מיץ לימון', 'הכנות ווק יבשים + חלבונים + רטבים לווק - מיץ לימון', 'morning', 'kitchen', 'high', 'daily', true, 0, 4, '2025-09-05 12:17:46.127065', '2025-09-05 12:17:46.127066');
INSERT INTO public.checklist_tasks VALUES (46, 'גזר', 'הכנת ירקות לסושי - גזר', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543026', '2025-09-09 16:32:59.543031');
INSERT INTO public.checklist_tasks VALUES (47, 'מלפפון', 'הכנת ירקות לסושי - מלפפון', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543032', '2025-09-09 16:32:59.543032');
INSERT INTO public.checklist_tasks VALUES (48, 'בטטה אצבעות', 'הכנת ירקות לסושי - בטטה אצבעות', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543033', '2025-09-09 16:32:59.543034');
INSERT INTO public.checklist_tasks VALUES (49, 'בטטה מעטפות', 'הכנת ירקות לסושי - בטטה מעטפות', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543035', '2025-09-09 16:32:59.543035');
INSERT INTO public.checklist_tasks VALUES (50, 'עירית', 'הכנת ירקות לסושי - עירית', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543036', '2025-09-09 16:32:59.543037');
INSERT INTO public.checklist_tasks VALUES (51, 'עירית קצוץ', 'הכנת ירקות לסושי - עירית קצוץ', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543038', '2025-09-09 16:32:59.543038');
INSERT INTO public.checklist_tasks VALUES (52, 'לימון', 'הכנת ירקות לסושי - לימון', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543039', '2025-09-09 16:32:59.54304');
INSERT INTO public.checklist_tasks VALUES (53, 'חסה קצוץ', 'הכנת ירקות לסושי - חסה קצוץ', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543041', '2025-09-09 16:32:59.543041');
INSERT INTO public.checklist_tasks VALUES (54, 'זוקיני', 'הכנת ירקות לסושי - זוקיני', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543042', '2025-09-09 16:32:59.543043');
INSERT INTO public.checklist_tasks VALUES (55, 'אושנקו', 'הכנת ירקות לסושי - אושנקו', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543043', '2025-09-09 16:32:59.543044');
INSERT INTO public.checklist_tasks VALUES (56, 'אספרגוס', 'הכנת ירקות לסושי - אספרגוס', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543044', '2025-09-09 16:32:59.543044');
INSERT INTO public.checklist_tasks VALUES (57, 'אבוקדו', 'הכנת ירקות לסושי - אבוקדו', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543045', '2025-09-09 16:32:59.543045');
INSERT INTO public.checklist_tasks VALUES (58, 'חלפיניו', 'הכנת ירקות לסושי - חלפיניו', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543045', '2025-09-09 16:32:59.543046');
INSERT INTO public.checklist_tasks VALUES (59, 'צ׳יפס', 'הכנת ירקות לסושי - צ׳יפס', 'morning', 'kitchen', 'high', 'daily', true, 0, 5, '2025-09-09 16:32:59.543046', '2025-09-09 16:32:59.543047');
INSERT INTO public.checklist_tasks VALUES (60, 'שומשום שחור', 'הכנות סושי יבשים - שומשום שחור', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295233', '2025-09-09 16:35:06.295238');
INSERT INTO public.checklist_tasks VALUES (61, 'שומשום סויה', 'הכנות סושי יבשים - שומשום סויה', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295239', '2025-09-09 16:35:06.29524');
INSERT INTO public.checklist_tasks VALUES (62, 'תוגראשי', 'הכנות סושי יבשים - תוגראשי', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295241', '2025-09-09 16:35:06.295242');
INSERT INTO public.checklist_tasks VALUES (63, 'בוטנים', 'הכנות סושי יבשים - בוטנים', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295243', '2025-09-09 16:35:06.295243');
INSERT INTO public.checklist_tasks VALUES (64, 'בצל קריספי', 'הכנות סושי יבשים - בצל קריספי', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295244', '2025-09-09 16:35:06.295245');
INSERT INTO public.checklist_tasks VALUES (65, 'טמפורה קריספי', 'הכנות סושי יבשים - טמפורה קריספי', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295246', '2025-09-09 16:35:06.295246');
INSERT INTO public.checklist_tasks VALUES (66, 'פנקו סגול', 'הכנות סושי יבשים - פנקו סגול', 'morning', 'kitchen', 'high', 'daily', true, 0, 6, '2025-09-09 16:35:06.295247', '2025-09-09 16:35:06.295248');
INSERT INTO public.checklist_tasks VALUES (67, 'סלמון נא', 'הכנות סושי חלבון - סלמון נא', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937939', '2025-09-09 16:37:35.937943');
INSERT INTO public.checklist_tasks VALUES (68, 'סלמון קפוא', 'הכנות סושי חלבון - סלמון קפוא', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937944', '2025-09-09 16:37:35.937945');
INSERT INTO public.checklist_tasks VALUES (69, 'סלמון צלוי', 'הכנות סושי חלבון - סלמון צלוי', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937946', '2025-09-09 16:37:35.937946');
INSERT INTO public.checklist_tasks VALUES (70, 'טונה אדומה', 'הכנות סושי חלבון - טונה אדומה', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937947', '2025-09-09 16:37:35.937948');
INSERT INTO public.checklist_tasks VALUES (71, 'סורימי', 'הכנות סושי חלבון - סורימי', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937949', '2025-09-09 16:37:35.937949');
INSERT INTO public.checklist_tasks VALUES (72, 'דג לבן', 'הכנות סושי חלבון - דג לבן', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.93795', '2025-09-09 16:37:35.93795');
INSERT INTO public.checklist_tasks VALUES (73, 'טוביקו שחור', 'הכנות סושי חלבון - טוביקו שחור', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937951', '2025-09-09 16:37:35.937952');
INSERT INTO public.checklist_tasks VALUES (74, 'טוביקו אדום', 'הכנות סושי חלבון - טוביקו אדום', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937953', '2025-09-09 16:37:35.937954');
INSERT INTO public.checklist_tasks VALUES (75, 'סביצה דג לבן', 'הכנות סושי חלבון - סביצה דג לבן', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937955', '2025-09-09 16:37:35.937955');
INSERT INTO public.checklist_tasks VALUES (76, 'סביצה טונה חריף', 'הכנות סושי חלבון - סביצה טונה חריף', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937956', '2025-09-09 16:37:35.937957');
INSERT INTO public.checklist_tasks VALUES (77, 'שרימפס דוריטוס', 'הכנות סושי חלבון - שרימפס דוריטוס', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937958', '2025-09-09 16:37:35.937958');
INSERT INTO public.checklist_tasks VALUES (78, 'סורימי קצוץ', 'הכנות סושי חלבון - סורימי קצוץ', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.937959', '2025-09-09 16:37:35.93796');
INSERT INTO public.checklist_tasks VALUES (79, 'טופו', 'הכנות סושי חלבון - טופו', 'morning', 'kitchen', 'high', 'daily', true, 0, 7, '2025-09-09 16:37:35.93796', '2025-09-09 16:37:35.937961');
INSERT INTO public.checklist_tasks VALUES (80, 'ספייסי מיונז', 'הכנות סושי רטבים - ספייסי מיונז', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352279', '2025-09-09 16:40:56.352284');
INSERT INTO public.checklist_tasks VALUES (81, 'איולי יוזו', 'הכנות סושי רטבים - איולי יוזו', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352285', '2025-09-09 16:40:56.352285');
INSERT INTO public.checklist_tasks VALUES (82, 'טריאקי', 'הכנות סושי רטבים - טריאקי', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352286', '2025-09-09 16:40:56.352287');
INSERT INTO public.checklist_tasks VALUES (83, 'סריראצה', 'הכנות סושי רטבים - סריראצה', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352287', '2025-09-09 16:40:56.352288');
INSERT INTO public.checklist_tasks VALUES (84, 'גבינת שמנת', 'הכנות סושי רטבים - גבינת שמנת', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352288', '2025-09-09 16:40:56.352288');
INSERT INTO public.checklist_tasks VALUES (85, 'גבינת כמיהין', 'הכנות סושי רטבים - גבינת כמיהין', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352289', '2025-09-09 16:40:56.352289');
INSERT INTO public.checklist_tasks VALUES (86, 'יוזו קשיו', 'הכנות סושי רטבים - יוזו קשיו', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.35229', '2025-09-09 16:40:56.35229');
INSERT INTO public.checklist_tasks VALUES (87, 'גבינת גאודה', 'הכנות סושי רטבים - גבינת גאודה', 'morning', 'kitchen', 'high', 'daily', true, 0, 8, '2025-09-09 16:40:56.352291', '2025-09-09 16:40:56.352291');


--
-- Data for Name: contact_messages; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.contact_messages VALUES (1, 'חליל שיבאן', 'khalilshiban@gmail.com', '0526647778', 'dfgsdfgsdfgdfg', false, '2025-11-21 11:39:25.217394');


--
-- Data for Name: cost_categories; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: file_imports; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.suppliers VALUES (1, 'שופרסל סיטונאות', 'משה כהן', '04-9876543', 'orders@shufersal.co.il', 'רחוב התעשייה 15, כרמיאל', 'Sun,Tue,Thu', NULL, 500, 'NET30', NULL, true, NULL);
INSERT INTO public.suppliers VALUES (2, 'מחסני השף', 'דינה לוי', '04-9567890', 'orders@chef-wh.co.il', 'אזור התעשייה אכסל, עכו', 'Mon,Wed,Fri', NULL, 300, 'NET14', NULL, true, NULL);
INSERT INTO public.suppliers VALUES (3, 'טבע טעמים', 'יוסי אברהם', '04-8765432', 'sales@nature.co.il', 'רחוב הגליל 22, נהריה', 'Tue,Thu', NULL, 200, 'CASH', NULL, true, NULL);
INSERT INTO public.suppliers VALUES (4, 'ניקיון ירוק', 'מירי דוד', '04-7654321', 'info@green.co.il', 'רחוב המלאכה 8, חיפה', 'Mon,Thu', NULL, 150, 'NET7', NULL, true, NULL);
INSERT INTO public.suppliers VALUES (5, 'אריזות הצפון', 'רונן ברק', '04-6543210', 'orders@north.co.il', 'רחוב התעשייה 45, קריית שמונה', 'Wed,Fri', NULL, 400, 'NET21', NULL, true, NULL);
INSERT INTO public.suppliers VALUES (6, 'משק הירקות הטריים', 'דוד כהן', '050-1234567', 'david@fresh-veggies.co.il', 'קיבוץ דן, עמק החולה', '1111100', '6:00-10:00', 500, '30 ימים', 'ירקות טריים מהמשק', true, '2025-09-08 20:58:44.983679');
INSERT INTO public.suppliers VALUES (8, 'בשרים איכותיים בע"מ', 'משה אברהם', '052-5555555', 'moshe@quality-meat.co.il', 'אזור התעשייה, אשקלון', '0111110', '7:00-14:00', 1000, '45 ימים', 'בשרים טריים וקפואים באיכות גבוהה', true, '2025-09-08 20:58:44.983679');
INSERT INTO public.suppliers VALUES (9, 'מאפיית הזהב', 'שרה פרידמן', '053-7777777', 'sara@golden-bakery.co.il', 'רחוב הרצל 25, תל אביב', '1111110', '5:00-12:00', 150, 'שוטף + 30', 'לחמים ומאפים טריים מדי בוקר', true, '2025-09-08 20:58:44.983679');
INSERT INTO public.suppliers VALUES (11, 'Shshsh', '', '', '', NULL, '1111111', NULL, 0, NULL, NULL, true, '2025-11-13 10:16:21.086124');


--
-- Data for Name: receipts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.receipts VALUES (2, 'static/uploads/receipts/20251112_122547_20250129_153746.jpg', '20250129_153746.jpg', 3783665, NULL, 1, NULL, NULL, NULL, NULL, 'ILS', 'failed', NULL, NULL, false, NULL, NULL, NULL, 'OpenAI quota exceeded', '2025-11-12 12:25:47.056236', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (10, 'static/uploads/receipts/20251112_225753_1000132000.jpg', '1000132000.jpg', 211738, NULL, 1, '2023-09-14', NULL, 6944, NULL, 'ILS', 'completed', '{"supplier_name": "\u05de\u05d6\u05e8\u05d7 \u05d5\u05de\u05e2\u05e8\u05d1 \u05d9\u05d1\u05d5\u05d0 \u05d5\u05e9\u05d9\u05d5\u05d5\u05e7 \u05d1\u05e2\"\u05de", "receipt_date": "2023-09-14", "total_amount": 6944.0, "items": [{"product_name": "\u05e9\u05de\u05df \u05e9\u05d5\u05de\u05e9\u05d5\u05dd \u05d8\u05d4\u05d5\u05e8 2 \u05dc\u05d9\u05d8\u05e8", "quantity": 4.0, "unit_price": 80.0, "total_price": 320.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 6.0, "unit_price": 13.4, "total_price": 80.4, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 5.0, "unit_price": 13.0, "total_price": 65.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 5.0, "unit_price": 12.6, "total_price": 63.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 5.0, "unit_price": 12.0, "total_price": 60.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 5.0, "unit_price": 11.0, "total_price": 55.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 32.5, "total_price": 65.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 3.0, "unit_price": 15.0, "total_price": 45.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 40.0, "total_price": 80.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 40.0, "total_price": 80.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 1140.0, "total_price": 2280.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "unit": "\u05de\"\u05dc"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-12 22:57:53.628362', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (11, 'static/uploads/receipts/20251113_081734_1000131962.jpg', '1000131962.jpg', 274473, NULL, 2, '2023-08-30', NULL, 4781.57, NULL, 'ILS', 'completed', '{"supplier_name": "\u05d4\u05db\u05e8\u05dd", "receipt_date": "2023-08-30", "total_amount": 4781.57, "items": [{"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}, {"product_name": "\u05d1\u05e7\u05d1\u05d5\u05e7 \u05d6\u05db\u05d5\u05db\u05d9\u05ea 330 \u05de\"\u05dc", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "unit": "\u05d1\u05e7\u05d1\u05d5\u05e7"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-13 08:17:35.00502', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (8, 'static/uploads/receipts/20251112_124620_20250129_153746.jpg', '20250129_153746.jpg', 3783665, NULL, 1, '2023-01-29', NULL, 1375, NULL, 'ILS', 'completed', '{"supplier_name": "\u05e8\u05d9\u05e7\u05d5\u05e1 \u05e6''\u05d5\u05d9\u05e1", "receipt_date": "2023-01-29", "total_amount": 1375.0, "items": [{"product_name": "\u05d2\u05de\u05d5\u05df \u05dc\u05d1\u05df \u05db\u05e3 \u05d0\u05d3\u05d5\u05d5\u05d9\u05e1 15 \u05e7\"\u05d2", "quantity": 2.0, "unit_price": 194.07, "total_price": 388.14, "unit": "\u05e7\u05f4\u05d2"}, {"product_name": "\u05d2\u05de\u05d5\u05df \u05dc\u05d1\u05df \u05db\u05e3 \u05d0\u05d3\u05d5\u05d5\u05d9\u05e1 15 \u05e7\"\u05d2", "quantity": 1.0, "unit_price": 185.59, "total_price": 185.59, "unit": "\u05e7\u05f4\u05d2"}, {"product_name": "\u05d1\u05ea\u05e2\u05e8\u05d5\u05d1\u05ea \u05db\u05d1\u05e9 \u05dc\u05db\u05dc\u05d1 10 \u05e7\"\u05d2", "quantity": 2.0, "unit_price": 295.76, "total_price": 591.52, "unit": "\u05e7\u05f4\u05d2"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-12 12:46:20.660898', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (9, 'static/uploads/receipts/20251112_162012_1000132000.jpg', '1000132000.jpg', 211738, NULL, 1, '2023-09-14', NULL, 6944, NULL, 'ILS', 'completed', '{"supplier_name": "\u05de\u05d6\u05e8\u05d7 \u05d5\u05de\u05e2\u05e8\u05d1 \u05d9\u05d1\u05d5\u05d0 \u05d5\u05e9\u05d9\u05d5\u05d5\u05e7 \u05d1\u05e2\"\u05de", "receipt_date": "2023-09-14", "total_amount": 6944.0, "items": [{"product_name": "\u05de\u05e9\u05d7\u05ea \u05e7\u05d0\u05e8\u05d9 \u05d0\u05d3\u05d5\u05dd 1 \u05e7\"\u05d2", "quantity": 4.0, "unit_price": 80.0, "total_price": 320.0, "unit": "\u05e7\u05f4\u05d2"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 500 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 65.0, "total_price": 130.0, "unit": "\u05de\u05f4\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 1 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 60.0, "total_price": 120.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 1.8 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 5 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 20 \u05dc\u05d9\u05d8\u05e8", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 540 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "unit": "\u05de\u05f4\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 1.8 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 5 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 20 \u05dc\u05d9\u05d8\u05e8", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 540 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "unit": "\u05de\u05f4\u05dc"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 1.8 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 5 \u05dc\u05d9\u05d8\u05e8", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 20 \u05dc\u05d9\u05d8\u05e8", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "unit": "\u05dc\u05d9\u05d8\u05e8"}, {"product_name": "\u05d7\u05d5\u05de\u05e5 \u05d0\u05d5\u05e8\u05d6 540 \u05de\"\u05dc", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "unit": "\u05de\u05f4\u05dc"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-12 16:20:12.621464', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (15, 'static/uploads/receipts/20251113_192438_17630618617051079157495073920663.jpg', '17630618617051079157495073920663.jpg', 1367777, NULL, 2, '2025-11-13', NULL, NULL, NULL, 'ILS', 'completed', '{"supplier_name": "\u05d4\u05d7\u05d1\u05e8\u05d4 \u05d4\u05de\u05e8\u05db\u05d6\u05d9\u05ea \u05dc\u05d4\u05e4\u05e6\u05ea \u05de\u05e9\u05e7\u05d0\u05d5\u05ea \u05d1\u05e2\"\u05de", "supplier_phone": "054-2899005", "supplier_email": "moked.sherut@cocacola.co.il", "supplier_address": "\u05ea.\u05d3 555, \u05e4\u05ea\u05d7 \u05ea\u05e7\u05d5\u05d4 4911401", "supplier_contact_person": null, "receipt_date": "2025-11-13", "total_amount": 0.0, "items": [{"product_name": "\u05e7\u05d5\u05e7\u05d4 \u05e7\u05d5\u05dc\u05d4 \u05e7\u05dc\u05d0\u05e1\u05d9 350 \u05de\"\u05dc", "quantity": 4, "unit_price": 0.0, "total_price": 0.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05e1\u05e4\u05e8\u05d9\u05d9\u05d8 \u05d1\u05e7\u05d1\u05d5\u05e7 330 \u05de\"\u05dc", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05e7\u05d5\u05e7\u05d4 \u05e7\u05d5\u05dc\u05d4 ZERO \u05e7\u05dc\u05d0\u05e1\u05d9 350 \u05de\"\u05dc", "quantity": 5, "unit_price": 0.0, "total_price": 0.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05ea\u05d4 FUZE \u05d1\u05e7\u05d1\u05d5\u05e7 330 \u05de\"\u05dc", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "unit": "\u05de\"\u05dc"}, {"product_name": "\u05e7\u05d5\u05e7\u05d4 \u05e7\u05d5\u05dc\u05d4 \u05e7\u05dc\u05d0\u05e1\u05d9 350 \u05de\"\u05dc", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "unit": "\u05de\"\u05dc"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-13 19:24:38.120174', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (12, '/tmp/test_receipt.jpg', 'test_receipt.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'ILS', 'pending', NULL, NULL, false, NULL, NULL, NULL, NULL, '2025-11-13 08:30:56.61292', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (13, 'static/uploads/receipts/20251113_095814_image-2230935222166988882.jpg', 'image-2230935222166988882.jpg', 1358521, NULL, 1, '2025-11-13', NULL, 1182, NULL, 'ILS', 'completed', '{"supplier_name": "\u05e1\u05d5\u05e4\u05e8\u05e0\u05d5\u05d1\u05d4 \u05d1\u05e2\"\u05de", "receipt_date": "2025-11-13", "total_amount": 1182.0, "items": [{"product_name": "GAMMA \u05e1\u05e8\u05d2\u05dc \u05d6\u05d5\u05d5\u05d9\u05ea", "quantity": 84.0, "unit_price": 8.5, "total_price": 714.0, "unit": "\u05d9\u05d7\u05d9\u05d3\u05d5\u05ea"}, {"product_name": "\u05d3\u05d1\u05e7 \u05d0\u05e7\u05e8\u05d9\u05dc\u05d9 \u05d3\u05d2\u05dd \u05d4\u05d5\u05e8\u05e1", "quantity": 72.0, "unit_price": 4.0, "total_price": 288.0, "unit": "\u05d9\u05d7\u05d9\u05d3\u05d5\u05ea"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-13 09:58:14.543241', NULL, NULL, NULL);
INSERT INTO public.receipts VALUES (14, 'static/uploads/receipts/20251113_095906_17630279325267814430604387202240.jpg', '17630279325267814430604387202240.jpg', 1316459, 11, 1, '2025-11-13', NULL, 1182, NULL, 'ILS', 'completed', '{"supplier_name": "\u05e1\u05d5\u05e4\u05e8\u05e0\u05d5\u05d1\u05d4 \u05d1\u05e2\"\u05de", "receipt_date": "2025-11-13", "total_amount": 1182.0, "items": [{"product_name": "\u05e1\u05db\u05d9\u05df \u05e9\u05d5\u05dc\u05d7\u05df \u05d3\u05d2\u05dd GAMMA", "quantity": 84.0, "unit_price": 8.5, "total_price": 714.0, "unit": "\u05d9\u05d7\u05d9\u05d3\u05d5\u05ea"}, {"product_name": "\u05de\u05d6\u05dc\u05d2 \u05d0\u05e8\u05d5\u05d7\u05d4 \u05d3\u05d2\u05dd \u05e9\u05d5\u05dc\u05d7\u05df \u05d3\u05d2\u05dd", "quantity": 72.0, "unit_price": 4.0, "total_price": 288.0, "unit": "\u05d9\u05d7\u05d9\u05d3\u05d5\u05ea"}]}', NULL, false, NULL, NULL, NULL, NULL, '2025-11-13 09:59:06.57564', NULL, NULL, NULL);


--
-- Data for Name: cost_entries; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: custom_field_definitions; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: custom_field_assignments; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: custom_sections; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: customer_addresses; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: delivery_zones; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: drivers; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: delivery_assignments; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: dietary_properties; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.dietary_properties VALUES (2, 'טבעוני', 'Vegan', 'leaf', '#28a745', 'צמחוני לחלוטין ללא מרכיבים מהחי', 'Completely plant-based, no animal ingredients', true, 0, '2025-09-30 10:17:35.118799');
INSERT INTO public.dietary_properties VALUES (1, 'צמחוני', 'Vegetarian', 'leaf', '#28a745', 'מנת צמחונים בלבד', 'Vegetarian option', true, 0, '2025-09-27 04:50:50.441575');
INSERT INTO public.dietary_properties VALUES (3, 'ללא גלוטן', 'Gluten free', 'ban', '#f50a0a', '', '', true, 0, '2025-10-30 11:24:54.135924');


--
-- Data for Name: driver_shifts; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: event_page_analytics; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.event_page_analytics VALUES (1, 'test_click', 'click', '2025-12-04 10:36:16.090938', 'curl/8.14.1', '', '');
INSERT INTO public.event_page_analytics VALUES (2, 'celebrations', 'click', '2025-12-04 10:39:49.987803', 'Mozilla/5.0 (Linux; Android 16; SM-S908E Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.171 Mobile Safari/537.36 Replit-Bonsai/2.155.0 (Android 16)', 'https://32298b58-b7f6-42dd-ad25-0ced079221ec-00-q1urz2278g7o.pike.replit.dev/events', 'eyJfZnJlc2giOmZhbHNlLCJjc3JmX3Rva2VuIjoiMWVhOTdmNjYwMWYyNTFjNmYzNjM3MTk0ZmNiNjU3MWVjZGQzNDM0ZiJ9.aSX');
INSERT INTO public.event_page_analytics VALUES (3, 'private_room', 'click', '2025-12-04 10:40:19.59331', 'Mozilla/5.0 (Linux; Android 16; SM-S908E Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.171 Mobile Safari/537.36 Replit-Bonsai/2.155.0 (Android 16)', 'https://32298b58-b7f6-42dd-ad25-0ced079221ec-00-q1urz2278g7o.pike.replit.dev/events', 'eyJfZnJlc2giOmZhbHNlLCJjc3JmX3Rva2VuIjoiMWVhOTdmNjYwMWYyNTFjNmYzNjM3MTk0ZmNiNjU3MWVjZGQzNDM0ZiJ9.aSX');
INSERT INTO public.event_page_analytics VALUES (4, 'gallery_5', 'click', '2025-12-04 10:56:35.614624', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', 'https://32298b58-b7f6-42dd-ad25-0ced079221ec-00-q1urz2278g7o.pike.replit.dev/events', '.eJxVjktqA0EQQ-_Say_6V11dvsxQX9vEmcBMvAq5exqyshYCPZDQT9ri8POersHP0y9pe1i6pjAuUnCKENfREKGEKJEomjfuNqd');


--
-- Data for Name: gallery_photos; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.gallery_photos VALUES (1, '/static/uploads/gallery_20251030_231751_31.jpg', '', '', 0, true, '2025-10-30 23:17:51.321312');
INSERT INTO public.gallery_photos VALUES (2, '/static/uploads/gallery_20251030_233229_238394_52.jpg', '', '', 1, true, '2025-10-30 23:32:29.513162');
INSERT INTO public.gallery_photos VALUES (3, '/static/uploads/gallery_20251030_233247_334091_42.jpg', '', '', 2, true, '2025-10-30 23:32:47.389637');
INSERT INTO public.gallery_photos VALUES (4, '/static/uploads/gallery_20251030_233254_744270_32.jpg', '', '', 3, true, '2025-10-30 23:32:54.772672');
INSERT INTO public.gallery_photos VALUES (5, '/static/uploads/gallery_20251030_233309_417691_24.jpg', '', '', 4, true, '2025-10-30 23:33:09.452318');
INSERT INTO public.gallery_photos VALUES (6, '/static/uploads/gallery_20251030_233313_718631_75.jpg', '', '', 5, true, '2025-10-30 23:33:13.747517');
INSERT INTO public.gallery_photos VALUES (7, '/static/uploads/gallery_20251030_233327_843961_85.jpg', '', '', 6, true, '2025-10-30 23:33:27.876549');
INSERT INTO public.gallery_photos VALUES (8, '/static/uploads/gallery_20251030_233333_370363_90.jpg', '', '', 7, true, '2025-10-30 23:33:33.399484');
INSERT INTO public.gallery_photos VALUES (9, '/static/uploads/gallery_20251030_233353_707259_107.jpg', '', '', 8, true, '2025-10-30 23:33:53.742537');
INSERT INTO public.gallery_photos VALUES (10, '/static/uploads/gallery_20251030_233419_139106_148.jpg', '', '', 9, true, '2025-10-30 23:34:19.196473');
INSERT INTO public.gallery_photos VALUES (11, '/static/uploads/gallery_20251030_233432_156623_146.jpg', '', '', 10, true, '2025-10-30 23:34:32.200507');
INSERT INTO public.gallery_photos VALUES (12, '/static/uploads/gallery_20251030_233453_686688_136.jpg', '', '', 11, true, '2025-10-30 23:34:53.731499');
INSERT INTO public.gallery_photos VALUES (13, '/static/uploads/gallery_20251030_233500_939110_128.jpg', '', '', 12, true, '2025-10-30 23:35:00.967278');
INSERT INTO public.gallery_photos VALUES (14, '/static/uploads/gallery_20251030_233514_823527_117.jpg', '', '', 13, true, '2025-10-30 23:35:14.87261');
INSERT INTO public.gallery_photos VALUES (15, '/static/uploads/gallery_20251030_233519_942530_112.jpg', '', '', 14, true, '2025-10-30 23:35:19.967956');
INSERT INTO public.gallery_photos VALUES (16, '/static/uploads/gallery_20251030_233535_426138_99.jpg', '', '', 15, true, '2025-10-30 23:35:35.466012');
INSERT INTO public.gallery_photos VALUES (17, '/static/uploads/gallery_20251030_233603_741734_106.jpg', '', '', 16, true, '2025-10-30 23:36:03.797226');


--
-- Data for Name: generated_checklists; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.generated_checklists VALUES (1, 'הכנות ווק', '2025-09-05', 'morning', 1, 'מגד', '[{"id": 26, "name": "\u05e7\u05e9\u05d9\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e7\u05e9\u05d9\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 27, "name": "\u05e6\u05d9\u05dc\u05d9 \u05e9\u05d8\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e6\u05d9\u05dc\u05d9 \u05e9\u05d8\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 28, "name": "\u05d1\u05e6\u05dc \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d1\u05e6\u05dc \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 29, "name": "\u05d1\u05e9\u05e8 \u05e4\u05e8\u05d5\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d1\u05e9\u05e8 \u05e4\u05e8\u05d5\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 30, "name": "\u05e2\u05d5\u05e3 \u05e4\u05e8\u05d5\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e2\u05d5\u05e3 \u05e4\u05e8\u05d5\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 31, "name": "\u05e9\u05e8\u05d9\u05de\u05e4\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e9\u05e8\u05d9\u05de\u05e4\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 32, "name": "\u05e7\u05dc\u05de\u05e8\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e7\u05dc\u05de\u05e8\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 33, "name": "\u05e2\u05d5\u05e3 \u05d8\u05de\u05e4\u05d5\u05e8\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e2\u05d5\u05e3 \u05d8\u05de\u05e4\u05d5\u05e8\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 34, "name": "\u05d8\u05d5\u05e4\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d8\u05d5\u05e4\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 35, "name": "\u05d1\u05d9\u05e6\u05d9\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d1\u05d9\u05e6\u05d9\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 36, "name": "\u05e6\u05d9\u05e8 \u05d1\u05e7\u05e8", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e6\u05d9\u05e8 \u05d1\u05e7\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 37, "name": "\u05e6\u05d9\u05e8 \u05e2\u05d5\u05e3", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e6\u05d9\u05e8 \u05e2\u05d5\u05e3", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 38, "name": "\u05e1\u05d5\u05d9\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e1\u05d5\u05d9\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 39, "name": "\u05d8\u05e8\u05d9\u05d0\u05e7\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d8\u05e8\u05d9\u05d0\u05e7\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 40, "name": "\u05e7\u05d0\u05e8\u05d9 \u05d9\u05e8\u05d5\u05e7", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e7\u05d0\u05e8\u05d9 \u05d9\u05e8\u05d5\u05e7", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 41, "name": "\u05e7\u05d0\u05e8\u05d9 \u05d0\u05d3\u05d5\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e7\u05d0\u05e8\u05d9 \u05d0\u05d3\u05d5\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 42, "name": "\u05d7\u05dc\u05d1 \u05e7\u05d5\u05e7\u05d5\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05d7\u05dc\u05d1 \u05e7\u05d5\u05e7\u05d5\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 43, "name": "\u05ea\u05de\u05e6\u05d9\u05ea \u05e2\u05d9\u05e9\u05d5\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05ea\u05de\u05e6\u05d9\u05ea \u05e2\u05d9\u05e9\u05d5\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 44, "name": "\u05e6\u05d9\u05dc\u05d9 \u05e7\u05d5\u05e8\u05d9\u05d0\u05e0\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05e6\u05d9\u05dc\u05d9 \u05e7\u05d5\u05e8\u05d9\u05d0\u05e0\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 45, "name": "\u05de\u05d9\u05e5 \u05dc\u05d9\u05de\u05d5\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7 - \u05de\u05d9\u05e5 \u05dc\u05d9\u05de\u05d5\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05d1\u05e9\u05d9\u05dd + \u05d7\u05dc\u05d1\u05d5\u05e0\u05d9\u05dd + \u05e8\u05d8\u05d1\u05d9\u05dd \u05dc\u05d5\u05d5\u05e7", "group_color": "#ffc107"}, {"id": 11, "name": "\u05db\u05e8\u05d5\u05d1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05db\u05e8\u05d5\u05d1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 12, "name": "\u05d2\u05d6\u05e8", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d2\u05d6\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 13, "name": "\u05d1\u05e6\u05dc \u05d9\u05e8\u05d5\u05e7", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d1\u05e6\u05dc \u05d9\u05e8\u05d5\u05e7", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 14, "name": "\u05d1\u05e6\u05dc \u05dc\u05d1\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d1\u05e6\u05dc \u05dc\u05d1\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 15, "name": "\u05e0\u05d1\u05d8\u05d9\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05e0\u05d1\u05d8\u05d9\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 16, "name": "\u05e4\u05dc\u05e4\u05dc \u05d2\u05de\u05d1\u05d4 \u05d0\u05d3\u05d5\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05e4\u05dc\u05e4\u05dc \u05d2\u05de\u05d1\u05d4 \u05d0\u05d3\u05d5\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 17, "name": "\u05e4\u05d8\u05e8\u05d9\u05d5\u05ea \u05e4\u05d5\u05e8\u05d8\u05d1\u05dc\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05e4\u05d8\u05e8\u05d9\u05d5\u05ea \u05e4\u05d5\u05e8\u05d8\u05d1\u05dc\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 18, "name": "\u05d1\u05d0\u05e7 \u05e6\u05d5\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d1\u05d0\u05e7 \u05e6\u05d5\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 19, "name": "\u05d6\u05d5\u05e7\u05d9\u05e0\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d6\u05d5\u05e7\u05d9\u05e0\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 20, "name": "\u05d1\u05e8\u05d5\u05e7\u05d5\u05dc\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d1\u05e8\u05d5\u05e7\u05d5\u05dc\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 21, "name": "\u05d0\u05e0\u05e0\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05e0\u05e0\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 22, "name": "\u05d1\u05d6\u05d9\u05dc\u05d9\u05e7\u05d5\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d1\u05d6\u05d9\u05dc\u05d9\u05e7\u05d5\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 23, "name": "\u05db\u05d5\u05e1\u05d1\u05e8\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05db\u05d5\u05e1\u05d1\u05e8\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 24, "name": "\u05e9\u05d5\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05e9\u05d5\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 25, "name": "\u05d2\u05f3\u05d9\u05e0\u05d2\u05f3\u05e8", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d2\u05f3\u05d9\u05e0\u05d2\u05f3\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#007bff"}, {"id": 6, "name": "\u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05d1\u05d9\u05e6\u05d9\u05dd", "description": "\u05d4\u05db\u05e0\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05d1\u05d9\u05e6\u05d9\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05e0\u05d5\u05d3\u05dc\u05e1", "group_color": "#6f42c1"}, {"id": 7, "name": "\u05d0\u05d9\u05d8\u05e8\u05d9\u05d5\u05ea \u05e9\u05d7\u05d5\u05e8\u05d5\u05ea", "description": "\u05d4\u05db\u05e0\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05d9\u05d8\u05e8\u05d9\u05d5\u05ea \u05e9\u05d7\u05d5\u05e8\u05d5\u05ea", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05e0\u05d5\u05d3\u05dc\u05e1", "group_color": "#6f42c1"}, {"id": 8, "name": "\u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05ea\u05e8\u05d3", "description": "\u05d4\u05db\u05e0\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05ea\u05e8\u05d3", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05e0\u05d5\u05d3\u05dc\u05e1", "group_color": "#6f42c1"}, {"id": 9, "name": "\u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05d0\u05d5\u05e8\u05d6", "description": "\u05d4\u05db\u05e0\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05d8\u05e8\u05d9\u05d5\u05ea \u05d0\u05d5\u05e8\u05d6", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05e0\u05d5\u05d3\u05dc\u05e1", "group_color": "#6f42c1"}, {"id": 10, "name": "\u05d0\u05d5\u05e8\u05d6 \u05dc\u05d1\u05df/\u05de\u05d0\u05d5\u05d3\u05d4", "description": "\u05d4\u05db\u05e0\u05ea \u05dc\u05db\u05dc \u05e1\u05d5\u05d2\u05d9 \u05d4\u05d5\u05d5\u05e7 - \u05d0\u05d5\u05e8\u05d6 \u05dc\u05d1\u05df/\u05de\u05d0\u05d5\u05d3\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05d5\u05d5\u05e7 \u05e0\u05d5\u05d3\u05dc\u05e1", "group_color": "#6f42c1"}]', '2025-09-05 12:26:55.567462', NULL);
INSERT INTO public.generated_checklists VALUES (3, 'הכנות סושי', '2025-09-09', 'morning', 2, '', '[{"id": 67, "name": "\u05e1\u05dc\u05de\u05d5\u05df \u05e0\u05d0", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05dc\u05de\u05d5\u05df \u05e0\u05d0", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 68, "name": "\u05e1\u05dc\u05de\u05d5\u05df \u05e7\u05e4\u05d5\u05d0", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05dc\u05de\u05d5\u05df \u05e7\u05e4\u05d5\u05d0", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 69, "name": "\u05e1\u05dc\u05de\u05d5\u05df \u05e6\u05dc\u05d5\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05dc\u05de\u05d5\u05df \u05e6\u05dc\u05d5\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 70, "name": "\u05d8\u05d5\u05e0\u05d4 \u05d0\u05d3\u05d5\u05de\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05d8\u05d5\u05e0\u05d4 \u05d0\u05d3\u05d5\u05de\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 71, "name": "\u05e1\u05d5\u05e8\u05d9\u05de\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05d5\u05e8\u05d9\u05de\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 72, "name": "\u05d3\u05d2 \u05dc\u05d1\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05d3\u05d2 \u05dc\u05d1\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 73, "name": "\u05d8\u05d5\u05d1\u05d9\u05e7\u05d5 \u05e9\u05d7\u05d5\u05e8", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05d8\u05d5\u05d1\u05d9\u05e7\u05d5 \u05e9\u05d7\u05d5\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 74, "name": "\u05d8\u05d5\u05d1\u05d9\u05e7\u05d5 \u05d0\u05d3\u05d5\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05d8\u05d5\u05d1\u05d9\u05e7\u05d5 \u05d0\u05d3\u05d5\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 75, "name": "\u05e1\u05d1\u05d9\u05e6\u05d4 \u05d3\u05d2 \u05dc\u05d1\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05d1\u05d9\u05e6\u05d4 \u05d3\u05d2 \u05dc\u05d1\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 76, "name": "\u05e1\u05d1\u05d9\u05e6\u05d4 \u05d8\u05d5\u05e0\u05d4 \u05d7\u05e8\u05d9\u05e3", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05d1\u05d9\u05e6\u05d4 \u05d8\u05d5\u05e0\u05d4 \u05d7\u05e8\u05d9\u05e3", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 77, "name": "\u05e9\u05e8\u05d9\u05de\u05e4\u05e1 \u05d3\u05d5\u05e8\u05d9\u05d8\u05d5\u05e1", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e9\u05e8\u05d9\u05de\u05e4\u05e1 \u05d3\u05d5\u05e8\u05d9\u05d8\u05d5\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 78, "name": "\u05e1\u05d5\u05e8\u05d9\u05de\u05d9 \u05e7\u05e6\u05d5\u05e5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05e1\u05d5\u05e8\u05d9\u05de\u05d9 \u05e7\u05e6\u05d5\u05e5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 79, "name": "\u05d8\u05d5\u05e4\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df - \u05d8\u05d5\u05e4\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d7\u05dc\u05d1\u05d5\u05df", "group_color": "#20c997"}, {"id": 60, "name": "\u05e9\u05d5\u05de\u05e9\u05d5\u05dd \u05e9\u05d7\u05d5\u05e8", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05e9\u05d5\u05de\u05e9\u05d5\u05dd \u05e9\u05d7\u05d5\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 61, "name": "\u05e9\u05d5\u05de\u05e9\u05d5\u05dd \u05e1\u05d5\u05d9\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05e9\u05d5\u05de\u05e9\u05d5\u05dd \u05e1\u05d5\u05d9\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 62, "name": "\u05ea\u05d5\u05d2\u05e8\u05d0\u05e9\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05ea\u05d5\u05d2\u05e8\u05d0\u05e9\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 63, "name": "\u05d1\u05d5\u05d8\u05e0\u05d9\u05dd", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05d1\u05d5\u05d8\u05e0\u05d9\u05dd", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 64, "name": "\u05d1\u05e6\u05dc \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05d1\u05e6\u05dc \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 65, "name": "\u05d8\u05de\u05e4\u05d5\u05e8\u05d4 \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05d8\u05de\u05e4\u05d5\u05e8\u05d4 \u05e7\u05e8\u05d9\u05e1\u05e4\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 66, "name": "\u05e4\u05e0\u05e7\u05d5 \u05e1\u05d2\u05d5\u05dc", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd - \u05e4\u05e0\u05e7\u05d5 \u05e1\u05d2\u05d5\u05dc", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05d1\u05e9\u05d9\u05dd", "group_color": "#28a745"}, {"id": 46, "name": "\u05d2\u05d6\u05e8", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d2\u05d6\u05e8", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 47, "name": "\u05de\u05dc\u05e4\u05e4\u05d5\u05df", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05de\u05dc\u05e4\u05e4\u05d5\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 48, "name": "\u05d1\u05d8\u05d8\u05d4 \u05d0\u05e6\u05d1\u05e2\u05d5\u05ea", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d1\u05d8\u05d8\u05d4 \u05d0\u05e6\u05d1\u05e2\u05d5\u05ea", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 49, "name": "\u05d1\u05d8\u05d8\u05d4 \u05de\u05e2\u05d8\u05e4\u05d5\u05ea", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d1\u05d8\u05d8\u05d4 \u05de\u05e2\u05d8\u05e4\u05d5\u05ea", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 50, "name": "\u05e2\u05d9\u05e8\u05d9\u05ea", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05e2\u05d9\u05e8\u05d9\u05ea", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 51, "name": "\u05e2\u05d9\u05e8\u05d9\u05ea \u05e7\u05e6\u05d5\u05e5", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05e2\u05d9\u05e8\u05d9\u05ea \u05e7\u05e6\u05d5\u05e5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 52, "name": "\u05dc\u05d9\u05de\u05d5\u05df", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05dc\u05d9\u05de\u05d5\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 53, "name": "\u05d7\u05e1\u05d4 \u05e7\u05e6\u05d5\u05e5", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d7\u05e1\u05d4 \u05e7\u05e6\u05d5\u05e5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 54, "name": "\u05d6\u05d5\u05e7\u05d9\u05e0\u05d9", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d6\u05d5\u05e7\u05d9\u05e0\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 55, "name": "\u05d0\u05d5\u05e9\u05e0\u05e7\u05d5", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d0\u05d5\u05e9\u05e0\u05e7\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 56, "name": "\u05d0\u05e1\u05e4\u05e8\u05d2\u05d5\u05e1", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d0\u05e1\u05e4\u05e8\u05d2\u05d5\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 57, "name": "\u05d0\u05d1\u05d5\u05e7\u05d3\u05d5", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d0\u05d1\u05d5\u05e7\u05d3\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 58, "name": "\u05d7\u05dc\u05e4\u05d9\u05e0\u05d9\u05d5", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05d7\u05dc\u05e4\u05d9\u05e0\u05d9\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 59, "name": "\u05e6\u05f3\u05d9\u05e4\u05e1", "description": "\u05d4\u05db\u05e0\u05ea \u05d9\u05e8\u05e7\u05d5\u05ea \u05dc\u05e1\u05d5\u05e9\u05d9 - \u05e6\u05f3\u05d9\u05e4\u05e1", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05d9\u05e8\u05e7\u05d5\u05ea", "group_color": "#fd7e14"}, {"id": 80, "name": "\u05e1\u05e4\u05d9\u05d9\u05e1\u05d9 \u05de\u05d9\u05d5\u05e0\u05d6", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05e1\u05e4\u05d9\u05d9\u05e1\u05d9 \u05de\u05d9\u05d5\u05e0\u05d6", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 81, "name": "\u05d0\u05d9\u05d5\u05dc\u05d9 \u05d9\u05d5\u05d6\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d0\u05d9\u05d5\u05dc\u05d9 \u05d9\u05d5\u05d6\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 82, "name": "\u05d8\u05e8\u05d9\u05d0\u05e7\u05d9", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d8\u05e8\u05d9\u05d0\u05e7\u05d9", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 83, "name": "\u05e1\u05e8\u05d9\u05e8\u05d0\u05e6\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05e1\u05e8\u05d9\u05e8\u05d0\u05e6\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 84, "name": "\u05d2\u05d1\u05d9\u05e0\u05ea \u05e9\u05de\u05e0\u05ea", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d2\u05d1\u05d9\u05e0\u05ea \u05e9\u05de\u05e0\u05ea", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 85, "name": "\u05d2\u05d1\u05d9\u05e0\u05ea \u05db\u05de\u05d9\u05d4\u05d9\u05df", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d2\u05d1\u05d9\u05e0\u05ea \u05db\u05de\u05d9\u05d4\u05d9\u05df", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 86, "name": "\u05d9\u05d5\u05d6\u05d5 \u05e7\u05e9\u05d9\u05d5", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d9\u05d5\u05d6\u05d5 \u05e7\u05e9\u05d9\u05d5", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}, {"id": 87, "name": "\u05d2\u05d1\u05d9\u05e0\u05ea \u05d2\u05d0\u05d5\u05d3\u05d4", "description": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd - \u05d2\u05d1\u05d9\u05e0\u05ea \u05d2\u05d0\u05d5\u05d3\u05d4", "category": "kitchen", "priority": "high", "frequency": "daily", "group_name": "\u05d4\u05db\u05e0\u05d5\u05ea \u05e1\u05d5\u05e9\u05d9 \u05e8\u05d8\u05d1\u05d9\u05dd", "group_color": "#28a745"}]', '2025-09-09 16:42:53.806815', NULL);


--
-- Data for Name: menu_templates; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.menu_templates VALUES (1, 'תבנית תפריט כרמיאל', 'תבנית נוצרה מ-תפריט כרמיאל', 2, false, 1, '[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]', '[25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112]', '{"columns": 2, "show_prices": true, "show_descriptions": true}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-24 15:36:19.016101', '2025-09-24 15:36:19.016103', '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);


--
-- Data for Name: generated_menus; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.generated_menus VALUES (1, 'תפריט כרמיאל', 2, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 46, 47, 48, 49, 50, 39, 40, 41, 42, 43, 44, 45, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T14:34:01.190868"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-24 14:34:01.192811', NULL, NULL, NULL, NULL);
INSERT INTO public.generated_menus VALUES (2, 'תפריט כרמיאל', 2, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T15:05:29.375192"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-24 15:05:29.377618', NULL, '{"iconStyle": "light", "addDividers": true, "colorScheme": "elegant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#2d2d2d", "addDecorators": false, "secondaryColor": "#daa520", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18]}', NULL);
INSERT INTO public.generated_menus VALUES (3, 'תפריט בדיקה לפיצ''רים חדשים', 1, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05dc\u05e4\u05d9\u05e6''\u05e8\u05d9\u05dd \u05d7\u05d3\u05e9\u05d9\u05dd", "branch_id": 1, "categories": [10, 11], "items": [25, 26, 27], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T15:20:50.065236"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-24 15:20:50.067279', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11]}, {"id": "page2", "name": "דף 2", "categories": []}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (4, 'תפריט כרמיאל', 2, 1, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T15:36:19.014641"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-24 15:36:19.062155', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (5, 'תפריט בדיקה מתקן', 1, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05de\u05ea\u05e7\u05df", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T16:09:59.089081"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-24 16:09:59.091694', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (6, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 91, 92, 93, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T16:14:17.215592"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-24 16:14:17.217341', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 2, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (7, 'תפריט בדיקה עם פיצ''רים חדשים', 1, NULL, '2025-09-24', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05e2\u05dd \u05e4\u05d9\u05e6''\u05e8\u05d9\u05dd \u05d7\u05d3\u05e9\u05d9\u05dd", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T16:15:25.046892"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-24 16:15:25.047429', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}, {"id": "page2", "name": "דף 2", "categories": []}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": false}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (8, 'Test Menu 7HefUb', 1, NULL, '2025-09-24', 1, '{"name": "Test Menu 7HefUb", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-24T16:41:54.895487"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-24 16:41:54.897392', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (9, 'Test Template pB7CXm', 1, NULL, '2025-09-26', 1, '{"name": "Test Template pB7CXm", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T09:11:49.189623"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 09:11:49.193065', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (10, 'ReferenceError Fix Test kOtIzx', 1, NULL, '2025-09-26', 1, '{"name": "ReferenceError Fix Test kOtIzx", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 27, 28], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T09:18:12.730564"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 09:18:12.732973', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (11, 'State Management Fix Test A2AoQ1', 1, NULL, '2025-09-26', 1, '{"name": "State Management Fix Test A2AoQ1", "branch_id": 1, "categories": [10, 11], "items": [25], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T09:56:47.891456"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 09:56:47.893285', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (12, 'State Management Fix Test A2AoQ1', 1, NULL, '2025-09-26', 1, '{"name": "State Management Fix Test A2AoQ1", "branch_id": 1, "categories": [11, 12, 13, 14, 15, 16, 17, 18, 19, 10], "items": [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 25, 26, 27], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T10:02:55.413538"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 10:02:55.414183', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (13, 'State Management Fix Test A2AoQ1', 1, NULL, '2025-09-26', 1, '{"name": "State Management Fix Test A2AoQ1", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 25, 26, 27], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T10:08:07.684796"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 10:08:07.685282', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (14, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 91, 92, 93], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T10:08:35.510364"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 10:08:35.511066', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [11, 12]}, {"id": "page4", "name": "דף 4", "categories": [19, 18]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 11, 19], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (15, 'תפריט בדיקה אוטומטי', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T11:11:18.701682"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 11:11:18.703472', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (16, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T11:48:03.217853"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 11:48:03.219586', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (17, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T11:55:05.110218"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 11:55:05.11214', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{}', NULL);
INSERT INTO public.generated_menus VALUES (18, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 91, 92, 93], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:20:12.318180"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:20:12.320217', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (19, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:22:30.773096"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:22:30.77371', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 2, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (20, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 91, 92, 93], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:32:11.896567"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:32:11.898675', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 2, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (21, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:42:12.069537"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:42:12.07182', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (22, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:42:12.370662"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:42:12.37116', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (23, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:42:12.616789"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:42:12.617383', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (24, 'תפריט כרמיאל', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T12:51:41.738426"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false}', '2025-09-26 12:51:41.740826', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [15, 16, 17]}, {"id": "page3", "name": "דף 3", "categories": [18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [15, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (25, 'תפריט בדיקה אוטומטי', 1, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T15:33:44.062709"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 15:33:44.065081', NULL, '{}', '{}', NULL);
INSERT INTO public.generated_menus VALUES (26, 'Test Menu - Automation', 1, NULL, '2025-09-26', 1, '{"name": "Test Menu - Automation", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 39, 40, 41, 42], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T15:45:52.992258"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 15:45:52.99886', NULL, '{}', '{}', NULL);
INSERT INTO public.generated_menus VALUES (37, 'תפריט בדיקה אוטומטי', 1, NULL, '2025-09-30', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9", "branch_id": 1, "categories": [11], "items": [39], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-30T10:20:28.985286"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": true}', '2025-09-30 10:20:28.987123', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11]}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"11": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (27, 'תפריט בדיקה אוטומטי', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T23:25:12.702840"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 23:25:12.704986', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (28, 'תפריט בדיקה אוטומטי', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T23:25:12.974991"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 23:25:12.975531', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (29, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-26', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-26T23:30:21.636224"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-26 23:30:21.638909', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (30, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T08:39:02.615168"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true}', '2025-09-27 08:39:02.61698', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 12, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [11]}, {"id": "page3", "name": "דף 3", "categories": [15, 17, 16]}], "showMenuTitle": false, "addPageNumbers": false, "separateIndexPage": false, "pageBreakCategories": [11, 15], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 2, "showItemsInOrder": true}, "19": {"columns": 2, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (31, 'תפריט בדיקה', 1, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d1\u05d3\u05d9\u05e7\u05d4", "branch_id": 1, "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19], "items": [39, 40, 41], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T08:51:54.098739"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": true}', '2025-09-27 08:51:54.102364', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (32, 'תפריט דיבוג', 1, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d3\u05d9\u05d1\u05d5\u05d2", "branch_id": 1, "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19], "items": [39, 41, 25], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T08:57:55.606733"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": false}', '2025-09-27 08:57:55.608725', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (33, 'תפריט חדש תיקון', 1, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05d7\u05d3\u05e9 \u05ea\u05d9\u05e7\u05d5\u05df", "branch_id": 1, "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19], "items": [39, 25], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T09:03:52.941187"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": true}', '2025-09-27 09:03:52.943231', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": false}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (34, 'תפריט תיקון סופי', 1, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05e4\u05e8\u05d9\u05d8 \u05ea\u05d9\u05e7\u05d5\u05df \u05e1\u05d5\u05e4\u05d9", "branch_id": 1, "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19], "items": [39, 40, 25, 26], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T09:08:26.658108"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": false}', '2025-09-27 09:08:26.66', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 10, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (35, 'תיקון סופי', 1, NULL, '2025-09-27', 1, '{"name": "\u05ea\u05d9\u05e7\u05d5\u05df \u05e1\u05d5\u05e4\u05d9", "branch_id": 1, "categories": [11, 10], "items": [39, 40], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-27T09:25:39.739330"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": false}', '2025-09-27 09:25:39.741146', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 10]}], "showMenuTitle": false, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (36, 'בדיקת קיבוץ דפים', 1, NULL, '2025-09-29', 1, '{"name": "\u05d1\u05d3\u05d9\u05e7\u05ea \u05e7\u05d9\u05d1\u05d5\u05e5 \u05d3\u05e4\u05d9\u05dd", "branch_id": 1, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [39, 40, 41, 42, 43, 44, 45, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-09-29T23:10:40.737672"}', '{"paper_size": "A4", "show_branch_info": true, "show_date": true, "show_menu_title": true}', '2025-09-29 23:10:40.740253', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [11, 12, 13, 14, 16, 17, 18, 19]}, {"id": "page2", "name": "דף 2", "categories": []}, {"id": "page3", "name": "דף 3", "categories": []}], "showMenuTitle": true, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 1, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 1, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (38, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-10-03', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-10-03T21:41:36.375179"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false, "show_menu_title": true}', '2025-10-03 21:41:36.377554', NULL, '{"iconStyle": "solid", "addDividers": true, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{}', NULL);
INSERT INTO public.generated_menus VALUES (39, 'תבנית תפריט כרמיאל - עותק', 2, NULL, '2025-10-03', 1, '{"name": "\u05ea\u05d1\u05e0\u05d9\u05ea \u05ea\u05e4\u05e8\u05d9\u05d8 \u05db\u05e8\u05de\u05d9\u05d0\u05dc - \u05e2\u05d5\u05ea\u05e7", "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "generated_at": "2025-10-03T21:56:03.795929"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false, "show_menu_title": false}', '2025-10-03 21:56:03.798876', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "categoriesPerPage": 1, "separateIndexPage": false, "pageBreakCategories": [], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 1, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);
INSERT INTO public.generated_menus VALUES (40, 'jsa jsa jsa', 2, NULL, '2025-10-03', 1, '{"name": "jsa jsa jsa", "items": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 102, 103, 104, 94, 95, 96, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 111, 112, 91, 92, 93], "layout": {"columns": 2, "show_prices": true, "show_descriptions": true}, "branch_id": 2, "categories": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 11, 10, 12, 13, 14, 15, 16, 17, 18, 19], "generated_at": "2025-10-03T22:07:17.433464"}', '{"paper_size": "A4", "show_branch_info": false, "show_date": false, "show_menu_title": false}', '2025-10-03 22:07:17.435859', NULL, '{"iconStyle": "solid", "addDividers": false, "colorScheme": "restaurant", "itemSpacing": "normal", "primaryFont": "Heebo", "baseFontSize": "medium", "primaryColor": "#1b2951", "addDecorators": false, "secondaryColor": "#c75450", "showCategoryIcons": true}', '{"addFooters": false, "addHeaders": false, "pageGroups": [{"id": "page1", "name": "דף 1", "categories": [10, 13, 14]}, {"id": "page2", "name": "דף 2", "categories": [11, 12]}, {"id": "page3", "name": "דף 3", "categories": [15]}, {"id": "page4", "name": "דף 4", "categories": [16, 17]}, {"id": "page5", "name": "דף 5", "categories": [18, 19]}], "showMenuTitle": false, "addPageNumbers": false, "categoriesPerPage": 2, "separateIndexPage": false, "pageBreakCategories": [11, 15, 16, 18], "categoryColumnSettings": {"10": {"columns": 2, "showItemsInOrder": true}, "11": {"columns": 2, "showItemsInOrder": true}, "12": {"columns": 1, "showItemsInOrder": true}, "13": {"columns": 1, "showItemsInOrder": true}, "14": {"columns": 1, "showItemsInOrder": true}, "15": {"columns": 2, "showItemsInOrder": true}, "16": {"columns": 1, "showItemsInOrder": true}, "17": {"columns": 1, "showItemsInOrder": true}, "18": {"columns": 1, "showItemsInOrder": true}, "19": {"columns": 1, "showItemsInOrder": true}}}', NULL);


--
-- Data for Name: kitchen_stations; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: kitchen_queue; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: live_events; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.live_events VALUES (4, 'ערב שירי יין', 'Wine & Songs Evening', 'טעימות יין ומוזיקה חיה', 'Wine tasting and live music', 'ערב רומנטי של טעימות יין ושירים. כניסה חופשית!', 'A romantic evening of wine tasting and songs. Free entry!', 'אורחים מיוחדים', 'Special Guests', 'pop', '2025-12-07', '20:00:00', '19:00:00', 180, NULL, 'מסעדת ריי רמה', 'Rai Restaurant Rama', 40, 38, true, 0, NULL, 'live_wine_songs.png', NULL, 'upcoming', true, false, false, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.live_events VALUES (2, 'מסיבת קומדי סטנדאפ', 'Stand-up Comedy Night', 'הקומיקאים הכי מצחיקים במופע אחד', 'The funniest comedians in one show', 'ערב של צחוקים עם הקומיקאים הכי חמים בישראל. מובטחים צחוקים ללא הפסקה!', 'An evening of laughter with Israel''s hottest comedians. Non-stop laughs guaranteed!', 'שי פרידמן ואורחים', 'Shai Friedman and Guests', 'other', '2025-12-18', '22:00:00', '21:00:00', 90, NULL, 'מסעדת ריי רמה', 'Rai Restaurant Rama', 80, 45, false, 120, NULL, 'live_comedy.png', NULL, 'upcoming', true, false, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.live_events VALUES (3, 'ערב מזרחי עם מנור לזרוף', 'Mizrahi Night with Manor Lazrof', 'מופע מוזיקה מזרחית מקורית', 'Original Mizrahi music show', 'הזמר המוכשר מנור לזרוף מגיע למופע מיוחד במיוחד! להיטים ישנים וחדשים.', 'Talented singer Manor Lazrof arrives for a very special show! Old and new hits.', 'מנור לזרוף', 'Manor Lazrof', 'mizrahi', '2025-12-25', '21:30:00', '20:30:00', 150, NULL, 'מסעדת ריי כרמיאל', 'Rai Restaurant Karmiel', 100, 79, false, 100, 200, 'live_mizrahi.png', NULL, 'upcoming', true, true, true, NULL, NULL, NULL, NULL, NULL, '2025-12-08 13:19:56.076632', NULL);


--
-- Data for Name: live_event_reservations; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.live_event_reservations VALUES (2, 3, 'חליל שיבאן', '0526647778', 'khalilshiban@gmail.com', 1, 'regular', 100, 'pending', false, 'LIVE133D4692', NULL, NULL, '2025-12-05 09:21:16.790333', '2025-12-08 14:16:45.280144', 'cash', 'pending', 'JQOZrmWfeqNp8IkgDwlTeIwfd9GKFLbDwGHquDx1nnw', NULL, NULL, false, false, NULL);


--
-- Data for Name: manager_pins; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.manager_pins VALUES (1, 'scrypt:32768:8:1$kRjQG6Qz2uKG5p5n$67fd8e3f3e7c6c8f3d3f8e8f8f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f3f', 'Test Manager PIN', 'Test PIN for development - 123456', true, '2025-11-23 23:22:25.821821', NULL, NULL);


--
-- Data for Name: media_files; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: menus; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.menus VALUES (1, 'תפריט ראשי', 'התפריט הראשי של המסעדה', true, false, '2025-11-25 15:39:34.4424', '2025-11-25 15:39:34.4424');


--
-- Data for Name: menu_categories; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.menu_categories VALUES (20, 'ארוחות בוקר', 'الفطور', NULL, NULL, 1, true, 'fa-sun', NULL, NULL, 'ארוחות הבוקר מוגשות עד השעה 12:30', 'وجبة الفطور تُقدّم حتى الساعة 12:30', true, true, NULL, false, 1);
INSERT INTO public.menu_categories VALUES (21, 'סלטים ומנות קטנות', 'السلطات والمقبلات الصغيرة', NULL, NULL, 2, true, 'fa-leaf', NULL, NULL, NULL, NULL, true, true, NULL, false, 1);
INSERT INTO public.menu_categories VALUES (22, 'מנות פתיחה', 'المقبلات', NULL, NULL, 3, true, 'fa-utensils', NULL, NULL, NULL, NULL, true, true, NULL, false, 1);
INSERT INTO public.menu_categories VALUES (23, 'מטבח הגליל', 'مطبخ الجليل', NULL, NULL, 4, true, 'fa-mountain', NULL, NULL, NULL, NULL, true, true, NULL, false, 1);
INSERT INTO public.menu_categories VALUES (24, 'מנות עיקריות', 'الأطباق الرئيسية', NULL, NULL, 5, true, 'fa-plate-wheat', NULL, NULL, NULL, NULL, true, true, NULL, false, 1);
INSERT INTO public.menu_categories VALUES (25, 'ארוחות ילדים', 'وجبات الأطفال', NULL, NULL, 6, true, 'fa-child', NULL, NULL, NULL, NULL, true, true, NULL, false, 1);


--
-- Data for Name: menu_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.menu_items VALUES (114, 20, 'בוקר ראי', 'فطور راي', 'סלט עגבניות, לחם, לבנה, חומוס, חביתה, מנאקיש, בניצה וחמוצים. שתייה קרה וחמה, קינוח.', 'سلطة بندورة، خبز، لبنة، حمص، عجة، مناقيش لبنة وبانيتسا، مخللات. مشروب بارد وساخن، حلوى.', NULL, NULL, NULL, NULL, 160, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (115, 20, 'בלקאן', 'بلقان', 'לחם, בייקון, נקניקיה וביצת עין וחרדל.', 'خبز، بيكون مقدد، نقانق وبيضة عيون مع خردل.', NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (116, 20, 'חומוס', 'حمص', NULL, NULL, NULL, NULL, NULL, NULL, 30, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (117, 20, 'חביתה', 'عجة', NULL, NULL, NULL, NULL, NULL, NULL, 28, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (118, 20, 'בניצה', 'بانتسا', NULL, NULL, NULL, NULL, NULL, NULL, 22, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (119, 21, 'סלט אלראי', 'سلطة الراي', 'חסה, שירי, קלמטה, ארטישוק, גבינת פרמזן ובצל אדום.', 'خص شيري، كالماتا، أرضي شوكي، جبنة برمجان، وبصل أحمر.', NULL, NULL, NULL, NULL, 64, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (145, 23, 'מג''דרה אורז', 'مجدرة أرز', NULL, NULL, NULL, NULL, NULL, NULL, 45, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:02:30.185339', true, true);
INSERT INTO public.menu_items VALUES (121, 21, 'סלט ריחן', 'سلطة ريحان', 'חסה, עגבניה, בצל, עגבניות מיובשות, שקדים וחמוציות. גבינת ברינזה בתיבול בזיליקום.', 'خص، بندورة، بصل، بندورة مجففة، لوز، توت بري، وجبنة برينزا بتتبيلة ريحان.', NULL, NULL, NULL, NULL, 52, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:32:13.152438', true, true);
INSERT INTO public.menu_items VALUES (122, 21, 'תבולה', 'تبولة', NULL, NULL, NULL, NULL, NULL, NULL, 45, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:32:24.544019', true, true);
INSERT INTO public.menu_items VALUES (123, 21, 'חציל בטאבון', 'باذنجان بالطابون', NULL, NULL, NULL, NULL, NULL, NULL, 38, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:32:30.473271', true, true);
INSERT INTO public.menu_items VALUES (124, 21, 'לבנה בתיבול פיקנטי', 'لبنة متبلة حارة', NULL, NULL, NULL, NULL, NULL, NULL, 32, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:32:43.152797', true, true);
INSERT INTO public.menu_items VALUES (125, 21, 'קישואים ביוגורט / תמצית רימונים', 'كوسا باللبن / رب الرمان', NULL, NULL, NULL, NULL, NULL, NULL, 32, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:32:52.108317', true, true);
INSERT INTO public.menu_items VALUES (126, 21, 'פצ''ני צ''ושקי', 'بتشيني تشوشكي', 'רצועות פלפל קלוי בתיבול בולגרי, גבינת שמנת, בריוש ופקאן קלוי.', 'شرائح فلفل مشوي بتتبيلة بلغارية، جبنة كريم، خبز بريوش، وجوز محمص.', NULL, NULL, NULL, NULL, 38, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:33:06.625838', true, true);
INSERT INTO public.menu_items VALUES (127, 21, 'ליוטניצה', 'ليوتنيتسا', NULL, NULL, NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:33:29.038698', true, true);
INSERT INTO public.menu_items VALUES (128, 21, 'חמוצי בורופו', 'مخللات بوروفو', NULL, NULL, NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:33:31.081042', true, true);
INSERT INTO public.menu_items VALUES (129, 21, 'צלחת חריפים', 'صحن فلفل حار', NULL, NULL, NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 11, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:33:35.308021', true, true);
INSERT INTO public.menu_items VALUES (130, 22, 'לחם הבית', 'خبز البيت', 'מוגש עם מטבלים.', 'مقدم مع صلصات.', NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:04.373146', true, true);
INSERT INTO public.menu_items VALUES (132, 22, 'מרק היום', 'شوربة اليوم', NULL, NULL, NULL, NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:16.389748', true, true);
INSERT INTO public.menu_items VALUES (131, 22, 'לחם הבית עם שום', 'خبز البيت مثوم', NULL, NULL, NULL, NULL, NULL, NULL, 24, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:19.472288', true, true);
INSERT INTO public.menu_items VALUES (133, 22, 'מחבת פטריות', 'قلاية فُقع', 'פטריות טריות, בצל, בצל ירוק ושקדים.', 'فطر طازج مع بصل، لوز، وبصل أخضر.', NULL, NULL, NULL, NULL, 42, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:21.515057', true, true);
INSERT INTO public.menu_items VALUES (135, 22, 'נקניקיות הבית', 'نقانق البيت', 'מוגשות עם כרוב וחרדל.', 'مقدمة مع ملفوف وخردل.', NULL, NULL, NULL, NULL, 58, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:31.355046', true, true);
INSERT INTO public.menu_items VALUES (136, 22, 'לבנה מטוגנת', 'لبنة مقلية', 'כדורי לבנה מטוגנים עם עגבניות מרוסקות ולחם.', 'كرات لبنة مقلية تقدم مع صلصة بندورة وخبز محمص.', NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:36.327536', true, true);
INSERT INTO public.menu_items VALUES (137, 22, 'קובה אלראי', 'كبة الراي', 'קובה עם בשר עגל בטאבון.', 'كبة محشوة بلحم عجل مطهوة في الطابون.', NULL, NULL, NULL, NULL, 78, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:41.009942', true, true);
INSERT INTO public.menu_items VALUES (138, 22, 'קטאייף', 'قطايف', 'במילוי בשר עגל על מצע שמנת חמוצה וצ''ימיצ''ורי.', 'محشوة بلحم عجل مع صوص الكريمة أو التشيميتشوري.', NULL, NULL, NULL, NULL, 58, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:46.242722', true, true);
INSERT INTO public.menu_items VALUES (139, 22, 'קדרת גבינות', 'فخارة أجبان', 'עגבניות, פלפלים קלויים, גבינה בולגרית וגבינה צהובה.', 'فلفل وبندورة مشوية مع جبنة بلغارية وصفراء.', NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:55.580048', true, true);
INSERT INTO public.menu_items VALUES (140, 22, 'תפו-ג''ינג''ר', 'بطاطا زنجبيل', 'תפוח אדמה עם שום וג''ינג''ר.', 'بطاطا مع ثوم وزنجبيل.', NULL, NULL, NULL, NULL, 38, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 11, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:35:07.104772', true, true);
INSERT INTO public.menu_items VALUES (141, 23, 'שולבטו', 'شلباطو', 'תבשיל בורגול גלילי עם ירקות', 'برغل مطبوخ مع الخضار', '', '', '', '', 40, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, 0, '[]', 1, NULL, 0, '', '', NULL, '', '', '[]', NULL, '2025-12-02 17:01:44.82159', false, false);
INSERT INTO public.menu_items VALUES (144, 23, 'קובה בלבן', 'كبة لبنية', 'קובה מטוגנת עם יוגורט מבושל', 'كبة مقلية مع لبن مطبوخ', NULL, NULL, NULL, NULL, 67, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:02:32.000928', true, true);
INSERT INTO public.menu_items VALUES (143, 23, 'עדשים ושומר בר', 'عدس وشومر', 'תבשיל עדשים עם שומר בר ויוגורט', 'عدس مع شومر ولبن', NULL, NULL, NULL, NULL, 48, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:02:33.816845', true, true);
INSERT INTO public.menu_items VALUES (142, 23, 'עלי גפן', 'ورق دوالي', 'במילוי בורגול וירקות עם יוגורט', 'برغل وخضار يقدم مع لبن', NULL, NULL, NULL, NULL, 45, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:02:35.632281', true, true);
INSERT INTO public.menu_items VALUES (148, 24, 'קבב בולגרי', 'كباب بلغاري', 'קבב חזיר עם חציל, ליוטניצה וטחינה.', 'كباب خنزير مع باذنجان ولوطنیتسا وطحينة.', NULL, NULL, NULL, NULL, 68, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:44.023323', true, true);
INSERT INTO public.menu_items VALUES (149, 24, 'שיש טאווק', 'شيش طاووق', 'שיפודי עוף על הגריל עם לחם וירקות.', 'دجاج مشوي مع خبز وخضار وتزاتزيكي.', NULL, NULL, NULL, NULL, 65, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:45.865124', true, true);
INSERT INTO public.menu_items VALUES (150, 24, 'סופלאקי', 'سوفلاكي', 'שיפודי חזיר עם ירקות אנטיפסטי.', 'لحم خنزير مشوي مع خضار وتزاتزيكي.', NULL, NULL, NULL, NULL, 85, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:47.705782', true, true);
INSERT INTO public.menu_items VALUES (151, 24, 'קוורמא עגל', 'قورمة عجل', 'עגל בבישול ארוך עם ירקות וגבינות, מוגש עם אורז.', 'عجل مطبوخ مع خضار وجبنة ورز.', NULL, NULL, NULL, NULL, 75, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:49.543411', true, true);
INSERT INTO public.menu_items VALUES (152, 24, 'פילה בבייקון', 'فيله ملفوف بيكون', 'פילה בבייקון עם פירה.', 'فيله ملفوف ببيكون مع بطاطا مهروسة.', NULL, NULL, NULL, NULL, 90, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:51.380371', true, true);
INSERT INTO public.menu_items VALUES (147, 24, 'האוסטייק', 'house steak', 'סטייק חזיר על הגריל עם ירקות קלויים.', 'ستيك خنزير مع خضار مشوية.', '', '', '', '', 105, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, 0, '[]', 1, NULL, 0, '', '', NULL, '', '', '[]', NULL, '2025-12-02 23:01:33.764268', false, false);
INSERT INTO public.menu_items VALUES (158, 25, 'שניצל עוף', 'دجاج بانيه', NULL, NULL, NULL, NULL, NULL, NULL, 50, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, true);
INSERT INTO public.menu_items VALUES (120, 21, 'שופסקה', 'شوبسكا', 'עגבניות, מלפפון, פטרוזיליה, בצל, פלפל קלוי וגבינה בולגרית.', 'بندورة، خيار، بقدونس، بصل، فلفل مشوي، وجبنة بلغارية.', '', '', '', '', 45, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, 0, '[]', 2, NULL, 0, '', '', NULL, '', '', '[]', NULL, '2025-12-02 13:17:36.261771', false, false);
INSERT INTO public.menu_items VALUES (134, 22, 'יקיטורי בולגרי', 'ياكيتوري بلغاري', 'שיפוד גבינה בולגרית ובייקון מוגש עם לחם ומטבלים.', 'شيش جبنة بلغارية مع بيكون مشوي، يقدم مع خبز مخصوص وصلصات.', NULL, NULL, NULL, NULL, 55, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:34:24.92291', true, true);
INSERT INTO public.menu_items VALUES (160, 22, 'פוטטו', 'potato', '', '', '', '', '', '', 28, NULL, NULL, false, false, false, false, false, false, false, false, false, false, false, false, false, NULL, NULL, 0, '[]', 0, NULL, 0, '', '', '1111111', '', '', '[]', '2025-12-02 16:36:50.41258', '2025-12-02 16:36:50.412584', false, false);
INSERT INTO public.menu_items VALUES (113, 20, 'מבולגריה', 'من بلغاريا', 'לחם, שופסקה, ליוֹטניצה, בניצה. קדרת גבינות, נקניק וביצה, חמוצים. שתייה קרה וחמה, קינוח.', 'خبز، شوبسكا، ليوتنتسا، بانيتسا. فخارة أجبان، نقانق وبیضة، مخللات. مشروب بارد وساخن، تحلية.', NULL, NULL, NULL, NULL, 140, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 16:38:10.831899', true, true);
INSERT INTO public.menu_items VALUES (161, 22, 'פוטטו', 'potatto', '', '', '', '', '', '', 28, NULL, NULL, false, false, false, false, false, false, false, false, false, false, false, false, false, NULL, NULL, 0, '[]', 0, NULL, 0, '', '', '1111111', '', '', '[]', '2025-12-02 16:39:22.668786', '2025-12-02 16:39:22.668789', false, false);
INSERT INTO public.menu_items VALUES (163, 22, 'פוטטו', 'potatoo', '', '', '', '', '', '', 28, NULL, NULL, false, false, false, false, false, false, false, false, false, false, false, false, true, NULL, NULL, 0, '[]', 12, NULL, 0, '', '', '1111111', '', '', '[]', '2025-12-02 16:56:18.886728', '2025-12-02 16:57:23.76631', false, false);
INSERT INTO public.menu_items VALUES (164, 22, 'צ׳יפס', 'chips', '', '', '', '', '', '', 23, NULL, NULL, false, false, false, false, false, false, false, false, false, false, false, false, true, NULL, NULL, 0, '[]', 13, NULL, 0, '', '', '1111111', '', '', '[]', '2025-12-02 17:00:17.69452', '2025-12-02 17:00:33.308136', false, false);
INSERT INTO public.menu_items VALUES (146, 23, 'שיש ברק', 'شيش برك', 'כיסונים במילוי בשר/צמחוני עם יוגורט', 'لحمة أو نباتي مع لبن مطبوخ', NULL, NULL, NULL, NULL, 72, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:02:28.145342', true, true);
INSERT INTO public.menu_items VALUES (155, 24, 'סינטה עגל', 'سنتا عجل', 'סינטה על הגריל.', 'سنتا مشوية مع خضار.', NULL, NULL, NULL, NULL, 125, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:55.054635', true, true);
INSERT INTO public.menu_items VALUES (156, 24, 'פלפלים ממולאים', 'فلفل محشي بالأرز', NULL, NULL, NULL, NULL, NULL, NULL, 55, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:56.891363', true, true);
INSERT INTO public.menu_items VALUES (157, 24, 'ארוחת טעימות השף', 'تشكيلة الشيف', NULL, NULL, NULL, NULL, NULL, NULL, 250, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 11, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:04:58.72816', true, true);
INSERT INTO public.menu_items VALUES (154, 24, 'שרימפס', 'قريدس', 'מטוגן/מבושל ברוטב חמאת עגבניות', 'جمبري مقلي أو مطبوخ مع صوص طماطم وزبدة.', '', '', '', '', 92, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, 0, '[]', 8, NULL, 0, '', '', NULL, '', '', '[]', NULL, '2025-12-02 17:08:51.808178', false, false);
INSERT INTO public.menu_items VALUES (153, 24, 'פילה לברק', 'فيليه سمك', 'פילה דג עם פירה ורוטב עגבניות.', 'سمك مع بطاطا مهروسة وصلصة بندورة.', '', '', '', '', 110, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, 0, '[]', 7, NULL, 0, '', '', NULL, '', '', '[]', NULL, '2025-12-02 17:11:56.314774', false, false);
INSERT INTO public.menu_items VALUES (159, 25, 'בורגר עגל', 'بورجر عجل', NULL, NULL, NULL, NULL, NULL, NULL, 50, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-12-02 17:12:38.444328', true, true);
INSERT INTO public.menu_items VALUES (165, 24, 'קופתיה', 'kuftee', 'קציצות בשר עגל מוגש עם קרפצ''יו חציל,ליוטניצה וטחינה גולמית', '', '', '', '', '', 68, NULL, NULL, false, false, false, false, false, false, false, false, false, false, false, false, true, NULL, NULL, 0, '[]', 3, NULL, 0, '', '', '1111111', '', '', '[]', '2025-12-02 17:11:18.361225', '2025-12-02 17:12:50.841731', false, false);


--
-- Data for Name: menu_item_dietary_properties; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: stock_categories; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_categories VALUES (1, 'ירקות ופירות', 'Vegetables & Fruits', 'ירקות ופירות טריים', 'Fresh vegetables and fruits', 'fa-carrot', '#28a745', 1, true, NULL);
INSERT INTO public.stock_categories VALUES (2, 'בשרים ודגים', 'Meat & Fish', 'מוצרי בשר ודגים', 'Meat and fish products', 'fa-fish', '#dc3545', 2, true, NULL);
INSERT INTO public.stock_categories VALUES (3, 'מוצרי חלב', 'Dairy Products', 'חלב, גבינות ומוצרי חלב', 'Milk, cheese and dairy products', 'fa-cheese', '#ffc107', 3, true, NULL);
INSERT INTO public.stock_categories VALUES (4, 'דגנים וקמח', 'Grains & Flour', 'דגנים, קמח ומוצרי אפייה', 'Grains, flour and baking products', 'fa-bread-slice', '#6f42c1', 4, true, NULL);
INSERT INTO public.stock_categories VALUES (5, 'תבלינים ורטבים', 'Spices & Sauces', 'תבלינים, רטבים ותוספות', 'Spices, sauces and seasonings', 'fa-pepper-hot', '#fd7e14', 5, true, NULL);
INSERT INTO public.stock_categories VALUES (6, 'שתייה', 'Beverages', 'משקאות חמים וקרים', 'Hot and cold beverages', 'fa-coffee', '#17a2b8', 6, true, NULL);
INSERT INTO public.stock_categories VALUES (7, 'חומרי ניקוי', 'Cleaning Supplies', 'חומרי ניקוי ותחזוקה', 'Cleaning and maintenance supplies', 'fa-broom', '#6c757d', 7, true, NULL);
INSERT INTO public.stock_categories VALUES (8, 'כלים חד פעמיים', 'Disposables', 'כלים חד פעמיים ואריזות', 'Disposable items and packaging', 'fa-box', '#20c997', 8, true, NULL);


--
-- Data for Name: stock_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_items VALUES (1, 'עגבניות', 'Tomatoes', 'עגבניות טריות', 'Fresh tomatoes', 'VEG001', NULL, 1, 'ingredient', 1, NULL, 'ק״ג', 'kg', 1, 8.5, 15, 10, 50, 20, true, 7, 'מקרר ירקות', 'refrigerated', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (4, 'חלב', 'Milk', 'חלב טרי 3%', 'Fresh milk 3%', 'DAIRY001', NULL, 3, 'ingredient', 1, NULL, 'ליטר', 'liter', 1, 5.5, 9, 20, 100, 40, true, 7, 'מקרר', 'refrigerated', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (5, 'קמח לבן', 'White Flour', 'קמח לבן למאפים', 'White flour for baking', 'FLOUR001', NULL, 4, 'ingredient', 2, NULL, 'ק״ג', 'kg', 1, 3.2, 6, 25, 100, 50, false, 365, 'מחסן יבש', 'dry storage', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (6, 'מלח', 'Salt', 'מלח בישול', 'Cooking salt', 'SPICE001', NULL, 5, 'ingredient', 3, NULL, 'ק״ג', 'kg', 1, 2.5, 5, 5, 20, 10, false, 0, 'מחסן יבש', 'dry storage', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (7, 'קפה', 'Coffee', 'קפה אספרסו', 'Espresso coffee', 'BEV001', NULL, 6, 'ingredient', 3, NULL, 'ק״ג', 'kg', 1, 80, 150, 3, 15, 5, false, 365, 'מחסן יבש', 'dry storage', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (8, 'נוזל כלים', 'Dish Soap', 'נוזל לניקוי כלים', 'Dish cleaning liquid', 'CLEAN001', NULL, 7, 'supply', 4, NULL, 'ליטר', 'liter', 1, 12, 0, 10, 50, 20, false, 0, 'מחסן ניקיון', 'cleaning storage', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (9, 'כוסות נייר', 'Paper Cups', 'כוסות חד פעמיות', 'Disposable cups', 'DISP001', NULL, 8, 'supply', 5, NULL, 'חבילה', 'pack', 100, 25, 0, 20, 100, 40, false, 0, 'מחסן כלים', 'supplies storage', true, NULL, NULL);
INSERT INTO public.stock_items VALUES (11, 'קולה', 'cola', NULL, NULL, NULL, NULL, 6, 'ingredient', NULL, NULL, 'בקבוק', 'בקבוק', 1, 4, NULL, 24, NULL, NULL, false, NULL, NULL, NULL, true, '2025-11-02 22:14:40.453368', '2025-11-02 22:14:40.453371');
INSERT INTO public.stock_items VALUES (14, 'מזלג ארוחה דגם שולחן דגם', 'מזלג ארוחה דגם שולחן דגם', NULL, NULL, NULL, NULL, NULL, 'ingredient', 11, NULL, 'יחידות', 'יחידות', 1, 4, NULL, 0, NULL, NULL, false, NULL, NULL, NULL, true, '2025-11-13 10:16:27.913255', '2025-11-13 10:16:27.91326');
INSERT INTO public.stock_items VALUES (13, 'סכין שולחן דגם GAMMA', 'סכין שולחן דגם GAMMA', NULL, NULL, NULL, NULL, 6, 'ingredient', 11, NULL, 'יחידות', 'יחידות', 1, 8.5, NULL, 5, NULL, NULL, false, NULL, NULL, NULL, true, '2025-11-13 10:16:27.632235', '2025-11-13 10:19:03.513632');


--
-- Data for Name: menu_item_ingredients; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: menu_item_prices; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: menu_item_variations; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: menu_print_configurations; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: menu_settings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.menu_settings VALUES (1, 'show_images', 'false', 'Show Images', NULL);


--
-- Data for Name: newsletter_subscribers; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.newsletter_subscribers VALUES (1, 'BkhZRosp@test.com', NULL, true, '2025-11-02 11:24:14.178222', NULL, 'footer');
INSERT INTO public.newsletter_subscribers VALUES (2, 'ZgCjU6@test.com', NULL, true, '2025-11-02 11:42:05.29359', NULL, 'footer');
INSERT INTO public.newsletter_subscribers VALUES (3, 'tOH8Ji@test.com', NULL, true, '2025-11-02 11:48:18.926731', NULL, 'footer');


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: payment_configs; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: payment_configuration; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.payment_configuration VALUES (1, 'grow', false, 'כרטיס אשראי (Grow)', 'Credit Card (Grow)', 1, NULL, NULL, NULL, NULL, 0, NULL, '2025-11-01 19:15:34.147388', '2025-11-01 19:15:34.147391');
INSERT INTO public.payment_configuration VALUES (2, 'max', false, 'כרטיס אשראי (Max)', 'Credit Card (Max)', 2, NULL, NULL, NULL, NULL, 0, NULL, '2025-11-01 19:15:34.192607', '2025-11-01 19:15:34.192654');


--
-- Data for Name: payment_transactions; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: pdf_menu_uploads; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.permissions VALUES (1, 'users.view', 'View Users', 'View user list and details', 'users', true, '2025-09-05 09:09:34.34787');
INSERT INTO public.permissions VALUES (2, 'users.create', 'Create Users', 'Create new users', 'users', true, '2025-09-05 09:09:34.394054');
INSERT INTO public.permissions VALUES (3, 'users.edit', 'Edit Users', 'Edit user information', 'users', true, '2025-09-05 09:09:34.43474');
INSERT INTO public.permissions VALUES (4, 'users.delete', 'Delete Users', 'Delete users from system', 'users', true, '2025-09-05 09:09:34.475919');
INSERT INTO public.permissions VALUES (5, 'roles.view', 'View Roles', 'View roles and permissions', 'roles', true, '2025-09-05 09:09:34.516723');
INSERT INTO public.permissions VALUES (6, 'roles.create', 'Create Roles', 'Create new roles', 'roles', true, '2025-09-05 09:09:34.558238');
INSERT INTO public.permissions VALUES (7, 'roles.edit', 'Edit Roles', 'Edit role permissions', 'roles', true, '2025-09-05 09:09:34.599024');
INSERT INTO public.permissions VALUES (8, 'roles.delete', 'Delete Roles', 'Delete roles', 'roles', true, '2025-09-05 09:09:34.641367');
INSERT INTO public.permissions VALUES (9, 'orders.view', 'View Orders', 'View order list and details', 'orders', true, '2025-09-05 09:09:34.684363');
INSERT INTO public.permissions VALUES (10, 'orders.create', 'Create Orders', 'Create new orders', 'orders', true, '2025-09-05 09:09:34.726063');
INSERT INTO public.permissions VALUES (11, 'orders.edit', 'Edit Orders', 'Modify order status and details', 'orders', true, '2025-09-05 09:09:34.768052');
INSERT INTO public.permissions VALUES (12, 'orders.delete', 'Delete Orders', 'Cancel/delete orders', 'orders', true, '2025-09-05 09:09:34.812563');
INSERT INTO public.permissions VALUES (13, 'kitchen.view', 'View Kitchen', 'Access kitchen display system', 'kitchen', true, '2025-09-05 09:09:34.85382');
INSERT INTO public.permissions VALUES (14, 'kitchen.manage', 'Manage Kitchen', 'Update order status in kitchen', 'kitchen', true, '2025-09-05 09:09:34.896123');
INSERT INTO public.permissions VALUES (15, 'delivery.view', 'View Deliveries', 'View delivery assignments', 'delivery', true, '2025-09-05 09:09:34.945063');
INSERT INTO public.permissions VALUES (16, 'delivery.manage', 'Manage Deliveries', 'Assign drivers and manage deliveries', 'delivery', true, '2025-09-05 09:09:34.986249');
INSERT INTO public.permissions VALUES (17, 'payments.view', 'View Payments', 'View payment transactions', 'payments', true, '2025-09-05 09:09:35.027563');
INSERT INTO public.permissions VALUES (18, 'payments.manage', 'Manage Payments', 'Process refunds and manage payments', 'payments', true, '2025-09-05 09:09:35.06847');
INSERT INTO public.permissions VALUES (19, 'menu.view', 'View Menu', 'View menu items and categories', 'menu', true, '2025-09-05 09:09:35.115376');
INSERT INTO public.permissions VALUES (20, 'menu.edit', 'Edit Menu', 'Edit menu items and categories', 'menu', true, '2025-09-05 09:09:35.156464');
INSERT INTO public.permissions VALUES (21, 'settings.view', 'View Settings', 'View system settings', 'settings', true, '2025-09-05 09:09:35.198148');
INSERT INTO public.permissions VALUES (22, 'settings.edit', 'Edit Settings', 'Modify system settings', 'settings', true, '2025-09-05 09:09:35.243183');
INSERT INTO public.permissions VALUES (23, 'branches.view', 'View Branches', 'View branch information', 'branches', true, '2025-09-05 09:09:35.284803');
INSERT INTO public.permissions VALUES (24, 'branches.edit', 'Edit Branches', 'Edit branch settings', 'branches', true, '2025-09-05 09:09:35.326805');
INSERT INTO public.permissions VALUES (25, 'checklists.view', 'View Checklists', 'View task checklists', 'checklists', true, '2025-09-05 09:09:35.368425');
INSERT INTO public.permissions VALUES (26, 'checklists.edit', 'Edit Checklists', 'Manage task checklists', 'checklists', true, '2025-09-05 09:09:35.409368');
INSERT INTO public.permissions VALUES (27, 'reports.view', 'View Reports', 'View system reports', 'reports', true, '2025-09-05 09:09:35.450116');
INSERT INTO public.permissions VALUES (28, 'system.admin', 'System Administration', 'Full system administration access', 'system', true, '2025-09-05 09:09:35.490681');
INSERT INTO public.permissions VALUES (29, 'stock.view', 'View Stock', 'View stock levels and items', 'stock', true, '2025-09-07 14:25:15.613077');
INSERT INTO public.permissions VALUES (30, 'stock.manage', 'Manage Stock', 'Add/edit stock items and levels', 'stock', true, '2025-09-07 14:25:15.66257');
INSERT INTO public.permissions VALUES (31, 'stock.transactions', 'Stock Transactions', 'Record stock transactions', 'stock', true, '2025-09-07 14:25:15.702809');
INSERT INTO public.permissions VALUES (32, 'stock.alerts', 'Stock Alerts', 'Manage stock alerts and notifications', 'stock', true, '2025-09-07 14:25:15.743023');
INSERT INTO public.permissions VALUES (33, 'stock.shopping_lists', 'Shopping Lists', 'Create and manage shopping lists', 'stock', true, '2025-09-07 14:25:15.783655');
INSERT INTO public.permissions VALUES (34, 'stock.suppliers', 'Manage Suppliers', 'Manage supplier information', 'stock', true, '2025-09-07 14:25:15.824699');
INSERT INTO public.permissions VALUES (35, 'stock.settings', 'Stock Settings', 'Configure stock management settings', 'stock', true, '2025-09-07 14:25:15.865206');
INSERT INTO public.permissions VALUES (36, 'stock.analytics', 'Stock Analytics', 'View stock reports and analytics', 'stock', true, '2025-09-07 14:25:15.905021');
INSERT INTO public.permissions VALUES (37, 'live_events.view', 'צפייה באירועי LIVE', 'View live events list', 'live_events', true, '2025-12-08 14:09:35.438193');
INSERT INTO public.permissions VALUES (38, 'live_events.create', 'יצירת אירועי LIVE', 'Create new live events', 'live_events', true, '2025-12-08 14:09:35.438193');
INSERT INTO public.permissions VALUES (39, 'live_events.edit', 'עריכת אירועי LIVE', 'Edit existing live events', 'live_events', true, '2025-12-08 14:09:35.438193');
INSERT INTO public.permissions VALUES (40, 'live_events.delete', 'מחיקת אירועי LIVE', 'Delete live events', 'live_events', true, '2025-12-08 14:09:35.438193');
INSERT INTO public.permissions VALUES (41, 'live_events.reservations', 'ניהול הזמנות LIVE', 'Manage live event reservations', 'live_events', true, '2025-12-08 14:09:35.438193');
INSERT INTO public.permissions VALUES (42, 'live_events.scanner', 'סריקת כניסה LIVE', 'Access entrance scanner for live events', 'live_events', true, '2025-12-08 14:09:35.438193');


--
-- Data for Name: phone_verifications; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: print_templates; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: printer_configs; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: privacy_policy; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: receipt_custom_field_audit; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: receipt_custom_field_values; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: shopping_lists; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.shopping_lists VALUES (5, 1, 11, 'קבלה 10 - Shshsh', 'נוצר אוטומטית מקבלה סרוקה #10', 'received', false, NULL, '2025-11-13', NULL, 1182, 1, 1, '2025-11-13 10:16:27.484898', '2025-11-13 10:16:27.484901');


--
-- Data for Name: receipt_imports; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.receipt_imports VALUES (3, 8, 'rejected', NULL, NULL, 0, '2023-01-29', 1375, 1, '2025-11-12 12:47:04.569663', '', 1, '2025-11-12 12:46:29.269841', '2025-11-12 12:47:04.57086', 1, '[]', '{"items": [{"unit": "ק״ג", "quantity": 2.0, "unit_price": 194.07, "total_price": 388.14, "product_name": "גמון לבן כף אדוויס 15 ק\"ג"}, {"unit": "ק״ג", "quantity": 1.0, "unit_price": 185.59, "total_price": 185.59, "product_name": "גמון לבן כף אדוויס 15 ק\"ג"}, {"unit": "ק״ג", "quantity": 2.0, "unit_price": 295.76, "total_price": 591.52, "product_name": "בתערובת כבש לכלב 10 ק\"ג"}], "receipt_date": "2023-01-29", "total_amount": 1375.0, "supplier_name": "ריקוס צ''ויס"}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (4, 9, 'needs_review', NULL, NULL, 0, '2023-09-14', 6944, NULL, NULL, NULL, 1, '2025-11-12 16:20:31.134388', '2025-11-12 16:20:31.134392', 1, '[]', '{"items": [{"unit": "ק״ג", "quantity": 4.0, "unit_price": 80.0, "total_price": 320.0, "product_name": "משחת קארי אדום 1 ק\"ג"}, {"unit": "מ״ל", "quantity": 2.0, "unit_price": 65.0, "total_price": 130.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 60.0, "total_price": 120.0, "product_name": "חומץ אורז 1 ליטר"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "product_name": "חומץ אורז 1.8 ליטר"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "product_name": "חומץ אורז 5 ליטר"}, {"unit": "ליטר", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "product_name": "חומץ אורז 20 ליטר"}, {"unit": "מ״ל", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "product_name": "חומץ אורז 540 מ\"ל"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "product_name": "חומץ אורז 1.8 ליטר"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "product_name": "חומץ אורז 5 ליטר"}, {"unit": "ליטר", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "product_name": "חומץ אורז 20 ליטר"}, {"unit": "מ״ל", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "product_name": "חומץ אורז 540 מ\"ל"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 110.0, "total_price": 220.0, "product_name": "חומץ אורז 1.8 ליטר"}, {"unit": "ליטר", "quantity": 2.0, "unit_price": 325.0, "total_price": 650.0, "product_name": "חומץ אורז 5 ליטר"}, {"unit": "ליטר", "quantity": 1.0, "unit_price": 325.0, "total_price": 325.0, "product_name": "חומץ אורז 20 ליטר"}, {"unit": "מ״ל", "quantity": 2.0, "unit_price": 45.0, "total_price": 90.0, "product_name": "חומץ אורז 540 מ\"ל"}], "receipt_date": "2023-09-14", "total_amount": 6944.0, "supplier_name": "מזרח ומערב יבוא ושיווק בע\"מ"}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (5, 10, 'needs_review', NULL, NULL, 0, '2023-09-14', 6944, NULL, NULL, NULL, 1, '2025-11-12 22:58:18.745223', '2025-11-12 22:58:18.745226', 1, '[]', '{"items": [{"unit": "ליטר", "quantity": 4.0, "unit_price": 80.0, "total_price": 320.0, "product_name": "שמן שומשום טהור 2 ליטר"}, {"unit": "מ\"ל", "quantity": 6.0, "unit_price": 13.4, "total_price": 80.4, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 5.0, "unit_price": 13.0, "total_price": 65.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 5.0, "unit_price": 12.6, "total_price": 63.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 5.0, "unit_price": 12.0, "total_price": 60.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 5.0, "unit_price": 11.0, "total_price": 55.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 32.5, "total_price": 65.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 3.0, "unit_price": 15.0, "total_price": 45.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 40.0, "total_price": 80.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 40.0, "total_price": 80.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 1140.0, "total_price": 2280.0, "product_name": "חומץ אורז 500 מ\"ל"}, {"unit": "מ\"ל", "quantity": 2.0, "unit_price": 33.0, "total_price": 66.0, "product_name": "חומץ אורז 500 מ\"ל"}], "receipt_date": "2023-09-14", "total_amount": 6944.0, "supplier_name": "מזרח ומערב יבוא ושיווק בע\"מ"}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (6, 11, 'needs_review', NULL, NULL, 0, '2023-08-30', 4781.57, NULL, NULL, NULL, 1, '2025-11-13 08:17:55.54492', '2025-11-13 08:17:55.544925', 2, '[]', '{"items": [{"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}, {"unit": "בקבוק", "quantity": 24.0, "unit_price": 10.0, "total_price": 240.0, "product_name": "בקבוק זכוכית 330 מ\"ל"}], "receipt_date": "2023-08-30", "total_amount": 4781.57, "supplier_name": "הכרם"}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (11, 15, 'needs_review', NULL, NULL, 0, '2025-11-13', NULL, NULL, NULL, NULL, 1, '2025-11-13 19:24:58.834299', '2025-11-13 19:24:58.834304', 2, '[]', '{"items": [{"unit": "מ\"ל", "quantity": 4, "unit_price": 0.0, "total_price": 0.0, "product_name": "קוקה קולה קלאסי 350 מ\"ל"}, {"unit": "מ\"ל", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "product_name": "ספרייט בקבוק 330 מ\"ל"}, {"unit": "מ\"ל", "quantity": 5, "unit_price": 0.0, "total_price": 0.0, "product_name": "קוקה קולה ZERO קלאסי 350 מ\"ל"}, {"unit": "מ\"ל", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "product_name": "תה FUZE בקבוק 330 מ\"ל"}, {"unit": "מ\"ל", "quantity": 1, "unit_price": 0.0, "total_price": 0.0, "product_name": "קוקה קולה קלאסי 350 מ\"ל"}], "receipt_date": "2025-11-13", "total_amount": 0.0, "supplier_name": "החברה המרכזית להפצת משקאות בע\"מ", "supplier_email": "moked.sherut@cocacola.co.il", "supplier_phone": "054-2899005", "supplier_address": "ת.ד 555, פתח תקוה 4911401", "supplier_contact_person": null}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (8, 12, 'scanned', NULL, NULL, NULL, NULL, 100, NULL, NULL, NULL, 3, '2025-11-13 08:30:56.643916', '2025-11-13 08:30:56.643921', NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (9, 13, 'needs_review', NULL, NULL, 0, '2025-11-13', 1182, NULL, NULL, NULL, 1, '2025-11-13 09:58:21.407616', '2025-11-13 09:58:21.40762', 1, '[]', '{"items": [{"unit": "יחידות", "quantity": 84.0, "unit_price": 8.5, "total_price": 714.0, "product_name": "GAMMA סרגל זווית"}, {"unit": "יחידות", "quantity": 72.0, "unit_price": 4.0, "total_price": 288.0, "product_name": "דבק אקרילי דגם הורס"}], "receipt_date": "2025-11-13", "total_amount": 1182.0, "supplier_name": "סופרנובה בע\"מ"}', NULL, NULL, NULL);
INSERT INTO public.receipt_imports VALUES (10, 14, 'approved', 11, NULL, 0, '2025-11-13', 1182, 1, '2025-11-13 10:16:27.150072', NULL, 1, '2025-11-13 09:59:13.047022', '2025-11-13 10:16:27.560207', 1, '[]', '{"items": [{"unit": "יחידות", "quantity": 84.0, "unit_price": 8.5, "total_price": 714.0, "product_name": "סכין שולחן דגם GAMMA"}, {"unit": "יחידות", "quantity": 72.0, "unit_price": 4.0, "total_price": 288.0, "product_name": "מזלג ארוחה דגם שולחן דגם"}], "receipt_date": "2025-11-13", "total_amount": 1182.0, "supplier_name": "סופרנובה בע\"מ"}', NULL, 5, 'RECEIPT_10_2965d33a');


--
-- Data for Name: supplier_items; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: receipt_import_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.receipt_import_items VALUES (1, 3, 'גמון לבן כף אדוויס 15 ק"ג', 2, 194.07, 388.14, 'ק״ג', NULL, NULL, 0, true, false, NULL, 'גמון לבן כף אדוויס 15 ק"ג', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (2, 3, 'גמון לבן כף אדוויס 15 ק"ג', 1, 185.59, 185.59, 'ק״ג', NULL, NULL, 0, true, false, NULL, 'גמון לבן כף אדוויס 15 ק"ג', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (3, 3, 'בתערובת כבש לכלב 10 ק"ג', 2, 295.76, 591.52, 'ק״ג', NULL, NULL, 0, true, false, NULL, 'בתערובת כבש לכלב 10 ק"ג', 3, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (4, 4, 'משחת קארי אדום 1 ק"ג', 4, 80, 320, 'ק״ג', NULL, NULL, 0, true, false, NULL, 'משחת קארי אדום 1 ק"ג', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (5, 4, 'חומץ אורז 500 מ"ל', 2, 65, 130, 'מ״ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (6, 4, 'חומץ אורז 1 ליטר', 2, 60, 120, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 1 ליטר', 3, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (7, 4, 'חומץ אורז 1.8 ליטר', 2, 110, 220, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 1.8 ליטר', 4, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (8, 4, 'חומץ אורז 5 ליטר', 2, 325, 650, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 5 ליטר', 5, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (9, 4, 'חומץ אורז 20 ליטר', 1, 325, 325, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 20 ליטר', 6, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (10, 4, 'חומץ אורז 540 מ"ל', 2, 45, 90, 'מ״ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 540 מ"ל', 7, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (11, 4, 'חומץ אורז 1.8 ליטר', 2, 110, 220, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 1.8 ליטר', 8, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (12, 4, 'חומץ אורז 5 ליטר', 2, 325, 650, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 5 ליטר', 9, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (13, 4, 'חומץ אורז 20 ליטר', 1, 325, 325, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 20 ליטר', 10, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (14, 4, 'חומץ אורז 540 מ"ל', 2, 45, 90, 'מ״ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 540 מ"ל', 11, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (15, 4, 'חומץ אורז 1.8 ליטר', 2, 110, 220, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 1.8 ליטר', 12, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (16, 4, 'חומץ אורז 5 ליטר', 2, 325, 650, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 5 ליטר', 13, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (17, 4, 'חומץ אורז 20 ליטר', 1, 325, 325, 'ליטר', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 20 ליטר', 14, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (18, 4, 'חומץ אורז 540 מ"ל', 2, 45, 90, 'מ״ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 540 מ"ל', 15, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (19, 5, 'שמן שומשום טהור 2 ליטר', 4, 80, 320, 'ליטר', NULL, NULL, 0, true, false, NULL, 'שמן שומשום טהור 2 ליטר', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (20, 5, 'חומץ אורז 500 מ"ל', 6, 13.4, 80.4, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (21, 5, 'חומץ אורז 500 מ"ל', 5, 13, 65, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 3, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (22, 5, 'חומץ אורז 500 מ"ל', 5, 12.6, 63, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 4, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (23, 5, 'חומץ אורז 500 מ"ל', 5, 12, 60, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 5, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (24, 5, 'חומץ אורז 500 מ"ל', 5, 11, 55, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 6, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (25, 5, 'חומץ אורז 500 מ"ל', 2, 32.5, 65, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 7, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (26, 5, 'חומץ אורז 500 מ"ל', 3, 15, 45, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 8, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (27, 5, 'חומץ אורז 500 מ"ל', 2, 33, 66, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 9, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (28, 5, 'חומץ אורז 500 מ"ל', 2, 33, 66, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 10, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (29, 5, 'חומץ אורז 500 מ"ל', 2, 40, 80, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 11, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (30, 5, 'חומץ אורז 500 מ"ל', 2, 40, 80, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 12, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (31, 5, 'חומץ אורז 500 מ"ל', 2, 33, 66, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 13, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (32, 5, 'חומץ אורז 500 מ"ל', 2, 1140, 2280, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 14, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (33, 5, 'חומץ אורז 500 מ"ל', 2, 33, 66, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'חומץ אורז 500 מ"ל', 15, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (34, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (35, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (36, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 3, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (37, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 4, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (38, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 5, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (39, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 6, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (40, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 7, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (41, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 8, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (42, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 9, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (43, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 10, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (44, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 11, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (45, 6, 'בקבוק זכוכית 330 מ"ל', 24, 10, 240, 'בקבוק', NULL, NULL, 0, true, false, NULL, 'בקבוק זכוכית 330 מ"ל', 12, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (46, 9, 'GAMMA סרגל זווית', 84, 8.5, 714, 'יחידות', NULL, NULL, 0, true, false, NULL, 'GAMMA סרגל זווית', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (47, 9, 'דבק אקרילי דגם הורס', 72, 4, 288, 'יחידות', NULL, NULL, 0, true, false, NULL, 'דבק אקרילי דגם הורס', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (48, 10, 'סכין שולחן דגם GAMMA', 84, 8.5, 714, 'יחידות', 13, NULL, 0, true, true, NULL, 'סכין שולחן דגם GAMMA', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (49, 10, 'מזלג ארוחה דגם שולחן דגם', 72, 4, 288, 'יחידות', 14, NULL, 0, true, true, NULL, 'מזלג ארוחה דגם שולחן דגם', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (50, 11, 'קוקה קולה קלאסי 350 מ"ל', 4, NULL, NULL, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'קוקה קולה קלאסי 350 מ"ל', 1, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (51, 11, 'ספרייט בקבוק 330 מ"ל', 1, NULL, NULL, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'ספרייט בקבוק 330 מ"ל', 2, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (52, 11, 'קוקה קולה ZERO קלאסי 350 מ"ל', 5, NULL, NULL, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'קוקה קולה ZERO קלאסי 350 מ"ל', 3, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (53, 11, 'תה FUZE בקבוק 330 מ"ל', 1, NULL, NULL, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'תה FUZE בקבוק 330 מ"ל', 4, NULL, 'pending');
INSERT INTO public.receipt_import_items VALUES (54, 11, 'קוקה קולה קלאסי 350 מ"ל', 1, NULL, NULL, 'מ"ל', NULL, NULL, 0, true, false, NULL, 'קוקה קולה קלאסי 350 מ"ל', 5, NULL, 'pending');


--
-- Data for Name: receipt_items; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: reservation_seating_areas; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.reservation_seating_areas VALUES (2, 'מרפסת', 'Patio', 'מרפסת חיצונית', 'Outdoor patio area', 'fa-tree', NULL, 2, NULL, 10);
INSERT INTO public.reservation_seating_areas VALUES (4, 'בר', 'Bar Area', 'ליד הבר', 'Near the bar', 'fa-glass-martini-alt', NULL, 4, NULL, 10);
INSERT INTO public.reservation_seating_areas VALUES (5, 'בחצר', 'garden', '', '', 'fa-chair', true, 0, '2025-11-21 22:51:00.310502', 10);
INSERT INTO public.reservation_seating_areas VALUES (6, 'אולם גדול', 'Main place', '', '', 'fa-chair', true, 0, '2025-11-21 22:51:38.710411', 10);


--
-- Data for Name: reservations; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.reservations VALUES (1, NULL, 'חליל שיבאן', '0526647778', 'khalilshiban@gmail.com', '2025-11-27', '20:30:00', 10, 'שולחן בן זונה', 'confirmed', '2025-11-21 22:19:52.794537', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (8, 1, 'David Cohen', '050-1234567', 'david@example.com', '2025-11-22', '12:00:00', 4, 'Window seat please', 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (9, 1, 'Sarah Levi', '050-2345678', 'sarah@example.com', '2025-11-22', '13:30:00', 2, 'Vegetarian menu', 'confirmed', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (10, 1, 'Michael Ben-David', '050-3456789', 'michael@example.com', '2025-11-22', '18:00:00', 6, 'Birthday celebration', 'pending', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (11, 1, 'Rachel Mizrahi', '050-4567890', 'rachel@example.com', '2025-11-22', '19:30:00', 3, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (12, 1, 'Yossi Katz', '050-5678901', 'yossi@example.com', '2025-11-22', '20:00:00', 8, 'Corporate dinner', 'confirmed', '2025-11-22 12:44:08.255467', 6, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (13, 1, 'Tal Shapira', '050-6789012', 'tal@example.com', '2025-11-22', '21:00:00', 2, 'Changed plans', 'cancelled', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (14, 1, 'Avi Goldstein', '050-7890123', 'avi@example.com', '2025-11-23', '12:30:00', 5, 'Anniversary', 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (15, 1, 'Maya Rosen', '050-8901234', 'maya@example.com', '2025-11-23', '14:00:00', 3, NULL, 'pending', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (16, 1, 'Chen Avraham', '050-9012345', 'chen@example.com', '2025-11-23', '19:00:00', 4, 'Kids menu needed', 'confirmed', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (17, 1, 'Noa Peretz', '050-0123456', 'noa@example.com', '2025-11-23', '20:30:00', 7, 'Large family dinner', 'confirmed', '2025-11-22 12:44:08.255467', 6, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (18, 1, 'Eli Friedman', '050-1111111', 'eli@example.com', '2025-11-24', '13:00:00', 2, 'Quick lunch', 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (19, 1, 'Shira Azoulay', '050-2222222', 'shira@example.com', '2025-11-24', '18:30:00', 4, 'Gluten-free options', 'pending', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (20, 1, 'Dan Miller', '050-3333333', 'dan@example.com', '2025-11-24', '20:00:00', 6, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (21, 1, 'Ronit Golan', '050-4444444', 'ronit@example.com', '2025-11-25', '12:00:00', 3, 'Outdoor seating', 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (22, 1, 'Yair Shalev', '050-5555555', 'yair@example.com', '2025-11-25', '14:30:00', 5, 'Business meeting', 'confirmed', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (23, 1, 'Liora Dahan', '050-6666666', 'liora@example.com', '2025-11-25', '17:00:00', 2, 'Emergency', 'cancelled', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (24, 1, 'Moshe Baruch', '050-7777777', 'moshe@example.com', '2025-11-25', '19:00:00', 8, 'Special occasion', 'confirmed', '2025-11-22 12:44:08.255467', 6, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (25, 1, 'Tamar Levy', '050-8888888', 'tamar@example.com', '2025-11-25', '21:00:00', 4, NULL, 'pending', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (26, 1, 'Gadi Hoffman', '050-9999999', 'gadi@example.com', '2025-11-26', '12:00:00', 6, 'Family reunion', 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (27, 1, 'Orly Kaplan', '050-0000000', 'orly@example.com', '2025-11-26', '13:00:00', 4, 'Kids friendly', 'confirmed', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (28, 1, 'Amir Cohen', '050-1212121', 'amir@example.com', '2025-11-26', '18:00:00', 10, 'Large group', 'confirmed', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (29, 1, 'Michal Stern', '050-2323232', 'michal@example.com', '2025-11-26', '19:00:00', 5, NULL, 'pending', '2025-11-22 12:44:08.255467', 6, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (30, 1, 'Uri Shapiro', '050-3434343', 'uri@example.com', '2025-11-26', '20:00:00', 3, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (31, 1, 'Hila Mazor', '050-4545454', 'hila@example.com', '2025-11-26', '21:30:00', 7, 'Celebration', 'confirmed', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (32, 1, 'Boaz Green', '050-5656565', 'boaz@example.com', '2025-11-27', '13:00:00', 4, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (33, 1, 'Sigal Alon', '050-6767676', 'sigal@example.com', '2025-11-27', '14:30:00', 2, 'Vegan options', 'pending', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (34, 1, 'Rami Zohar', '050-7878787', 'rami@example.com', '2025-11-27', '19:00:00', 6, 'Allergy: nuts', 'confirmed', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (35, 1, 'Irit Weiss', '050-8989898', 'irit@example.com', '2025-11-27', '20:30:00', 5, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 6, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (36, 1, 'Kobi Mor', '050-9090909', 'kobi@example.com', '2025-11-28', '12:30:00', 3, 'Quiet table', 'pending', '2025-11-22 12:44:08.255467', 2, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (37, 1, 'Nurit Paz', '050-0101010', 'nurit@example.com', '2025-11-28', '18:00:00', 4, NULL, 'confirmed', '2025-11-22 12:44:08.255467', 4, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (38, 1, 'Eyal Koren', '050-1313131', 'eyal@example.com', '2025-11-28', '19:30:00', 2, 'Date night', 'confirmed', '2025-11-22 12:44:08.255467', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (39, NULL, 'Test Customer AVgw3D', '+972501234567', 'test@example.com', '2025-11-23', '19:00:00', 4, 'Testing reservation', 'confirmed', '2025-11-22 13:11:08.8765', 5, NULL, NULL, NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (40, NULL, 'Test Customer 2jcgbD', '+972526647778', 'test@example.com', '2025-11-23', '19:00:00', 4, 'Window seat please', 'confirmed', '2025-11-22 13:53:30.337837', NULL, 'hwNUo8Kh-8nGm8zo2BNme2HuYUpgXCzIahVUtGEdjk8', '2025-11-22 13:53:30.335523', NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (41, NULL, 'Test Customer NYgViv', '+972526647778', 'test@example.com', '2025-11-28', '17:57:00', 4, 'Window seat please', 'confirmed', '2025-11-22 13:56:35.574948', NULL, '3F0RQcNTyLkVf0uui4OOl6oQeIvnu94EqmwwCQjXt-o', '2025-11-22 13:56:35.572671', NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (42, NULL, 'בדיקה אוטומטית', '0509998887', 'test@example.com', '2025-12-15', '19:00:00', 2, '', 'confirmed', '2025-11-23 19:15:46.050368', 5, '8PvBN2F-1vtkVYAIjHYUUfksafyg7fCYnW06S937SQU', '2025-11-23 19:15:46.044541', NULL, NULL, NULL, NULL, 'regular');
INSERT INTO public.reservations VALUES (43, NULL, 'חליל שיבאן', '0526647778', 'khalilshiban@gmail.com', '2025-11-24', '18:12:00', 6, '', 'pending', '2025-11-23 20:13:19.624139', 5, '9ssgLw8J60KvtHqYpb7t6EI5LlucP3rFg2QVHLK6phQ', '2025-11-23 20:13:19.621359', NULL, NULL, NULL, NULL, 'regular');


--
-- Data for Name: reservation_alerts; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: reservation_blackouts; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: reservation_settings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.reservation_settings VALUES (1, true, 'https://tbit.be/BHWCPU', 'הזמינו שולחן', 'Reserve a Table', 'הזמנת שולחן', 'Table Reservation', NULL, NULL, true, NULL, '2025-11-23 21:45:24.914809', '{"monday": {"open": "11:00", "close": "22:00", "enabled": true}, "tuesday": {"open": "11:00", "close": "22:00", "enabled": true}, "wednesday": {"open": "11:00", "close": "22:00", "enabled": true}, "thursday": {"open": "11:00", "close": "22:00", "enabled": true}, "friday": {"open": "11:00", "close": "23:00", "enabled": true}, "saturday": {"open": "11:00", "close": "23:00", "enabled": true}, "sunday": {"open": "11:00", "close": "22:00", "enabled": true}}', 12, 0, 30, 90, true, 3, '10:00', '19:00', true, NULL, NULL, false, 'שלום {customer_name}, זוהי תזכורת להזמנת השולחן שלך ב-{restaurant_name} ב-{date} בשעה {time}. לאישור: {confirm_link}', 'שלום {customer_name}, רצינו לוודא שאתה עדיין מגיע להזמנת השולחן שלך ב-{restaurant_name} ב-{date} בשעה {time}. תודה!');


--
-- Data for Name: reservation_table_types; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: reservation_tables; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: restaurant_events; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.roles VALUES (1, 'superadmin', 'Super Administrator', 'Full system access with all permissions', true, true, '2025-09-05 09:09:35.535707');
INSERT INTO public.roles VALUES (2, 'admin', 'Administrator', 'Full administrative access to most features', true, true, '2025-09-05 09:09:35.579717');
INSERT INTO public.roles VALUES (3, 'manager', 'Manager', 'Management access to operations and reports', true, false, '2025-09-05 09:09:35.621082');
INSERT INTO public.roles VALUES (4, 'kitchen', 'Kitchen Staff', 'Kitchen operations and order management', true, false, '2025-09-05 09:09:35.662468');
INSERT INTO public.roles VALUES (5, 'delivery', 'Delivery Manager', 'Delivery and driver management', true, false, '2025-09-05 09:09:35.704051');
INSERT INTO public.roles VALUES (6, 'cashier', 'Cashier', 'Order taking and payment processing', true, false, '2025-09-05 09:09:35.745445');
INSERT INTO public.roles VALUES (7, 'viewer', 'Viewer', 'Read-only access to reports and data', true, false, '2025-09-05 09:09:35.795136');
INSERT INTO public.roles VALUES (8, 'testrole', 'test role', 'A test role for verification', true, false, '2025-12-08 21:21:53.223791');


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.role_permissions VALUES (1, 3);
INSERT INTO public.role_permissions VALUES (1, 17);
INSERT INTO public.role_permissions VALUES (1, 28);
INSERT INTO public.role_permissions VALUES (1, 20);
INSERT INTO public.role_permissions VALUES (1, 18);
INSERT INTO public.role_permissions VALUES (1, 16);
INSERT INTO public.role_permissions VALUES (1, 6);
INSERT INTO public.role_permissions VALUES (1, 21);
INSERT INTO public.role_permissions VALUES (1, 25);
INSERT INTO public.role_permissions VALUES (1, 2);
INSERT INTO public.role_permissions VALUES (1, 10);
INSERT INTO public.role_permissions VALUES (1, 7);
INSERT INTO public.role_permissions VALUES (1, 23);
INSERT INTO public.role_permissions VALUES (1, 13);
INSERT INTO public.role_permissions VALUES (1, 4);
INSERT INTO public.role_permissions VALUES (1, 12);
INSERT INTO public.role_permissions VALUES (1, 24);
INSERT INTO public.role_permissions VALUES (1, 27);
INSERT INTO public.role_permissions VALUES (1, 5);
INSERT INTO public.role_permissions VALUES (1, 19);
INSERT INTO public.role_permissions VALUES (1, 14);
INSERT INTO public.role_permissions VALUES (1, 15);
INSERT INTO public.role_permissions VALUES (1, 8);
INSERT INTO public.role_permissions VALUES (1, 9);
INSERT INTO public.role_permissions VALUES (1, 1);
INSERT INTO public.role_permissions VALUES (1, 22);
INSERT INTO public.role_permissions VALUES (1, 26);
INSERT INTO public.role_permissions VALUES (1, 11);
INSERT INTO public.role_permissions VALUES (2, 17);
INSERT INTO public.role_permissions VALUES (2, 3);
INSERT INTO public.role_permissions VALUES (2, 20);
INSERT INTO public.role_permissions VALUES (2, 18);
INSERT INTO public.role_permissions VALUES (2, 16);
INSERT INTO public.role_permissions VALUES (2, 6);
INSERT INTO public.role_permissions VALUES (2, 21);
INSERT INTO public.role_permissions VALUES (2, 25);
INSERT INTO public.role_permissions VALUES (2, 2);
INSERT INTO public.role_permissions VALUES (2, 10);
INSERT INTO public.role_permissions VALUES (2, 7);
INSERT INTO public.role_permissions VALUES (2, 23);
INSERT INTO public.role_permissions VALUES (2, 13);
INSERT INTO public.role_permissions VALUES (2, 4);
INSERT INTO public.role_permissions VALUES (2, 12);
INSERT INTO public.role_permissions VALUES (2, 24);
INSERT INTO public.role_permissions VALUES (2, 27);
INSERT INTO public.role_permissions VALUES (2, 5);
INSERT INTO public.role_permissions VALUES (2, 19);
INSERT INTO public.role_permissions VALUES (2, 15);
INSERT INTO public.role_permissions VALUES (2, 14);
INSERT INTO public.role_permissions VALUES (2, 8);
INSERT INTO public.role_permissions VALUES (2, 9);
INSERT INTO public.role_permissions VALUES (2, 1);
INSERT INTO public.role_permissions VALUES (2, 26);
INSERT INTO public.role_permissions VALUES (2, 22);
INSERT INTO public.role_permissions VALUES (2, 11);
INSERT INTO public.role_permissions VALUES (3, 12);
INSERT INTO public.role_permissions VALUES (3, 13);
INSERT INTO public.role_permissions VALUES (3, 25);
INSERT INTO public.role_permissions VALUES (3, 15);
INSERT INTO public.role_permissions VALUES (3, 24);
INSERT INTO public.role_permissions VALUES (3, 27);
INSERT INTO public.role_permissions VALUES (3, 14);
INSERT INTO public.role_permissions VALUES (3, 9);
INSERT INTO public.role_permissions VALUES (3, 10);
INSERT INTO public.role_permissions VALUES (3, 26);
INSERT INTO public.role_permissions VALUES (3, 19);
INSERT INTO public.role_permissions VALUES (3, 23);
INSERT INTO public.role_permissions VALUES (3, 20);
INSERT INTO public.role_permissions VALUES (3, 11);
INSERT INTO public.role_permissions VALUES (3, 16);
INSERT INTO public.role_permissions VALUES (4, 12);
INSERT INTO public.role_permissions VALUES (4, 14);
INSERT INTO public.role_permissions VALUES (4, 9);
INSERT INTO public.role_permissions VALUES (4, 10);
INSERT INTO public.role_permissions VALUES (4, 13);
INSERT INTO public.role_permissions VALUES (4, 11);
INSERT INTO public.role_permissions VALUES (5, 12);
INSERT INTO public.role_permissions VALUES (5, 15);
INSERT INTO public.role_permissions VALUES (5, 9);
INSERT INTO public.role_permissions VALUES (5, 10);
INSERT INTO public.role_permissions VALUES (5, 11);
INSERT INTO public.role_permissions VALUES (5, 16);
INSERT INTO public.role_permissions VALUES (6, 17);
INSERT INTO public.role_permissions VALUES (6, 12);
INSERT INTO public.role_permissions VALUES (6, 9);
INSERT INTO public.role_permissions VALUES (6, 10);
INSERT INTO public.role_permissions VALUES (6, 11);
INSERT INTO public.role_permissions VALUES (6, 18);
INSERT INTO public.role_permissions VALUES (7, 17);
INSERT INTO public.role_permissions VALUES (7, 21);
INSERT INTO public.role_permissions VALUES (7, 15);
INSERT INTO public.role_permissions VALUES (7, 25);
INSERT INTO public.role_permissions VALUES (7, 27);
INSERT INTO public.role_permissions VALUES (7, 5);
INSERT INTO public.role_permissions VALUES (7, 9);
INSERT INTO public.role_permissions VALUES (7, 1);
INSERT INTO public.role_permissions VALUES (7, 19);
INSERT INTO public.role_permissions VALUES (7, 23);
INSERT INTO public.role_permissions VALUES (7, 13);
INSERT INTO public.role_permissions VALUES (1, 32);
INSERT INTO public.role_permissions VALUES (1, 34);
INSERT INTO public.role_permissions VALUES (1, 35);
INSERT INTO public.role_permissions VALUES (1, 33);
INSERT INTO public.role_permissions VALUES (1, 36);
INSERT INTO public.role_permissions VALUES (1, 29);
INSERT INTO public.role_permissions VALUES (1, 30);
INSERT INTO public.role_permissions VALUES (1, 31);
INSERT INTO public.role_permissions VALUES (2, 32);
INSERT INTO public.role_permissions VALUES (2, 34);
INSERT INTO public.role_permissions VALUES (2, 35);
INSERT INTO public.role_permissions VALUES (2, 33);
INSERT INTO public.role_permissions VALUES (2, 36);
INSERT INTO public.role_permissions VALUES (2, 29);
INSERT INTO public.role_permissions VALUES (2, 30);
INSERT INTO public.role_permissions VALUES (2, 31);
INSERT INTO public.role_permissions VALUES (7, 29);
INSERT INTO public.role_permissions VALUES (3, 34);
INSERT INTO public.role_permissions VALUES (3, 29);
INSERT INTO public.role_permissions VALUES (3, 35);
INSERT INTO public.role_permissions VALUES (3, 32);
INSERT INTO public.role_permissions VALUES (3, 33);
INSERT INTO public.role_permissions VALUES (3, 36);
INSERT INTO public.role_permissions VALUES (3, 31);
INSERT INTO public.role_permissions VALUES (3, 30);
INSERT INTO public.role_permissions VALUES (4, 29);
INSERT INTO public.role_permissions VALUES (4, 31);
INSERT INTO public.role_permissions VALUES (2, 37);
INSERT INTO public.role_permissions VALUES (2, 38);
INSERT INTO public.role_permissions VALUES (2, 39);
INSERT INTO public.role_permissions VALUES (2, 40);
INSERT INTO public.role_permissions VALUES (2, 41);
INSERT INTO public.role_permissions VALUES (2, 42);
INSERT INTO public.role_permissions VALUES (8, 19);
INSERT INTO public.role_permissions VALUES (8, 42);
INSERT INTO public.role_permissions VALUES (8, 41);
INSERT INTO public.role_permissions VALUES (8, 37);


--
-- Data for Name: shopping_list_items; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.shopping_list_items VALUES (1, 5, 13, 84, 8.5, 714, 84, 8.5, 714, 'received', NULL);
INSERT INTO public.shopping_list_items VALUES (2, 5, 14, 72, 4, 288, 72, 4, 288, 'received', NULL);


--
-- Data for Name: site_settings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.site_settings VALUES (1, 'Rai', 'Rai', 'Rai', 'Rai', 'מטבח בלקני-מזרחי', '', 'חוויה קולינרית ייחודית של טעמי אסיה', '', 'אודותינו', 'About Us', 'ברוכים הבאים למסעדה ויקב ראי – המקום שבו המטבח הבלקני נפגש עם המטבח המזרחי. אנו מגישים מנות אותנטיות, בשרים על האש, סלטים מסורתיים ויינות בוטיק מהיקב שלנו, באווירה חמה ומלאת אופי. מתאים למשפחה, זוגות, אירועים וחגיגות מיוחדות. מסעדה שמשלבת טעמים, תרבות ויין לחוויה בלתי נשכחת.', 'ברוכים הבאים למסעדה ויקב ראי – המקום שבו המטבח הבלקני נפגש עם המטבח המזרחי. אנו מגישים מנות אותנטיות, בשרים על האש, סלטים מסורתיים ויינות בוטיק מהיקב שלנו, באווירה חמה ומלאת אופי. מתאים למשפחה, זוגות, אירועים וחגיגות מיוחדות. מסעדה שמשלבת טעמים, תרבות ויין לחוויה בלתי נשכחת.', 'https://facebook.com', 'https://www.instagram.com/sumo.karmiel', 'None', '2025-12-04 11:13:30.918927', false, false, false, false, 50, 0.18, true, false, true, true, 'hero_desktop_20251121_213758_image00019.jpg', 'logo_nobg.png', NULL, '#ff8c00', '#dc3545', 20, 150, '45-60', 0, '₪', '', '', false, 'משלוח חינם מעל 150₪', 'Free delivery over ₪150', false, '#ffc107', true, 'גלריה', 'Gallery', NULL, NULL, 8, false, 'https://apps.apple.com/app/sumo-kitchen', 'https://play.google.com/store/apps/details?id=com.sumo.kitchen', 'הזמנות ומשלוחים זמינים דרך האפליקציה!', 'Orders & Delivery via App Only!', '', '', false, 'הזמנות ומשלוחים זמינים באפליקציה', 'Order via App', 'הורידו עכשיו', 'Download Now', true, 'קייטרינג ואירועים מיוחדים', 'Premium Catering Services', 'הביאו את הטעמים האסיאתיים האותנטיים לחגיגה הבאה שלכם. אנו מציעים תפריטי קייטרינג מותאמים אישית לחתונות, ימי הולדת ואירועי חברה.', 'Let us make your special event unforgettable with our authentic Asian cuisine', 'catering_20251121_213758_WhatsApp_Image_2021-12-01_at_10.38.19_1.jpg', true, 'קייטרינג ואירועים מיוחדים', 'Catering & Special Events', 'הפכו את האירוע שלכם לבלתי נשכח עם המטבח האותנטי שלנו', 'Make your event unforgettable with our authentic cuisine', 'מנות ורגעים בלתי נשכחים', 'Gallery', '', '', 'מוכנים להפוך את האירוע שלכם למיוחד?', 'Ready to Make Your Event Special?', 'צרו קשר עכשיו לייעוץ חינם ותפריט מותאם אישית', 'Contact us now for a free consultation and custom menu', 'הצטרפו לצוות שלנו', 'Join Our Team', 'בואו להיות חלק ממשפחת סומו - מקום שבו כישרון פוגש תשוקה', 'Be part of the SUMO family - where talent meets passion', 'משרות פתוחות', 'Open Positions', 'מצאו את המשרה המושלמת עבורכם', 'Find the perfect position for you', 'מעוניינים להצטרף?', 'Interested in Joining?', 'שלחו לנו את פרטיכם ונחזור אליכם בהקדם', 'Send us your details and we will get back to you soon', 'careers_bg.jpg', false, 'הצטרפו לצוות שלנו', 'Join Our Team', 'מחפשים אנשי מקצוע מוכשרים להצטרף למשפחת סומו. גלו הזדמנויות קריירה מרגשות במטבח האסייתי המוביל.', 'Looking for talented professionals to join the SUMO family. Discover exciting career opportunities at the leading Asian kitchen.', 'office@sumo-rest.co.il', 'office@sumo-rest.co.il', 'office@sumo-rest.co.il', false, 'מסעדת ויקב ראי - ראמה', 'Rai Winery and restaurant - Rama', 'מסעדת ראי , מטבח בלקני בניחוח גלילי - מנות מיוחדות,אירועים וקייטרינג  .', '', 'מסעדה בראמה , מסעדה בצפון, בולגריה, אוכל בולגרי , מסעדה בגליל , הזמנת שולחן,הזמנת מקום, אירועים', 'asian restaurant, karmiel, rama, bulgarian cuisine, asian food, reservations, events', 'ראי admin', 'מסעדת ויקב ראי', 'Rai Winery and Restaurant', 'חוויה קולינרית בולגרית אותנטית בראמה', 'Authentic Bulgarian culinary experience in Rama', NULL, 'מסעדת ויקב ראי ', '', 'ראמה', '', 'Bulgarian, Mediterranean', '$$', 'Su-Th 9:00-23:00, Fr-Sa 9:00-23:00', true, 24, true, true, true);


--
-- Data for Name: stock_alerts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_alerts VALUES (2, 7, 2, 'low_stock', 'מלאי נמוך: קפה (4 ק״ג נותרו)', 'Low stock: Coffee (4 kg remaining)', 'high', false, false, NULL, NULL, '2025-09-07 12:30:47.039462');
INSERT INTO public.stock_alerts VALUES (4, 7, 1, 'low_stock', 'מלאי נמוך מאוד: קפה (פחות מ-3 ק״ג)', 'Very low stock: Coffee (less than 3 kg)', 'high', false, false, NULL, NULL, '2025-09-07 13:45:47.039462');


--
-- Data for Name: stock_levels; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_levels VALUES (4, 4, 1, 65, 5, 60, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (5, 5, 1, 80, 0, 80, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (6, 6, 1, 15, 0, 15, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (7, 7, 1, 8, 1, 7, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (8, 8, 1, 35, 0, 35, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (9, 9, 1, 75, 5, 70, '2025-09-06 14:30:02.897158', '2025-09-07 14:30:02.897158');
INSERT INTO public.stock_levels VALUES (11, 1, 2, 18, 1, 17, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (14, 4, 2, 45, 3, 42, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (15, 5, 2, 55, 5, 50, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (16, 6, 2, 8, 0, 8, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (17, 7, 2, 4, 0, 4, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (18, 8, 2, 25, 0, 25, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (19, 9, 2, 45, 8, 37, '2025-09-05 14:30:21.020016', '2025-09-07 14:30:21.020016');
INSERT INTO public.stock_levels VALUES (21, 13, 1, 84, 0, 84, NULL, '2025-11-13 10:16:27.849061');
INSERT INTO public.stock_levels VALUES (22, 14, 1, 72, 0, 72, NULL, '2025-11-13 10:16:28.087127');
INSERT INTO public.stock_levels VALUES (1, 1, 1, 100, 10, 90, '2025-09-06 14:30:02.897158', '2025-11-13 11:57:01.384272');


--
-- Data for Name: stock_settings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_settings VALUES (1, 1, true, true, true, true, false, 7, 3, 'weekly', 'Sunday', NULL, NULL);
INSERT INTO public.stock_settings VALUES (2, 2, true, true, true, true, false, 5, 2, 'weekly', 'Monday', NULL, NULL);
INSERT INTO public.stock_settings VALUES (3, NULL, true, true, true, true, false, 3, 7, 'weekly', 'sunday', '2025-09-08 10:18:38.645049', '2025-09-08 10:18:38.645053');


--
-- Data for Name: stock_transactions; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.stock_transactions VALUES (1, 13, 1, 'delivery', 84, 8.5, 714, 'RECEIPT_10', 11, NULL, NULL, 1, 'קבלה סרוקה #10 - RECEIPT_10_2965d33a', '2025-11-13 00:00:00');
INSERT INTO public.stock_transactions VALUES (2, 14, 1, 'delivery', 72, 4, 288, 'RECEIPT_10', 11, NULL, NULL, 1, 'קבלה סרוקה #10 - RECEIPT_10_2965d33a', '2025-11-13 00:00:00');


--
-- Data for Name: system_config; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: task_templates; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: terms_of_use; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.terms_of_use VALUES (1, '<h3>תנאי שימוש - סומו אסיאן קיצ''ן</h3>

<p>ברוכים הבאים לאתר הבית של סומו אסיאן קיצ''ן. השימוש באתר זה כפוף לתנאים המפורטים להלן. אנא קרא תנאים אלה בעיון לפני השימוש באתר.</p>

<h4>1. קבלת התנאים</h4>
<p>השימוש באתר מהווה הסכמה מלאה לתנאי השימוש. אם אינך מסכים לתנאים אלה, אנא הימנע משימוש באתר.</p>

<h4>2. שינויים בתנאי השימוש</h4>
<p>אנו שומרים לעצמנו את הזכות לעדכן תנאים אלה מעת לעת. שינויים יכנסו לתוקף מיד עם פרסומם באתר.</p>

<h4>3. הזמנות והמשלוחים</h4>
<p>כל ההזמנות כפופות לאישור ולזמינות המלאי. אנו שומרים לעצמנו את הזכות לסרב להזמנה או לבטלה מכל סיבה שהיא.</p>
<ul>
    <li>זמני האספקה המוצעים הם הערכות בלבד ואינם מהווים התחייבות.</li>
    <li>אנו נעשה את מירב המאמצים לספק הזמנות במועד, אך איננו אחראים לעיכובים שאינם בשליטתנו.</li>
</ul>

<h4>4. תשלום</h4>
<p>התשלום יבוצע באמצעות אחת משיטות התשלום המאושרות באתר. המחירים באתר כוללים מע"מ אלא אם צוין אחרת.</p>

<h4>5. מדיניות ביטול וזיכוי</h4>
<p>ניתן לבטל הזמנה עד 15 דקות לאחר ביצועה. ביטול לאחר מכן כפוף לשיקול דעתנו.</p>

<h4>6. פרטיות</h4>
<p>אנו מתחייבים להגן על פרטיותך. המידע שתמסור ישמש רק לצורך עיבוד הזמנתך ולשיפור השירות שלנו.</p>

<h4>7. קניין רוחני</h4>
<p>כל התוכן באתר, לרבות טקסטים, תמונות, לוגו ועיצובים, הם רכושנו הבלעדי ומוגנים בזכויות יוצרים.</p>

<h4>8. הגבלת אחריות</h4>
<p>אנו לא נישא באחריות לנזקים ישירים או עקיפים הנובעים משימוש באתר או מהאמון במידע המופיע בו.</p>

<h4>9. שיפוט וסמכות שיפוט</h4>
<p>תנאים אלה כפופים לחוקי מדינת ישראל. סמכות השיפוט הבלעדית נתונה לבתי המשפט המוסמכים בישראל.</p>

<h4>10. יצירת קשר</h4>
<p>לשאלות או הבהרות לגבי תנאי שימוש אלה, אנא צור איתנו קשר דרך דף "צור קשר" באתר.</p>

<p><small>תאריך עדכון אחרון: אוקטובר 2025</small></p>', '<h3>Terms of Use - Sumo Asian Kitchen</h3>

<p>Welcome to the Sumo Asian Kitchen website. Use of this site is subject to the terms outlined below. Please read these terms carefully before using the site.</p>

<h4>1. Acceptance of Terms</h4>
<p>By using this website, you fully agree to these terms of use. If you do not agree to these terms, please refrain from using the site.</p>

<h4>2. Changes to Terms of Use</h4>
<p>We reserve the right to update these terms from time to time. Changes will take effect immediately upon posting on the site.</p>

<h4>3. Orders and Delivery</h4>
<p>All orders are subject to confirmation and stock availability. We reserve the right to refuse or cancel any order for any reason.</p>
<ul>
    <li>Delivery times provided are estimates only and do not constitute a commitment.</li>
    <li>We will make every effort to deliver orders on time, but we are not responsible for delays beyond our control.</li>
</ul>

<h4>4. Payment</h4>
<p>Payment will be made through one of the approved payment methods on the site. Prices on the site include VAT unless otherwise stated.</p>

<h4>5. Cancellation and Refund Policy</h4>
<p>Orders may be cancelled up to 15 minutes after placing them. Cancellations after this time are subject to our discretion.</p>

<h4>6. Privacy</h4>
<p>We are committed to protecting your privacy. The information you provide will only be used to process your order and improve our service.</p>

<h4>7. Intellectual Property</h4>
<p>All content on the site, including texts, images, logos, and designs, is our exclusive property and protected by copyright.</p>

<h4>8. Limitation of Liability</h4>
<p>We will not be liable for any direct or indirect damages arising from the use of the site or reliance on information appearing on it.</p>

<h4>9. Governing Law and Jurisdiction</h4>
<p>These terms are governed by the laws of the State of Israel. Exclusive jurisdiction is granted to the competent courts in Israel.</p>

<h4>10. Contact</h4>
<p>For questions or clarifications regarding these terms of use, please contact us through the "Contact" page on the site.</p>

<p><small>Last updated: October 2025</small></p>', NULL, NULL, NULL, NULL, NULL);


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.user_roles VALUES (1, 1);
INSERT INTO public.user_roles VALUES (3, 1);
INSERT INTO public.user_roles VALUES (3, 2);
INSERT INTO public.user_roles VALUES (3, 3);
INSERT INTO public.user_roles VALUES (3, 4);
INSERT INTO public.user_roles VALUES (3, 5);
INSERT INTO public.user_roles VALUES (3, 6);
INSERT INTO public.user_roles VALUES (3, 7);
INSERT INTO public.user_roles VALUES (4, 3);
INSERT INTO public.user_roles VALUES (6, 8);


--
-- Data for Name: working_hours; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.working_hours VALUES (1, 1, 0, 'ראשון', 'Sunday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (2, 1, 1, 'שני', 'Monday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (3, 1, 2, 'שלישי', 'Tuesday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (4, 1, 3, 'רביעי', 'Wednesday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (5, 1, 4, 'חמישי', 'Thursday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (6, 1, 5, 'שישי', 'Friday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (7, 1, 6, 'שבת', 'Saturday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (13, 2, 5, 'שישי', 'Friday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (14, 2, 6, 'שבת', 'Saturday', '12:00', '23:00', false);
INSERT INTO public.working_hours VALUES (8, 2, 0, 'ראשון', 'Sunday', '12:00', '22:30', false);
INSERT INTO public.working_hours VALUES (9, 2, 1, 'שני', 'Monday', '12:00', '22:30', false);
INSERT INTO public.working_hours VALUES (10, 2, 2, 'שלישי', 'Tuesday', '12:00', '22:30', false);
INSERT INTO public.working_hours VALUES (11, 2, 3, 'רביעי', 'Wednesday', '12:00', '22:30', false);
INSERT INTO public.working_hours VALUES (12, 2, 4, 'חמישי', 'Thursday', '12:00', '22:30', false);


--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.admin_users_id_seq', 6, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 3, true);


--
-- Name: branch_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.branch_config_id_seq', 1, false);


--
-- Name: branches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.branches_id_seq', 2, true);


--
-- Name: career_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.career_contacts_id_seq', 3, true);


--
-- Name: career_positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.career_positions_id_seq', 1, true);


--
-- Name: catering_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catering_contacts_id_seq', 1, true);


--
-- Name: catering_gallery_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catering_gallery_images_id_seq', 13, true);


--
-- Name: catering_highlights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catering_highlights_id_seq', 6, true);


--
-- Name: catering_packages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catering_packages_id_seq', 3, true);


--
-- Name: checklist_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.checklist_tasks_id_seq', 87, true);


--
-- Name: contact_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contact_messages_id_seq', 1, true);


--
-- Name: cost_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cost_categories_id_seq', 1, false);


--
-- Name: cost_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cost_entries_id_seq', 1, false);


--
-- Name: custom_field_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.custom_field_assignments_id_seq', 1, false);


--
-- Name: custom_field_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.custom_field_definitions_id_seq', 1, false);


--
-- Name: custom_sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.custom_sections_id_seq', 1, false);


--
-- Name: customer_addresses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_addresses_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customers_id_seq', 1, false);


--
-- Name: delivery_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.delivery_assignments_id_seq', 1, false);


--
-- Name: delivery_zones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.delivery_zones_id_seq', 1, false);


--
-- Name: dietary_properties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dietary_properties_id_seq', 3, true);


--
-- Name: driver_shifts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.driver_shifts_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.drivers_id_seq', 1, false);


--
-- Name: event_page_analytics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.event_page_analytics_id_seq', 4, true);


--
-- Name: file_imports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.file_imports_id_seq', 1, false);


--
-- Name: gallery_photos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.gallery_photos_id_seq', 17, true);


--
-- Name: generated_checklists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.generated_checklists_id_seq', 3, true);


--
-- Name: generated_menus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.generated_menus_id_seq', 40, true);


--
-- Name: kitchen_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.kitchen_queue_id_seq', 1, false);


--
-- Name: kitchen_stations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.kitchen_stations_id_seq', 1, false);


--
-- Name: live_event_reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.live_event_reservations_id_seq', 2, true);


--
-- Name: live_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.live_events_id_seq', 4, true);


--
-- Name: manager_pins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.manager_pins_id_seq', 1, true);


--
-- Name: media_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.media_files_id_seq', 1, false);


--
-- Name: menu_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_categories_id_seq', 25, true);


--
-- Name: menu_item_ingredients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_item_ingredients_id_seq', 1, false);


--
-- Name: menu_item_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_item_prices_id_seq', 1, false);


--
-- Name: menu_item_variations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_item_variations_id_seq', 1, false);


--
-- Name: menu_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_items_id_seq', 165, true);


--
-- Name: menu_print_configurations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_print_configurations_id_seq', 1, false);


--
-- Name: menu_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_settings_id_seq', 1, true);


--
-- Name: menu_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menu_templates_id_seq', 1, true);


--
-- Name: menus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.menus_id_seq', 1, true);


--
-- Name: newsletter_subscribers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.newsletter_subscribers_id_seq', 3, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: payment_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_configs_id_seq', 1, false);


--
-- Name: payment_configuration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_configuration_id_seq', 2, true);


--
-- Name: payment_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_transactions_id_seq', 1, false);


--
-- Name: pdf_menu_uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pdf_menu_uploads_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.permissions_id_seq', 42, true);


--
-- Name: phone_verifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.phone_verifications_id_seq', 1, false);


--
-- Name: print_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.print_templates_id_seq', 1, false);


--
-- Name: printer_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.printer_configs_id_seq', 1, false);


--
-- Name: privacy_policy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.privacy_policy_id_seq', 1, false);


--
-- Name: receipt_custom_field_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipt_custom_field_audit_id_seq', 1, false);


--
-- Name: receipt_custom_field_values_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipt_custom_field_values_id_seq', 1, false);


--
-- Name: receipt_import_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipt_import_items_id_seq', 54, true);


--
-- Name: receipt_imports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipt_imports_id_seq', 11, true);


--
-- Name: receipt_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipt_items_id_seq', 1, false);


--
-- Name: receipts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.receipts_id_seq', 15, true);


--
-- Name: reservation_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_alerts_id_seq', 1, false);


--
-- Name: reservation_blackouts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_blackouts_id_seq', 1, false);


--
-- Name: reservation_seating_areas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_seating_areas_id_seq', 6, true);


--
-- Name: reservation_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_settings_id_seq', 1, true);


--
-- Name: reservation_table_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_table_types_id_seq', 1, false);


--
-- Name: reservation_tables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservation_tables_id_seq', 1, false);


--
-- Name: reservations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reservations_id_seq', 43, true);


--
-- Name: restaurant_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.restaurant_events_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_id_seq', 8, true);


--
-- Name: shopping_list_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.shopping_list_items_id_seq', 2, true);


--
-- Name: shopping_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.shopping_lists_id_seq', 5, true);


--
-- Name: site_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.site_settings_id_seq', 1, true);


--
-- Name: stock_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_alerts_id_seq', 4, true);


--
-- Name: stock_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_categories_id_seq', 8, true);


--
-- Name: stock_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_items_id_seq', 14, true);


--
-- Name: stock_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_levels_id_seq', 23, true);


--
-- Name: stock_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_settings_id_seq', 3, true);


--
-- Name: stock_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_transactions_id_seq', 2, true);


--
-- Name: supplier_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.supplier_items_id_seq', 1, false);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 13, true);


--
-- Name: system_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.system_config_id_seq', 1, false);


--
-- Name: task_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_groups_id_seq', 8, true);


--
-- Name: task_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_templates_id_seq', 1, false);


--
-- Name: terms_of_use_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.terms_of_use_id_seq', 1, true);


--
-- Name: working_hours_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.working_hours_id_seq', 14, true);


--
-- PostgreSQL database dump complete
--

