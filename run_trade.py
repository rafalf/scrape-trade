#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
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
        if platform == 'darwin':  # OSX
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Chrome('C:\gitprojects\drivers\chromedriver.exe')

    def scrape_soup(self, r):

        self.driver.get(self.site_url)

        if r:
            self._select_report(r)

        for _ in range(60):
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
            logger.info('Did not scrape table. Is the site live?')

    @staticmethod
    def _scrape_table(table):

        rows = table.findAll("tr")

        tbl_data = []
        for row in rows:
            tds_ = row.find_all("td")
            row_data = []
            for ctr, td in enumerate(tds_):
                if td.text.strip().count('-'):
                    logger.info('Table not ready for scraping yet')
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
                else:
                    row_data.append(d)
            tbl_data.append(row_data)
            logger.info('Scraped row data: {}'.format(row_data))
        return tbl_data

    def tear_down(self):
        if self.driver:
            self.driver.quit()

    def stdout_options(self):

        self.driver.get(self.site_url)

        try:
            op_el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "lists")))
            select = Select(op_el)
            opts_ = select.options
            for opt_ in opts_:
                logger.info('report: {}'.format(opt_.get_attribute('value')))
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

    scrape.scrape_soup(report)
    scrape.tear_down()