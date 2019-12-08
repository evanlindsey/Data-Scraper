import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


class DataScraper:

    driver = None
    wait = None

    url = 'https://data.gov'
    home_title = 'Data.gov'
    search_xpath = '//input[@type=\'search\']'

    catalog_title = 'DATA CATALOG'
    catalog_header_xpath = '//div[@class=\'main-heading\']/h1'
    next_icon_xpath = '//li/a[text()=\'»\']'

    name_class = 'dataset-heading'
    org_type_class = 'organization-type-wrap'
    contents_class = 'notes'
    formats_class = 'dataset-resources unstyled'

    def __init__(self):
        self.driver = webdriver.Chrome('./drivers/chromedriver.exe')
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.url)
        self.driver.maximize_window()
        assert self.driver.title == self.home_title, f'Page title equals {self.home_title}'

    def search_term(self, term):
        search = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.search_xpath)))
        search.clear()
        search.send_keys(term)
        search.send_keys(Keys.RETURN)

    def scrape_page(self):
        header = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, self.catalog_header_xpath)))
        assert self.catalog_title in header.text, f'Results header equals {self.catalog_title}'
        html = self.driver.execute_script(
            'return document.documentElement.innerHTML;')
        return BeautifulSoup(html, 'html.parser')

    def pull_data(self):
        data = []
        soup = self.scrape_page()
        results = soup.findAll('div', {'class': 'dataset-content'})
        for res in results:
            entry = {}
            name = res.find('h3', {'class': self.name_class})
            entry["Name"] = name.find(
                'a').get_text() if name is not None else ""
            org_type = res.find('div', {'class': self.org_type_class})
            entry["OrganizationType"] = org_type.find('span').find(
                'span').get_text() if org_type is not None else ""
            contents = res.find('div', {'class': self.contents_class})
            entry["Organization"] = contents.find('p').get_text()[
                :-2] if contents is not None else ""
            entry["Description"] = contents.find(
                'div').get_text() if contents is not None else ""
            formats = res.find('ul', {'class': self.formats_class})
            if formats is not None:
                format_list = [x.find('a').get_text()
                               for x in formats.findAll('li')]
                entry["Formats"] = ','.join(format_list)
            else:
                entry["Formats"] = ""
            data.append(entry)
        return data

    def check_pagination(self):
        try:
            next_icon = self.driver.find_element_by_xpath(self.next_icon_xpath)
            next_icon.click()
            return True
        except NoSuchElementException:
            return False

    def teardown(self):
        self.driver.quit()


class Main():

    scraper = None

    def get_results(self, count):
        data = self.scraper.pull_data()
        while int(len(data)) < int(count):
            if self.scraper.check_pagination():
                data.extend(self.scraper.pull_data())
            else:
                break
        return data[0:int(count)]

    def write_results(self, results):
        print(f'Result Set Count:\n{len(results)}')
        with open('data.json', 'w') as outfile:
            json.dump(results, outfile)

    def run(self):
        try:
            term = input('Enter a term to search on Data.gov:\n')
            count = input('Enter the target result set count:\n')
            self.scraper = DataScraper()
            self.scraper.search_term(term)
            results = self.get_results(count)
            self.write_results(results)
        except Exception as e:
            print(f'Something went wrong:\n{str(e)}')
        finally:
            self.scraper.teardown()


if __name__ == '__main__':
    Main().run()
