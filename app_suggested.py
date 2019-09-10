#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
from requests.exceptions import ConnectionError
import time
import argparse
import configparser
import textwrap
import sys
import os
import json
from numpy import percentile

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class PrivateIGScrapper(object):
    def __init__(self, username, login_user, login_pass, driver):
        
        self.username = username
        self.login_user = login_user
        self.login_pass = login_pass
        self.driver = driver

        # Use driver dependng on the chosen solution. 
        # Driver has to be in PATH
        if self.driver == 'chromedriver':
            # Desde mediados de agosto los mamones de IG 
            # detectan que estás conectado con Chromedriver o 
            # con geckodriver. Incluimos la opción headless 
            # para que no nos detecten.
            # Ver https://duo.com/decipher/driving-headless-chrome-with-python
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            self.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif self.driver == 'geckodriver':
            # https://www.edureka.co/community/10026/headless-gecko-driver-using-selenium
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            self.browser = webdriver.Firefox(firefox_options=firefox_options)
        
        self.url = "https://www.instagram.com/" + str(self.username)
    
    def isElementPresent(self, locator):
        try:
            self.browser.find_element(By.XPATH, locator)
        except NoSuchElementException:
            print ('No more scrolling buttons')
            return False
        return True

    def suggested_imgs_urls(self):
        try:
            self.request = requests.get(self.url)
        except ConnectionError:
            print('Web site does not exist')
        else:
            print('Web site exists. Login with provided credentials.')
            
            try:
                # Obtenemos el contenido de la página
                # No se facilita la info de Suegrencias para ti
                self.browser.get(self.url)

                # Comenzamos con un attempting de login
                elem = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div/div[2]/div[2]/div[3]/div/span/a[1]/button')
                actions = ActionChains(self.browser)
                actions.click(elem).perform()
                # Metemos usuario y contraseña y clicamos
                time.sleep(2)
                user_name_elem = self.browser.find_element_by_xpath("//input[@name='username']")
                user_name_elem.clear()
                user_name_elem.send_keys(self.login_user)
                password_elem = self.browser.find_element_by_xpath("//input[@name='password']")
                password_elem.clear()
                password_elem.send_keys(self.login_pass)
                time.sleep(2)
                login_button = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]').click()
                time.sleep(2)

                # Volvemos a hacer un browser.get(url)
                wait = WebDriverWait(self.browser, 10)
                wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/span/section/main/div/div/article/div[2]/div')))
                #self.browser.find_all("img", attrs={"class": "_6q-tv"})
                self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/div')
                
                print('Scrapping suggested friends profile pics urls.')

                soup = BeautifulSoup(self.browser.page_source, 'html.parser')

                profile_pic = soup.find("img", attrs={"class": "be6sR"}).get('src')

                images_urls = list()
                for img in soup.find_all("img", attrs={"class": "_6q-tv"}):
                    images_urls.append(img.get('src'))
                
                usernames = list()
                for _id in soup.find_all("a", attrs={"class": "FPmhX notranslate Qj3-a"}):
                    usernames.append(_id.get('title'))


                # Vamos a intentar activar todas las imágenes en el carousel de IG
                locators = ['//*[@id="react-root"]/section/main/div/div/article/div[2]/div/div[2]/button',
                '//*[@id="react-root"]/section/main/div/div/article/div[2]/div/div[2]/button[2]'
                ]
                
                carousel_button = self.browser.find_element(By.XPATH, locators[0])
                carousel_button.click()
                time.sleep(2)
                soup = BeautifulSoup(self.browser.page_source, 'html.parser')
                time.sleep(2)
                for img in soup.find_all("img", attrs={"class": "_6q-tv"}):
                    images_urls.append(img.get('src'))
                for _id in soup.find_all("a", attrs={"class": "FPmhX notranslate Qj3-a"}):
                    usernames.append(_id.get('title'))
                time.sleep(2)

                while self.isElementPresent(locators[1]):
                    carousel_button = self.browser.find_element(By.XPATH, locators[1])
                    carousel_button.click()
                    time.sleep(1)
                    soup = BeautifulSoup(self.browser.page_source, 'html.parser')
                    time.sleep(1)
                    for img in soup.find_all("img", attrs={"class": "_6q-tv"}):
                        images_urls.append(img.get('src'))
                    for _id in soup.find_all("a", attrs={"class": "FPmhX notranslate Qj3-a"}):
                        usernames.append(_id.get('title'))
                    time.sleep(1)

                images_urls = list(dict.fromkeys(images_urls))
                suggested = list(dict.fromkeys(usernames))

            except TimeoutException:
                print("Timed out waiting for page to load")

        self.browser.close()

        return images_urls, profile_pic, suggested

