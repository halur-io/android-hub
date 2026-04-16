from database import db

from models.user import (
    user_roles, role_permissions,
    Role, Permission, AdminUser,
)
from models.site import (
    SiteSettings, CustomSection, ReservationSettings, MediaFile,
    TermsOfUse, PrivacyPolicy, ConsentSettings,
)
from models.branch import Branch, BranchMenuItem, WorkingHours
from models.menu import (
    menu_item_dietary_properties,
    MenuCategory, MenuItem, MenuItemPrice, MenuItemIngredient,
    MenuItemVariation, DietaryProperty, MenuSettings,
    MenuItemOptionGroup, MenuItemOptionChoice,
    GlobalOptionGroup, GlobalOptionChoice, GlobalOptionGroupLink,
)
from models.order import (
    FoodOrder, FoodOrderItem, OrderActivityLog,
    ArchivedOrder, ReleasedOrderNumber,
)
from models.stock import (
    StockCategory, Supplier, StockItem, StockLevel, StockTransaction,
    StockAlert, ShoppingList, ShoppingListItem, StockSettings, SupplierItem,
)
from models.receipt import (
    Receipt, ReceiptImport, ReceiptImportItem,
    CostCategory, CostEntry, ReceiptItem,
    CustomFieldDefinition, CustomFieldAssignment,
    ReceiptCustomFieldValue, ReceiptCustomFieldAudit, FileImport,
)
from models.checklist import (
    TaskGroup, ChecklistTask, GeneratedChecklist, TaskTemplate,
    PrintTemplate, MenuTemplate, GeneratedMenu, MenuPrintConfiguration,
)
from models.marketing import (
    Popup, Coupon, CouponUsage, Deal, UpsellRule,
    PopupLead, CustomerConsent,
)
from models.payment import PaymentConfiguration
from models.sms import SMSLog, SMSTemplate, SMSAutoTrigger
from models.catering import CateringPackage, CateringHighlight, CateringGalleryImage
from models.content import (
    GalleryPhoto, ContactMessage, CateringContact,
    CareerPosition, CareerContact, NewsletterSubscriber,
    Reservation, PDFMenuUpload,
)
from models.ops import ManagerPIN, EnrolledDevice, TimeLog
from models.print_ import (
    Printer, PrintStation, PrinterStation,
    PrintDevice, ApiKey, PendingPrintJob, PrintSyncLog,
)
from models.dine_in import DineInTable, DineInSession, DineInPaymentSplit
from models.audit import AuditLog
