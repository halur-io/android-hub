"""
Tabit Office Automation Service
Automates login, report download, and stock updates from Tabit
"""
import os
import logging
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TabitAutomation:
    """Handles automated interactions with Tabit Office"""
    
    def __init__(self):
        self.username = os.environ.get('TABIT_USERNAME')
        self.password = os.environ.get('TABIT_PASSWORD')
        self.base_url = 'https://office.tabit.cloud/'
        
        if not self.username or not self.password:
            raise ValueError("TABIT_USERNAME and TABIT_PASSWORD must be set in environment variables")
    
    def login(self, page):
        """Login to Tabit Office"""
        logger.info("Navigating to Tabit Office login page...")
        page.goto(self.base_url, wait_until='networkidle')
        
        logger.info("Entering credentials...")
        
        # Wait for and fill username
        page.wait_for_selector('input[type="email"], input[name="username"], input[name="email"]', timeout=10000)
        username_field = page.locator('input[type="email"], input[name="username"], input[name="email"]').first
        username_field.fill(self.username)
        
        # Fill password
        password_field = page.locator('input[type="password"]').first
        password_field.fill(self.password)
        
        # Click login button
        login_button = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first
        login_button.click()
        
        logger.info("Waiting for login to complete...")
        # Wait for navigation after login
        page.wait_for_load_state('networkidle', timeout=15000)
        
        logger.info("✅ Login successful!")
        return True
    
    def navigate_to_reports(self, page):
        """Navigate to the reports section"""
        logger.info("Navigating to reports section...")
        
        # This will need to be customized based on actual Tabit UI
        # Common patterns: Reports menu, Analytics, etc.
        try:
            # Try common report navigation patterns
            reports_link = page.locator('a:has-text("Reports"), a:has-text("דוחות"), [href*="report"]').first
            reports_link.click(timeout=5000)
            page.wait_for_load_state('networkidle')
            logger.info("✅ Navigated to reports section")
        except Exception as e:
            logger.warning(f"Could not find standard reports link: {e}")
            logger.info("Manual navigation may be required - taking screenshot for debugging")
            page.screenshot(path='tabit_dashboard.png')
    
    def download_sales_report(self, page, start_date=None, end_date=None):
        """Download sales report for specified date range"""
        if not start_date:
            start_date = datetime.now().date()
        if not end_date:
            end_date = start_date
        
        logger.info(f"Downloading sales report from {start_date} to {end_date}...")
        
        # This will need to be customized based on actual Tabit UI
        # Taking screenshot to help identify elements
        page.screenshot(path='tabit_reports_page.png')
        logger.info("📸 Screenshot saved to tabit_reports_page.png for debugging")
        
        # Placeholder - needs actual UI selectors
        logger.info("⚠️  Report download logic needs to be customized based on Tabit UI")
        return None
    
    def explore_tabit_interface(self):
        """
        Interactive exploration of Tabit interface
        Takes screenshots and logs page structure to help build the automation
        """
        logger.info("🔍 Starting Tabit interface exploration...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # Must be headless in Replit
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                # Login
                self.login(page)
                
                # Take screenshot of dashboard
                page.screenshot(path='static/tabit_dashboard.png', full_page=True)
                logger.info("📸 Dashboard screenshot: static/tabit_dashboard.png")
                
                # Wait a bit to see the page
                time.sleep(2)
                
                # Try to find reports section
                self.navigate_to_reports(page)
                
                # Take screenshot of reports page
                page.screenshot(path='static/tabit_reports.png', full_page=True)
                logger.info("📸 Reports screenshot: static/tabit_reports.png")
                
                # Get page HTML structure
                html_content = page.content()
                with open('tabit_page_structure.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info("📄 Page structure saved to tabit_page_structure.html")
                
                logger.info("\n✅ Exploration complete! Check the screenshots and HTML file.")
                logger.info("Next steps: Review the screenshots to identify:")
                logger.info("  1. Where is the Reports/דוחות menu?")
                logger.info("  2. What type of sales report do you need?")
                logger.info("  3. How to select date range?")
                logger.info("  4. Where is the download/export button?")
                
                # Keep browser open for manual inspection
                input("\nPress Enter to close browser and continue...")
                
            except Exception as e:
                logger.error(f"❌ Error during exploration: {e}")
                page.screenshot(path='static/tabit_error.png')
                logger.error("📸 Error screenshot saved to static/tabit_error.png")
                raise
            finally:
                browser.close()
    
    def test_connection(self):
        """Test connection to Tabit - just login and take a screenshot"""
        logger.info("🧪 Testing Tabit connection...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                result = self.login(page)
                page.screenshot(path='static/tabit_logged_in.png', full_page=True)
                logger.info("✅ Connection test successful! Screenshot saved.")
                return result
            except Exception as e:
                logger.error(f"❌ Connection test failed: {e}")
                page.screenshot(path='static/tabit_connection_error.png')
                return False
            finally:
                browser.close()


if __name__ == "__main__":
    # Test the automation
    automation = TabitAutomation()
    automation.explore_tabit_interface()
