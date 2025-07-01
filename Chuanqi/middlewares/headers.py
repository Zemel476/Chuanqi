import random

from Chuanqi.utils.header_util import HeaderGenerator


class SmartHeaderMiddleware:
    def __init__(self):
        self.header_gen = HeaderGenerator()
        # 站点ID到设备类型的映射缓存
        self.site_device_map = {}

    def process_request(self, request, spider):
        # 从任务数据中获取站点ID
        task_data = request.meta.get('task_data', {})

        site_id = task_data.get('site_id')

        # 确定设备类型（桌面端/移动端）
        is_mobile = self._determine_device_type(site_id, request)

        # 生成请求头
        headers = self.header_gen.get_headers(
            site_id=site_id,
            is_mobile=is_mobile,
        )

        # 设置到请求中
        request.headers['Accept'] = headers.get('Accept')
        request.headers['Accept-Language'] = headers.get('Accept-Language')
        request.headers['Upgrade-Insecure-Requests'] = headers.get('Upgrade-Insecure-Requests')
        request.headers['TE'] = headers.get('TE')
        request.headers['User-Agent'] = headers.get('User-Agent')
        request.headers['Referer'] = headers.get('Referer')
        request.headers['X-Wap-Profile'] = headers.get('X-Wap-Profile')
        request.headers['Sec-CH-UA-Mobile'] = headers.get('Sec-CH-UA-Mobile')

        # # 特殊处理：为某些站点添加指纹头
        # if site_id in [101, 201]:
        #     self._add_fingerprint_headers(request, site_id)

    def _determine_device_type(self, site_id, request):
        """确定请求使用的设备类型"""
        # 如果任务中明确指定了设备类型
        if 'device_type' in request.meta:
            return request.meta['device_type'] == 'mobile'

        # 根据站点配置确定
        if site_id not in self.site_device_map:
            # 实际项目中从数据库或配置加载
            site_device_config = {
                101: 0.7,  # 70%概率使用移动端
                201: 0.3,  # 30%概率使用移动端
                301: 0.0  # 0%概率使用移动端
            }
            self.site_device_map[site_id] = site_device_config.get(site_id, 0.5)

        # 按概率确定设备类型
        return random.random() < self.site_device_map[site_id]

    def _add_fingerprint_headers(self, request, site_id):
        """添加浏览器指纹头"""
        fingerprint = self._generate_browser_fingerprint(site_id)
        request.headers.update({
            'X-Client-Fingerprint': fingerprint['id'],
            'X-Client-Resolution': fingerprint['resolution'],
            'X-Client-Timezone': fingerprint['timezone'],
            'X-Client-Language': fingerprint['language'],
            'X-Client-Platform': fingerprint['platform']
        })

    def _generate_browser_fingerprint(self, site_id):
        """生成浏览器指纹"""
        # 分辨率池
        resolutions = [
            '1920x1080', '1366x768', '1536x864',
            '1440x900', '1280x720', '1600x900'
        ]

        # 时区池
        timezones = [
            'Asia/Shanghai', 'America/New_York',
            'Europe/London', 'Europe/Paris', 'Asia/Tokyo'
        ]

        # 语言池
        languages = [
            'en-US,en;q=0.9', 'zh-CN,zh;q=0.9,en;q=0.8',
            'ja-JP,ja;q=0.9,en;q=0.8', 'de-DE,de;q=0.9,en;q=0.8'
        ]

        # 平台池
        platforms = ['Win32', 'MacIntel', 'Linux x86_64']

        return {
            'id': f"fp_{random.randint(1000000000, 9999999999)}",
            'resolution': random.choice(resolutions),
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'platform': random.choice(platforms)
        }