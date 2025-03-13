import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
                                     TimeoutException, 
                                     WebDriverException)
import time
import logging
import random
from config import config  # Changed from 'Config' to 'config'
from contextlib import contextmanager
from utils import LoggerSetup
import os
os.environ['WDM_LOG_LEVEL'] = '0'  # Suppress webdriver-manager logs
from selenium.webdriver.support.ui import Select
from utils import log_error  # Yeni import
import traceback
from datetime import datetime
from version import get_version_info

class PrezzoBot:
    def __init__(self):
        self.version_info = get_version_info()
        self.setup_logging()
        self.logger.info(f"Starting {self.version_info}")
        self.config = config  # Use the imported config instance
        self.setup_driver()
        self.load_data()
        self.running = True
        self.consecutive_errors = 0

    def setup_logging(self):
        self.logger = LoggerSetup.setup()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        
        # Browser optimization settings
        options.add_argument(f'--window-size={self.config.WINDOW_WIDTH},{self.config.WINDOW_HEIGHT}')
        options.add_argument(f'--user-agent={self.config.USER_AGENT}')
        
        # Performance and resource loading settings
        options.add_experimental_option('prefs', self.config.get_prefs())
        
        # Additional optimization arguments
        optimization_args = [
            '--disable-gpu',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',
            '--disable-extensions',
            '--disable-browser-side-navigation',
            '--disable-infobars',
            '--disable-web-security',
            '--disable-features=NetworkService',
            '--disable-features=VizDisplayCompositor',
        ]
        
        if self.config.BLOCK_RESOURCES:
            optimization_args.extend([
                '--block-new-web-contents',
                '--disable-downloads',
                '--disable-background-networking',
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-domain-reliability',
                '--disable-sync',
            ])
        
        if self.config.DISABLE_ANIMATIONS:
            optimization_args.extend([
                '--disable-threaded-animation',
                '--disable-threaded-scrolling',
                '--disable-composited-antialiasing',
            ])
        
        if self.config.FORCE_DARK_MODE:
            options.add_argument('--force-dark-mode')
        
        if self.config.REDUCED_MOTION:
            options.add_argument('--force-prefers-reduced-motion')
        
        for arg in optimization_args:
            options.add_argument(arg)
        
        if self.config.HEADLESS:
            options.add_argument('--headless')
        
        if self.config.USE_PROXY:
            proxy = random.choice(self.config.PROXY_LIST)
            options.add_argument(f'--proxy-server={proxy}')
        
        # Add options to suppress DevTools logging
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)
        self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
        self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
        self.wait = WebDriverWait(self.driver, 3)

        # Set viewport size
        self.driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': self.config.VIEWPORT_WIDTH,
            'height': self.config.VIEWPORT_HEIGHT,
            'deviceScaleFactor': 1,
            'mobile': False
        })
        
        # Inject CSS for performance
        self.driver.execute_script("""
            var style = document.createElement('style');
            style.innerHTML = `
                * { 
                    animation: none !important;
                    transition: none !important;
                }
                @media (prefers-reduced-motion: reduce) {
                    * {
                        animation: none !important;
                        transition: none !important;
                    }
                }
            `;
            document.head.appendChild(style);
        """)

    def load_data(self):
        try:
            self.data = pd.read_excel(self.config.EXCEL_FILE)
            self.logger.info(f"Loaded {len(self.data)} rows from excel")
        except Exception as e:
            self.logger.error(f"Failed to load excel file: {e}")
            raise

    @contextmanager
    def error_handling(self, operation):
        try:
            yield
        except (NoSuchElementException, TimeoutException) as e:
            error_details = {
                'operation': operation,
                'error_type': type(e).__name__,
                'element': getattr(e, 'msg', str(e)),
                'screenshot': self.take_error_screenshot()
            }
            log_error(
                self.logger,
                f"Error during {operation}",
                exc_info=e,
                details=error_details,
                stack=traceback.format_exc()
            )
            raise
        except Exception as e:
            error_details = {
                'operation': operation,
                'error_type': type(e).__name__,
                'message': str(e),
                'screenshot': self.take_error_screenshot()
            }
            log_error(
                self.logger,
                f"Unexpected error during {operation}",
                exc_info=e,
                details=error_details,
                stack=traceback.format_exc()
            )
            raise

    def take_error_screenshot(self):
        """Hata durumunda ekran görüntüsü al"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"error_{timestamp}.png"
            filepath = os.path.join('logs', filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except:
            return "Screenshot failed"

    def get_progress_percentage(self):
        """Get current progress from the progress bar"""
        try:
            # Birden fazla seçici dene
            selectors = [
                (By.ID, 'ProgressPercentage'),
                (By.CSS_SELECTOR, '#Progress'),
                (By.CSS_SELECTOR, '[aria-hidden="true"]#Progress'),
                (By.XPATH, "//div[@id='ProgressBarholder']//div[@id='Progress']")
            ]
            
            for by, selector in selectors:
                try:
                    element = self.driver.find_element(by, selector)
                    if element:
                        # Ya text veya style width değerinden yüzdeyi al
                        if element.text and '%' in element.text:
                            return int(element.text.replace('%', ''))
                        style = element.get_attribute('style')
                        if style and 'width:' in style:
                            width = style.split('width:')[1].split('%')[0].strip()
                            return int(float(width))
                except:
                    continue
            
            return 0
        except Exception as e:
            self.logger.debug(f"Could not get progress percentage: {e}")
            return 0

    def get_current_section(self):
        """Get current section based on progress percentage"""
        progress = self.get_progress_percentage()
        sections = {
            (0, 10): "Initial Navigation",
            (10, 20): "Visit Time",
            (20, 30): "Visit Details",
            (30, 40): "Previous Visits",
            (40, 50): "Overall Satisfaction",
            (50, 60): "Food Satisfaction",
            (60, 70): "Service Satisfaction",
            (70, 80): "Problem Section",
            (80, 90): "Return and Recommendations",
            (90, 100): "Final Details"
        }
        
        for (start, end), section_name in sections.items():
            if start <= progress < end:
                return section_name
        return "Unknown Section"

    def log_progress(self, action=""):
        """Log current progress and section"""
        try:
            progress = self.get_progress_percentage()
            section = self.get_current_section()
            self.logger.info(f"Progress: {progress}% - Section: {section} {action}")
        except Exception as e:
            self.logger.debug(f"Could not log progress: {e}")

    def is_browser_alive(self):
        """Tarayıcının hala açık olup olmadığını kontrol et"""
        try:
            # Basit bir JavaScript komutu çalıştırmayı dene
            self.driver.execute_script("return true;")
            return True
        except Exception:
            return False

    def wait_for_page_load(self):
        """Optimize edilmiş sayfa yükleme beklemesi"""
        try:
            # Sayfa yüklenme kontrolü
            self.wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(0.3)  # Reduced from 1 to 0.3 seconds
            
            if not self.is_browser_alive():
                self.logger.error("Browser window was closed")
                self.running = False
                raise WebDriverException("Browser window was closed by user")
                
            self.log_progress("Page loaded")
            self.consecutive_errors = 0
            
        except Exception as e:
            self.consecutive_errors += 1
            self.logger.warning(f"Page load wait warning: {e}")
            if self.consecutive_errors >= self.config.MAX_CONSECUTIVE_ERRORS:
                self.running = False
                raise Exception("Too many consecutive errors, stopping execution")

    def safe_click(self, by, value, alternate_by=None, alternate_value=None):
        """Optimized clicking with minimal waits"""
        try:
            element = None
            try:
                if (by == By.ID and value.startswith('FNSR')) or (alternate_by == By.ID and alternate_value.startswith('FNSR')):
                    element = self.find_dynamic_element('FNSR')
                else:
                    element = self.wait.until(EC.element_to_be_clickable((by, value)))
            except:
                if alternate_by and alternate_value:
                    element = self.wait.until(EC.element_to_be_clickable((alternate_by, alternate_value)))
                
            if element:
                if not self.is_browser_alive():
                    self.running = False
                    raise WebDriverException("Browser window was closed")
                    
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant'});", element)
                element.click()
                time.sleep(0.1)  # Minimal wait after click
                
                self.log_progress(f"Clicked: {value}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to click element {value}: {str(e)}")
            raise

    def smart_click(self, by, value):
        return self.safe_click(by, value)

    def smart_send_keys(self, by, value, text, max_attempts=3):
        """Gelişmiş text giriş metodu"""
        attempts = 0
        last_error = None
        
        while attempts < max_attempts:
            try:
                # Sayfanın tamamen yüklenmesini bekle
                self.wait_for_page_load()
                
                # Element'i bul (daha uzun timeout ile)
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((by, value))
                )
                
                # JavaScript ile scroll ve focus
                self.driver.execute_script("""
                    arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});
                    arguments[0].focus();
                    arguments[0].click();
                """, element)
                
                # Clear ve yazma öncesi bekle
                time.sleep(1)
                element.clear()
                
                # Değeri ayarla
                element.send_keys(str(text))
                
                # Event'leri tetikle
                self.driver.execute_script("""
                    var el = arguments[0];
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, element)
                
                # Değerin doğru ayarlandığını kontrol et
                actual_value = element.get_attribute('value')
                if actual_value == str(text):
                    self.logger.debug(f"Successfully sent keys to {value}: {text}")
                    return True
                    
                attempts += 1
                time.sleep(1)
                
            except Exception as e:
                last_error = e
                self.logger.debug(f"Attempt {attempts + 1} failed: {e}")
                attempts += 1
                time.sleep(1)
                
        # Son hata durumu için detaylı log
        error_details = {
            'element': value,
            'text': text,
            'attempts': attempts,
            'last_error': str(last_error)
        }
        log_error(
            self.logger,
            f"Failed to send keys to {value} after {max_attempts} attempts",
            exc_info=last_error,
            details=error_details,
            stack=traceback.format_exc()
        )
        raise TimeoutException(f"Failed to send keys to {value} after {max_attempts} attempts")

    def find_dynamic_element(self, pattern, attribute_type="id"):
        """Dinamik ID'li elementleri bulmak için yardımcı fonksiyon"""
        try:
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(@{attribute_type}, '{pattern}')]")
            if elements:
                return elements[0]
            return None
        except Exception as e:
            self.logger.debug(f"Element not found with pattern {pattern}: {e}")
            return None

    def find_and_click_option(self, option_number, section_pattern):
        """Dinamik ID'li seçenekleri bulmak ve tıklamak için"""
        try:
            # Section ID'sini bul
            section = self.wait.until(lambda d: self.find_dynamic_element(section_pattern))
            if not section:
                self.logger.debug(f"Section not found with pattern: {section_pattern}")
                return False

            # Option'ı bul ve tıkla
            try:
                option = section.find_element(By.CSS_SELECTOR, f"td.Opt{option_number}.inputtyperbloption")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                time.sleep(0.5)
                option.click()
                time.sleep(1)  # Tıklama sonrası bekle
                return True
            except Exception as e:
                self.logger.debug(f"Failed to click option {option_number}: {e}")
                return False
        except Exception as e:
            self.logger.debug(f"Error in find_and_click_option: {e}")
            return False

    def wait_and_click_next(self):
        """Optimized NextButton click"""
        try:
            next_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'NextButton')))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant'});", next_button)
            next_button.click()
            time.sleep(0.2)  # Reduced from 1 to 0.2 seconds
            return True
        except Exception as e:
            self.logger.error(f"Failed to click NextButton: {e}")
            return False

    def click_radio_option(self, option_value, name):
        """Radio butonları için özel tıklama metodu"""
        try:
            # Önce div'i bul
            option_div = self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    f"div[class='Opt{option_value} rbloption']"
                ))
            )
            
            # Radio input'u bul
            radio_input = option_div.find_element(
                By.CSS_SELECTOR, 
                f"input[name='{name}'][value='{option_value}']"
            )
            
            # JavaScript ile tıkla
            self.driver.execute_script(
                "arguments[0].click(); arguments[0].checked = true;", 
                radio_input
            )
            
            # Label'a da tıkla (extra güvenlik için)
            label = option_div.find_element(
                By.CSS_SELECTOR, 
                f"label[for='{name}.{option_value}']"
            )
            self.driver.execute_script("arguments[0].click();", label)
            
            time.sleep(1)  # Tıklama sonrası bekle
            return True
        except Exception as e:
            self.logger.debug(f"Failed to click radio option {option_value}: {e}")
            return False

    def click_dine_option(self, is_dine_in=True):
        """Özel olarak dine-in/dine-at-home seçimi için metod"""
        try:
            # Fieldset içindeki radio butonlarını bul
            fieldset = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "FNSITEM"))
            )
            
            # Doğru div'i seç
            option_class = "Opt1" if is_dine_in else "Opt2"
            option_div = fieldset.find_element(By.CLASS_NAME, option_class)
            
            # Önce JavaScript ile radio butonu seç
            radio_input = option_div.find_element(By.TAG_NAME, "input")
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, radio_input)
            
            # Sonra label'a tıkla
            label = option_div.find_element(By.TAG_NAME, "label")
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].dispatchEvent(new Event('click', { bubbles: true }));
            """, label)
            
            time.sleep(1)
            
            # Seçimin yapıldığını kontrol et
            if not radio_input.is_selected():
                self.logger.warning("Radio button was not selected, trying alternative method")
                option_div.click()
                time.sleep(0.5)
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to click dine option: {e}")
            return False

    def click_dine_option_v2(self, is_dine_in=True):
        """Alternatif dine-in seçim metodu"""
        try:
            # Birden fazla seçici stratejisi
            selectors = [
                # Direkt radio input
                (By.CSS_SELECTOR, f"input[name='R000004'][value='{1 if is_dine_in else 2}']"),
                # Div + radio input
                (By.CSS_SELECTOR, f".Opt{1 if is_dine_in else 2}.rbloption input"),
                # Label üzerinden
                (By.XPATH, f"//label[contains(text(), '{'Dine-in' if is_dine_in else 'Dine at home'}')]"),
                # Fieldset içinde arama
                (By.XPATH, f"//fieldset[@id='FNSR000004']//div[contains(@class, 'Opt{1 if is_dine_in else 2}')]")
            ]

            for by, selector in selectors:
                try:
                    # Her seçiciyi dene
                    element = self.wait.until(EC.presence_of_element_located((by, selector)))
                    
                    # Element görünür ve tıklanabilir olana kadar bekle
                    self.wait.until(EC.visibility_of(element))
                    self.wait.until(EC.element_to_be_clickable((by, selector)))
                    
                    # Önce JavaScript ile seçmeyi dene
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView(true);
                        arguments[0].click();
                        if (arguments[0].type === 'radio') {
                            arguments[0].checked = true;
                            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """, element)
                    
                    time.sleep(1)
                    
                    # Seçimin başarılı olup olmadığını kontrol et
                    radio = self.driver.find_element(By.CSS_SELECTOR, f"input[name='R000004'][value='{1 if is_dine_in else 2}']")
                    if radio.is_selected():
                        self.logger.debug(f"Successfully selected dine option using selector: {selector}")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Failed with selector {selector}: {e}")
                    continue
                    
            raise Exception("No selector worked for dine option")
            
        except Exception as e:
            self.logger.error(f"Failed to click dine option v2: {e}")
            return False

    def click_dine_option_v3(self, is_dine_in=True):
        """Yeni dine-in seçim metodu"""
        try:
            # Önce fieldset'i bul
            fieldset = self.wait.until(
                EC.presence_of_element_located((By.ID, "FNSR000004"))
            )
            
            # Seçilecek radio input ID'si
            input_id = "R000004.1" if is_dine_in else "R000004.2"
            
            try:
                # Radio input elementini bul
                radio = fieldset.find_element(By.ID, input_id)
                
                # Önce görünür olmasını bekle
                self.driver.execute_script("arguments[0].style.display = 'block';", radio)
                time.sleep(0.5)
                
                # Radio butonu seç
                self.driver.execute_script("""
                    arguments[0].click();
                    arguments[0].checked = true;
                    arguments[0].dispatchEvent(new Event('change'));
                """, radio)
                
                # Label'ı da tıkla
                label = fieldset.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                self.driver.execute_script("""
                    arguments[0].click();
                    arguments[0].dispatchEvent(new Event('click'));
                """, label)
                
                # rbloption div'ini de tıkla
                option_div = label.find_element(By.XPATH, "..")
                option_div.click()
                
                time.sleep(1)
                
                # Seçildiğini kontrol et
                if radio.get_attribute('checked'):
                    self.logger.debug(f"Successfully selected {input_id}")
                    return True
                    
                return False
                
            except Exception as e:
                self.logger.debug(f"Failed to interact with radio {input_id}: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to find fieldset: {e}")
            return False

    def click_yes_no_option(self, question_id, select_yes=True):
        """Optimized Yes/No selection"""
        try:
            row = self.wait.until(
                EC.presence_of_element_located((By.ID, f"FNSR{question_id}"))
            )
            
            option_class = "Opt1" if select_yes else "Opt2"
            option_cell = row.find_element(By.CLASS_NAME, option_class)
            radio_input = option_cell.find_element(By.TAG_NAME, "input")
            
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, radio_input)
            
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].setAttribute('aria-checked', 'true');
            """, option_cell)
            
            time.sleep(0.2)  # Reduced from 0.5 to 0.2 seconds
            
            if radio_input.get_attribute('checked') or option_cell.get_attribute('aria-checked') == 'true':
                self.logger.debug(f"Successfully selected {option_class} for question {question_id}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to click yes/no option: {e}")
            return False

    def click_satisfaction_rating(self, rate_value):
        """Özel olarak satisfaction rating seçimi için metod"""
        try:
            # String'e çevir ve kontrol et
            rate_str = str(rate_value)
            if rate_str not in ['1', '2', '3', '4', '5']:
                raise ValueError(f"Invalid rating value: {rate_value}")

            # Önce row elementi bul
            row = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.InputRow"))
            )

            # Rating için td elementini bul (index tersten: 5=1, 4=2, 3=3, 2=4, 1=5)
            td_index = 6 - int(rate_str)  # 5 için 1, 1 için 5
            td_element = row.find_element(By.CSS_SELECTOR, f"td:nth-child({td_index})")

            # Input elementini bul
            radio_input = td_element.find_element(By.TAG_NAME, "input")
            
            # JavaScript ile tıkla
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, radio_input)
            
            time.sleep(0.2)
            return True

        except Exception as e:
            self.logger.error(f"Failed to click satisfaction rating: {e}")
            return False

    def click_satisfaction_rating_v2(self, rate_value):
        """Yeni satisfaction rating seçim metodu"""
        try:
            # String'e çevir ve kontrol et
            rate_str = str(rate_value)
            if rate_str not in ['1', '2', '3', '4', '5']:
                raise ValueError(f"Invalid rating value: {rate_value}")

            # FNSR000008 row'unu bul
            row = self.wait.until(
                EC.presence_of_element_located((By.ID, "FNSR000008"))
            )
            
            # Opt sınıfını kullanarak hücreyi bul
            cell = row.find_element(By.CLASS_NAME, f"Opt{rate_str}")
            
            # Radio input'u bul
            radio_input = cell.find_element(By.ID, f"R000008.{rate_str}")
            
            # Görünür yap
            self.driver.execute_script("arguments[0].style.display = 'block';", radio_input)
            
            # Radio butonu seç ve event'leri tetikle
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].checked = true;
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, radio_input)
            
            # Hücreyi de tıkla ve aria-checked güncelle
            self.driver.execute_script("""
                arguments[0].click();
                arguments[0].setAttribute('aria-checked', 'true');
                arguments[0].dispatchEvent(new Event('click', { bubbles: true }));
            """, cell)
            
            time.sleep(0.2)
            
            # Seçimin başarılı olup olmadığını kontrol et
            if radio_input.get_attribute('checked') or cell.get_attribute('aria-checked') == 'true':
                self.logger.debug(f"Successfully selected rating {rate_str}")
                return True
                
            return False

        except Exception as e:
            self.logger.error(f"Failed to click satisfaction rating v2: {e}")
            return False

    def select_satisfaction_table_ratings(self, rate_value):
        """Tüm satisfaction rating sorularını doldur"""
        try:
            # String'e çevir ve kontrol et
            rate_str = str(rate_value)
            if rate_str not in ['1', '2', '3', '4', '5', '9']:
                raise ValueError(f"Invalid rating value: {rate_value}")
                
            # Tablodaki tüm soruları bul
            rows = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.InputRowOdd, tr.InputRowEven"))
            )
            
            success_count = 0
            
            for row in rows:
                try:
                    # ID'yi al
                    question_id = row.get_attribute('id').replace('FNSR', '')
                    
                    # N/A seçeneği varsa kontrol et (class=Opt9)
                    has_na = len(row.find_elements(By.CSS_SELECTOR, "td.Opt9")) > 0
                    if has_na and rate_str == '5':  # 5 yerine N/A kullan
                        rate_to_use = '9'
                    else:
                        rate_to_use = rate_str

                    # Hücreyi ve radio butonu CSS Selector ile bul
                    cell = row.find_element(By.CSS_SELECTOR, f"td.Opt{rate_to_use}.inputtyperbloption")
                    radio = cell.find_element(By.CSS_SELECTOR, f"input[id$='.{rate_to_use}']")
                    
                    # JavaScript ile görünür yap ve seç
                    self.driver.execute_script("""
                        var radio = arguments[0];
                        var cell = arguments[1];
                        
                        // Radio butonu görünür yap
                        radio.style.display = 'block';
                        radio.scrollIntoView({behavior: 'instant', block: 'center'});
                        
                        // Radio butonu seç
                        radio.click();
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Hücreyi de güncelle
                        cell.setAttribute('aria-checked', 'true');
                        cell.click();
                    """, radio, cell)
                    
                    time.sleep(0.2)
                    
                    # Seçimin başarılı olup olmadığını kontrol et
                    if radio.is_selected() or cell.get_attribute('aria-checked') == 'true':
                        success_count += 1
                    
                except Exception as e:
                    self.logger.debug(f"Failed to set rating for question {question_id}: {e}")
                    continue
                    
            if success_count > 0:
                self.logger.debug(f"Successfully set {success_count} ratings")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to set table ratings: {e}")
            return False

    def click_yes_no_table_option(self, question_id, select_yes=True, table_class="YesNoASC"):
        """Yes/No table yapısı için seçim metodu"""
        try:
            # Row'u bul
            row = self.wait.until(
                EC.presence_of_element_located((By.ID, f"FNSR{question_id}"))
            )
            
            # Yes için 1, No için 2
            opt_num = "1" if select_yes else "2"
            
            # Hücreyi bul (daha spesifik selector)
            cell = row.find_element(By.CSS_SELECTOR, f"td.Opt{opt_num}.inputtyperbloption[role='radio']")
            
            # Radio span ve input'u bul
            span = cell.find_element(By.CSS_SELECTOR, "span.radioSimpleInput")
            radio = cell.find_element(By.CSS_SELECTOR, f"input.simpleInput.rbl[id='R{question_id}.{opt_num}']")
            
            # Görünür yap ve seç
            self.driver.execute_script("""
                var radio = arguments[0];
                var cell = arguments[1];
                var span = arguments[2];
                
                // Radio butonu görünür yap
                radio.style.display = 'block';
                radio.scrollIntoView({behavior: 'instant', block: 'center'});
                
                // Radio butonu seç
                radio.click();
                radio.checked = true;
                radio.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Span ve cell'i güncelle
                span.style.backgroundPosition = '0px -11px';
                cell.setAttribute('aria-checked', 'true');
                cell.click();
            """, radio, cell, span)
            
            time.sleep(0.2)
            
            # Seçimin başarılı olup olmadığını kontrol et
            if radio.get_attribute('checked') or cell.get_attribute('aria-checked') == 'true':
                self.logger.debug(f"Successfully selected {opt_num} for YesNo question {question_id}")
                return True
                
            return False

        except Exception as e:
            self.logger.error(f"Failed to click YesNo table option: {e}")
            return False

    def process_survey(self, row):
        with self.error_handling("survey processing"):
            self.driver.get(self.config.URL)
            self.wait_for_page_load()
            
            # Initial navigation with progress tracking
            self.logger.info(f"Starting new survey process ({self.version_info})")
            
            # Initial navigation
            self.safe_click(By.ID, 'NextButton')
            self.wait_for_page_load()
            
            # Survey code and bill amount
            self.smart_send_keys(By.ID, 'InputCouponNum', row['survey_code'])
            self.smart_send_keys(By.ID, 'AmountSpent1', str(row['total_bill_1']))
            self.smart_send_keys(By.ID, 'AmountSpent2', str(row['total_bill_2']))
            self.safe_click(By.ID, 'NextButton')
            self.wait_for_page_load()

            # Visit Time - try multiple selectors
            self.logger.debug("Processing Visit Time section")
            time_value = row['visit_time']
            time_mapping = {'12-15': 1, '15-17': 2, '17-19': 3, '19-21': 4}
            visit_time_selectors = [
                (By.XPATH, f"//div[contains(@class, 'timeslot')]//*[contains(text(), '{time_value}')]"),
                (By.XPATH, f"//*[@id='FNSR000252']/div/div/div[{time_mapping[time_value]}]/label"),
                (By.CSS_SELECTOR, f"label[for$='{time_value}']"),
                (By.XPATH, f"//label[contains(text(), '{time_value}')]")
            ]
            
            success = False
            for by, selector in visit_time_selectors:
                try:
                    if self.safe_click(by, selector):
                        success = True
                        self.logger.debug(f"Successfully clicked time selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Failed to click {selector}: {str(e)}")
                    continue
                    
            if not success:
                raise NoSuchElementException("Could not find any working time selector")

            self.safe_click(By.ID, 'NextButton')
            self.wait_for_page_load()

            # Did you visit - dinamik ID ile
            self.logger.debug("Processing Did you visit section")
            option = '1' if row['did_you_visit'] == 'Yes' else '2'
            if not self.find_and_click_option(option, 'FNSR'):
                raise NoSuchElementException("Could not find did_you_visit options")
            self.smart_click(By.ID, 'NextButton')

            # Dine in or Takeaway - en son metod ile
            self.logger.debug("Processing Dine in/Takeaway section")
            self.wait_for_page_load()
            
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    # Yeni metodu dene
                    if self.click_dine_option_v3(row['dine_in'].lower() == 'in'):
                        self.logger.debug("Successfully clicked dine option")
                        time.sleep(1)
                        if self.wait_and_click_next():
                            success = True
                            break
                except Exception as e:
                    self.logger.debug(f"Dine option attempt {retry_count + 1} failed: {e}")
                
                retry_count += 1
                time.sleep(1)
            
            if not success:
                self.logger.error("Failed to complete dine-in section")
                raise NoSuchElementException("Could not complete dine-in section")

            self.wait_for_page_load()

            # Previous visits - yeni metod ile
            self.logger.debug("Processing Previous visits section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                if self.click_yes_no_option('000159', row['have_you_befor'].lower() == 'yes'):
                    success = True
                    if self.wait_and_click_next():
                        break
                retry_count += 1
                time.sleep(0.5)
            
            if not success:
                raise NoSuchElementException("Could not complete previous visits section")

            # Overall satisfaction - en son metod ile
            self.logger.debug("Processing Overall satisfaction section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.click_satisfaction_rating_v2(row['rate']):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Rating attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.2)
            
            if not success:
                raise NoSuchElementException("Could not complete satisfaction rating section")

            # Very satisfied experience
            self.logger.debug("Processing Satisfaction confirmation section")
            selector = "tr[id^='FNSR'] td.Opt1.inputtyperbloption" if row['very_satisfied'] == 'Yes' else "tr[id^='FNSR'] td.Opt2.inputtyperbloption"
            self.smart_click(By.CSS_SELECTOR, selector)
            self.smart_click(By.ID, 'NextButton')

            # Restaurant satisfaction
            self.logger.debug("Processing Restaurant satisfaction section")
            selector = f"tr[id^='FNSR'] td.Opt{row['rate_restorant']}.inputtyperbloption"
            self.smart_click(By.CSS_SELECTOR, selector)
            self.smart_click(By.ID, 'NextButton')

            # Food satisfaction - güncellenen metod ile 
            self.logger.debug("Processing Food satisfaction section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.select_satisfaction_table_ratings(row['rate_food']):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Food rating attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.2)
            
            if not success:
                raise NoSuchElementException("Could not complete food satisfaction section")

            # Service satisfaction - aynı tablo seçim metodu ile
            self.logger.debug("Processing Service satisfaction section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.select_satisfaction_table_ratings(row['rate_service']):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Service rating attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.2)
            
            if not success:
                raise NoSuchElementException("Could not complete service satisfaction section")

            # Problem section
            self.logger.debug("Processing Problem section")
            problem_xpath = "//*[@id='FNSR000090']/td[1]" if row['problem'] == 'Yes' else "//*[@id='FNSR000090']/td[2]"
            self.smart_click(By.XPATH, problem_xpath)
            self.smart_click(By.ID, 'NextButton')

            # Return likelihood
            self.logger.debug("Processing Return likelihood section")
            return_xpath = f"//*[@id='FNSR000093']/td[{6-int(row['return_to'])}]"
            self.smart_click(By.XPATH, return_xpath)
            self.smart_click(By.ID, 'NextButton')

            # Recommendation likelihood
            self.logger.debug("Processing Recommendation section")
            recommend_xpath = f"//*[@id='FNSR000094']/td[{11-int(row['return_to'])}]"
            self.smart_click(By.XPATH, recommend_xpath)
            self.smart_click(By.ID, 'NextButton')

            # Comments and details
            self.logger.debug("Processing Comments section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.smart_send_keys(By.ID, 'S000247', row['comment_detail']):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Comments attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.5)
            
            if not success:
                raise NoSuchElementException("Could not complete comments section")

            # Member details - aynı şekilde güncelle
            self.logger.debug("Processing Member details section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.smart_send_keys(By.ID, 'S000152', row['member_detail']):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Member details attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.5)
            
            if not success:
                raise NoSuchElementException("Could not complete member details section")

            # Dietary information
            self.logger.debug("Processing Dietary information section")
            if row['return_to'] == '10':
                self.smart_click(By.XPATH, "//*[@id='FNSR000237']/span")
            self.smart_click(By.ID, 'NextButton')

            # Additional information
            self.logger.debug("Processing Additional information section")
            self.smart_click(By.XPATH, "//*[@id='R000238']/option[3]")
            self.smart_click(By.XPATH, "//*[@id='R000129']/option[2]")
            self.smart_click(By.XPATH, "//*[@id='R000130']/option[8]")
            self.smart_click(By.ID, 'NextButton')

            # Prize Draw entry - dinamik ID ile
            self.logger.debug("Processing Prize Draw section")
            draw_element = self.find_dynamic_element('FNSR', 'id')
            if draw_element:
                draw_element.find_element(By.CSS_SELECTOR, "td:nth-child(2)").click()
            else:
                raise NoSuchElementException("Could not find prize draw section")
            self.smart_click(By.ID, 'NextButton')

            # News information - dinamik ID ile
            self.logger.debug("Processing News information section")
            news_element = self.find_dynamic_element('FNSR', 'id')
            if news_element:
                news_element.find_element(By.CSS_SELECTOR, "td:nth-child(2)").click()
            else:
                raise NoSuchElementException("Could not find news section")
            self.smart_click(By.ID, 'NextButton')

            # Drink offer section
            self.logger.debug("Processing Drink offer section")
            success = False
            retry_count = 0
            
            while not success and retry_count < 3:
                try:
                    if self.click_yes_no_table_option('000142', row['offer_drink'].lower() == 'yes'):
                        success = True
                        if self.wait_and_click_next():
                            break
                except Exception as e:
                    self.logger.debug(f"Drink offer attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(0.2)
            
            if not success:
                raise NoSuchElementException("Could not complete drink offer section")

            current_progress = self.get_progress_percentage()
            current_section = self.get_current_section()
            
            self.logger.info(f"Survey completed. Final progress: {current_progress}% - Section: {current_section}")

    def change_identity(self):
        if self.config.USE_PROXY:
            proxy = random.choice(self.config.PROXY_LIST)
            self.driver.quit()
            options = webdriver.ChromeOptions()
            options.add_argument(f'--proxy-server={proxy}')
            self.driver = webdriver.Chrome(options=options)
            self.logger.info(f"Changed proxy to: {proxy}")

    def run(self):
        for index, row in self.data.iterrows():
            if not self.running:
                self.logger.info("Execution stopped by user")
                break
                
            retry_count = 0
            while retry_count < self.config.MAX_RETRIES and self.running:
                try:
                    self.logger.info(f"Processing row {index + 1}")
                    
                    if retry_count > 0:
                        if not self.is_browser_alive():
                            self.logger.error("Browser was closed, stopping execution")
                            return
                        self.cleanup()
                        self.setup_driver()
                    
                    self.process_survey(row)
                    self.logger.info(f"Successfully processed row {index + 1}")
                    break
                    
                except WebDriverException as e:
                    if "Browser window was closed" in str(e):
                        self.logger.info("Browser was closed by user, stopping execution")
                        return
                    retry_count += 1
                    self.logger.warning(f"Attempt {retry_count} failed: {e}")
                    
                except Exception as e:
                    retry_count += 1
                    self.logger.warning(f"Attempt {retry_count} failed: {e}")
                    
                if retry_count < self.config.MAX_RETRIES and self.running:
                    time.sleep(self.config.RETRY_DELAY)
                else:
                    self.logger.error(f"Failed to process row {index + 1} after {retry_count} attempts")

    def cleanup(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    bot = PrezzoBot()
    try:
        bot.run()
    finally:
        bot.cleanup()
