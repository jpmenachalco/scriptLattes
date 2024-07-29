#!/usr/bin/python
# encoding: utf-8

import argparse
import bs4
#import logging
import time
import os
import urllib.request, urllib.parse, urllib.error
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, TimeoutException
from selenium.webdriver.chrome.service import Service
import platform

import warnings
warnings.filterwarnings("ignore")

RESULTS_DIR = os.environ.get('DATA_DIR', 'htmls')
URL = 'http://buscatextual.cnpq.br/buscatextual/preview.do?metodo=apresentar&id={0}'
URL_LATTES_ID10 = 'http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id={0}'
URL_LATTES_ID16 = 'http://lattes.cnpq.br/{0}'


class LattesRobot:
    def __init__(self, driver_path, results_dir):
        #logging.getLogger('selenium').setLevel(logging.WARNING)
        self.driver_path = driver_path
        self.results_dir = results_dir
        self.driver = None
        #self.ua = UserAgent()
        self.identifiers = set()
        self.downloaded_identifiers = set()
        self.sleep_time = 4
        self.lid_type = -1
        self.initialize()

    def initialize(self):
        if not os.path.exists(self.driver_path):
            #logging.error('Invalid driver path: %s' % self.driver_path)
            exit(1)

        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def load_codes(self, id_lattes):
        self.identifiers.add(id_lattes)
        self._set_lid_type()

    def check_downloaded_cvs(self):
        self.downloaded_identifiers = {h for h in os.listdir(self.results_dir) if len(h) == self.lid_type}


    def create_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false') 
        chrome_options.add_argument("headless")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', {'download.default_directory': self.results_dir})
 
        so = platform.system()
        if so == 'Windows':
            chrome_driver_path = os.path.abspath("chromedriver.exe")
        elif so == 'Linux':
            chrome_driver_path = os.path.abspath("chromedriver")
        else:
            print('Sistema Operacional não identificado')
            
        service = Service(chrome_driver_path)
 
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Erro ao inicializar o driver: {e}")
 


    def collect_html_cvs(self, start, end):
        total_lids = len(list(self.identifiers)[start:end])

        for identifier in sorted(self.identifiers)[start:end]:
            lids = self._get_lids_10_16(identifier)

            if lids[10]:
                if lids[self.lid_type] not in self.downloaded_identifiers:
                    self._execute_js(lids)


    def store_html(self, lid, page):
        with open(os.path.join(self.results_dir, lid), 'wb') as fout:
            try:
                #data = page.encode('iso-8859-1', 'replace').strip()
                data = page.encode('utf-8', 'replace').strip()
            except UnicodeEncodeError:
                data = page.encode('utf-8').strip()

            if data:
                fout.write(data)

    def _execute_js(self, lids):
        self.driver.get(URL.format(lids[10]))
        time.sleep(self.sleep_time)

        cmd_open_cv = 'abreCV()'
        self.driver.execute_script(cmd_open_cv)
        time.sleep(self.sleep_time)

        self.driver.switch_to.window(self.driver.window_handles[-1])

        if not lids[16]:
            lids[16] = self._extract_lid16(self.driver.page_source)

            if self.lid_type == 16 and len(lids[16]) != 16:
                #logging.error('It was not possible to obtain Lattes identifier with 16 chars for %s' % str(lids))
                return

        self.store_html(lids[self.lid_type], self.driver.page_source)

    def _get_lids_10_16(self, lid):
        lids = {10: '', 16: ''}

        if len(lid) == 10:
            lids[10] = lid

        if len(lid) == 16:
            lids[16] = lid

            self.driver.get(URL_LATTES_ID16.format(lid))
            lid10 = urllib.parse.parse_qs(urllib.parse.urlparse(self.driver.current_url.encode()).query)[b'id'][0].decode('utf-8')

            if len(lid10) == 10:
                lids[10] = lid10

        return lids

    def _extract_lid16(self, page_source):
        soup = bs4.BeautifulSoup(page_source, 'html.parser')
        lid16 = soup.find('span', attrs={'style': 'font-weight: bold; color: #326C99;'}).text.encode()

        if len(lid16) == 16 and lid16.isdigit():
            return lid16

    def _set_lid_type(self):
        if len(self.identifiers) > 0:
            ld = len(list(self.identifiers)[0])
            self.lid_type = ld


def __get_data(id_lattes, diretorio):
    rob = LattesRobot(driver_path="./chromedriver", results_dir=diretorio)
    print(f"Baixando CV Lattes: {id_lattes}. Este processo pode demorar alguns segundos.")
    rob.load_codes(id_lattes)
    rob.check_downloaded_cvs()
    rob.create_driver()

    try:
        #logging.info('Collecting cvs (there are %d cvs to be collected)...' % len(rob.identifiers))
        rob.collect_html_cvs(0, None)
    #except KeyboardInterrupt:
    #    logging.info('Execution was interrupted')
    finally:
        rob.driver.quit()




def baixaCVLattes(id_lattes, diretorio ):
    
    # caso nao for baixado, tenta novamente ate 5 vezes
    count = 5
    while count>0:
        __get_data(id_lattes, diretorio)

        if os.path.exists ( diretorio+"/"+id_lattes ):
            break
        else:
            count = count - 1

    #raise Exception("Nao foi possivel baixar o CV Lattes em 5 tentativas")
