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

# Form doldurma fonksiyonu
def fill_form(row):
    # Survey Entry Code ve Fatura Tutarı
    
    driver.find_element(By.ID, 'NextButton').click()
    driver.find_element(By.ID, 'InputCouponNum').send_keys(row['survey_code'])
    driver.find_element(By.ID, 'AmountSpent1').send_keys(row['total_bill_1'])
    driver.find_element(By.ID, 'AmountSpent2').send_keys(row['total_bill_2'])

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle    
   
    #ToDo: Sayfada hata okunursa tekrar deneme yapılacak. 

    # Ziyaret Saati
    if row['visit_time'] == '12-15':
        driver.find_element(By.XPATH, "//*[@id='FNSR000252']/div/div/div[1]/label").click()
    elif row['visit_time'] == '15-17':
        driver.find_element(By.XPATH, "//*[@id='FNSR000252']/div/div/div[2]/label").click()
    elif row['visit_time'] == '17-19':
        driver.find_element(By.XPATH, "//*[@id='FNSR000252']/div/div/div[3]/label").click()
    elif row['visit_time'] == '19-21':
        driver.find_element(By.XPATH, "//*[@id='FNSR000252']/div/div/div[4]/label").click()
    

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # Did you visit .....
    if row['did_you_visit'] == 'Yes':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
    elif row['did_you_visit'] == 'No':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
  
    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # Dine in or Takeaway
    if row['dine_in'] == 'In':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
    elif row['dine_in'] == 'Home':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

  
    # Have you ever visited this restaurant before?
    if row['have_you_befor'] == 'Yes':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
    elif row['have_you_befor'] == 'No':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # Please Rate your overall satisfaction with your experience at this restaurant
    if row['rate'] == '5':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt5.inputtyperbloption > span").click()
    elif row['rate'] == '4':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt4.inputtyperbloption > span").click()
    elif row['rate'] == '3':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt3.inputtyperbloption > span").click()
    elif row['rate'] == '2':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption > span").click()
    elif row['rate'] == '1':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption > span").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

 
    # Its selected that you were very satisfied with your experience. 
    if row['very_satisfied'] == 'Yes':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()
    elif row['very_satisfied'] == 'No':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()

        # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

