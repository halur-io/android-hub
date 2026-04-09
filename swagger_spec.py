def get_apispec():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SUMO Restaurant API",
            "description": "API documentation for the SUMO restaurant system — covering public content, consumer ordering, kitchen display (KDS), operations/printing, and popup endpoints.",
            "version": "1.0.0",
        },
        "servers": [{"url": "/", "description": "Current server"}],
        "tags": [
            {"name": "Public", "description": "Public content endpoints (settings, branches, menu, gallery, dietary properties, featured items, checklists)"},
            {"name": "Ordering", "description": "Consumer ordering flow (OTP, onboarding, order status, streets proxy)"},
            {"name": "Kitchen Display", "description": "KDS / order dashboard endpoints (auth, orders feed, status updates, dish management, settings)"},
            {"name": "Operations", "description": "Operations & printing endpoints (unprinted orders, SSE stream, mark-printed, device management)"},
            {"name": "Popup", "description": "Popup microservice (active popups, impressions, clicks, form submissions)"},
        ],
        "paths": _build_paths(),
        "components": {"schemas": _build_schemas()},
    }


def _build_schemas():
    return {
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Failed to fetch settings"},
            },
        },
        "Success": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
            },
        },
        "SiteSettings": {
            "type": "object",
            "properties": {
                "site_name_he": {"type": "string", "example": "סומו"},
                "site_name_en": {"type": "string", "example": "SUMO"},
                "hero_title_he": {"type": "string"},
                "hero_title_en": {"type": "string"},
                "hero_subtitle_he": {"type": "string"},
                "hero_subtitle_en": {"type": "string"},
                "hero_description_he": {"type": "string"},
                "hero_description_en": {"type": "string"},
                "about_title_he": {"type": "string"},
                "about_title_en": {"type": "string"},
                "about_content_he": {"type": "string"},
                "about_content_en": {"type": "string"},
                "facebook_url": {"type": "string"},
                "instagram_url": {"type": "string"},
                "whatsapp_number": {"type": "string"},
            },
        },
        "WorkingHour": {
            "type": "object",
            "properties": {
                "day_of_week": {"type": "integer", "example": 0},
                "day_name_he": {"type": "string", "example": "ראשון"},
                "day_name_en": {"type": "string", "example": "Sunday"},
                "open_time": {"type": "string", "example": "10:00"},
                "close_time": {"type": "string", "example": "22:00"},
                "is_closed": {"type": "boolean", "example": False},
            },
        },
        "Branch": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name_he": {"type": "string", "example": "סומו ראשון"},
                "name_en": {"type": "string", "example": "SUMO Rishon"},
                "address_he": {"type": "string"},
                "address_en": {"type": "string"},
                "phone": {"type": "string", "example": "03-1234567"},
                "email": {"type": "string"},
                "waze_link": {"type": "string"},
                "google_maps_link": {"type": "string"},
                "working_hours": {"type": "array", "items": {"$ref": "#/components/schemas/WorkingHour"}},
            },
        },
        "DietaryProperty": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name_he": {"type": "string", "example": "טבעוני"},
                "name_en": {"type": "string", "example": "Vegan"},
                "icon": {"type": "string"},
                "color": {"type": "string"},
            },
        },
        "MenuItem": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name_he": {"type": "string", "example": "פאד תאי"},
                "name_en": {"type": "string", "example": "Pad Thai"},
                "description_he": {"type": "string"},
                "description_en": {"type": "string"},
                "base_price": {"type": "number", "example": 52.0},
                "effective_price": {"type": "number", "example": 52.0},
                "discount_percentage": {"type": "number", "nullable": True},
                "image_path": {"type": "string"},
                "is_vegetarian": {"type": "boolean"},
                "is_vegan": {"type": "boolean"},
                "is_gluten_free": {"type": "boolean"},
                "is_spicy": {"type": "boolean"},
                "is_signature": {"type": "boolean"},
                "is_new": {"type": "boolean"},
                "is_popular": {"type": "boolean"},
                "spice_level": {"type": "integer"},
                "dietary_properties": {"type": "array", "items": {"$ref": "#/components/schemas/DietaryProperty"}},
                "special_offer_text_he": {"type": "string", "nullable": True},
                "special_offer_text_en": {"type": "string", "nullable": True},
            },
        },
        "MenuCategory": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name_he": {"type": "string", "example": "מנות עיקריות"},
                "name_en": {"type": "string", "example": "Main Courses"},
                "description_he": {"type": "string"},
                "description_en": {"type": "string"},
                "icon": {"type": "string"},
                "color": {"type": "string"},
                "items": {"type": "array", "items": {"$ref": "#/components/schemas/MenuItem"}},
            },
        },
        "GalleryItem": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "file_path": {"type": "string"},
                "caption_he": {"type": "string"},
                "caption_en": {"type": "string"},
            },
        },
        "FeaturedItem": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name_he": {"type": "string"},
                "name_en": {"type": "string"},
                "description_he": {"type": "string"},
                "description_en": {"type": "string"},
                "price": {"type": "number"},
                "image_path": {"type": "string"},
                "is_signature": {"type": "boolean"},
                "is_new": {"type": "boolean"},
                "is_popular": {"type": "boolean"},
            },
        },
        "ChecklistTask": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "shift_type": {"type": "string", "enum": ["morning", "evening", "closing", "night"]},
                "category": {"type": "string", "enum": ["kitchen", "cleaning", "service", "inventory", "safety"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                "display_order": {"type": "integer"},
                "group_id": {"type": "integer", "nullable": True},
            },
        },
        "TaskTemplate": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "shift_type": {"type": "string"},
                "branch_id": {"type": "integer"},
                "is_default": {"type": "boolean"},
                "tasks_config": {"type": "array", "items": {"type": "object"}},
                "assigned_groups": {"type": "array", "items": {"type": "integer"}},
                "created_at": {"type": "string", "format": "date-time"},
            },
        },
        "GeneratedChecklist": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "date": {"type": "string", "format": "date"},
                "shift_type": {"type": "string"},
                "branch_id": {"type": "integer"},
                "branch_name": {"type": "string", "nullable": True},
                "manager_name": {"type": "string"},
                "tasks_data": {"type": "array", "items": {"type": "object"}},
                "created_at": {"type": "string", "format": "date-time"},
                "completed_at": {"type": "string", "format": "date-time", "nullable": True},
            },
        },
        "TaskGroup": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "shift_type": {"type": "string"},
                "category": {"type": "string"},
                "color": {"type": "string", "example": "#007bff"},
                "task_count": {"type": "integer"},
                "tasks": {"type": "array", "items": {"$ref": "#/components/schemas/ChecklistTask"}},
                "created_at": {"type": "string", "format": "date-time"},
            },
        },
        "OtpRequest": {
            "type": "object",
            "required": ["phone"],
            "properties": {
                "phone": {"type": "string", "example": "0501234567"},
            },
        },
        "OtpVerify": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {"type": "string", "example": "1234"},
            },
        },
        "OnboardingRequest": {
            "type": "object",
            "required": ["first_name", "last_name", "phone", "email"],
            "properties": {
                "branch_id": {"type": "integer"},
                "order_type": {"type": "string", "enum": ["delivery", "pickup"], "default": "delivery"},
                "first_name": {"type": "string", "example": "ישראל"},
                "last_name": {"type": "string", "example": "ישראלי"},
                "phone": {"type": "string", "example": "0501234567"},
                "email": {"type": "string", "example": "user@example.com"},
            },
        },
        "OrderStatusResponse": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "preparing"},
                "status_he": {"type": "string", "example": "בהכנה"},
                "badge_class": {"type": "string", "example": "primary"},
                "confirmed_at": {"type": "string", "nullable": True},
                "preparing_at": {"type": "string", "nullable": True},
                "ready_at": {"type": "string", "nullable": True},
                "estimated_ready_at": {"type": "string", "nullable": True},
                "ready_by_time": {"type": "string", "nullable": True},
            },
        },
        "StreetsResponse": {
            "type": "object",
            "properties": {
                "streets": {"type": "array", "items": {"type": "string"}},
                "city": {"type": "string"},
                "count": {"type": "integer"},
            },
        },
        "KdsAuthRequest": {
            "type": "object",
            "properties": {
                "pin_id": {"type": "string", "example": "1"},
                "pin": {"type": "string", "example": "1234"},
            },
        },
        "KdsAuthResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "redirect": {"type": "string", "example": "/order-dashboard/orders"},
                "message": {"type": "string"},
            },
        },
        "OrderFeedItem": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "order_number": {"type": "string", "example": "ORD-260314-1234"},
                "customer_name": {"type": "string"},
                "customer_phone": {"type": "string"},
                "order_type": {"type": "string", "enum": ["delivery", "pickup"]},
                "status": {"type": "string", "enum": ["pending", "confirmed", "preparing", "ready", "delivered", "pickedup", "cancelled"]},
                "status_label": {"type": "string"},
                "total_amount": {"type": "number"},
                "pickup_time": {"type": "string"},
                "created_at": {"type": "string"},
            },
        },
        "StatusUpdateRequest": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"type": "string", "enum": ["pending", "confirmed", "preparing", "ready", "delivered", "pickedup", "cancelled"]},
                "prep_minutes": {"type": "integer", "example": 20},
                "admin_note": {"type": "string"},
            },
        },
        "StatusUpdateResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "new_status": {"type": "string"},
                "status_label": {"type": "string"},
            },
        },
        "UnprintedOrderItem": {
            "type": "object",
            "properties": {
                "menu_item_id": {"type": "integer"},
                "name_he": {"type": "string"},
                "print_name": {"type": "string"},
                "qty": {"type": "integer"},
                "price": {"type": "number"},
                "options": {"type": "array", "items": {"type": "object", "properties": {"choice_name_he": {"type": "string"}}}},
                "excluded_ingredients": {"type": "array", "items": {"type": "string"}},
            },
        },
        "UnprintedOrder": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "order_number": {"type": "string", "example": "ORD-260407-1234"},
                "order_type": {"type": "string"},
                "status": {"type": "string"},
                "branch_id": {"type": "integer"},
                "customer_name": {"type": "string"},
                "customer_phone": {"type": "string"},
                "delivery_address": {"type": "string"},
                "delivery_city": {"type": "string"},
                "delivery_notes": {"type": "string"},
                "customer_notes": {"type": "string"},
                "subtotal": {"type": "number"},
                "delivery_fee": {"type": "number"},
                "discount_amount": {"type": "number"},
                "total_amount": {"type": "number"},
                "payment_method": {"type": "string"},
                "coupon_code": {"type": "string"},
                "created_at": {"type": "string"},
                "items": {"type": "array", "items": {"$ref": "#/components/schemas/UnprintedOrderItem"}},
                "items_by_station": {"type": "object", "additionalProperties": {"type": "array", "items": {"$ref": "#/components/schemas/UnprintedOrderItem"}}},
            },
        },
        "DeviceRegisterRequest": {
            "type": "object",
            "required": ["device_id", "branch_id", "device_name"],
            "properties": {
                "device_id": {"type": "string", "example": "android-a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
                "branch_id": {"type": "integer", "example": 1},
                "device_name": {"type": "string", "example": "Tablet Cashier 1"},
            },
        },
        "PrintDevice": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "device_id": {"type": "string"},
                "branch_id": {"type": "integer"},
                "device_name": {"type": "string"},
                "last_heartbeat": {"type": "string", "format": "date-time"},
                "is_online": {"type": "boolean"},
                "registered_at": {"type": "string", "format": "date-time"},
                "config": {"type": "object"},
            },
        },
        "DeviceConfig": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string"},
                "device_db_id": {"type": "integer"},
                "branch_id": {"type": "integer"},
                "branch_name": {"type": "string"},
                "poll_interval_seconds": {"type": "integer", "example": 5},
                "sse_reconnect_delay_ms": {"type": "integer", "example": 3000},
                "heartbeat_interval_seconds": {"type": "integer", "example": 30},
                "sound_enabled": {"type": "boolean"},
                "sound_file": {"type": "string"},
                "notification_enabled": {"type": "boolean"},
                "encoding": {"type": "string", "example": "iso-8859-8"},
                "codepage_num": {"type": "integer", "example": 32},
                "default_printer": {"type": "object"},
                "station_map": {"type": "object"},
                "printers": {"type": "array", "items": {"type": "object"}},
            },
        },
        "PrinterInfo": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "ip_address": {"type": "string", "example": "192.168.1.100"},
                "port": {"type": "integer", "example": 9100},
                "encoding": {"type": "string"},
                "codepage_num": {"type": "integer"},
                "cut_feed_lines": {"type": "integer"},
                "checker_copies": {"type": "integer"},
                "payment_copies": {"type": "integer"},
                "is_default": {"type": "boolean"},
                "stations": {"type": "array", "items": {"type": "string"}},
            },
        },
        "PopupConfig": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "title_he": {"type": "string"},
                "title_en": {"type": "string"},
                "content_he": {"type": "string"},
                "content_en": {"type": "string"},
                "popup_type": {"type": "string"},
                "is_active": {"type": "boolean"},
                "priority": {"type": "integer"},
            },
        },
        "PopupFormSubmission": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "source_page": {"type": "string"},
                "newsletter_consent": {"type": "boolean"},
                "terms_consent": {"type": "boolean"},
                "marketing_consent": {"type": "boolean"},
                "language": {"type": "string", "enum": ["he", "en"]},
                "screen_width": {"type": "integer"},
                "utm_source": {"type": "string"},
                "utm_medium": {"type": "string"},
                "utm_campaign": {"type": "string"},
            },
        },
        "SseEvent": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["connected", "new_order", "order_status_changed"]},
                "id": {"type": "integer"},
                "order_number": {"type": "string"},
                "order_type": {"type": "string"},
                "branch_id": {"type": "integer"},
                "customer_name": {"type": "string"},
                "total_amount": {"type": "number"},
            },
        },
    }


