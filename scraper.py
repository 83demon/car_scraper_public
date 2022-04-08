from utils import Logger, DataBase, StrTools, Randomness
from selenium import webdriver


class Scraper:
    def __init__(self):
        self._driver = webdriver.Firefox()
        self._time_to_load_page = None

    def _open_url(self, url):
        self._driver.get(url)

    def _find_element_by_text(self, text: str):
        return self._driver.find_element_by_xpath(f"//*[contains(text(), '{text}')]")

    def _find_element_by_link_text(self, text):
        return self._driver.find_element_by_link_text(text)

    def _find_multiple_elements_by_link_text(self, text) -> list:
        return self._driver.find_elements_by_partial_link_text(text)

    @staticmethod
    def _click_on_element(element):
        element.click()

    def _go_back(self):
        self._driver.back()

    def _close(self):
        self._driver.quit()

    def wait_seconds(self,num):
        self._driver.implicitly_wait(num)
        return num


class ToyotaScraper(Scraper):
    def __init__(self, site_url, random_seed, db_path, log_path,page=1):
        super().__init__()
        self._site_url = site_url
        self._str_tools = StrTools()
        self._database = DataBase(db_path)
        self._page = page
        self._site_pages_limit = 99
        self._limit_of_cars_on_page = 10
        self._logger = Logger(log_path)
        self._randomness = Randomness(random_seed, self._driver)
        self._seconds_to_wait_in_cycle = [2,4]  # time to wait after scanning each car
        self._seconds_to_wait_after_cycle = [25,35]
        self._random_seconds_time = 4
        self._wait_every_n_times = 3
        self._time_to_load_page = 1

    def main(self):
        """Opens cars, gathers data and goes to the next page"""
        try:
            self._open_url(self._site_url)
            for page in range(self._page-1, self._site_pages_limit):
                self.wait_seconds(self._time_to_load_page)
                for index in range(self._limit_of_cars_on_page):
                    all_cars = self._find_all_cars()
                    next_car = self._find_next_car(all_cars, index)
                    self._open_new_car(next_car)
                    self.wait_seconds(self._time_to_load_page)
                    data = self._gather_data()
                    log_data = f'Page: {self._page}, cars on the page: {index+1}/{self._limit_of_cars_on_page}, total progress: ' \
                               f'{((self._page-1)*self._limit_of_cars_on_page)+(index+1)}/' \
                               f'{self._site_pages_limit*self._limit_of_cars_on_page}'
                    self._database.archive(data)
                    if (index%self._wait_every_n_times==0):
                        self._randomness.wait_rnm_seconds(self._random_seconds_time)
                    time_ = self._randomness.wait2_rnm_seconds(self._seconds_to_wait_in_cycle[0],self._seconds_to_wait_in_cycle[1])
                    self._logger.archive(log_data + '\tAwaited '+str(time_)+' seconds')
                    self._go_back()
                    self.wait_seconds(self._time_to_load_page)
                self._logger.unarchive()
                self._database.unarchive()
                self._randomness.wait2_rnm_seconds(self._seconds_to_wait_after_cycle[0], self._seconds_to_wait_after_cycle[1])
                self._open_next_page()
        except Exception as e:  # for emergency terminating
            self._database.unarchive()
            self._logger.archive(e)
            self._logger.unarchive()
        else:
            self._logger.write_to_file('The job has been done')
        finally:
            self._driver.close()

    def _open_new_car(self, element):
        self._click_on_element(element)

    def _find_next_car(self, all_cars, index):
        return all_cars[index]

    def _find_all_cars(self):
        """
        Returns the generator object which contains all cars elements on the page
        We assume that button 'More' opens the car info window
        """
        return self._find_multiple_elements_by_link_text('More')

    def _open_next_page(self):
        if self._page < self._site_pages_limit:  # limit of the site
            self._page += 1
            page_element = self._find_element_by_link_text(str(self._page))
            self._click_on_element(page_element)

    def _gather_data(self):
        data = {}
        sold_status = 'Sold status'
        attributes = ['Final bid','Mileage','Primary Damage','Secondary Damage','Year','VIN','Condition','Auction',
                      'Lot number','Date of sale','Engine','Seller','Documents','Location','Estimated Retail Value',
                      'Estimated Repair Cost','Transmission','Body color','Drive','Fuel','Keys','Notes']
        data[sold_status] = self._identify_sold_status()
        for attr in attributes:
            temp = self._str_tools._str_adjust(attr,self._find_element_by_text(attr).text)
            data[attr] = temp
        data['URL'] = self._driver.current_url
        data['Car images'] = self._search_car_images()
        return data

    def _identify_sold_status(self):
        statuses = ['Sold', 'Timed auction', 'I buy fast', 'On approval']
        for status in statuses:
            try:
                img = self._driver.find_element_by_xpath(f"//img[@title='{status}']")
                if img:
                    return status
            except:
                continue
        return "No info"

    def _search_car_images(self):
        model = 'corolla'
        images = self._driver.find_elements_by_tag_name('img')
        res = set()
        for image in images:
            temp = image.get_attribute('src')
            if model in temp:
                res.add(temp)
        return res

    def close(self):
        return self._close()


"""toyota_scraper = ToyotaScraper("https://en.bidfax.info/toyota/corolla/f/from-year=2021/to-year=2021/page/6/",
                               83,'toyota_corolla_2021.csv','toyota_corolla_2021_log.txt', page=6)
toyota_scraper.main()"""

