import threading
import queue
import time

from scrapy.http import HtmlResponse
from Chuanqi.selenium_request import SeleniumRequest
from Chuanqi.utils.selenium_util import SeleniumUtil


class SeleniumMiddleware:
    def __init__(self, driver_pool_size=10):
        self.driver_pool = queue.Queue(maxsize=driver_pool_size)
        self.lock = threading.Lock()
        self.init_driver_pool(driver_pool_size)

    def init_driver_pool(self, size):
        for _ in range(size):
            self.driver_pool.put(self.create_driver())

    def create_driver(self):
        return SeleniumUtil().driver

    def process_request(self, request, spider):
        if isinstance(request, SeleniumRequest):
            driver = self.driver_pool.get(timeout=10)
            try:
                request.meta['driver'] = driver
                driver.get(request.url)

                # 智能等待
                if request.meta.get('wait_for'):
                    time.sleep(request.meta['wait_for'])

                body = driver.page_source.encode('utf-8')
                response = HtmlResponse(
                    url=driver.current_url,
                    body=body,
                    encoding='utf-8',
                    request=request,
                )
                self.driver_pool.put(driver)
                return response
            except Exception as e:
                spider.logger.error(f"Selenium error: {str(e)}")
                if driver:
                    driver.quit()  # 销毁问题driver
                    self.driver_pool.put(self.create_driver())  # 补充新driver
                return None

        return None