def _build_paths():
    paths = {}

    # ── Public endpoints (/api/*) ────────────────────────────────────
    paths["/api/settings"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get site settings",
            "description": "Returns site-wide settings including names, hero content, about section, and social links.",
            "responses": {
                "200": {"description": "Site settings", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SiteSettings"}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    paths["/api/branches"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all active branches",
            "description": "Returns all active branches with their working hours, ordered by display_order.",
            "responses": {
                "200": {"description": "List of branches", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Branch"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    paths["/api/menu"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get complete menu",
            "description": "Returns all active menu categories with their available items, including pricing, dietary properties, and special offers.",
            "responses": {
                "200": {"description": "Menu categories with items", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/MenuCategory"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    paths["/api/gallery"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get gallery images",
            "description": "Returns gallery images filtered by section, ordered by display_order.",
            "parameters": [
                {"name": "section", "in": "query", "schema": {"type": "string", "default": "gallery"}, "description": "Section name to filter images (e.g. gallery, hero, about)"},
            ],
            "responses": {
                "200": {"description": "Gallery images", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/GalleryItem"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    paths["/api/dietary-properties"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all dietary properties",
            "description": "Returns all active dietary properties (vegan, gluten-free, etc.) with icons and colors.",
            "responses": {
                "200": {"description": "Dietary properties", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/DietaryProperty"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    paths["/api/featured"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get featured menu items",
            "description": "Returns up to 6 featured items that are signature, popular, or new.",
            "responses": {
                "200": {"description": "Featured items", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/FeaturedItem"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        }
    }

    # Checklist Tasks
    paths["/api/checklist-tasks"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all active checklist tasks",
            "responses": {
                "200": {"description": "List of tasks", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/ChecklistTask"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
        "post": {
            "tags": ["Public"],
            "summary": "Create a new checklist task",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "shift_type": {"type": "string"},
                        "category": {"type": "string"},
                        "priority": {"type": "string", "default": "medium"},
                        "frequency": {"type": "string", "default": "daily"},
                        "group_id": {"type": "integer", "nullable": True},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Task created", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "id": {"type": "integer"}}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
    }

    paths["/api/checklist-tasks/{task_id}"] = {
        "put": {
            "tags": ["Public"],
            "summary": "Update a checklist task",
            "parameters": [{"name": "task_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "shift_type": {"type": "string"},
                        "category": {"type": "string"},
                        "priority": {"type": "string"},
                        "frequency": {"type": "string"},
                        "group_id": {"type": "integer", "nullable": True},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Task updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
        "delete": {
            "tags": ["Public"],
            "summary": "Soft-delete a checklist task",
            "parameters": [{"name": "task_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Task deleted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
    }

    # Task Templates
    paths["/api/task-templates"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all task templates",
            "responses": {
                "200": {"description": "List of templates", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/TaskTemplate"}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
        "post": {
            "tags": ["Public"],
            "summary": "Create a new task template from current tasks",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "required": ["name", "shift_type"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "shift_type": {"type": "string"},
                        "branch_id": {"type": "integer"},
                        "is_default": {"type": "boolean", "default": False},
                        "assigned_groups": {"type": "array", "items": {"type": "integer"}},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Template created", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "id": {"type": "integer"}}}}}},
                "500": {"description": "Server error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
            },
        },
    }

    paths["/api/task-templates/{template_id}/load"] = {
        "post": {
            "tags": ["Public"],
            "summary": "Load tasks from a template",
            "description": "Creates new tasks from a template's configuration. Optionally replaces existing tasks for the same shift type.",
            "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "replace_existing": {"type": "boolean", "default": False, "description": "If true, deactivates existing tasks for this shift type before creating new ones"},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Tasks created", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "created_count": {"type": "integer"}, "template_name": {"type": "string"}}}}}},
                "400": {"description": "Template has no tasks"},
                "500": {"description": "Server error"},
            },
        }
    }

    paths["/api/task-templates/{template_id}"] = {
        "delete": {
            "tags": ["Public"],
            "summary": "Delete a task template",
            "parameters": [{"name": "template_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Template deleted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error"},
            },
        }
    }

    # Generated Checklists
    paths["/api/generated-checklists"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all generated checklists",
            "responses": {
                "200": {"description": "List of checklists", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/GeneratedChecklist"}}}}},
                "500": {"description": "Server error"},
            },
        },
        "post": {
            "tags": ["Public"],
            "summary": "Create a generated checklist",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "required": ["name", "date", "shift_type"],
                    "properties": {
                        "name": {"type": "string"},
                        "date": {"type": "string", "format": "date", "example": "2026-04-09"},
                        "shift_type": {"type": "string"},
                        "branch_id": {"type": "integer"},
                        "manager_name": {"type": "string"},
                        "tasks_data": {"type": "array", "items": {"type": "object"}},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Checklist created", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "id": {"type": "integer"}, "message": {"type": "string"}}}}}},
                "500": {"description": "Server error"},
            },
        },
    }

    paths["/api/generated-checklists/{checklist_id}"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get a specific generated checklist",
            "parameters": [{"name": "checklist_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Checklist details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/GeneratedChecklist"}}}},
                "404": {"description": "Checklist not found"},
                "500": {"description": "Server error"},
            },
        },
        "delete": {
            "tags": ["Public"],
            "summary": "Delete a generated checklist",
            "parameters": [{"name": "checklist_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Checklist deleted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error"},
            },
        },
    }

    # Task Groups
    paths["/api/task-groups"] = {
        "get": {
            "tags": ["Public"],
            "summary": "Get all task groups with tasks",
            "responses": {
                "200": {"description": "List of groups", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/TaskGroup"}}}}},
                "500": {"description": "Server error"},
            },
        },
        "post": {
            "tags": ["Public"],
            "summary": "Create a task group",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "required": ["name", "shift_type", "category"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "shift_type": {"type": "string"},
                        "category": {"type": "string"},
                        "color": {"type": "string", "default": "#007bff"},
                        "tasks": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}, "frequency": {"type": "string"}}}},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Group created", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "group_id": {"type": "integer"}, "tasks_created": {"type": "integer"}}}}}},
                "500": {"description": "Server error"},
            },
        },
    }

    paths["/api/task-groups/{group_id}"] = {
        "put": {
            "tags": ["Public"],
            "summary": "Update a task group",
            "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "color": {"type": "string"},
                        "category": {"type": "string"},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Group updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error"},
            },
        },
        "delete": {
            "tags": ["Public"],
            "summary": "Delete a task group",
            "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "delete_tasks": {"type": "boolean", "default": False, "description": "If true, soft-deletes tasks in the group; otherwise removes group assignment"},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Group deleted", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "500": {"description": "Server error"},
            },
        },
    }

    # ── Ordering endpoints (/order/*) ────────────────────────────────
    paths["/order/send-otp"] = {
        "post": {
            "tags": ["Ordering"],
            "summary": "Send OTP verification code",
            "description": "Sends a 4-digit OTP code via SMS to the provided phone number for customer verification.",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OtpRequest"}}},
            },
            "responses": {
                "200": {"description": "OTP sent", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
                "400": {"description": "Invalid phone number"},
            },
        }
    }

    paths["/order/verify-otp"] = {
        "post": {
            "tags": ["Ordering"],
            "summary": "Verify OTP code",
            "description": "Verifies the OTP code entered by the customer. Maximum 5 attempts; code expires after 5 minutes.",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OtpVerify"}}},
            },
            "responses": {
                "200": {"description": "OTP verified", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
                "400": {"description": "Invalid or expired code"},
                "429": {"description": "Too many attempts"},
            },
        }
    }

    paths["/order/complete-onboarding"] = {
        "post": {
            "tags": ["Ordering"],
            "summary": "Complete customer onboarding",
            "description": "Saves customer details after OTP verification. Requires a verified OTP session.",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OnboardingRequest"}}},
            },
            "responses": {
                "200": {"description": "Onboarding complete", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
                "400": {"description": "Missing required fields or OTP not verified"},
            },
        }
    }

    paths["/order/status/{order_number}"] = {
        "get": {
            "tags": ["Ordering"],
            "summary": "Get order status (JSON)",
            "description": "Returns the current status of an order for live polling from the confirmation page.",
            "parameters": [{"name": "order_number", "in": "path", "required": True, "schema": {"type": "string"}, "example": "ORD-260314-1234"}],
            "responses": {
                "200": {"description": "Order status", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OrderStatusResponse"}}}},
                "404": {"description": "Order not found"},
            },
        }
    }

    paths["/order/api/streets"] = {
        "get": {
            "tags": ["Ordering"],
            "summary": "Israeli streets autocomplete",
            "description": "Proxies the data.gov.il streets API. Returns street names for a given Hebrew city name.",
            "parameters": [
                {"name": "city", "in": "query", "required": True, "schema": {"type": "string"}, "description": "Hebrew city name (min 2 chars)", "example": "תל אביב"},
            ],
            "responses": {
                "200": {"description": "Street names", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/StreetsResponse"}}}},
            },
        }
    }

    # ── KDS endpoints (/order-dashboard/*) ───────────────────────────
    paths["/order-dashboard/auth"] = {
        "post": {
            "tags": ["Kitchen Display"],
            "summary": "Authenticate KDS staff",
            "description": "Verifies PIN against ManagerPIN model. On success, sets session and returns redirect URL.",
            "requestBody": {
                "required": True,
                "content": {"application/x-www-form-urlencoded": {"schema": {"$ref": "#/components/schemas/KdsAuthRequest"}}},
            },
            "responses": {
                "200": {"description": "Auth result", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/KdsAuthResponse"}}}},
            },
        }
    }

    paths["/order-dashboard/orders/feed"] = {
        "get": {
            "tags": ["Kitchen Display"],
            "summary": "Live orders feed (JSON)",
            "description": "Returns today's orders for auto-refresh (30-second polling). Requires KDS authentication.",
            "parameters": [
                {"name": "branch_id", "in": "query", "schema": {"type": "integer"}, "description": "Filter by branch ID"},
            ],
            "responses": {
                "200": {"description": "Orders feed", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/OrderFeedItem"}}}}},
                "302": {"description": "Redirect to login if not authenticated"},
            },
        }
    }

    paths["/order-dashboard/orders/{order_id}/update-status"] = {
        "post": {
            "tags": ["Kitchen Display"],
            "summary": "Update order status",
            "description": "Changes order status with optional prep time estimate and admin note. Requires KDS authentication.",
            "parameters": [{"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "required": True,
                "content": {
                    "application/x-www-form-urlencoded": {"schema": {"$ref": "#/components/schemas/StatusUpdateRequest"}},
                    "application/json": {"schema": {"$ref": "#/components/schemas/StatusUpdateRequest"}},
                },
            },
            "responses": {
                "200": {"description": "Status updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/StatusUpdateResponse"}}}},
                "403": {"description": "Order not in staff's branch"},
            },
        }
    }

    paths["/order-dashboard/dishes/toggle-availability"] = {
        "post": {
            "tags": ["Kitchen Display"],
            "summary": "Toggle dish availability",
            "description": "Toggles the availability of a menu item. Requires KDS authentication.",
            "requestBody": {
                "required": True,
                "content": {"application/x-www-form-urlencoded": {"schema": {"type": "object", "properties": {"item_id": {"type": "integer"}}}}},
            },
            "responses": {
                "200": {"description": "Availability toggled", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "is_available": {"type": "boolean"}}}}}},
            },
        }
    }

    paths["/order-dashboard/settings"] = {
        "get": {
            "tags": ["Kitchen Display"],
            "summary": "Get KDS settings page data",
            "description": "Returns settings for ordering toggles, working hours, and dish management. Requires KDS authentication.",
            "responses": {
                "200": {"description": "Settings page"},
                "302": {"description": "Redirect to login"},
            },
        },
        "post": {
            "tags": ["Kitchen Display"],
            "summary": "Update KDS settings",
            "description": "Handles multiple actions: toggle_pause, toggle_ordering, toggle_delivery, toggle_pickup, toggle_enforce_hours, save_messages, update_delivery_time, save_working_hours, toggle_tracking.",
            "requestBody": {
                "required": True,
                "content": {"application/x-www-form-urlencoded": {"schema": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {
                        "action": {"type": "string", "enum": ["toggle_pause", "toggle_ordering", "toggle_delivery", "toggle_pickup", "toggle_enforce_hours", "save_messages", "update_delivery_time", "save_working_hours", "toggle_tracking"]},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Setting updated", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}}}}}},
            },
        },
    }

    paths["/order-dashboard/switch-branch"] = {
        "post": {
            "tags": ["Kitchen Display"],
            "summary": "Switch active branch (superadmin)",
            "description": "Allows superadmin to switch the active branch in the KDS dashboard.",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"type": "object", "properties": {"branch_id": {"type": "integer"}}}}},
            },
            "responses": {
                "200": {"description": "Branch switched", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
            },
        }
    }

    # ── Operations / Printing endpoints (/ops/api/*) ──────────────────
    _ops_print_key = {"name": "X-Print-Key", "in": "header", "required": True, "schema": {"type": "string"}, "description": "API key for print agent authentication (PRINT_AGENT_KEY env var)"}

    paths["/ops/api/orders/unprinted"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "Get unprinted orders",
            "description": "Returns all orders that have not been printed yet. Used by the Android print hub for polling.",
            "parameters": [
                _ops_print_key,
                {"name": "branch_id", "in": "query", "schema": {"type": "integer"}, "description": "Filter by branch"},
            ],
            "responses": {
                "200": {"description": "Unprinted orders", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "orders": {"type": "array", "items": {"$ref": "#/components/schemas/UnprintedOrder"}}}}}}},
                "401": {"description": "Unauthorized — invalid or missing API key"},
            },
        }
    }

    paths["/ops/api/orders/stream"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "SSE order stream",
            "description": "Server-Sent Events stream for real-time order notifications. Emits new_order and order_status_changed events. Sends keepalive every ~25 seconds.",
            "parameters": [
                {"name": "key", "in": "query", "required": True, "schema": {"type": "string"}, "description": "API key (since SSE doesn't easily support custom headers)"},
                {"name": "branch_id", "in": "query", "schema": {"type": "integer"}, "description": "Filter events by branch"},
            ],
            "responses": {
                "200": {"description": "SSE event stream", "content": {"text/event-stream": {"schema": {"$ref": "#/components/schemas/SseEvent"}}}},
                "401": {"description": "Unauthorized — invalid or missing API key"},
            },
        }
    }

    paths["/ops/api/orders/mark-printed"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Mark orders as printed",
            "description": "Marks one or more orders as printed after the print agent successfully prints them.",
            "parameters": [_ops_print_key],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"type": "object", "required": ["order_ids"], "properties": {"order_ids": {"type": "array", "items": {"type": "integer"}, "example": [42, 43]}}}}},
            },
            "responses": {
                "200": {"description": "Orders marked", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "message": {"type": "string"}}}}}},
                "401": {"description": "Unauthorized — invalid or missing API key"},
            },
        }
    }

    paths["/ops/api/orders/{order_id}/ack"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Acknowledge order receipt",
            "description": "Acknowledges that the print device has received the order (before printing). Records ack timestamp and device ID.",
            "parameters": [
                _ops_print_key,
                {"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "requestBody": {
                "content": {"application/json": {"schema": {"type": "object", "properties": {"device_id": {"type": "string"}}}}},
            },
            "responses": {
                "200": {"description": "Order acknowledged", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "message": {"type": "string"}}}}}},
            },
        }
    }

    paths["/ops/api/orders/{order_id}/print-status"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Report print result",
            "description": "Reports the print outcome for an order — success, partial, or failure. Primary mechanism for the server to know the print result.",
            "parameters": [
                _ops_print_key,
                {"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "required": ["status"],
                    "properties": {
                        "status": {"type": "string", "enum": ["success", "partial", "failed"]},
                        "device_id": {"type": "string"},
                        "printers_ok": {"type": "array", "items": {"type": "string"}},
                        "printers_failed": {"type": "array", "items": {"type": "string"}},
                        "error": {"type": "string"},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Status recorded", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
            },
        }
    }

    paths["/ops/api/orders/{order_id}/detail"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "Get full order detail (JSON)",
            "description": "Returns complete order information including items, options, station breakdown, and customer details.",
            "parameters": [
                _ops_print_key,
                {"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Order detail", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UnprintedOrder"}}}},
                "404": {"description": "Order not found"},
            },
        }
    }

    paths["/ops/api/devices/register"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Register a print device",
            "description": "Registers a new Android tablet print device or updates an existing registration.",
            "parameters": [_ops_print_key],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/DeviceRegisterRequest"}}},
            },
            "responses": {
                "200": {"description": "Device registered", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "device": {"$ref": "#/components/schemas/PrintDevice"}}}}}},
            },
        }
    }

    paths["/ops/api/devices/heartbeat"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Send device heartbeat",
            "description": "Periodic heartbeat to keep a device marked as online. If no heartbeat is received for 2 minutes, the device is marked offline.",
            "parameters": [_ops_print_key],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"type": "object", "required": ["device_id"], "properties": {"device_id": {"type": "string"}}}}},
            },
            "responses": {
                "200": {"description": "Heartbeat received", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "server_time": {"type": "string", "format": "date-time"}}}}}},
            },
        }
    }

    paths["/ops/api/devices"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "List all print devices",
            "description": "Returns all registered print devices with their status. Accepts API key or ops session auth.",
            "parameters": [_ops_print_key],
            "responses": {
                "200": {"description": "Devices list", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "devices": {"type": "array", "items": {"$ref": "#/components/schemas/PrintDevice"}}}}}}},
            },
        }
    }

    paths["/ops/api/devices/{device_db_id}/config"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "Get device configuration",
            "description": "Returns the full configuration for a print device including printer mappings, polling intervals, and station assignments.",
            "parameters": [
                _ops_print_key,
                {"name": "device_db_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Device config", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "config": {"$ref": "#/components/schemas/DeviceConfig"}}}}}},
                "404": {"description": "Device not found"},
            },
        },
        "put": {
            "tags": ["Operations"],
            "summary": "Update device configuration",
            "description": "Remotely update a device's configuration (admin operation). Accepts API key or ops session auth.",
            "parameters": [
                _ops_print_key,
                {"name": "device_db_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "device_name": {"type": "string"},
                        "branch_id": {"type": "integer"},
                        "config": {"type": "object", "properties": {
                            "poll_interval_seconds": {"type": "integer"},
                            "sound_enabled": {"type": "boolean"},
                            "notification_enabled": {"type": "boolean"},
                            "sse_reconnect_delay_ms": {"type": "integer"},
                        }},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Config updated", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "device": {"$ref": "#/components/schemas/PrintDevice"}}}}}},
            },
        },
    }

    paths["/ops/api/devices/{device_db_id}"] = {
        "delete": {
            "tags": ["Operations"],
            "summary": "Delete a print device",
            "parameters": [
                _ops_print_key,
                {"name": "device_db_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Device deleted", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
            },
        }
    }

    paths["/ops/api/branch/{branch_id}/printers"] = {
        "get": {
            "tags": ["Operations"],
            "summary": "Get branch printer configuration",
            "description": "Returns all printers configured for a branch, including station-to-printer mapping and default printer.",
            "parameters": [
                _ops_print_key,
                {"name": "branch_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Branch printers", "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "branch_id": {"type": "integer"},
                        "branch_name": {"type": "string"},
                        "default_printer": {"$ref": "#/components/schemas/PrinterInfo"},
                        "station_map": {"type": "object", "additionalProperties": {"$ref": "#/components/schemas/PrinterInfo"}},
                        "printers": {"type": "array", "items": {"$ref": "#/components/schemas/PrinterInfo"}},
                    },
                }}}},
            },
        }
    }

    paths["/ops/api/device/log-error"] = {
        "post": {
            "tags": ["Operations"],
            "summary": "Log a device error",
            "description": "Allows the Android app to send error logs to the server for remote diagnostics.",
            "parameters": [_ops_print_key],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "error_type": {"type": "string"},
                        "error_message": {"type": "string"},
                        "stack_trace": {"type": "string"},
                    },
                }}},
            },
            "responses": {
                "200": {"description": "Error logged", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
            },
        }
    }

    # ── Popup endpoints (/api/popups/*) ──────────────────────────────
    paths["/api/popups/active"] = {
        "get": {
            "tags": ["Popup"],
            "summary": "Get active popups",
            "description": "Returns all currently active popups configured for frontend display, ordered by priority.",
            "responses": {
                "200": {"description": "Active popups", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/PopupConfig"}}}}},
            },
        }
    }

    paths["/api/popup/{popup_id}/impression"] = {
        "post": {
            "tags": ["Popup"],
            "summary": "Track popup impression",
            "description": "Records that a popup was shown to a user. Rate-limited per session.",
            "parameters": [{"name": "popup_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Impression tracked", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "403": {"description": "Invalid request origin"},
            },
        }
    }

    paths["/api/popup/{popup_id}/click"] = {
        "post": {
            "tags": ["Popup"],
            "summary": "Track popup CTA click",
            "description": "Records that a user clicked the popup's call-to-action button. Rate-limited per session.",
            "parameters": [{"name": "popup_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Click tracked", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "403": {"description": "Invalid request origin"},
            },
        }
    }

    paths["/api/popup/{popup_id}/close"] = {
        "post": {
            "tags": ["Popup"],
            "summary": "Track popup close",
            "description": "Records that a user closed the popup. Rate-limited per session.",
            "parameters": [{"name": "popup_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Close tracked", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Success"}}}},
                "403": {"description": "Invalid request origin"},
            },
        }
    }

    paths["/api/popup/{popup_id}/submit"] = {
        "post": {
            "tags": ["Popup"],
            "summary": "Submit popup form (lead capture)",
            "description": "Handles popup form submission — collects lead information (name, email, phone), records consent choices (newsletter, terms, marketing), and stores UTM attribution data.",
            "parameters": [{"name": "popup_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PopupFormSubmission"}}},
            },
            "responses": {
                "200": {"description": "Form submitted", "content": {"application/json": {"schema": {"type": "object", "properties": {"success": {"type": "boolean"}, "message": {"type": "string"}}}}}},
                "400": {"description": "Missing required field"},
                "403": {"description": "Invalid request origin"},
                "404": {"description": "Popup not found or form not enabled"},
                "500": {"description": "Server error"},
            },
        }
    }

    return paths
