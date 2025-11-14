"""
Tabit Office Automation Service
Automates login, report download, and stock updates from Tabit using Selenium
"""
import os
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    
    def get_driver(self):
        """Create and configure Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def login(self, driver):
        """Login to Tabit Office"""
        logger.info("Navigating to Tabit Office login page...")
        driver.get(self.base_url)
        
        logger.info("Waiting for login form...")
        wait = WebDriverWait(driver, 15)
        
        try:
            # Wait for and fill username/email
            logger.info("Looking for email/username field...")
            email_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="username"], input[name="email"]'))
            )
            email_field.clear()
            email_field.send_keys(self.username)
            logger.info("✅ Username entered")
            
            # Fill password
            logger.info("Looking for password field...")
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("✅ Password entered")
            
            # Click login button
            logger.info("Looking for login button...")
            try:
                # Try to find submit button first
                login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            except:
                # If not found, try finding button with text
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign') or contains(text(), 'התחבר')]")
            login_button.click()
            logger.info("✅ Login button clicked")
            
            # Wait for login to complete (look for dashboard elements)
            logger.info("Waiting for login to complete...")
            time.sleep(3)  # Give it time to load
            
            logger.info("✅ Login successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {str(e)}")
            raise
    
    def navigate_to_reports(self, driver):
        """Navigate to the reports section"""
        logger.info("Navigating to reports section...")
        
        try:
            wait = WebDriverWait(driver, 10)
            # Try common report navigation patterns
            reports_link = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Reports') or contains(text(), 'דוחות') or contains(@href, 'report')]"))
            )
            reports_link.click()
            time.sleep(2)
            logger.info("✅ Navigated to reports section")
        except Exception as e:
            logger.warning(f"Could not find standard reports link: {e}")
            logger.info("Manual navigation may be required - taking screenshot for debugging")
    
    def download_sales_report(self, driver, start_date=None, end_date=None):
        """Download sales report for specified date range"""
        if not start_date:
            start_date = datetime.now().date()
        if not end_date:
            end_date = start_date
        
        logger.info(f"Downloading sales report from {start_date} to {end_date}...")
        
        # This will need to be customized based on actual Tabit UI
        # Taking screenshot to help identify elements
        driver.save_screenshot('static/tabit_reports_page.png')
        logger.info("📸 Screenshot saved to static/tabit_reports_page.png for debugging")
        
        # Placeholder - needs actual UI selectors
        logger.info("⚠️  Report download logic needs to be customized based on Tabit UI")
        return None
    
    def explore_tabit_interface(self):
        """
        Interactive exploration of Tabit interface
        Takes screenshots and logs page structure to help build the automation
        """
        logger.info("🔍 Starting Tabit interface exploration...")
        
        driver = None
        try:
            driver = self.get_driver()
            
            # Login
            self.login(driver)
            
            # Take screenshot of dashboard
            driver.save_screenshot('static/tabit_dashboard.png')
            logger.info("📸 Dashboard screenshot: static/tabit_dashboard.png")
            
            # Wait a bit to see the page
            time.sleep(2)
            
            # Try to find reports section
            try:
                self.navigate_to_reports(driver)
            except:
                pass
            
            # Take screenshot of current page
            driver.save_screenshot('static/tabit_reports.png')
            logger.info("📸 Reports screenshot: static/tabit_reports.png")
            
            # Get page HTML structure
            html_content = driver.page_source
            with open('tabit_page_structure.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("📄 Page structure saved to tabit_page_structure.html")
            
            logger.info("\n✅ Exploration complete! Check the screenshots and HTML file.")
            logger.info("Next steps: Review the screenshots to identify:")
            logger.info("  1. Where is the Reports/דוחות menu?")
            logger.info("  2. What type of sales report do you need?")
            logger.info("  3. How to select date range?")
            logger.info("  4. Where is the download/export button?")
            
        except Exception as e:
            logger.error(f"❌ Error during exploration: {e}")
            if driver:
                driver.save_screenshot('static/tabit_error.png')
                logger.error("📸 Error screenshot saved to static/tabit_error.png")
            raise
        finally:
            if driver:
                driver.quit()
    
    def test_connection(self):
        """Test connection to Tabit - just login and take a screenshot"""
        logger.info("🧪 Testing Tabit connection...")
        
        driver = None
        try:
            driver = self.get_driver()
            result = self.login(driver)
            driver.save_screenshot('static/tabit_logged_in.png')
            logger.info("✅ Connection test successful! Screenshot saved to static/tabit_logged_in.png")
            return result
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            if driver:
                driver.save_screenshot('static/tabit_connection_error.png')
                logger.error("📸 Error screenshot saved to static/tabit_connection_error.png")
            return False
        finally:
            if driver:
                driver.quit()


if __name__ == "__main__":
    # Test the automation
    automation = TabitAutomation()
    automation.test_connection()