#FNSR000021 > td.Opt5.inputtyperbloption
#FNSR000013 > td.Opt5.inputtyperbloption
    # Rate your satisfaction
    if row['rate_restorant'] == '5':
        # Very Satisfied
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt5.inputtyperbloption").click()
    elif row['rate_restorant'] == '4':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt4.inputtyperbloption").click()
    elif row['rate_restorant'] == '3':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt3.inputtyperbloption").click()
    elif row['rate_restorant'] == '2':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt2.inputtyperbloption").click()
    elif row['rate_restorant'] == '1':
        driver.find_element(By.CSS_SELECTOR, "tr[id^='FNSR'] td.Opt1.inputtyperbloption").click()

        # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # Please rate your satisfaction with...
    if row['rate_food'] == '5':
        # Very Satisfied
        driver.find_element(By.XPATH, "//*[@id='FNSR000014']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000028']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000164']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000018']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000021']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000148']/td[1]").click()
    elif row['rate_food'] == '4':
        driver.find_element(By.XPATH, "//*[@id='FNSR000014']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000028']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000164']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000018']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000021']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000148']/td[2]").click()
    elif row['rate_food'] == '3':
        driver.find_element(By.XPATH, "//*[@id='FNSR000014']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000028']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000164']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000018']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000021']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000148']/td[3]").click()
    elif row['rate_food'] == '2':
        driver.find_element(By.XPATH, "//*[@id='FNSR000014']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000028']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000164']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000018']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000021']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000148']/td[4]").click()
    elif row['rate_food'] == '1':
        driver.find_element(By.XPATH, "//*[@id='FNSR000014']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000028']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000164']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000018']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000021']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000148']/td[5]").click()

        # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # Please rate your satisfaction with...
    if row['rate_service'] == '5':
        # Very Satisfied
        driver.find_element(By.XPATH, "//*[@id='FNSR000013']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000019']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000012']/td[1]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000029']/td[1]").click()
    elif row['rate_service'] == '4':
        driver.find_element(By.XPATH, "//*[@id='FNSR000013']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000019']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000012']/td[2]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000029']/td[2]").click()
    elif row['rate_service'] == '3':
        driver.find_element(By.XPATH, "//*[@id='FNSR000013']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000019']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000012']/td[3]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000029']/td[3]").click()
    elif row['rate_service'] == '2':
        driver.find_element(By.XPATH, "//*[@id='FNSR000013']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000019']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000012']/td[4]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000029']/td[4]").click()
    elif row['rate_service'] == '1':
        driver.find_element(By.XPATH, "//*[@id='FNSR000013']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000019']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000012']/td[5]").click()
        driver.find_element(By.XPATH, "//*[@id='FNSR000029']/td[5]").click()


    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # did you have problem. 
    if row['problem'] == 'Yes':
        driver.find_element(By.XPATH, "//*[@id='FNSR000090']/td[1]").click()
    elif row['problem'] == 'No':
        driver.find_element(By.XPATH, "//*[@id='FNSR000090']/td[2]").click() 

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

  
    # Return to this restaurant
    if row['return_to'] == '5':
        driver.find_element(By.XPATH, "//*[@id='FNSR000093']/td[1]").click()
    elif row['return_to'] == '4':
        driver.find_element(By.XPATH, "//*[@id='FNSR000093']/td[2]").click()
    elif row['return_to'] == '3':
        driver.find_element(By.XPATH, "//*[@id='FNSR000093']/td[3]").click()
    elif row['return_to'] == '2':
        driver.find_element(By.XPATH, "//*[@id='FNSR000093']/td[4]").click()
    elif row['return_to'] == '1':
        driver.find_element(By.XPATH, "//*[@id='FNSR000093']/td[5]").click()
        

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle


    # Recommend this restaurant
    if row['return_to'] == '10':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[1]").click()
    elif row['return_to'] == '9':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[2]").click()
    elif row['return_to'] == '8':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[3]").click()
    elif row['return_to'] == '7':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[4]").click()
    elif row['return_to'] == '6':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[5]").click()
    elif row['return_to'] == '5':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[6]").click()
    elif row['return_to'] == '4':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[7]").click()        
    elif row['return_to'] == '3':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[8]").click()
    elif row['return_to'] == '2':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[9]").click()
    elif row['return_to'] == '1':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[10]").click()
    elif row['return_to'] == '0':
        driver.find_element(By.XPATH, "//*[@id='FNSR000094']/td[11]").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    driver.find_element(By.ID, 'S000247').send_keys(row['comment_detail'])

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    driver.find_element(By.ID, 'S000152').send_keys(row['member_detail'])

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

        # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle


    # diatery  // ToDo: Diatery bilgileri eklenecek
    if row['return_to'] == '10':
        driver.find_element(By.XPATH, "//*[@id='FNSR000237']/span").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # ToDo: Burada daha fazla bilgi girmek için bir döngü yapılacak.
    # many people
    driver.find_element(By.XPATH, "//*[@id='R000238']/option[3]").click()
    # gender
    driver.find_element(By.XPATH, "//*[@id='R000129']/option[2]").click()
    # age
    driver.find_element(By.XPATH, "//*[@id='R000130']/option[8]").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle
    # Prize Draw entry /// NO
    driver.find_element(By.XPATH, "//*[@id='FNSR000132']/td[2]").click()

    # Next butonuna tıklama
    driver.find_element(By.ID, 'NextButton').click()
    time.sleep(2)  # Sayfanın yüklenmesini bekle

    # News information /// NO
    driver.find_element(By.XPATH, "//*[@id='FNSR000133']/td[2]").click()

    

# Her satır için formu doldurma
for index, row in data.iterrows():
    fill_form(row)
    # IP ve MAC adresi değiştirme fonksiyonu burada çağrılacak
    # change_ip_and_mac()

# Tarayıcıyı kapatma
driver.quit()

# Log dosyasını yapılandırma
logging.basicConfig(filename='bot.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Her satır için formu doldurma
for index, row in data.iterrows():
    try:
        logging.info(f"Processing row {index + 1}")
        fill_form(row)
        logging.info(f"Successfully processed row {index + 1}")
    except NoSuchElementException as e:
        logging.error(f"Error processing row {index + 1}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing row {index + 1}: {e}")
    # IP ve MAC adresi değiştirme fonksiyonu burada çağrılacak
    # change_ip_and_mac()

    #id değerleri yerine xpath kullanılacak yada css selector kullanılacak
    # Log eklenecek
   #  try:
   # driver.find_element(By.ID, 'InputCouponNum').send_keys(row['survey_code']) # işlem
#except NoSuchElementException: # Hata yakalama
 #   logging.error("Survey code input field not found.")