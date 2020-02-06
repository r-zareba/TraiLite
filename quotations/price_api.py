import abc
# import requests

import selenium
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import (InvalidSessionIdException,
                                        WebDriverException,
                                        NoSuchWindowException,
                                        StaleElementReferenceException)


class BasePriceAPI:
    """ Base implementation of Selenium type price getters """
    __slots__ = ('_asset', 'is_ready')

    @property
    @abc.abstractmethod
    def PriceAPIExceptions(self):
        """ Required class static attribute """
        pass

    def __init__(self, asset: str) -> None:
        self._asset = asset
        self.is_ready = False

    @abc.abstractmethod
    def init(self) -> None:
        pass

    @abc.abstractmethod
    def get_price(self) -> float:
        pass

    @abc.abstractmethod
    def close(self) -> None:
        pass


class TradingViewAPI(BasePriceAPI):
    """ Implementation of Trading View prices using Selenium """
    __slots__ = ('_asset_url', '_driver', '_price_element')

    PriceAPIExceptions = (
        InvalidSessionIdException,
        WebDriverException,
        AttributeError,
        NoSuchWindowException,
        StaleElementReferenceException)

    price_url = 'https://www.tradingview.com/symbols/'
    price_xpath = '/html/body/div[2]/div[3]/div/header/div/div[3]/div[1]/' \
                  'div/div/div/div[1]/div[1]'

    def __init__(self, asset: str) -> None:
        super().__init__(asset)
        self._asset_url: str = self.price_url + self._asset
        self._driver: selenium.webdriver = None
        self._price_element: selenium.webdriver = None

    def init(self) -> None:
        """ Sets the driver and price element - prepares for price reading """
        if not self.is_ready:
            self._set_driver()
            self._set_price_element()
            self.is_ready = True

    def _set_driver(self) -> None:
        """ Set selenium driver as Firefox without notifications """
        options = Options()
        options.set_preference("dom.webnotifications.enabled", False)
        driver = selenium.webdriver.Firefox(options=options)
        self._driver = driver

    def _set_price_element(self) -> None:
        """ Set price element to read """
        self._driver.get(self._asset_url)
        try:
            WebDriverWait(self._driver, 15).until(
                EC.presence_of_element_located((By.XPATH, self.price_xpath)))
        except TimeoutException:
            print(f'Price element not found!\nError occured in: {self}')
            print('Closing current session...')
            self.close()
        else:
            self._price_element = self._driver.find_element(
                By.XPATH, self.price_xpath)

    def get_price(self) -> float:
        if self.is_ready:
            return float(self._price_element.text)

    def close(self) -> None:
        self.is_ready = False
        if self._driver.service.process:
            self._driver.quit()


class PriceAPIFactory:
    """ Implementation of Price API Factory to get best working Price API """
    __slots__ = ()

    @staticmethod
    def get_price_api(asset: str) -> BasePriceAPI:
        """
        Returns Price API object, that had succesfully set price element """
        for PriceAPI in BasePriceAPI.__subclasses__():
            price_api = PriceAPI(asset)
            price_api.init()

            if price_api.is_ready:
                return price_api
            continue

        raise ConnectionError('None of Price APIs is working! '
                              'Check internet connection!')


# class FreeForexAPI(BasePriceAPI):
#     """
#     Free Forex API class
#     """
#     APIExceptions = (
#         AttributeError
#     )
#
#     def __init__(self, asset: str) -> None:
#         super().__init__(asset)
#         self._session = None
#
#     @property
#     def ready(self):
#         return self._ready
#
#     def init(self) -> None:
#         self._session = requests.Session()
#
#     def get_price(self):
#         try:
#             data = self.session.get(
#                 f'https://www.freeforexapi.com/api/live?pairs={self._asset}')
#         except Exception as e:
#             print('asd')
#         else:
#             return data.json()['rates'][self._asset]['rate']
#
#     def close(self):
#         self._session.close()
