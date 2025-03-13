import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import logging

# Excel'den veri okuma
data = pd.read_excel('veriler.xlsx')

# Tarayıcıyı başlatma
driver = webdriver.Chrome()
driver.get('https://www.prezzovoice.co.uk')

# Log dosyasını yapılandırma
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# IP ve MAC adresi değiştirme fonksiyonu (Bu fonksiyonun içeriği sizin ihtiyaçlarınıza göre doldurulmalıdır)
def change_ip_and_mac():
    # Burada IP ve MAC adresi değiştirme işlemleri yapılacak
    logging.info("IP and MAC address changed.")

# Form doldurma fonksiyonu
def fill_form(row):
    try:
        # Survey Entry Code ve Fatura Tutarı
        driver.find_element(By.ID, 'NextButton').click()
        driver.find_element(By.ID, 'InputCouponNum').send_keys(row['survey_code'])
        driver.find_element(By.ID, 'AmountSpent1').send_keys(row['total_bill_1'])
        driver.find_element(By.ID, 'AmountSpent2').send_keys(row['total_bill_2'])
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Ziyaret Saati
        visit_time_xpath = {
            '12-15': "//*[@id='FNSR000252']/div/div/div[1]/label",
            '15-17': "//*[@id='FNSR000252']/div/div/div[2]/label",
            '17-19': "//*[@id='FNSR000252']/div/div/div[3]/label",
            '19-21': "//*[@id='FNSR000252']/div/div/div[4]/label"
        }
        driver.find_element(By.XPATH, visit_time_xpath[row['visit_time']]).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Did you visit .....
        if row['did_you_visit'] == 'Yes':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
        elif row['did_you_visit'] == 'No':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Dine in or Takeaway
        if row['dine_in'] == 'In':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
        elif row['dine_in'] == 'Home':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Have you ever visited this restaurant before?
        if row['have_you_befor'] == 'Yes':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
        elif row['have_you_befor'] == 'No':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)


        # Please Rate your overall satisfaction with your experience at this restaurant
        rate_xpath = {
            '5': "/html/body/div[1]/div[3]/div[2]/form/div/table/tbody/tr[2]/td[1]/input",
            '4': "/html/body/div[1]/div[3]/div[2]/form/div/table/tbody/tr[2]/td[2]/input",
            '3': "/html/body/div[1]/div[3]/div[2]/form/div/table/tbody/tr[2]/td[3]/input",
            '2': "/html/body/div[1]/div[3]/div[2]/form/div/table/tbody/tr[2]/td[4]/input",
            '1': "/html/body/div[1]/div[3]/div[2]/form/div/table/tbody/tr[2]/td[5]/input"
        }
        driver.find_element(By.XPATH, rate_xpath[row['rate']]).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Its selected that you were very satisfied with your experience.
        if row['very_satisfied'] == 'Yes':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
        elif row['very_satisfied'] == 'No':
            driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Rate your satisfaction
        rate_restaurant_xpath = {
            '5': "tr[id^='FNSR'] td.Opt5.inputtyperbloption",
            '4': "tr[id^='FNSR'] td.Opt4.inputtyperbloption",
            '3': "tr[id^='FNSR'] td.Opt3.inputtyperbloption",
            '2': "tr[id^='FNSR'] td.Opt2.inputtyperbloption",
            '1': "tr[id^='FNSR'] td.Opt1.inputtyperbloption"
        }
        driver.find_element(By.CSS_SELECTOR, rate_restaurant_xpath[row['rate_restorant']]).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Please rate your satisfaction with...
        rate_food_xpath = {
            '5': ["//*[@id='FNSR000014']/td[1]", "//*[@id='FNSR000028']/td[1]", "//*[@id='FNSR000164']/td[1]", "//*[@id='FNSR000018']/td[1]", "//*[@id='FNSR000021']/td[1]", "//*[@id='FNSR000148']/td[1]"],
            '4': ["//*[@id='FNSR000014']/td[2]", "//*[@id='FNSR000028']/td[2]", "//*[@id='FNSR000164']/td[2]", "//*[@id='FNSR000018']/td[2]", "//*[@id='FNSR000021']/td[2]", "//*[@id='FNSR000148']/td[2]"],
            '3': ["//*[@id='FNSR000014']/td[3]", "//*[@id='FNSR000028']/td[3]", "//*[@id='FNSR000164']/td[3]", "//*[@id='FNSR000018']/td[3]", "//*[@id='FNSR000021']/td[3]", "//*[@id='FNSR000148']/td[3]"],
            '2': ["//*[@id='FNSR000014']/td[4]", "//*[@id='FNSR000028']/td[4]", "//*[@id='FNSR000164']/td[4]", "//*[@id='FNSR000018']/td[4]", "//*[@id='FNSR000021']/td[4]", "//*[@id='FNSR000148']/td[4]"],
            '1': ["//*[@id='FNSR000014']/td[5]", "//*[@id='FNSR000028']/td[5]", "//*[@id='FNSR000164']/td[5]", "//*[@id='FNSR000018']/td[5]", "//*[@id='FNSR000021']/td[5]", "//*[@id='FNSR000148']/td[5]"]
        }
        for xpath in rate_food_xpath[row['rate_food']]:
            driver.find_element(By.XPATH, xpath).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Please rate your satisfaction with...
        rate_service_xpath = {
            '5': ["//*[@id='FNSR000013']/td[1]", "//*[@id='FNSR000019']/td[1]", "//*[@id='FNSR000012']/td[1]", "//*[@id='FNSR000029']/td[1]"],
            '4': ["//*[@id='FNSR000013']/td[2]", "//*[@id='FNSR000019']/td[2]", "//*[@id='FNSR000012']/td[2]", "//*[@id='FNSR000029']/td[2]"],
            '3': ["//*[@id='FNSR000013']/td[3]", "//*[@id='FNSR000019']/td[3]", "//*[@id='FNSR000012']/td[3]", "//*[@id='FNSR000029']/td[3]"],
            '2': ["//*[@id='FNSR000013']/td[4]", "//*[@id='FNSR000019']/td[4]", "//*[@id='FNSR000012']/td[4]", "//*[@id='FNSR000029']/td[4]"],
            '1': ["//*[@id='FNSR000013']/td[5]", "//*[@id='FNSR000019']/td[5]", "//*[@id='FNSR000012']/td[5]", "//*[@id='FNSR000029']/td[5]"]
        }
        for xpath in rate_service_xpath[row['rate_service']]:
            driver.find_element(By.XPATH, xpath).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Did you have a problem?
        if row['problem'] == 'Yes':
            driver.find_element(By.XPATH, "//*[@id='FNSR000090']/td[1]").click()
        elif row['problem'] == 'No':
            driver.find_element(By.XPATH, "//*[@id='FNSR000090']/td[2]").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Return to this restaurant
        return_to_xpath = {
            '5': "//*[@id='FNSR000093']/td[1]",
            '4': "//*[@id='FNSR000093']/td[2]",
            '3': "//*[@id='FNSR000093']/td[3]",
            '2': "//*[@id='FNSR000093']/td[4]",
            '1': "//*[@id='FNSR000093']/td[5]"
        }
        driver.find_element(By.XPATH, return_to_xpath[row['return_to']]).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Recommend this restaurant
        recommend_xpath = {
            '10': "//*[@id='FNSR000094']/td[1]",
            '9': "//*[@id='FNSR000094']/td[2]",
            '8': "//*[@id='FNSR000094']/td[3]",
            '7': "//*[@id='FNSR000094']/td[4]",
            '6': "//*[@id='FNSR000094']/td[5]",
            '5': "//*[@id='FNSR000094']/td[6]",
            '4': "//*[@id='FNSR000094']/td[7]",
            '3': "//*[@id='FNSR000094']/td[8]",
            '2': "//*[@id='FNSR000094']/td[9]",
            '1': "//*[@id='FNSR000094']/td[10]",
            '0': "//*[@id='FNSR000094']/td[11]"
        }
        driver.find_element(By.XPATH, recommend_xpath[row['return_to']]).click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Comment detail
        driver.find_element(By.ID, 'S000247').send_keys(row['comment_detail'])
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Member detail
        driver.find_element(By.ID, 'S000152').send_keys(row['member_detail'])
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Dietary information
        if row['return_to'] == '10':
            driver.find_element(By.XPATH, "//*[@id='FNSR000237']/span").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Additional information
        driver.find_element(By.XPATH, "//*[@id='R000238']/option[3]").click()
        driver.find_element(By.XPATH, "//*[@id='R000129']/option[2]").click()
        driver.find_element(By.XPATH, "//*[@id='R000130']/option[8]").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # Prize Draw entry
        driver.find_element(By.XPATH, "//*[@id='FNSR000132']/td[2]").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

        # News information
        driver.find_element(By.XPATH, "//*[@id='FNSR000133']/td[2]").click()
        driver.find_element(By.ID, 'NextButton').click()
        time.sleep(2)

    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Her satır için formu doldurma
for index, row in data.iterrows():
    try:
        logging.info(f"Processing row {index + 1}")
        fill_form(row)
        logging.info(f"Successfully processed row {index + 1}")
    except Exception as e:
        logging.error(f"Error processing row {index + 1}: {e}")
    finally:
        change_ip_and_mac()

    # Tarayıcıyı kapatma
    # Wait for a few seconds before quitting
        time.sleep(5)
    
    # Wait for user input to quit
    input("Press Enter to quit...")