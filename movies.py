import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = 'https://www.imdb.com/chart/top'


class UiScraper:

    driver = None

    header_css = 'h1.header'
    header_text = 'Top Rated Movies'

    def init_driver(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.driver.get(url)
        self.driver.maximize_window()

    def wait_for_load(self):
        wait = WebDriverWait(self.driver, 10)
        element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, self.header_css)))
        assert element.text == self.header_text, f'Header text equals {self.header_text}'

    def scrape(self):
        self.init_driver()
        self.wait_for_load()
        html = self.driver.execute_script(
            'return document.documentElement.innerHTML;')
        self.driver.quit()
        return BeautifulSoup(html, 'html.parser')


class HttpScraper:

    def scrape(self):
        html = requests.get(url).text
        return BeautifulSoup(html, 'html.parser')


class Actions:

    def get_titles(self, soup):
        cols = soup.findAll('td', {'class': 'titleColumn'})
        return [x.find('a').get_text() for x in cols]

    def print_list(self, the_list):
        for item in the_list:
            print(item)


class Main:

    def run(self):
        try:
            # input
            method = input(
                'Enter (1) to use HTTP Request\nEnter (2) to use Web UI\n')
            if method == '1':
                scraper = HttpScraper()
            elif method == '2':
                scraper = UiScraper()
            else:
                raise Exception('Invalid input')
            # actions
            soup = scraper.scrape()
            actions = Actions()
            titles = actions.get_titles(soup)
            # output
            actions.print_list(titles)
        except Exception as e:
            print(f'Something went wrong:\n{str(e)}')


if __name__ == '__main__':
    Main().run()
