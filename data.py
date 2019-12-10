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
        html = self.driver.execute_script(
            'return document.documentElement.innerHTML;')
        return BeautifulSoup(html, 'html.parser')

    def pull_data(self):
        data = []
        soup = self.scrape_page()
        results = soup.findAll('div', {'class': 'dataset-content'})
        for res in results:
            entry = {}
            # name
            name = res.find('h3', {'class': self.name_class}).a
            entry["Name"] = name.get_text() if name is not None else ""
            # organization type
            org_type = res.find('div', {'class': self.org_type_class})
            entry["OrganizationType"] = org_type.span.span.get_text(
            ) if org_type is not None else ""
            # organization
            organization = res.find('div', {'class': self.contents_class}).p
            entry["Organization"] = organization.get_text(
            )[:-2] if organization is not None else ""
            # description
            description = res.find('div', {'class': self.contents_class}).div
            entry["Description"] = description.get_text(
            ) if description is not None else ""
            # formats
            formats = res.find('ul', {'class': self.formats_class})
            if formats is not None:
                format_list = [x.a.get_text() for x in formats.findAll('li')]
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

    def get_results(self, count):
        data = self.pull_data()
        while int(len(data)) < int(count):
            if self.check_pagination():
                data.extend(self.pull_data())
            else:
                break
        return data[0:int(count)]

    def teardown(self):
        self.driver.quit()


class Main:

    def write_results(self, results):
        print(f'Result Set Count:\n{len(results)}')
        with open('data.json', 'w') as outfile:
            json.dump(results, outfile)

    def run(self):
        try:
            # input
            term = input('Enter a term to search on Data.gov:\n')
            count = input('Enter the target result set count:\n')
            # actions
            scraper = DataScraper()
            scraper.search_term(term)
            results = scraper.get_results(count)
            # output
            self.write_results(results)
        except Exception as e:
            print(f'Something went wrong:\n{str(e)}')
        finally:
            scraper.teardown()


if __name__ == '__main__':
    Main().run()
