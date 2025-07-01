import logging
import random
import time

import requests


class SmartProxyMiddleware:
    PROXY_API = "http://proxy-service:5000/get_proxy"
    BAD_PROXY_TTL = 600  # 10分钟

    def __init__(self):
        self.proxy_pool = []
        self.bad_proxies = {}
        self.last_refresh = 0
        self.refresh_interval = 300  # 5分钟

    def get_proxy(self):
        # 刷新代理池
        if time.time() - self.last_refresh > self.refresh_interval:
            self.refresh_proxy_pool()

        # 清理过期坏代理
        self.clean_bad_proxies()

        if self.proxy_pool:
            proxy = random.choice(self.proxy_pool)
            return proxy

        return None

    def refresh_proxy_pool(self):
        try:
            resp = requests.get(self.PROXY_API, params={'count': 50}, timeout=10)
            if resp.status_code == 200:
                self.proxy_pool = resp.json().get('proxies', [])
                self.last_refresh = time.time()
        except Exception as e:
            logging.error(f"Proxy refresh failed: {str(e)}")

    def clean_bad_proxies(self):
        now = time.time()
        for proxy in list(self.bad_proxies.keys()):
            if now - self.bad_proxies[proxy] > self.BAD_PROXY_TTL:
                del self.bad_proxies[proxy]

    def process_request(self, request, spider):
        if request.meta.get('proxy_strategy', 'none') != 'none':
            proxy = self.get_proxy()
            if proxy:
                request.meta['proxy'] = proxy
                spider.logger.debug(f"Using proxy: {proxy}")

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('proxy')
        if proxy:
            # 标记坏代理
            self.bad_proxies[proxy] = time.time()
            # 从池中移除
            if proxy in self.proxy_pool:
                self.proxy_pool.remove(proxy)

            spider.logger.warning(f"Proxy failed: {proxy}, reason: {str(exception)}")

            # 强制刷新策略
            if request.meta.get('proxy_strategy') == 'force_change':
                new_proxy = self.get_proxy()
                if new_proxy:
                    request.meta['proxy'] = new_proxy
                    return request