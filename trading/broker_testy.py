import abc
import os
from datetime import datetime as dt

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

import objsize


class BaseBrokerAPI:
    """
    Implementation of abstract broker API
    """
    __slots__ = ('_auth_file_path',)

    def __init__(self, auth_file_path: str) -> None:
        self._auth_file_path = auth_file_path

    @abc.abstractmethod
    def init(self) -> None:
        pass

    @abc.abstractmethod
    def go_long(self, asset: str, position_size: int) -> None:
        pass

    @abc.abstractmethod
    def go_short(self, asset: str, position_size: int) -> None:
        pass


class CMCMarketsAPI(BaseBrokerAPI):
    """
    Implementation of CMC Markets Broker
    """
    __slots__ = ('_driver', '_current_asset', 'is_ready')

    login_url = 'https://platform.cmcmarkets.com/#/login?b=CMC-CFD&r=PL&l=pl'
    login_button_xpath = '/html/body/div[1]/cmc-login/div/section/div[1]/' \
                         'div[1]/form/div[4]/input'

    asset_tab_xpaths = {
        'EURUSD': '/html/body/div[1]/header/div[2]/div[1]/div[2]/ul/li[1]',
        'DAX': '/html/body/div[1]/header/div[2]/div[1]/div[2]/ul/li[2]',
        'GBPUSD': '/html/body/div[1]/header/div[2]/div[1]/div[2]/ul/li[3]'}

    position_tab_xpaths = {
        'long': '/html/body/div[1]/main/div[3]/div/div[3]/div/div/section//'
                'div[@class="price-box buy stale"]',
        'short': '/html/body/div[1]/main/div[3]/div/div[3]/div/div/section//'
                 'div[@class="price-box sell stale"]'}

    take_position_xpath = ''

    def __init__(self, auth_file_path: str) -> None:
        super().__init__(auth_file_path)
        self._driver: selenium.webdriver = None
        self._current_asset: str = ''
        self.is_ready: bool = False

    def _set_driver(self) -> None:
        """
        Set selenium driver as Firefox without notifications
        """
        options = Options()
        options.set_preference("dom.webnotifications.enabled", False)
        driver = selenium.webdriver.Firefox(options=options)
        self._driver = driver

    def _read_auth_data(self) -> tuple:
        """
        Reads authenctication login data from text file
        :return: tuple with username and password
        """
        if os.path.isfile(self._auth_file_path):
            with open(self._auth_file_path, 'r') as f:
                data = f.readlines()
        else:
            raise IOError('Broker authentication file does not exist!')

        username = data[0].rstrip()
        password = data[1].rstrip()
        return username, password

    def _login(self) -> None:
        self._driver.get(self.login_url)
        username, password = self._read_auth_data()

        # Fill username and password fields
        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located(
            (By.NAME, 'username'))).send_keys(username)

        WebDriverWait(self._driver, 10).until(EC.presence_of_element_located(
            (By.NAME, 'password'))).send_keys(password)

        # Click Log In
        WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, self.login_button_xpath)))
        self._driver.find_element(By.XPATH, self.login_button_xpath).click()

    def init(self) -> None:

        if not self.is_ready:
            self._set_driver()
            self._login()
            self.is_ready = True

    def close(self) -> None:

        self.is_ready = False
        if self._driver.service.process:
            self._driver.quit()

    def _switch_asset_tab(self, asset: str) -> None:
        """
        Changes trading tab on website to specific asset
        if it is different than current
        :param asset: name of asset to trade, for example 'EURUSD'
        """
        if asset != self._current_asset:
            WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, self.asset_tab_xpaths[asset])))
            self._driver.find_element(
                By.XPATH, self.asset_tab_xpaths[asset]).click()

    def _swtich_position_type(self, position_type: str) -> None:
        """
        Waits for spinner to dissapear and click long or short tab
        :param position_type: 'long' or 'short'
        """
        WebDriverWait(self._driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, self.position_tab_xpaths[position_type])))

        element = self._driver.find_element(
            By.XPATH, self.position_tab_xpaths[position_type])
        self._driver.execute_script("arguments[0].click();", element)

    def _take_position(self) -> None:
        """
        Clicks on take position button
        """
        # TODO to finish
        pass
        # WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable(
        #     (By.XPATH, self.take_position_xpath)))
        # self._driver.find_element(By.XPATH, self.take_position_xpath).click()

    def go_long(self, asset: str, position_size: int) -> None:
        """
        Takes long position on specific asset
        """
        self._switch_asset_tab(asset=asset)
        self._swtich_position_type(position_type='long')
        self._take_position()
        self._current_asset = asset

    def go_short(self, asset: str, position_size: int) -> None:
        """
        Takes short position on specific asset
        """
        self._switch_asset_tab(asset=asset)
        self._swtich_position_type(position_type='short')
        self._take_position()
        self._current_asset = asset


broker_api = CMCMarketsAPI('/home/rafal/Desktop/GITHUB/cmc_markets.txt')
broker_api.init()
# print(objsize.get_deep_size(broker_api))
