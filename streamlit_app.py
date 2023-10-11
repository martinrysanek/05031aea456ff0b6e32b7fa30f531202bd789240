# -*- coding: utf-8 -*-
"""
Created on Mon May  1 03:18:27 2023

@author: Z66483668
"""

from unittest import addModuleCleanup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException  

from datetime import datetime, timedelta
import locale
import time, sys, os
import pandas as pd
import random
import array
import pathlib
import json
import pyautogui
import getopt
import re

VERBOSE = False

SHORT_PAUSE = 0.3
NORMAL_PAUSE = 0.6
LONG_PAUSE =   1.5
ELEMENT_WAIT = 5

MIN_LEN = 3

driver = None
  
def get_methods(object, spacing=24): 
  methodList = [] 
  for method_name in dir(object): 
    try: 
        if callable(getattr(object, method_name)): 
            methodList.append(str(method_name)) 
    except: 
        methodList.append(str(method_name)) 
  processFunc = (lambda s: ' '.join(s.split())) or (lambda s: s) 
  for method in methodList: 
    try: 
        print(str(method.ljust(spacing)) + ' ' + 
              processFunc(str(getattr(object, method).__doc__)[0:90])) 
    except: 
        print(method.ljust(spacing) + ' ' + ' getattr() failed') 
        
        
def element_by_xpath(xpath, wait=ELEMENT_WAIT):
    global driver
    WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH,xpath)))
    return driver.find_element(By.XPATH,xpath)

def element_by_xpath_visible(xpath, wait=ELEMENT_WAIT):
    global driver
    WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH,xpath)))
    return driver.find_element(By.XPATH,xpath)

def element_by_id(element_id, wait=ELEMENT_WAIT):
    global driver
    WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.ID,element_id)))
    return driver.find_element(By.ID,element_id)

def check_exists_by_xpath(xpath, wait=ELEMENT_WAIT):
    global driver
    try:
        WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH,xpath)))
        item = driver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return None
    except TimeoutException:
        return None
    return item

try:

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    
    with open("config.json", encoding='utf-8') as file:
       config = json.load(file)    

    columns = ['Kategorie', 'Podkategorie', 'Druh', 'Název', 'Obchod', 'Cena', 'Cena za', 'Jednotková cena', 'Platnost', 'Unit_num', 'Unit_amount']
    data = pd.DataFrame(columns=columns)
    
    for line in config:
        options = Options()
        # options.add_argument('--headless') # Runs Chrome in headless mode.
        options.add_argument('--no-sandbox') # Bypass OS security model
        # options.add_argument("--incognito")
        options.add_argument("--lang=cs")
        options.add_argument("--disable-web-security")
        # exclude USB device message and control
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("start-maximized")
        # to save session data
        script_directory = pathlib.Path().absolute()
        options.add_argument("user-data-dir={}\\{}".format(script_directory, 'Context'))
 
        driver = webdriver.Chrome(options=options)
        base_url = 'https://www.kupi.cz/slevy/'
        # driver.get(config[line]['server_url'])
        driver.get(base_url + line)
        driver.maximize_window()
        time.sleep(NORMAL_PAUSE)    
        # display whole dynamic HTML
        while True:
            xpath = f"//*[contains(text(), 'Načíst další zboží')]"
            read_additional = check_exists_by_xpath(xpath, wait=3)
            if read_additional:
                read_additional.click()
                time.sleep(LONG_PAUSE)        
            else:
                break
    
        initial_element_xpath = '/html/body/div[2]/div[5]/div[1]/div/div[3]'
        initial_element = element_by_xpath_visible(initial_element_xpath)
        inner_element_class = 'group_discounts' 
        elements = initial_element.find_elements(By.CLASS_NAME, inner_element_class)
        
        df = pd.DataFrame(columns=columns)

        # Process the found elements as needed
        for element in elements:
            # if element == elements[-1]:
            #     print('LAST ELEMENT')
            # Do something with each element
            item = element.find_element(By.XPATH, './div[3]/div/div/div/h2/a/strong')
            name_text = item.text
            print(name_text)  # Print the text of each element, for example
            table = element.find_element(By.TAG_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                shop = row.find_element(By.XPATH, './td[2]/span/a/span')
            
                shop_text = driver.execute_script("return arguments[0].textContent;", shop).strip(" \t\n\r")
                shop_text = re.sub(r' +', ' ', re.sub(r'[\n\t]+| +', ' ', shop_text))
            
                price = row.find_element(By.XPATH, './td[3]/div[1]/strong')
                price_text = driver.execute_script("return arguments[0].textContent;", price).strip(" \t\n\r")
                price_text = re.sub(r' +', ' ', re.sub(r'[\n\t]+| +', ' ', price_text))
                if len(price_text) < MIN_LEN or not 'Kč' in price_text:
                    price_text = ' '
                
                amount = row.find_element(By.XPATH, './td[3]/div[2]')
                amount_text = driver.execute_script("return arguments[0].textContent;", amount).strip(" \t\n\r")
                amount_text = re.sub(r' +', ' ', re.sub(r'[\n\t]+| +', ' ', amount_text))
                if len(amount_text) < MIN_LEN or not '/' in amount_text:
                    amount_text = ' '
            
                unit = row.find_element(By.XPATH, './td[3]/span[2]')
                unit_text = driver.execute_script("return arguments[0].textContent;", unit).strip(" \t\n\r")
                unit_text = re.sub(r' +', ' ', re.sub(r'[\n\t]+| +', ' ', unit_text))
                unit_amount = ' '
                unit_num = 100000.0
                if len(unit_text) < MIN_LEN or not '/' in unit_text:
                    unit_text = ' '
                else:
                    pattern = r'([\d,]+)\s*Kč\s*/\s*(.+)'
                    match = re.search(pattern, unit_text)
                    if match:
                        unit_price = match.group(1)
                        unit_amount  = match.group(2)
                        unit_num = float(unit_price.replace(',', '.'))
            
                until = row.find_element(By.XPATH, './td[4]')
                until_text = driver.execute_script("return arguments[0].textContent;", until).strip(" \t\n\r")
                until_text = re.sub(r' +', ' ', re.sub(r'[\n\t]+| +', ' ', until_text))
                if len(until_text) < MIN_LEN:
                    until_text = ' '
                    
                if VERBOSE:            
                    print (' {:<20}, {:<20}, {:<8}'.format(shop_text, price_text + amount_text, unit_text) )
                    
                new_row = {'Kategorie': config[line]['Kategorie'], 'Podkategorie' : config[line]['Podkategorie'], 'Druh' : '', 'Název' : f'{name_text}', 'Obchod' : f'{shop_text}', 'Cena' : f'{price_text}', 'Cena za' : f'{amount_text}', 'Jednotková cena' : f'{unit_text}', 'Platnost' : f'{until_text}', 'Unit_num' : f'{unit_num}', 'Unit_amount' : f'{unit_amount}'}
                df.loc[len(df.index)] = new_row

        df['Název'].replace(dict(config[line]['Sub']), regex=True, inplace=True)
        
        df['Druh'] = [next((category for substring, category in config[line]['Druhy'].items() if substring in name), config[line]['Default_druh']) for name in df['Název']]
        if data.empty:
            data = df
        else:
            data = pd.concat([data, df], axis=0) 
        driver.quit()   
     
    data.to_excel('slevy.xlsx', index=False)
        
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print("\nException!\n", e.__class__, exc_type, exc_obj, '\n', exc_tb.tb_frame.f_code.co_filename, '[', exc_tb.tb_lineno, ']' )
finally:
    # driver.quit()   
    print("\nFinishing...")
    
print('Finished.')