def nsfw_api_batch_post(input, suggested, username):
    """
    Llamada en batch al servicio https://github.com/eblancoh/nsfw_api
    montado en Heroku y obtención de las response con los scores
    """
    basedir = os.path.dirname(os.path.abspath(__file__))
    
    url = "https://nsfw-api.herokuapp.com/batch-classify"
    querystring = {"":""}

    payload = {"urls": input}
    payload = json.dumps(payload)
    headers = {
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.11.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "236b7128-d38c-4a2d-b4df-f9e4c6aa5556,fc8c41fc-24c0-4bf1-9539-f0e607c1e5ac",
        'Host': "nsfw-api.herokuapp.com",
        'accept-encoding': "gzip, deflate",
        'content-length': "441",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    try:
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        # En el caso de que no exista la carpeta porque o hayamos ejecutado app.py antes:
        if not os.path.exists(os.path.join(basedir, username)):
            os.makedirs(os.path.join(basedir, username))

        # Guardamos las scores en el fichero de destino con sus correspondientes urls:
        with open(os.path.join(basedir, username, 'scores_suggestions.json'), 'w') as outfile:
            json_obj = json.loads(response.text)

            for i in range(len(suggested)): 
                json_obj['predictions'][i]['username']=suggested[i]
                
            json_obj['predictions'] = sorted(json_obj['predictions'], key=lambda x : x['score'], reverse=True)
            #json.dump(json.loads(response.text), outfile, indent=4, separators=[',', ':'], sort_keys=True, ensure_ascii=False)
            json.dump(json_obj, outfile, indent=4, separators=[',', ':'], sort_keys=True, ensure_ascii=False)
            #add trailing newline for POSIX compatibility
            outfile.write('\n')
        #return response.text
        return json_obj
        
        
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

def scores_analyzer(payload):
    """
    Resumen estadístico de lo explícito del contenido de la cuenta pública
    """
    nsfw_scores = []
    for i in payload['predictions']:
        try:
            nsfw_scores.append(i['score'])
        except KeyError:
            continue

    quartiles = percentile(nsfw_scores, [25, 50, 75])
    # Calculamos min/max
    data_min, data_max = min(nsfw_scores), max(nsfw_scores)
    # 5-number summary
    print('---------------------------------------------')
    print('Statistical Summary for retrieved nsfw-scores')
    print('---------------------------------------------')
    print('Min: %.3f' % data_min)
    print('Q1: %.3f' % quartiles[0])
    print('Q2: %.3f' % quartiles[1])
    print('Q3: %.3f' % quartiles[2])
    print('Max: %.3f' % data_max)


def main():
    parser = argparse.ArgumentParser(
        description="Scrapes suggested friends profile pics urls of a private instagram user.",
        epilog=textwrap.dedent("""
        You can hide your credentials from the history, by reading your
        username from a local file:

        $ instagram-scraper @insta_args.txt user_to_scrape

        with insta_args.txt looking like this:
        -u=my_username
        -p=my_password
        """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@'
    )

    parser.add_argument('username', help='Instagram user(s) to scrape')
    parser.add_argument('--login-user', '--login_user', '-u', default=None, type=str, help='Instagram login user')
    parser.add_argument('--login-pass', '--login_pass', '-p', default=None, type=str, help='Instagram login password')
    
    args = parser.parse_args()

    if not args.username:
        raise ValueError('Must provide username')

    if (args.login_user and args.login_pass is None) or (args.login_user is None and args.login_pass) or (args.login_user and args.login_pass is None):
        raise ValueError('Must provide login user AND password.')

    scraper = PrivateIGScrapper(username=args.username, 
                                login_user=args.login_user, 
                                login_pass=args.login_pass, 
                                #driver='geckodriver')
                                driver='chromedriver')

    images_urls = scraper.suggested_imgs_urls()

    print("Calling NSFW API in Heroku for scores retrieval")

    preds = nsfw_api_batch_post(images_urls, args.username)
    print(scores_analyzer(json.loads(preds)))

if __name__ == '__main__':
    main()