import logging

import requests


class CaptchaMiddleware:
    CAPTCHA_API = "http://captcha-service:6000/solve"

    def solve_captcha(self, response, site_id):
        # 自动检测验证码类型
        captcha_type = self.detect_captcha_type(response)

        # 获取验证码图片
        img_url = self.find_captcha_image(response)
        if not img_url:
            return None

        # 下载验证码图片
        img_data = requests.get(img_url).content

        # 调用验证码服务
        files = {'image': ('captcha.png', img_data, 'image/png')}
        data = {'site_id': site_id, 'type': captcha_type}

        try:
            resp = requests.post(self.CAPTCHA_API, files=files, data=data, timeout=15)
            if resp.status_code == 200:
                result = resp.json()
                if result['success']:
                    return {
                        'captcha_input': result['solution'],
                        'captcha_token': response.meta.get('captcha_token')
                    }
        except Exception as e:
            logging.error(f"Captcha solve failed: {str(e)}")
        return None

    def detect_captcha_type(self, response):
        # 基于URL或页面特征识别验证码类型
        if 'recaptcha' in response.url:
            return 'google_recaptcha_v2'
        elif 'hcaptcha' in response.text:
            return 'hcaptcha'
        else:
            # 使用CNN模型自动识别
            return self.classify_captcha(response)

    def find_captcha_image(self, response):
        # 从页面中提取验证码图片URL
        img_sel = response.css('img#captcha, img.captcha-image')
        if img_sel:
            return response.urljoin(img_sel.attrib['src'])
        return None

    def classify_captcha(self, response):
        pass