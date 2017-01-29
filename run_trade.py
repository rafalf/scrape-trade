#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from sys import platform
from selenium.webdriver.common.by import By
import logging
import time
from bs4 import BeautifulSoup
import sys
import getopt
import csv

logger = logging.getLogger('scrape')


class Scrape:

    def __init__(self):

        self.site_url = 'https://www.iextrading.com/apps/tops/'
        self.csv_file = None
        if platform == 'darwin':  # OSX
            self.driver = webdriver.Chrome()
        elif platform == 'linux' or platform == 'linux2':  # headless
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
            self.driver = webdriver.Chrome()
        else:  # windows
            self.driver = webdriver.Chrome('chromedriver.exe')

    def scrape_soup(self, r):

        self.driver.get(self.site_url)

        if r:
            self._select_report(r)
            self.csv_file = "{}_{}.csv".format(time.strftime("%Y%m%d%H%M", time.localtime()), r)
        else:
            self.csv_file = "{}_{}.csv".format(time.strftime("%Y%m%d%H%M", time.localtime()), 'top')

        for _ in range(30):
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            table = soup.find("table", {"id": "quotesTable"})
            table_ = self._scrape_table(table)
            if table_:
                logger.info('Table scraped! ')
                break
            else:
                time.sleep(1)
        else:
            logger.info('Is the site live? Found placeholders on page. Scrape either way')
            table_ = self._scrape_table(table, True)

        self._write_row(['No', 'Ticker', 'Mkt %', 'Shares', 'Bid Quantity', 'Bid Price',
                         'Ask Price', 'Ask Quantity', 'Last Sale Price', 'Last Sale Quantity'])

        table_.pop(0)  # off header
        for wr in table_:
            self._write_row(wr)

    @staticmethod
    def _scrape_table(table, force=False):

        rows = table.findAll("tr")

        tbl_data = []
        for row in rows:
            tds_ = row.find_all("td")
            row_data = []
            for ctr, td in enumerate(tds_):
                if td.text.strip().count('-') and not td.text.strip().count('--:--:'):
                    if not force:
                        logger.info('Table not ready for scraping')
                        return False
                # drop time
                if ctr in [1, 6]:
                    d = td.text.strip()[:-8]
                else:
                    d = td.text.strip()
                # split x
                if d.count(u'\xd7'):
                    dsplit = d.split(u'\xd7')
                    row_data.append(dsplit[0].strip())
                    row_data.append(dsplit[1].strip())
                elif d.count('%'):
                    row_data.append(d.rstrip('%'))
                else:
                    row_data.append(d)
            tbl_data.append(row_data)
            logger.info('Scraped row data: {}'.format(row_data))
        return tbl_data

    def _write_row(self, row):
        with open(self.csv_file, 'ab') as hlr:
            wrt = csv.writer(hlr, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            wrt.writerow(row)
            logger.info('Add row: {}'.format(row))

    def tear_down(self):
        if self.driver:
            self.driver.quit()

    def stdout_options(self):

        self.driver.get(self.site_url)

        try:
            o = []
            op_el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "lists")))
            select = Select(op_el)
            opts_ = select.options
            for opt_ in opts_:
                option = opt_.get_attribute('value')
                logger.info('report: {}'.format(option))
                o.append(option)
            return o
        except TimeoutException:
            logger.error('Is the page live? Timed out on the reports select element')

    def _select_report(self, value):

        try:
            op_el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "lists")))
            select = Select(op_el)
            select.select_by_value(value)
        except TimeoutException:
            logger.error('Is the page live? Timed out on the reports select element')


if __name__ == '__main__':

    print_report = None
    report = None

    timestamp = time.strftime('%d%m%y', time.localtime())
    file_hndlr = logging.FileHandler('output.log')
    logger.addHandler(file_hndlr)
    console = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console)
    ch = logging.Formatter('[%(levelname)s] %(message)s')
    console.setFormatter(ch)
    file_hndlr.setFormatter(ch)
    logger.setLevel('DEBUG')
    console.setLevel(logging.getLevelName('DEBUG'))

    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "vr:p", ["verbose", "report=", "print-reports"])
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-r", "--print-reports"):
            print_report = True
        elif opt in ("-r", "--report"):
            report = arg

    logger.info('CLI args: {}'.format(opts))

    scrape = Scrape()

    if print_report:
        scrape.stdout_options()
        scrape.tear_down()
        sys.exit(1)

    if report != 'all':
        scrape.scrape_soup(report)
    else:
        for option_ in scrape.stdout_options():
            if option_ != 'mylist':
                scrape.scrape_soup(option_)
    scrape.tear_down()