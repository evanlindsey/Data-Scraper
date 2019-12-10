import os
import requests


class AffiliateScraper:

    url = 'https://www.crossfit.com/cf/find-a-box.php?page='
    filename = 'affiliates.json'
    the_file = None

    def __init__(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        self.the_file = open(self.filename, 'a')

    def write_to_file(self, content):
        self.the_file.write(content)

    def close_file(self):
        self.the_file.close()

    def process(self):
        self.write_to_file('[')
        i = 1
        while True:
            print(f'Scraping page #{i}')
            response = requests.get(f'{self.url}{i}').text
            formatted = response.replace(
                '{"affiliates":[', "").replace(']}', "")
            if formatted == '':
                break
            if i != 1:
                self.write_to_file(',')
            self.write_to_file(formatted)
            i += 1
        self.write_to_file(']')


class Main:

    def run(self):
        try:
            print('Scraping Affiliate JSON')
            scraper = AffiliateScraper()
            scraper.process()
        except Exception as e:
            print(f'Something went wrong:\n{str(e)}')
        finally:
            scraper.close_file()
            print('Finished successfully')


if __name__ == '__main__':
    Main().run()
