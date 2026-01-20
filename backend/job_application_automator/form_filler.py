#!/usr/bin/env python3
"""
Simple Form Filler - Automatically fills job application forms
Takes JSON output from form extractor with user-filled values and submits the form
"""

import asyncio
import json
import sys
import logging
import os
import warnings
from typing import Dict, Any, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Page, ElementHandle
from undetected_playwright import stealth_async

# Try to import geocoder, fallback if not available
try:
    import geocoder
    GEOCODER_AVAILABLE = True
except ImportError:
    GEOCODER_AVAILABLE = False
    print("⚠️ Warning: 'geocoder' library not found. Install with: pip install geocoder")
    print("   Falling back to hardcoded San Francisco coordinates.")

# Suppress Windows asyncio pipe warnings
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed.*")
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*pipe.*")

# Configure logging
import tempfile
import os
from pathlib import Path

# Create a proper log directory
try:
    # Try to use user's home directory first
    log_dir = Path.home() / '.job-automator'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'form_filler.log'
except (PermissionError, OSError):
    # Fallback to temporary directory
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

class SimpleFormFiller:
    def __init__(self):
        self.logger = logger
        self.page = None
        self.context = None
        self.browser = None
        self.form_data = None  # Store form data for helper methods
        self.iframe_frame = None  # Store iframe frame context when needed
        
        # Multi-page tracking (NEW)
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
            'geolocation': 5000,  # Timeout for geolocation operations
            'page_transition': 3000  # NEW: Wait for page transitions
        }
        
        # Geolocation configuration
        self.geolocation_config = {
            'enabled': True,
            'default_coordinates': None,  # Will be set by _get_real_location()
            'timeout': 5000,  # 5 seconds timeout for locate me operations
            'location_keywords': ['location', 'city', 'state', 'country', 'address', 'zip', 'postal']
        }
    
    async def fill_form(self, json_file_path: str) -> bool:
        """Main method to fill form based on JSON data."""
        try:
            # Reset iframe frame for new session
            self.iframe_frame = None
            
            # Get real location coordinates before browser initialization
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
            
            # Fill all form fields with multi-page support
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
            # Proper cleanup to prevent Windows pipe exceptions
            await self._cleanup_browser()
    
    def _load_form_data(self, json_file_path: str) -> Optional[Dict[str, Any]]:
        """Load and validate form data from JSON file."""
        try:
            if not os.path.exists(json_file_path):
                self.logger.error(f"JSON file not found: {json_file_path}")
                return None
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_keys = ['url', 'form_context', 'user_input_template']
            for key in required_keys:
                if key not in data:
                    self.logger.error(f"Missing required key in JSON: {key}")
                    return None
            
            self.logger.info(f"Loaded form data for: {data.get('job_title', 'Unknown Job')}")
            self.logger.info(f"Company: {data.get('company', 'Unknown Company')}")
            self.logger.info(f"Total fields to fill: {len(data['user_input_template'])}")
            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading JSON data: {e}")
            return None
    
    async def _initialize_browser(self):
        """Initialize browser with stealth mode."""
        self.logger.info("Initializing browser...")
        
        playwright = await async_playwright().__aenter__()
        
        # Launch browser in non-headless mode for user interaction
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--aggressive-cache-discard',
                '--memory-pressure-off'
            ]
        )
        
        # Create context with realistic settings and geolocation permissions
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9'
            },
            # Grant geolocation permissions and set default coordinates
            geolocation=self.geolocation_config['default_coordinates'],
            permissions=['geolocation']
        )
        
        self.page = await self.context.new_page()
        
        # Apply stealth mode
        await stealth_async(self.page)
        
        self.logger.info("Browser initialized successfully")
        self.logger.info(f"🌍 Geolocation enabled with coordinates: {self.geolocation_config['default_coordinates']['latitude']}, {self.geolocation_config['default_coordinates']['longitude']}")
        self.logger.info("📍 'Locate me' buttons will be clicked AFTER all form fields are filled")
    
    async def _navigate_to_form(self, form_data: Dict[str, Any]) -> Optional[Page]:
        """Navigate to the form page, handling iframes if needed."""
        try:
            url = form_data['url']
            form_context = form_data['form_context']
            
            self.logger.info(f"Navigating to: {url}")
            
            # Navigate to the URL
            response = await self.page.goto(url, timeout=self.timeouts['navigation'])
            if response:
                self.logger.info(f"Navigation response: {response.status}")
            
            # Wait for page to load
            await self.page.wait_for_load_state('domcontentloaded')
            await self._smart_wait(500)
            
            # Dismiss any overlays/cookie banners
            await self._dismiss_overlays()
            
            # Handle iframe if needed
            if form_context.get('is_iframe', False):
                self.logger.info("🔍 Form is embedded in iframe, attempting iframe access...")
                iframe_result = await self._handle_iframe_navigation(form_context)
                if iframe_result:
                    self.logger.info("✅ Iframe handling completed successfully")
                else:
                    self.logger.error("❌ Failed to handle iframe navigation")
                return iframe_result
            else:
                self.logger.info("Using main page for form filling")
                return self.page
                
        except Exception as e:
            self.logger.error(f"Error navigating to form: {e}")
            return None
    
    async def _handle_iframe_navigation(self, form_context: Dict[str, Any]) -> Optional[Page]:
        """Handle accessing iframe within the parent page, with fallback to direct navigation."""
        try:
            iframe_src = form_context.get('iframe_src')
            
            if not iframe_src:
                self.logger.error("No iframe_src provided in form context")
                return None
            
            self.logger.info(f"Looking for iframe with src: {iframe_src}")
            
            # Wait for iframe to be present on the page
            await self._smart_wait(1000)  # Extra wait for iframe to load
            
            # Try to find the iframe element using different strategies
            iframe_element = None
            
            # Strategy 1: Find by exact src match
            try:
                iframe_element = await self.page.wait_for_selector(f'iframe[src="{iframe_src}"]', timeout=5000)
                if iframe_element:
                    self.logger.info("Found iframe by exact src match")
            except:
                pass
            
            # Strategy 2: Find by partial src match (in case of relative URLs)
            if not iframe_element:
                try:
                    iframes = await self.page.query_selector_all('iframe')
                    for iframe in iframes:
                        src = await iframe.get_attribute('src')
                        if src and (iframe_src in src or src in iframe_src):
                            iframe_element = iframe
                            self.logger.info("Found iframe by partial src match")
                            break
                except:
                    pass
            
            # Strategy 3: Find first iframe if only one exists
            if not iframe_element:
                try:
                    iframes = await self.page.query_selector_all('iframe')
                    if len(iframes) == 1:
                        iframe_element = iframes[0]
                        self.logger.info("Using single iframe found on page")
                except:
                    pass
            
            # Strategy 4: If iframe not found, navigate directly to iframe src URL
            if not iframe_element:
                self.logger.warning("Could not find iframe element on the page")
                self.logger.info(f"🔄 Attempting fallback: navigating directly to iframe src URL: {iframe_src}")
                
                try:
                    # Check if iframe_src is a relative URL and make it absolute if needed
                    if iframe_src.startswith('/'):
                        from urllib.parse import urljoin
                        current_url = self.page.url
                        iframe_src = urljoin(current_url, iframe_src)
                        self.logger.info(f"Converted relative URL to absolute: {iframe_src}")
                    
                    # Navigate directly to the iframe URL
                    response = await self.page.goto(iframe_src, timeout=self.timeouts['navigation'])
                    if response:
                        self.logger.info(f"Direct navigation response: {response.status}")
                    
                    # Wait for page to load
                    await self.page.wait_for_load_state('domcontentloaded')
                    await self._smart_wait(1000)
                    
                    # Dismiss any overlays on the new page
                    await self._dismiss_overlays()
                    
                    # Reset iframe_frame since we're now on the main page (not iframe)
                    self.iframe_frame = None
                    
                    self.logger.info("✅ Successfully navigated directly to iframe src URL")
                    self.logger.info("📋 Form filling will continue on the main page")
                    return self.page
                    
                except Exception as nav_error:
                    self.logger.error(f"Failed to navigate directly to iframe src URL: {nav_error}")
                    return None
            
            # Original iframe access logic (when iframe is found)
            try:
                # Get the iframe's frame context
                frame = await iframe_element.content_frame()
                if not frame:
                    self.logger.error("Could not access iframe content frame")
                    # Fallback to direct navigation if frame access fails
                    self.logger.info(f"🔄 Frame access failed, attempting direct navigation to: {iframe_src}")
                    return await self._navigate_to_iframe_src_directly(iframe_src)
                
                # Wait for iframe content to load
                await frame.wait_for_load_state('domcontentloaded')
                await self._smart_wait(1000)  # Extra wait for form content to load
                
                # Store the frame for use in form filling
                self.iframe_frame = frame
                
                self.logger.info("✅ Successfully accessed iframe content frame")
                return self.page  # Return page but we'll use iframe_frame for form operations
                
            except Exception as frame_error:
                self.logger.error(f"Error accessing iframe frame: {frame_error}")
                # Fallback to direct navigation if frame access fails
                self.logger.info(f"🔄 Frame access failed, attempting direct navigation to: {iframe_src}")
                return await self._navigate_to_iframe_src_directly(iframe_src)
                
        except Exception as e:
            self.logger.error(f"Error in iframe navigation: {e}")
            return None
    
    async def _navigate_to_iframe_src_directly(self, iframe_src: str) -> Optional[Page]:
        """Navigate directly to the iframe src URL as a fallback method."""
        try:
            # Check if iframe_src is a relative URL and make it absolute if needed
            if iframe_src.startswith('/'):
                from urllib.parse import urljoin
                current_url = self.page.url
                iframe_src = urljoin(current_url, iframe_src)
                self.logger.info(f"Converted relative URL to absolute: {iframe_src}")
            
            # Navigate directly to the iframe URL
            response = await self.page.goto(iframe_src, timeout=self.timeouts['navigation'])
            if response:
                self.logger.info(f"Direct navigation response: {response.status}")
            
            # Wait for page to load
            await self.page.wait_for_load_state('domcontentloaded')
            await self._smart_wait(1000)
            
            # Dismiss any overlays on the new page
            await self._dismiss_overlays()
            
            # Reset iframe_frame since we're now on the main page (not iframe)
            self.iframe_frame = None
            
            self.logger.info("✅ Successfully navigated directly to iframe src URL")
            self.logger.info("📋 Form filling will continue on the main page")
            return self.page
            
        except Exception as e:
            self.logger.error(f"Failed to navigate directly to iframe src URL: {e}")
            return None
    
    def _get_form_context(self):
        """Get the appropriate context for form operations (page or iframe frame)."""
        return self.iframe_frame if self.iframe_frame else self.page
    
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
                
                # Fill fields visible on current page
                fields_filled = await self._fill_visible_fields(page, form_data)
                
                self.logger.info(f"✅ Filled {fields_filled} fields on page {page_number}")
                self.pages_filled.append({
                    'page_number': page_number,
                    'fields_filled': fields_filled,
                    'url': self.page.url
                })
                
                # Handle geolocation after filling fields
                if fields_filled > 0:
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
                    
                    # Skip empty required fields but warn
                    if not field_value and field_data.get('required', False):
                        self.logger.warning(f"Required field is empty: {field_id}")
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
                'next_button': None,
                'submit_button': None,
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
    
    async def _fill_all_fields(self, page: Page, form_data: Dict[str, Any]) -> bool:
        """Fill all fields based on user input template."""
        try:
            user_inputs = form_data['user_input_template']
            filled_count = 0
            total_count = len(user_inputs)
            
            self.logger.info(f"Starting to fill {total_count} fields...")
            
            for i, field_data in enumerate(user_inputs, 1):
                try:
                    field_id = field_data['id']
                    field_value = field_data.get('value', '').strip()
                    field_type = field_data['type']
                    field_question = field_data['question']
                    
                    self.logger.info(f"[{i}/{total_count}] Filling: {field_question}")
                    
                    # Skip empty non-required fields
                    if not field_value and not field_data.get('required', False):
                        self.logger.info(f"Skipping empty optional field: {field_id}")
                        continue
                    
                    # Skip empty required fields but warn
                    if not field_value and field_data.get('required', False):
                        self.logger.warning(f"Required field is empty: {field_id}")
                        continue
                    
                    # Fill field based on type
                    success = await self._fill_field_by_type(page, field_data)
                    
                    if success:
                        filled_count += 1
                        self.logger.info(f"✅ Successfully filled: {field_question}")
                    else:
                        self.logger.warning(f"❌ Failed to fill: {field_question}")
                    
                    # Small delay between fields
                    await self._smart_wait(100)
                    
                except Exception as e:
                    self.logger.error(f"Error filling field {field_data.get('id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Form filling completed: {filled_count}/{total_count} fields filled")
            return filled_count > 0
            
        except Exception as e:
            self.logger.error(f"Error in fill_all_fields: {e}")
            return False
    
    async def _fill_field_by_type(self, page: Page, field_data: Dict[str, Any]) -> bool:
        """Fill a single field based on its type."""
        field_id = field_data['id']
        field_value = field_data['value']
        field_type = field_data['type']
        
        try:
            if field_type in ['text', 'email', 'url', 'phone']:
                return await self._fill_text_field(page, field_id, field_value)
            elif field_type == 'dropdown':
                return await self._fill_dropdown_field(page, field_id, field_value)
            elif field_type == 'file':
                return await self._fill_file_field(page, field_id, field_value)
            elif field_type == 'textarea':
                return await self._fill_textarea_field(page, field_id, field_value)
            else:
                self.logger.warning(f"Unknown field type: {field_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error filling field {field_id}: {e}")
            return False
    
    async def _fill_text_field(self, page: Page, field_id: str, value: str) -> bool:
        """Fill text, email, url, or phone input fields."""
        try:
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Get field label from the JSON data for more accurate selection
            field_label = self._get_field_label_by_id(field_id)
            
            element = None
            
            # Method 1: Try by role and name (most reliable for Greenhouse forms)
            if field_label:
                try:
                    element = await context.get_by_role('textbox', name=field_label).first
                    if element:
                        await element.scroll_into_view_if_needed()
                        await element.fill(value)
                        # Verify the value was set
                        actual_value = await element.input_value()
                        if actual_value == value:
                            return True
                except Exception as e:
                    self.logger.debug(f"Method 1 failed for {field_id}: {e}")
            
            # Method 2: Try multiple selectors for finding the field (fallback)
            selectors = [
                f'#{field_id}',
                f'input[id="{field_id}"]',
                f'input[name="{field_id}"]',
                f'[data-qa="{field_id}"]',
                f'[data-testid="{field_id}"]'
            ]
            
            for selector in selectors:
                try:
                    element = await context.wait_for_selector(selector, timeout=5000)
                    if element:
                        break
                except:
                    continue
            
            if not element:
                self.logger.error(f"Could not find text field: {field_id}")
                return False
            
            # Scroll to element and ensure it's visible
            await element.scroll_into_view_if_needed()
            await self._smart_wait(100)
            
            # Clear existing value and fill new value
            await element.click()
            await element.fill('')  # Clear first
            await element.fill(value)
            
            # Verify the value was set
            actual_value = await element.input_value()
            if actual_value == value:
                return True
            else:
                self.logger.warning(f"Value mismatch for {field_id}: expected '{value}', got '{actual_value}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Error filling text field {field_id}: {e}")
            return False
    
    async def _fill_dropdown_field(self, page: Page, field_id: str, value: str) -> bool:
        """Fill dropdown/select fields."""
        try:
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Get field label from the JSON data for more accurate selection
            field_label = self._get_field_label_by_id(field_id)
            
            element = None
            
            # Method 1: Try by role and name (most reliable for Greenhouse forms)
            if field_label:
                try:
                    element = await context.get_by_role('combobox', name=field_label).first
                    if element:
                        # Click to open the dropdown
                        await element.scroll_into_view_if_needed()
                        await self._smart_wait(100)
                        
                        # Click the toggle button to open dropdown
                        toggle_button = context.locator('button:has-text("Toggle flyout")').first
                        try:
                            await toggle_button.click()
                            await self._smart_wait(300)
                        except:
                            # Fallback: click the combobox itself
                            await element.click()
                            await self._smart_wait(300)
                        
                        # Look for the option by exact text match
                        try:
                            option = context.get_by_role('option', name=value, exact=True)
                            await option.click()
                            await self._smart_wait(200)
                            return True
                        except Exception as e:
                            self.logger.debug(f"Exact option match failed for '{value}': {e}")
                            # Try partial match
                            try:
                                option = context.get_by_role('option').filter(has_text=value).first
                                await option.click()
                                await self._smart_wait(200)
                                return True
                            except:
                                pass
                        
                except Exception as e:
                    self.logger.debug(f"Method 1 failed for {field_id}: {e}")
            
            # Method 2: Try multiple selectors for dropdown (fallback)
            selectors = [
                f'#{field_id}',
                f'select[id="{field_id}"]',
                f'select[name="{field_id}"]',
                f'[role="combobox"][id="{field_id}"]',
                f'[data-qa="{field_id}"]'
            ]
            
            for selector in selectors:
                try:
                    element = await context.wait_for_selector(selector, timeout=5000)
                    if element:
                        break
                except:
                    continue
            
            if not element:
                self.logger.error(f"Could not find dropdown field: {field_id}")
                return False
            
            # Scroll to element
            await element.scroll_into_view_if_needed()
            await self._smart_wait(100)
            
            # Check if it's a standard HTML select
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
            
            if tag_name == 'select':
                # Standard HTML select
                try:
                    await element.select_option(label=value)
                    return True
                except:
                    # Try by value
                    try:
                        await element.select_option(value=value.lower().replace(' ', '_'))
                        return True
                    except:
                        self.logger.warning(f"Could not select option '{value}' in select {field_id}")
                        return False
            else:
                # Custom dropdown (combobox) - fallback method
                try:
                    # Click to open dropdown
                    await element.click()
                    await self._smart_wait(300)
                    
                    # Look for option with matching text
                    option_selectors = [
                        f'[role="option"]:has-text("{value}")',
                        f'[role="listbox"] [role="option"]:has-text("{value}")',
                        f'li:has-text("{value}")',
                        f'.option:has-text("{value}")',
                        f'[data-value*="{value.lower()}"]'
                    ]
                    
                    option_found = False
                    for option_selector in option_selectors:
                        try:
                            option = await context.wait_for_selector(option_selector, timeout=3000)
                            if option:
                                await option.click()
                                option_found = True
                                break
                        except:
                            continue
                    
                    if not option_found:
                        # Try typing the value directly
                        await element.fill(value)
                        await self._smart_wait(200)
                        await context.keyboard.press('Enter')
                    
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Error with custom dropdown {field_id}: {e}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error filling dropdown field {field_id}: {e}")
            return False
    
    async def _fill_file_field(self, page: Page, field_id: str, file_path: str) -> bool:
        """Fill file upload fields using the improved Greenhouse pattern."""
        try:
            if not file_path or not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return False
            
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Get field label from the JSON data
            field_label = self._get_field_label_by_id(field_id)
            
            # Method 1: Try by group label and "Attach" button (Greenhouse pattern)
            if field_label:
                try:
                    # Look for the group with the field label (e.g., "Resume/CV*")
                    group = context.get_by_role('group', name=field_label).first
                    if not group:
                        # Try without asterisk
                        clean_label = field_label.replace('*', '').strip()
                        group = context.get_by_role('group', name=clean_label).first
                    
                    if group:
                        # Find the "Attach" button within this group
                        attach_button = group.get_by_role('button', name='Attach').first
                        await attach_button.scroll_into_view_if_needed()
                        await self._smart_wait(100)
                        
                        # Click the attach button to open file chooser
                        async with page.expect_file_chooser() as fc_info:
                            await attach_button.click()
                        file_chooser = await fc_info.value
                        
                        # Set the file
                        await file_chooser.set_files(file_path)
                        await self._smart_wait(500)  # Wait for upload to process
                        
                        self.logger.info(f"Uploaded file using group method: {os.path.basename(file_path)}")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Group method failed for {field_id}: {e}")
            
            # Method 2: Try to find file inputs more broadly
            try:
                # Try multiple selectors for file input - more comprehensive search
                selectors = [
                    f'#{field_id}',
                    f'input[type="file"][id="{field_id}"]',
                    f'input[type="file"][name="{field_id}"]',
                    f'[data-qa="{field_id}"] input[type="file"]',
                    f'[data-testid="{field_id}"] input[type="file"]',
                    # Generic file upload patterns
                    'input[type="file"]'
                ]
                
                element = None
                for selector in selectors:
                    try:
                        # File inputs are often hidden, so use query_selector_all
                        elements = await context.query_selector_all(selector)
                        for elem in elements:
                            # Check if this might be the right file input
                            elem_id = await elem.get_attribute('id') or ''
                            elem_name = await elem.get_attribute('name') or ''
                            elem_aria = await elem.get_attribute('aria-label') or ''
                            
                            # If we're looking for a specific field_id, try to match it
                            if field_id in ['resume_cv', 'resume', 'cv']:
                                if any(keyword in (elem_id + elem_name + elem_aria).lower() 
                                      for keyword in ['resume', 'cv']):
                                    element = elem
                                    self.logger.info(f"Found resume file input via {selector}")
                                    break
                            elif field_id in ['cover_letter', 'cover']:
                                if any(keyword in (elem_id + elem_name + elem_aria).lower() 
                                      for keyword in ['cover', 'letter']):
                                    element = elem
                                    self.logger.info(f"Found cover letter file input via {selector}")
                                    break
                            elif elem_id == field_id or elem_name == field_id:
                                element = elem
                                self.logger.info(f"Found file input by exact match via {selector}")
                                break
                        
                        if element:
                            break
                            
                    except Exception as e:
                        self.logger.debug(f"Error with selector {selector}: {e}")
                        continue
                
                # If still not found, try the first available file input as fallback
                if not element:
                    try:
                        all_file_inputs = await context.query_selector_all('input[type="file"]')
                        if all_file_inputs:
                            element = all_file_inputs[0]
                            self.logger.warning(f"Using first available file input as fallback for {field_id}")
                    except:
                        pass
                
                if element:
                    # Upload file using the traditional method
                    await element.set_input_files(file_path)
                    await self._smart_wait(500)  # Wait for upload to process
                    
                    self.logger.info(f"Uploaded file using traditional method: {os.path.basename(file_path)}")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Traditional file upload failed: {e}")
            
            self.logger.error(f"Could not find file field: {field_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error filling file field {field_id}: {e}")
            return False
    
    def _get_field_label_by_id(self, field_id: str) -> Optional[str]:
        """Get the field label from form data by field ID."""
        try:
            for field in self.form_data.get('user_input_template', []):
                if field.get('id') == field_id:
                    return field.get('question', '')
            return None
        except:
            return None
    
    async def _fill_textarea_field(self, page: Page, field_id: str, value: str) -> bool:
        """Fill textarea fields."""
        try:
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Try multiple selectors for textarea
            selectors = [
                f'#{field_id}',
                f'textarea[id="{field_id}"]',
                f'textarea[name="{field_id}"]',
                f'[data-qa="{field_id}"]'
            ]
            
            element = None
            for selector in selectors:
                try:
                    element = await context.wait_for_selector(selector, timeout=5000)
                    if element:
                        break
                except:
                    continue
            
            if not element:
                self.logger.error(f"Could not find textarea field: {field_id}")
                return False
            
            # Scroll to element
            await element.scroll_into_view_if_needed()
            await self._smart_wait(100)
            
            # Fill textarea
            await element.click()
            await element.fill('')  # Clear first
            await element.fill(value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling textarea field {field_id}: {e}")
            return False
    
    async def _dismiss_overlays(self):
        """Dismiss cookie banners and modal overlays."""
        try:
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Common cookie banner and overlay selectors
            dismiss_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("Accept Cookies")',
                'button:has-text("Dismiss")',
                'button:has-text("OK")',
                'button:has-text("Continue")',
                '[aria-label="close"]',
                '.cookie-banner button',
                '.modal-close'
            ]
            
            for selector in dismiss_selectors:
                try:
                    elements = await context.query_selector_all(selector)
                    for element in elements:
                        try:
                            # Check if element is visible
                            box = await element.bounding_box()
                            if box and box['width'] > 0 and box['height'] > 0:
                                await element.click(timeout=2000)
                                await self._smart_wait(300)
                                self.logger.info(f"Dismissed overlay with: {selector}")
                                return  # Exit after first successful dismissal
                        except:
                            continue
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error dismissing overlays: {e}")
    
    async def _smart_wait(self, milliseconds: int):
        """Smart wait function."""
        await asyncio.sleep(milliseconds / 1000)
    
    async def _wait_for_user_action(self):
        """Wait for user to manually review and submit the form - IMPROVED VERSION."""
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
                await asyncio.sleep(2)  # Check every 2 seconds
                
                try:
                    current_url = self.page.url
                    
                    # Only consider it a submission if URL changes to a confirmation page
                    # (not just a different page of the form)
                    if current_url != initial_url:
                        # Check if it's a thank you / confirmation page
                        if any(keyword in current_url.lower() for keyword in ['thank', 'confirm', 'success', 'complete']):
                            self.logger.info("🎉 Form submission detected! You can close the browser.")
                            await self._smart_wait(5000)  # Give user time to see confirmation
                            break
                        else:
                            # URL changed but might be multi-page form - don't close yet
                            self.logger.debug(f"URL changed to {current_url} but not a confirmation page")
                            initial_url = current_url  # Update to new URL
                    
                    # Check for success messages
                    success_text = await self.page.evaluate('''() => {
                        const text = document.body.innerText.toLowerCase();
                        return text.includes('thank you') || 
                               text.includes('application submitted') || 
                               text.includes('successfully submitted') ||
                               text.includes('application received') ||
                               text.includes('submission successful');
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
    
    async def _wait_for_user_submission(self):
        """Deprecated: Use _wait_for_user_action instead."""
        await self._wait_for_user_action()
    
    async def _cleanup_browser(self):
        """Properly cleanup browser resources to prevent Windows pipe exceptions."""
        try:
            if self.browser:
                # Close all contexts and pages first
                if self.context:
                    await self.context.close()
                
                # Then close the browser
                await self.browser.close()
                
                # Small delay to allow cleanup
                await asyncio.sleep(0.5)
                
                self.logger.info("Browser resources cleaned up successfully")
        except Exception as e:
            self.logger.debug(f"Error during browser cleanup: {e}")
        finally:
            # Reset references
            self.page = None
            self.context = None
            self.browser = None

    def _is_location_field(self, field_id: str, field_question: str) -> bool:
        """Check if a field is location-related based on ID and question text."""
        try:
            # Convert to lowercase for comparison
            field_text = (field_id + ' ' + field_question).lower()
            
            # Check for location-related keywords
            for keyword in self.geolocation_config['location_keywords']:
                if keyword in field_text:
                    return True
            
            return False
        except:
            return False
    
    async def _handle_locate_me_button(self, context, field_id: str, field_question: str) -> bool:
        """Try to find and click 'Locate me' button for location fields."""
        try:
            if not self.geolocation_config['enabled']:
                return False
            
            self.logger.info(f"🔍 Looking for 'Locate me' button for field: {field_question}")
            
            # Common selectors for "Locate me" buttons - broader search for post-fill
            locate_selectors = [
                # Text-based selectors
                'button:has-text("Locate me")',
                'button:has-text("Use my location")',
                'button:has-text("Current location")',
                'button:has-text("Detect location")',
                'a:has-text("Locate me")',
                'a:has-text("Use my location")',
                'a:has-text("Current location")',
                '[aria-label*="locate"]',
                '[aria-label*="location"]',
                
                # Class and ID based selectors
                '.locate-me',
                '.location-btn', 
                '.geo-locate',
                '.use-location',
                '.detect-location',
                '#locate-me',
                '#location-btn',
                
                # Icon-based selectors (GPS/location icons)
                'button[class*="location"]',
                'button[class*="gps"]',
                'button[title*="location"]',
                'button[title*="locate"]',
                'button[title*="gps"]',
                
                # Additional patterns for post-fill search
                '[data-testid*="location"]',
                '[data-qa*="location"]',
                'span:has-text("Locate me")',
                'div:has-text("Use my location")'
            ]
            
            # Try to find and click locate button
            for selector in locate_selectors:
                try:
                    elements = await context.query_selector_all(selector)
                    for element in elements:
                        # Check if element is visible and interactable
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            # Scroll to element and make it visible
                            await element.scroll_into_view_if_needed()
                            await self._smart_wait(300)
                            
                            self.logger.info(f"📍 Found 'Locate me' button, clicking...")
                            await element.click()
                            
                            # Wait for geolocation to process
                            await self._smart_wait(self.geolocation_config['timeout'])
                            
                            self.logger.info("✅ Successfully clicked 'Locate me' button")
                            return True
                            
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            self.logger.debug(f"❌ No 'Locate me' button found for field: {field_question}")
            return False
            
        except Exception as e:
            self.logger.debug(f"Error in _handle_locate_me_button: {e}")
            return False

    async def _check_location_auto_populated(self, context, field_id: str) -> bool:
        """Check if location field was auto-populated after clicking 'Locate me'."""
        try:
            # Try to find the field and check if it has a value
            selectors = [
                f'#{field_id}',
                f'select[id="{field_id}"]',
                f'input[id="{field_id}"]',
                f'[role="combobox"][id="{field_id}"]'
            ]
            
            for selector in selectors:
                try:
                    element = await context.query_selector(selector)
                    if element:
                        # Check for value in different ways based on element type
                        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                        
                        if tag_name == 'select':
                            selected_value = await element.evaluate('el => el.value')
                            selected_text = await element.evaluate('el => el.options[el.selectedIndex]?.text || ""')
                            if selected_value and selected_value != '' and selected_text and selected_text.strip() != '':
                                self.logger.info(f"Location auto-populated: {selected_text}")
                                return True
                        elif tag_name == 'input':
                            input_value = await element.input_value()
                            if input_value and input_value.strip() != '':
                                self.logger.info(f"Location auto-populated: {input_value}")
                                return True
                        else:
                            # For custom dropdowns, check text content
                            text_content = await element.text_content()
                            if text_content and text_content.strip() != '' and 'select' not in text_content.lower():
                                self.logger.info(f"Location auto-populated: {text_content}")
                                return True
                                
                except Exception as e:
                    self.logger.debug(f"Error checking auto-population with {selector}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error in _check_location_auto_populated: {e}")
            return False

    async def _handle_post_fill_geolocation(self, form_data: Dict[str, Any]) -> bool:
        """Handle 'Locate me' buttons after all form fields are filled."""
        try:
            if not self.geolocation_config['enabled']:
                return False
            
            self.logger.info("\n🌍 Starting post-fill geolocation process...")
            
            # Get the appropriate context (page or iframe frame)
            context = self._get_form_context()
            
            # Method 1: Field-specific approach - find location fields and their locate buttons
            location_fields = []
            for field_data in form_data.get('user_input_template', []):
                field_id = field_data['id']
                field_question = field_data['question']
                
                if self._is_location_field(field_id, field_question):
                    location_fields.append({
                        'id': field_id,
                        'question': field_question,
                        'type': field_data['type']
                    })
            
            locate_buttons_found = 0
            
            if location_fields:
                self.logger.info(f"📋 Found {len(location_fields)} location field(s): {[f['question'] for f in location_fields]}")
                
                # Try to find "Locate me" buttons for specific location fields
                for field in location_fields:
                    self.logger.info(f"📍 Processing location field: {field['question']}")
                    
                    locate_success = await self._handle_locate_me_button(context, field['id'], field['question'])
                    
                    if locate_success:
                        locate_buttons_found += 1
                        # Wait for geolocation to process
                        await self._smart_wait(2000)
                        
                        # Check if location was auto-populated
                        if await self._check_location_auto_populated(context, field['id']):
                            self.logger.info(f"✅ Location auto-populated for: {field['question']}")
                        else:
                            self.logger.info(f"⚠️ Location not auto-populated for: {field['question']}")
                    
                    # Small delay between fields
                    await self._smart_wait(500)
            
            # Method 2: General approach - search for any locate buttons on the page
            self.logger.info("\n🔍 Performing comprehensive search for all 'Locate me' buttons...")
            general_buttons_found = await self._find_and_click_all_locate_buttons(context)
            
            total_buttons = locate_buttons_found + general_buttons_found
            
            if total_buttons > 0:
                self.logger.info(f"\n🎯 Geolocation process completed!")
                self.logger.info(f"   • Field-specific buttons: {locate_buttons_found}")
                self.logger.info(f"   • General search buttons: {general_buttons_found}")
                self.logger.info(f"   • Total buttons clicked: {total_buttons}")
                self.logger.info("⏳ Waiting for all location updates to complete...")
                await self._smart_wait(3000)  # Extra wait for all locations to update
                return True
            else:
                self.logger.info("❌ No 'Locate me' buttons found on this form")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in post-fill geolocation: {e}")
            return False

    async def _find_and_click_all_locate_buttons(self, context) -> int:
        """Find and click all 'Locate me' buttons on the page (general search)."""
        try:
            self.logger.info("🌐 Performing general search for all 'Locate me' buttons...")
            
            # Comprehensive selectors for any "Locate me" button on the page
            general_locate_selectors = [
                # Text-based - most common patterns
                'button:has-text("Locate me")',
                'button:has-text("Use my location")',
                'button:has-text("Current location")',
                'button:has-text("Detect location")',
                'button:has-text("Auto-detect")',
                'a:has-text("Locate me")',
                'a:has-text("Use my location")',
                'span:has-text("Locate me")',
                
                # Class/ID patterns
                '.locate-me',
                '.location-btn',
                '.geo-locate',
                '.use-location',
                '.detect-location',
                '.auto-location',
                '#locate-me',
                '#location-btn',
                
                # Data attributes
                '[data-testid*="locate"]',
                '[data-testid*="location"]',
                '[data-qa*="locate"]',
                '[data-qa*="location"]',
                
                # ARIA labels
                '[aria-label*="locate"]',
                '[aria-label*="location"]',
                '[aria-label*="detect location"]',
                
                # Title attributes
                '[title*="locate"]',
                '[title*="location"]',
                '[title*="gps"]',
                
                # Icon-based (GPS symbols)
                'button[class*="gps"]',
                'button[class*="location"]'
            ]
            
            buttons_clicked = 0
            clicked_elements = set()  # To avoid clicking the same button twice
            
            for selector in general_locate_selectors:
                try:
                    elements = await context.query_selector_all(selector)
                    for element in elements:
                        # Check if we already clicked this element
                        element_handle = str(element)
                        if element_handle in clicked_elements:
                            continue
                        
                        # Check if element is visible and interactable
                        box = await element.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            # Get element text to confirm it's a locate button
                            text_content = await element.text_content() or ""
                            inner_text = await element.inner_text() or ""
                            combined_text = (text_content + " " + inner_text).lower()
                            
                            # Verify it's actually a locate button
                            locate_keywords = ['locate', 'location', 'gps', 'detect', 'auto-detect', 'current']
                            if any(keyword in combined_text for keyword in locate_keywords):
                                try:
                                    await element.scroll_into_view_if_needed()
                                    await self._smart_wait(300)
                                    
                                    self.logger.info(f"📍 Clicking locate button: '{combined_text.strip()}'")
                                    await element.click()
                                    
                                    clicked_elements.add(element_handle)
                                    buttons_clicked += 1
                                    
                                    # Wait between clicks
                                    await self._smart_wait(1000)
                                    
                                except Exception as e:
                                    self.logger.debug(f"Error clicking locate button: {e}")
                                    continue
                            
                except Exception as e:
                    self.logger.debug(f"Error with general selector {selector}: {e}")
                    continue
            
            if buttons_clicked > 0:
                self.logger.info(f"🎯 Clicked {buttons_clicked} 'Locate me' button(s) in total")
                # Wait for all geolocation processes to complete
                await self._smart_wait(3000)
            else:
                self.logger.info("❌ No 'Locate me' buttons found on the page")
            
            return buttons_clicked
            
        except Exception as e:
            self.logger.error(f"Error in general locate button search: {e}")
            return 0

    def _get_real_location(self) -> Dict[str, Any]:
        """Get real location coordinates using IP-based geolocation with multiple fallback options."""
        try:
            if not GEOCODER_AVAILABLE:
                self.logger.warning("❌ Geocoder library not available, using San Francisco as fallback")
                return self._get_fallback_coordinates()
            
            self.logger.info("🌍 Detecting your real location...")
            
            # Method 1: Try geocoder.ip() for general IP location
            try:
                g = geocoder.ip('me')
                if g.ok and g.latlng:
                    coordinates = {
                        'latitude': g.latlng[0],
                        'longitude': g.latlng[1],
                        'accuracy': 10000  # IP-based is less precise (10km radius)
                    }
                    self.logger.info(f"✅ Location detected via IP: {g.city}, {g.country} ({coordinates['latitude']}, {coordinates['longitude']})")
                    return coordinates
            except Exception as e:
                self.logger.debug(f"geocoder.ip() failed: {e}")
            
            # Method 2: Try specific IP geolocation services
            services = ['ipapi', 'freegeoip', 'ipinfo']
            for service in services:
                try:
                    g = getattr(geocoder, service)('me')
                    if g.ok and g.latlng:
                        coordinates = {
                            'latitude': g.latlng[0],
                            'longitude': g.latlng[1],
                            'accuracy': 10000
                        }
                        self.logger.info(f"✅ Location detected via {service}: {g.city}, {g.country} ({coordinates['latitude']}, {coordinates['longitude']})")
                        return coordinates
                except Exception as e:
                    self.logger.debug(f"geocoder.{service}() failed: {e}")
                    continue
            
            # Method 3: Manual IP lookup fallback
            try:
                import requests
                response = requests.get('http://ip-api.com/json/', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        coordinates = {
                            'latitude': data['lat'],
                            'longitude': data['lon'],
                            'accuracy': 10000
                        }
                        self.logger.info(f"✅ Location detected via ip-api.com: {data.get('city')}, {data.get('country')} ({coordinates['latitude']}, {coordinates['longitude']})")
                        return coordinates
            except Exception as e:
                self.logger.debug(f"Manual IP lookup failed: {e}")
            
            self.logger.warning("❌ Could not detect real location, using San Francisco as fallback")
            
        except Exception as e:
            self.logger.warning(f"Error detecting location: {e}")
        
        # Fallback to San Francisco coordinates
        return self._get_fallback_coordinates()
    
    def _get_fallback_coordinates(self) -> Dict[str, Any]:
        """Get fallback San Francisco coordinates."""
        fallback_coordinates = {
            'latitude': 37.7749,  # San Francisco coordinates
            'longitude': -122.4194,
            'accuracy': 0
        }
        self.logger.info(f"📍 Using fallback coordinates: San Francisco ({fallback_coordinates['latitude']}, {fallback_coordinates['longitude']})")
        return fallback_coordinates

async def main():
    """Main function to run the form filler."""
    if len(sys.argv) != 2:
        print("Usage: python simple_form_filler.py <path_to_filled_json>")
        print("Example: python simple_form_filler.py test_filled_form.json")
        return
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        return
    
    filler = SimpleFormFiller()
    success = await filler.fill_form(json_file)
    
    if success:
        print("\n✅ Form filling completed successfully!")
    else:
        print("\n❌ Form filling failed. Check logs for details.")

def suppress_asyncio_warnings():
    """Suppress Windows asyncio pipe cleanup warnings."""
    import sys
    if sys.platform == "win32":
        # Redirect stderr temporarily to suppress pipe warnings
        import io
        import contextlib
        
        @contextlib.contextmanager
        def suppress_stderr():
            with open(os.devnull, "w") as devnull:
                old_stderr = sys.stderr
                sys.stderr = devnull
                try:
                    yield
                finally:
                    sys.stderr = old_stderr
        
        return suppress_stderr()
    else:
        return contextlib.nullcontext()

if __name__ == "__main__":
    try:
        # Suppress warnings for Windows
        if sys.platform == "win32":
            import contextlib
            # Temporarily suppress stderr during cleanup
            asyncio.run(main())
            # Give a moment for cleanup, then suppress any remaining warnings
            import time
            time.sleep(0.1)
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Program interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
