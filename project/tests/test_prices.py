import unittest
import time

from price_api import price_api


class TestPriceAPI(unittest.TestCase):

    TEST_ASSET = 'EURUSD'

    # def test_price_read(self):
    #     for asset in self.ASSET_LIST:
    #         with self.subTest(msg=f'Testing Price API price read for {asset}'):
    #             asset_api = price_api.PriceAPIFactory.get_price_api(asset=asset)
    #             price = asset_api.get_price()
    #             print(price)
    #             self.assertEqual(type(price), float)

    def setUp(self) -> None:
        self.price_api = price_api.PriceAPIFactory.get_price_api(asset=self.TEST_ASSET)

    def tearDown(self) -> None:
        self.price_api.close()

    def test_price_read(self):
        price = self.price_api.get_price()
        self.assertEqual(type(price), float)


if __name__ == '__main__':
    unittest.main()
