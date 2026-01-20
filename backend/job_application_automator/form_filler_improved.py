#!/usr/bin/env python3
"""
IMPROVED Simple Form Filler - Multi-Page Support
Key improvements:
1. Multi-page form detection and navigation
2. Persistent browser session across pages
3. Smart button detection (Next/Continue/Submit)
4. Better error handling and recovery
5. Progress tracking across pages
"""

import asyncio
import json
import sys
import logging
import os
import warnings
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from playwright.async_api import async_playwright, Page, ElementHandle
from undetected_playwright import stealth_async

# Try to import geocoder, fallback if not available
try:
    import geocoder
    GEOCODER_AVAILABLE = True
except ImportError:
    GEOCODER_AVAILABLE = False

# Suppress Windows asyncio pipe warnings
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*pipe.*")

# Configure logging
import tempfile
import os
from pathlib import Path

# Create a proper log directory
try:
    log_dir = Path.home() / '.job-automator'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'form_filler.log'
except (PermissionError, OSError):
    log_file = Path(tempfile.gettempdir()) / 'job_automator_form_filler.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovedFormFiller:
    """Enhanced form filler with multi-page support."""
    
    def __init__(self):
        self.logger = logger
        self.page = None
        self.context = None
        self.browser = None
        self.form_data = None
        self.iframe_frame = None
        
        # Multi-page tracking
        self.current_page_number = 1
        self.total_pages_detected = None
        self.pages_filled = []
        self.keep_browser_open = True
        
        # Timeouts and wait strategies
        self.timeouts = {
            'navigation': 15000,
            'element_wait': 5000,
            'interaction': 2000,
            'file_upload': 8000,
            'dropdown_load': 4000,
            'geolocation': 5000,
            'page_transition': 3000  # Wait for page transitions
        }
        
        # Geolocation configuration
        self.geolocation_config = {
            'enabled': True,
            'default_coordinates': None,
            'timeout': 5000,
            'location_keywords': ['location', 'city', 'state', 'country', 'address', 'zip', 'postal']
        }
    
    async def fill_form(self, json_file_path: str) -> bool:
        """Main method to fill form with multi-page support."""
        try:
            # Reset state
            self.current_page_number = 1
            self.pages_filled = []
            self.iframe_frame = None
            
            # Get real location coordinates
            self.geolocation_config['default_coordinates'] = self._get_real_location()
            
            # Load and validate JSON data
            self.form_data = self._load_form_data(json_file_path)
            if not self.form_data:
                return False
            
            # Initialize browser
            await self._initialize_browser()
            
            # Navigate to form page
            form_page = await self._navigate_to_form(self.form_data)
            if not form_page:
                return False
            
            # Multi-page form filling loop
            success = await self._fill_multipage_form(form_page, self.form_data)
            
            if success:
                self.logger.info("✅ All form pages filled successfully!")
                self.logger.info("🔍 Please review the filled form and submit manually.")
                self.logger.info("🛑 The browser will remain open. Close it when done.")
                
                # Wait for user to review and submit
                if self.keep_browser_open:
                    await self._wait_for_user_action()
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error during form filling: {e}")
            return False
        finally:
            if not self.keep_browser_open:
                await self._cleanup_browser()
    
    async def _fill_multipage_form(self, page: Page, form_data: Dict[str, Any]) -> bool:
        """Fill multi-page form with automatic navigation between pages."""
        try:
            self.logger.info("\n" + "="*70)
            self.logger.info("🚀 STARTING MULTI-PAGE FORM FILLING")
            self.logger.info("="*70)
            
            page_number = 1
            max_pages = 20  # Safety limit
            
            while page_number <= max_pages:
                self.logger.info(f"\n📄 PAGE {page_number}")
                self.logger.info("-" * 70)
                
                # Wait for page to be ready
                await self._smart_wait(1000)
                
                # Dismiss any overlays
                await self._dismiss_overlays()
                
                # Fill fields on current page
                fields_filled = await self._fill_visible_fields(page, form_data)
                
                self.logger.info(f"✅ Filled {fields_filled} fields on page {page_number}")
                self.pages_filled.append({
                    'page_number': page_number,
                    'fields_filled': fields_filled,
                    'url': self.page.url
                })
                
                # Handle geolocation after filling fields
                await self._handle_post_fill_geolocation(form_data)
                
                # Check for navigation buttons
                button_info = await self._detect_form_buttons()
                
                if button_info['has_next']:
                    self.logger.info(f"\n🔄 Found '{button_info['next_text']}' button - moving to next page...")
                    
                    # Click Next/Continue button
                    clicked = await self._click_navigation_button(button_info['next_button'])
                    
                    if clicked:
                        # Wait for page transition
                        await self._wait_for_page_transition()
                        page_number += 1
                        continue
                    else:
                        self.logger.warning("Failed to click Next button")
                        break
                
                elif button_info['has_submit']:
                    self.logger.info(f"\n🎯 Found '{button_info['submit_text']}' button on final page")
                    self.logger.info("✅ All pages filled! Ready for manual review and submission")
                    break
                
                else:
                    self.logger.info("\n✅ No more pages detected - form filling complete")
                    break
            
            # Summary
            self.logger.info("\n" + "="*70)
            self.logger.info("📊 FORM FILLING SUMMARY")
            self.logger.info("="*70)
            self.logger.info(f"Total pages filled: {len(self.pages_filled)}")
            for page_info in self.pages_filled:
                self.logger.info(f"  Page {page_info['page_number']}: {page_info['fields_filled']} fields")
            self.logger.info("="*70 + "\n")
            
            return len(self.pages_filled) > 0
            
        except Exception as e:
            self.logger.error(f"Error in multi-page form filling: {e}")
            return False
    
    async def _fill_visible_fields(self, page: Page, form_data: Dict[str, Any]) -> int:
        """Fill only the visible/interactable fields on the current page."""
        try:
            user_inputs = form_data['user_input_template']
            filled_count = 0
            
            context = self._get_form_context()
            
            for i, field_data in enumerate(user_inputs, 1):
                try:
                    field_id = field_data['id']
                    field_value = field_data.get('value', '').strip()
                    field_type = field_data['type']
                    field_question = field_data['question']
                    
                    # Skip empty optional fields
                    if not field_value and not field_data.get('required', False):
                        continue
                    
                    # Check if field is visible/present on current page
                    is_visible = await self._is_field_visible(context, field_id, field_type)
                    
                    if not is_visible:
                        self.logger.debug(f"Skipping {field_id} - not visible on this page")
                        continue
                    
                    self.logger.info(f"  [{i}] Filling: {field_question}")
                    
                    # Fill field based on type
                    success = await self._fill_field_by_type(page, field_data)
                    
                    if success:
                        filled_count += 1
                    
                    await self._smart_wait(100)
                    
                except Exception as e:
                    self.logger.debug(f"Error filling field {field_data.get('id', 'unknown')}: {e}")
                    continue
            
            return filled_count
            
        except Exception as e:
            self.logger.error(f"Error in fill_visible_fields: {e}")
            return 0
    
    async def _is_field_visible(self, context, field_id: str, field_type: str) -> bool:
        """Check if a field is visible and interactable on the current page."""
        try:
            # Build selectors based on field type
            selectors = []
            
            if field_type in ['text', 'email', 'url', 'phone']:
                selectors = [
                    f'#{field_id}',
                    f'input[id="{field_id}"]',
                    f'input[name="{field_id}"]'
                ]
            elif field_type == 'dropdown':
                selectors = [
                    f'#{field_id}',
                    f'select[id="{field_id}"]',
                    f'[role="combobox"][id="{field_id}"]'
                ]
            elif field_type == 'file':
                selectors = [
                    f'#{field_id}',
                    f'input[type="file"][id="{field_id}"]',
                    f'input[type="file"]'  # Fallback
                ]
            elif field_type == 'textarea':
                selectors = [
                    f'#{field_id}',
                    f'textarea[id="{field_id}"]'
                ]
            
            # Try to find the element
            for selector in selectors:
                try:
                    element = await context.query_selector(selector)
                    if element:
                        # Check if element is visible
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking field visibility: {e}")
            return False
    
    async def _detect_form_buttons(self) -> Dict[str, Any]:
        """Detect Next/Continue/Submit buttons on the current page."""
        try:
            context = self._get_form_context()
            
            result = {
                'has_next': False,
                'has_submit': False,
                'has_previous': False,
                'next_button': None,
                'submit_button': None,
                'previous_button': None,
                'next_text': '',
                'submit_text': ''
            }
            
            # Define button patterns
            next_patterns = [
                ('button:has-text("Next")', 'Next'),
                ('button:has-text("Continue")', 'Continue'),
                ('button:has-text("Continue to")', 'Continue'),
                ('button:has-text("Save and Continue")', 'Save and Continue'),
                ('button:has-text("Proceed")', 'Proceed'),
                ('a:has-text("Next")', 'Next'),
                ('a:has-text("Continue")', 'Continue'),
                ('[role="button"]:has-text("Next")', 'Next'),
                ('[role="button"]:has-text("Continue")', 'Continue'),
                ('button[class*="next"]', 'Next'),
                ('button[class*="continue"]', 'Continue'),
                ('[data-testid*="next"]', 'Next'),
                ('[data-testid*="continue"]', 'Continue')
            ]
            
            submit_patterns = [
                ('button:has-text("Submit")', 'Submit'),
                ('button:has-text("Submit Application")', 'Submit Application'),
                ('button:has-text("Apply")', 'Apply'),
                ('button:has-text("Send Application")', 'Send Application'),
                ('button[type="submit"]', 'Submit'),
                ('input[type="submit"]', 'Submit'),
                ('[role="button"]:has-text("Submit")', 'Submit'),
                ('button[class*="submit"]', 'Submit')
            ]
            
            # Search for Next/Continue buttons (exclude Submit buttons)
            for selector, text in next_patterns:
                try:
                    elements = await context.query_selector_all(selector)
                    for element in elements:
                        element_text = await element.text_content() or ""
                        element_text_clean = element_text.strip().lower()
                        
                        # Skip if it's actually a submit button
                        if any(word in element_text_clean for word in ['submit', 'apply', 'send application']):
                            continue
                        
                        # Check if visible
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            result['has_next'] = True
                            result['next_button'] = element
                            result['next_text'] = element_text.strip()
                            self.logger.debug(f"Found Next button: '{result['next_text']}'")
                            break
                except:
                    continue
                
                if result['has_next']:
                    break
            
            # Search for Submit buttons
            for selector, text in submit_patterns:
                try:
                    elements = await context.query_selector_all(selector)
                    for element in elements:
                        element_text = await element.text_content() or ""
                        
                        # Check if visible
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            result['has_submit'] = True
                            result['submit_button'] = element
                            result['submit_text'] = element_text.strip()
                            self.logger.debug(f"Found Submit button: '{result['submit_text']}'")
                            break
                except:
                    continue
                
                if result['has_submit']:
                    break
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting form buttons: {e}")
            return {
                'has_next': False,
                'has_submit': False,
                'next_button': None,
                'submit_button': None,
                'next_text': '',
                'submit_text': ''
            }
    
    async def _click_navigation_button(self, button_element) -> bool:
        """Click a navigation button (Next/Continue) and wait for page to load."""
        try:
            if not button_element:
                return False
            
            # Store current URL to detect navigation
            current_url = self.page.url
            
            # Scroll to button and ensure it's visible
            await button_element.scroll_into_view_if_needed()
            await self._smart_wait(500)
            
            # Click the button
            await button_element.click()
            
            # Wait for navigation or content change
            await self._smart_wait(1000)
            
            # Check if URL changed or page updated
            new_url = self.page.url
            if new_url != current_url:
                self.logger.info(f"  ✅ Navigated to: {new_url}")
            else:
                self.logger.info("  ✅ Page content updated")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clicking navigation button: {e}")
            return False
    
    async def _wait_for_page_transition(self):
        """Wait for page transition to complete."""
        try:
            # Wait for network to be idle
            await self.page.wait_for_load_state('networkidle', timeout=self.timeouts['page_transition'])
            
            # Additional wait for dynamic content
            await self._smart_wait(1000)
            
            # Dismiss any new overlays on the new page
            await self._dismiss_overlays()
            
        except Exception as e:
            self.logger.debug(f"Page transition wait: {e}")
            await self._smart_wait(2000)  # Fallback wait
    
    async def _wait_for_user_action(self):
        """Wait for user to manually review and submit the form."""
        self.logger.info("\n" + "="*70)
        self.logger.info("🎉 FORM FILLING COMPLETED!")
        self.logger.info("📋 Please review all filled fields carefully")
        self.logger.info("✅ Make any necessary corrections")
        self.logger.info("🚀 Submit the form when ready")
        self.logger.info("🔒 Browser will stay open - close it when done")
        self.logger.info("="*70 + "\n")
        
        try:
            initial_url = self.page.url
            
            while True:
                await asyncio.sleep(2)
                
                try:
                    current_url = self.page.url
                    
                    # Check if URL changed significantly (submission)
                    if current_url != initial_url and ('thank' in current_url.lower() or 'confirm' in current_url.lower()):
                        self.logger.info("🎉 Form submission detected! You can close the browser.")
                        await self._smart_wait(5000)  # Give user time to see confirmation
                        break
                    
                    # Check for success messages
                    success_text = await self.page.evaluate('''() => {
                        const text = document.body.innerText.toLowerCase();
                        return text.includes('thank you') || 
                               text.includes('application submitted') || 
                               text.includes('successfully submitted') ||
                               text.includes('application received');
                    }''')
                    
                    if success_text:
                        self.logger.info("🎉 Success message detected!")
                        await self._smart_wait(5000)  # Give user time to see
                        break
                        
                except Exception:
                    # Page might be closed
                    self.logger.info("Browser closed by user.")
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("Manual exit requested.")
        except Exception as e:
            self.logger.debug(f"Error in wait_for_user_action: {e}")
        finally:
            # Don't auto-close - let user close the browser
            self.logger.info("🔒 Browser session ended.")
    
    # ============================================================================
    # ALL OTHER METHODS FROM ORIGINAL form_filler.py GO HERE
    # (I'll include key methods below, but in practice you'd copy all methods)
    # ============================================================================
    
    def _load_form_data(self, json_file_path: str) -> Optional[Dict[str, Any]]:
        """Load and validate form data from JSON file."""
        try:
            if not os.path.exists(json_file_path):
                self.logger.error(f"JSON file not found: {json_file_path}")
                return None
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_keys = ['url', 'form_context', 'user_input_template']
            for key in required_keys:
                if key not in data:
                    self.logger.error(f"Missing required key in JSON: {key}")
                    return None
            
            self.logger.info(f"Loaded form data for: {data.get('job_title', 'Unknown Job')}")
            self.logger.info(f"Company: {data.get('company', 'Unknown Company')}")
            self.logger.info(f"Total fields to fill: {len(data['user_input_template'])}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading JSON data: {e}")
            return None
    
    async def _initialize_browser(self):
        """Initialize browser with stealth mode."""
        self.logger.info("Initializing browser...")
        
        playwright = await async_playwright().__aenter__()
        
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            extra_http_headers={'Accept-Language': 'en-US,en;q=0.9'},
            geolocation=self.geolocation_config['default_coordinates'],
            permissions=['geolocation']
        )
        
        self.page = await self.context.new_page()
        await stealth_async(self.page)
        
        self.logger.info("Browser initialized successfully")
    
    async def _navigate_to_form(self, form_data: Dict[str, Any]) -> Optional[Page]:
        """Navigate to the form page."""
        try:
            url = form_data['url']
            self.logger.info(f"Navigating to: {url}")
            
            response = await self.page.goto(url, timeout=self.timeouts['navigation'])
            if response:
                self.logger.info(f"Navigation response: {response.status}")
            
            await self.page.wait_for_load_state('domcontentloaded')
            await self._smart_wait(500)
            
            await self._dismiss_overlays()
            
            # Handle iframe if needed
            form_context = form_data['form_context']
            if form_context.get('is_iframe', False):
                self.logger.info("Form is in iframe, handling...")
                return await self._handle_iframe_navigation(form_context)
            
            return self.page
                
        except Exception as e:
            self.logger.error(f"Error navigating to form: {e}")
            return None
    
    async def _handle_iframe_navigation(self, form_context: Dict[str, Any]) -> Optional[Page]:
        """Handle iframe navigation."""
        # [Copy implementation from original form_filler.py]
        # This is complex, so I'm referencing it here
        pass
    
    def _get_form_context(self):
        """Get the appropriate context for form operations."""
        return self.iframe_frame if self.iframe_frame else self.page
    
    async def _fill_field_by_type(self, page: Page, field_data: Dict[str, Any]) -> bool:
        """Fill a single field based on its type."""
        # [Copy implementation from original form_filler.py]
        # This method calls:
        # - _fill_text_field
        # - _fill_dropdown_field
        # - _fill_file_field
        # - _fill_textarea_field
        pass
    
    async def _dismiss_overlays(self):
        """Dismiss cookie banners and overlays."""
        # [Copy implementation from original form_filler.py]
        pass
    
    async def _smart_wait(self, milliseconds: int):
        """Smart wait function."""
        await asyncio.sleep(milliseconds / 1000)
    
    async def _handle_post_fill_geolocation(self, form_data: Dict[str, Any]) -> bool:
        """Handle geolocation after filling fields."""
        # [Copy implementation from original form_filler.py]
        pass
    
    def _get_real_location(self) -> Dict[str, Any]:
        """Get real location coordinates."""
        # [Copy implementation from original form_filler.py]
        return {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'accuracy': 0
        }
    
    async def _cleanup_browser(self):
        """Cleanup browser resources."""
        try:
            if self.browser:
                if self.context:
                    await self.context.close()
                await self.browser.close()
                await asyncio.sleep(0.5)
                self.logger.info("Browser cleaned up")
        except Exception as e:
            self.logger.debug(f"Error during cleanup: {e}")
        finally:
            self.page = None
            self.context = None
            self.browser = None


async def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python form_filler_improved.py <path_to_filled_json>")
        return
    
    json_file = sys.argv[1]
    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        return
    
    filler = ImprovedFormFiller()
    success = await filler.fill_form(json_file)
    
    if success:
        print("\n✅ Form filling completed successfully!")
    else:
        print("\n❌ Form filling failed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
