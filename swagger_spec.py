def get_apispec():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "SUMO Print Hub API",
            "description": "API documentation for the SUMO Android Print Hub app — device registration, order polling, SSE streaming, print status reporting, and printer configuration.\n\nAuthentication: pass your API key in the `X-Print-Key` header (or as `?key=` query param for SSE). Keys are created in the admin panel under API Keys.",
            "version": "1.0.0",
        },
        "servers": [{"url": "/", "description": "Current server"}],
        "tags": [
            {"name": "Orders", "description": "Order fetching, streaming, acknowledgment, and print status"},
            {"name": "Devices", "description": "Device registration, heartbeat, configuration, and management"},
            {"name": "Printers", "description": "Branch printer configuration and station mapping"},
            {"name": "Diagnostics", "description": "Error logging and remote diagnostics"},
        ],
        "components": {
            "securitySchemes": {
                "PrintApiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Print-Key",
                    "description": "API key for print agent authentication (PRINT_AGENT_KEY env var)",
                },
            },
            "schemas": _build_schemas(),
        },
        "security": [{"PrintApiKey": []}],
        "paths": _build_paths(),
    }


def _build_schemas():
    return {
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
                "order_type": {"type": "string", "enum": ["delivery", "pickup"]},
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
                "printers": {"type": "array", "items": {"$ref": "#/components/schemas/PrinterInfo"}},
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

    # ── Orders ──────────────────────────────────────────────────────────

    paths["/ops/api/orders/unprinted"] = {
        "get": {
            "tags": ["Orders"],
            "summary": "Get unprinted orders",
            "description": "Returns all orders that have not been printed yet. Used by the Android print hub for polling.",
            "parameters": [
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
            "tags": ["Orders"],
            "summary": "SSE order stream",
            "description": "Server-Sent Events stream for real-time order notifications. Emits `new_order` and `order_status_changed` events. Sends keepalive every ~25 seconds. Use query param `key` for auth since SSE doesn't support custom headers.",
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
            "tags": ["Orders"],
            "summary": "Mark orders as printed",
            "description": "Marks one or more orders as printed after the print agent successfully prints them.",
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
            "tags": ["Orders"],
            "summary": "Acknowledge order receipt",
            "description": "Acknowledges that the print device has received the order (before printing). Records ack timestamp and device ID.",
            "parameters": [
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
            "tags": ["Orders"],
            "summary": "Report print result",
            "description": "Reports the print outcome for an order — success, partial, or failure.",
            "parameters": [
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
            "tags": ["Orders"],
            "summary": "Get full order detail",
            "description": "Returns complete order information including items, options, station breakdown, and customer details.",
            "parameters": [
                {"name": "order_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Order detail", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UnprintedOrder"}}}},
                "404": {"description": "Order not found"},
            },
        }
    }

    # ── Devices ─────────────────────────────────────────────────────────

    paths["/ops/api/devices/register"] = {
        "post": {
            "tags": ["Devices"],
            "summary": "Register a print device",
            "description": "Registers a new Android tablet print device or updates an existing registration.",
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
            "tags": ["Devices"],
            "summary": "Send device heartbeat",
            "description": "Periodic heartbeat to keep a device marked as online. If no heartbeat is received for 2 minutes, the device is marked offline.",
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
            "tags": ["Devices"],
            "summary": "List all print devices",
            "description": "Returns all registered print devices with their online status.",
            "responses": {
                "200": {"description": "Devices list", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "devices": {"type": "array", "items": {"$ref": "#/components/schemas/PrintDevice"}}}}}}},
            },
        }
    }

    paths["/ops/api/devices/{device_db_id}/config"] = {
        "get": {
            "tags": ["Devices"],
            "summary": "Get device configuration",
            "description": "Returns the full configuration for a print device including printer mappings, polling intervals, and station assignments.",
            "parameters": [
                {"name": "device_db_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Device config", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "config": {"$ref": "#/components/schemas/DeviceConfig"}}}}}},
                "404": {"description": "Device not found"},
            },
        },
        "put": {
            "tags": ["Devices"],
            "summary": "Update device configuration",
            "description": "Remotely update a device's configuration (admin operation).",
            "parameters": [
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
            "tags": ["Devices"],
            "summary": "Delete a print device",
            "parameters": [
                {"name": "device_db_id", "in": "path", "required": True, "schema": {"type": "integer"}},
            ],
            "responses": {
                "200": {"description": "Device deleted", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}}}},
            },
        }
    }

    # ── Printers ────────────────────────────────────────────────────────

    paths["/ops/api/branch/{branch_id}/printers"] = {
        "get": {
            "tags": ["Printers"],
            "summary": "Get branch printer configuration",
            "description": "Returns all printers configured for a branch, including station-to-printer mapping and default printer.",
            "parameters": [
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

    # ── Diagnostics ─────────────────────────────────────────────────────

    paths["/ops/api/device/log-error"] = {
        "post": {
            "tags": ["Diagnostics"],
            "summary": "Log a device error",
            "description": "Allows the Android app to send error logs to the server for remote diagnostics.",
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

    return paths
