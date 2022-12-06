from scraper.utils import read_excel_file
from scraper.items import ScraperItem
from scraper import PROJECT_ROOT_DIR

from urllib.parse import urlencode

import scrapy


class HeadersMiddleware:
    def process_request(self, request, spider):
        headers = {
            "DNT": "1",
            "Origin": "https://www.noon.com",
            "Referer": "https://www.noon.com/",
        }

        request.headers.update(headers)


class LegoYellowblocksMeSpider(scrapy.Spider):
    name = "www.noon.com"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "DOWNLOADER_MIDDLEWARES": {
            HeadersMiddleware: 1100,
        },
    }

    API_URL = "https://www.noon.com/uae-en/search/"
    API_URL_PARAMS = {
        "limit":"50",
        "q":"10274",
    }

    def start_requests(self):
        params = self.API_URL_PARAMS.copy()
        df = read_excel_file(filepath=f"{PROJECT_ROOT_DIR}/products.xlsx")
        for item in df[["Product Number", "Product Name EN"]].values.tolist():
            product_number, product_name = item
            params["query"] = product_number
            yield scrapy.Request(
                url=f"{self.API_URL}?{urlencode(params)}",
                callback=self.parse,
                meta={
                    "_product_number": product_number,
                    "_product_name": product_name,
                },
            )

    def parse(self, response):
        data = response.json()
        if data.get("products"):
            product = data["products"][0]
            price = product.get("crossedPrice", {}).get("value", 0)
            discount_price = product.get("price", {}).get("value", 0)

            yield ScraperItem(
                product_number=response.meta["_product_number"],
                product_name=response.meta["_product_name"],
                discount_price=discount_price,
                price=price,
            )
