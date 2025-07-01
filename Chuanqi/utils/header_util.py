import random

from fake_useragent import UserAgent

# 全局基础请求头
BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers',
}

# 站点特定请求头配置
SITE_SPECIFIC_HEADERS = {
    # 电商类站点
    101: {
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    },
    # 新闻类站点
    201: {
        'Referer': 'https://news.google.com/',
        'DNT': '1',
        'Cache-Control': 'max-age=0',
    },
    # API接口类
    301: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {token}',
        'Origin': 'https://api.example.com',
    }
}

# 移动端请求头模板
MOBILE_HEADERS_TEMPLATE = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android {version}; {model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36',
    'X-Wap-Profile': 'http://wap.samsung.com/uaprof/{model}.xml',
    'Sec-CH-UA-Mobile': '?1'
}

# PC端请求头模板
DESKTOP_HEADERS_TEMPLATE = {
    'User-Agent': 'Mozilla/5.0 ({system}; {os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36',
    'Sec-CH-UA': '"Google Chrome";v="{chrome_ver}", "Chromium";v="{chrome_ver}", "Not=A?Brand";v="24"',
    'Sec-CH-UA-Platform': '{platform}'
}


class HeaderGenerator:
    def __init__(self):
        self.ua = UserAgent()
        self.user_agent_pool = self._init_user_agent_pool()
        self.referer_pool = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.baidu.com/',
            'https://www.yahoo.com/',
            'https://www.duckduckgo.com/'
        ]

    def _init_user_agent_pool(self, size=100):
        """初始化User-Agent池"""
        pool = []
        for _ in range(size // 2):
            # 桌面端
            pool.append(self.ua.chrome)
            pool.append(self.ua.firefox)
            pool.append(self.ua.safari)
            # 移动端
            pool.append(self.ua.android)
            pool.append(self.ua.iphone)
        return pool

    def get_random_user_agent(self):
        """获取随机User-Agent"""
        return random.choice(self.user_agent_pool)

    def get_headers(self, site_id=None, is_mobile=False, extra_headers=None):
        """
        生成完整的请求头
        :param site_id: 站点ID，用于加载站点特定头
        :param is_mobile: 是否为移动端
        :param extra_headers: 额外添加的请求头
        :return: 完整的请求头字典
        """
        headers = BASE_HEADERS.copy()

        # 添加User-Agent
        headers['User-Agent'] = self.get_random_user_agent()

        # 添加Referer策略
        headers['Referer'] = self._get_referer_strategy(site_id)

        # 添加站点特定头
        if site_id and site_id in SITE_SPECIFIC_HEADERS:
            site_headers = SITE_SPECIFIC_HEADERS[site_id].copy()
            # 处理需要动态生成的值
            for key, value in site_headers.items():
                if isinstance(value, str) and '{' in value:
                    site_headers[key] = self._render_dynamic_value(value)
            headers.update(site_headers)

        # 添加移动端特有头
        if is_mobile:
            mobile_headers = self._generate_mobile_headers()
            headers.update(mobile_headers)
        # # 添加额外头
        # if extra_headers:
        #     headers.update(extra_headers)

        return headers

    def _get_referer_strategy(self, site_id):
        """智能Referer策略"""
        # 50%概率使用随机搜索引擎Referer
        if random.random() > 0.5:
            return random.choice(self.referer_pool)

        # 30%概率使用同域名Referer
        if site_id and random.random() > 0.7:
            domain = self._get_domain_from_site_id(site_id)
            if domain:
                return f"https://{domain}/page{random.randint(1, 100)}.html"

        # 20%概率不设置Referer
        return None

    def _generate_mobile_headers(self):
        """生成移动端特有请求头"""
        # 随机安卓版本
        android_versions = ['10', '11', '12', '13']
        # 随机手机型号
        phone_models = ['SM-G991B', 'SM-G998B', 'SM-F926B', 'SM-S908E', 'SM-A528B']
        # Chrome版本
        chrome_versions = ['98.0.4758', '99.0.4844', '100.0.4896', '101.0.4951']

        headers = MOBILE_HEADERS_TEMPLATE.copy()
        headers['User-Agent'] = headers['User-Agent'].format(
            version=random.choice(android_versions),
            model=random.choice(phone_models),
            chrome_ver=random.choice(chrome_versions)
        )
        headers['X-Wap-Profile'] = headers['X-Wap-Profile'].format(
            model=random.choice(phone_models)
        )
        return headers

    def _render_dynamic_value(self, value):
        """渲染动态值（如Token）"""
        if '{token}' in value:
            # 实际项目中从Token管理器获取
            return value.replace('{token}', 'dynamic_token_here')
        return value

    def _get_domain_from_site_id(self, site_id):
        """从站点ID获取域名（简化示例）"""
        domain_map = {
            101: 'example-store.com',
            201: 'news-site.com',
            301: 'api-service.com'
        }
        return domain_map.get(site_id)