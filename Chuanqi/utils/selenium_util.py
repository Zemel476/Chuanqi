from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

_chrome_driver_path = r'F:\Python\tools\chrome\chromedriver.exe'
_chrome_exe_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

class SeleniumUtil:
    def __init__(self, headless=False, implicit_wait=10, window_size=(1920, 1080)):
        """
        :param browser: 浏览器类型 (chrome/firefox/edge)
        :param headless: 是否无头模式
        :param implicit_wait: 隐式等待时间（秒）
        :param window_size: 窗口大小 (width, height)
        """
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.window_size = window_size
        self.driver = None

    def init_driver(self):
        """初始化浏览器驱动"""
        try:
            options = webdriver.ChromeOptions()
            # 常用配置
            options.add_argument("--disable-blink-features=AutomationControlled")  # 屏蔽自动化检测
            options.add_argument("--disable-infobars")  # 禁用信息栏
            options.add_argument("--start-maximized" if not self.window_size else f"--window-size={self.window_size[0]},{self.window_size[1]}")
            if self.headless:
                options.add_argument("--headless=new")  # Chrome 114+ 新版无头模式
                options.add_argument("--disable-gpu")
            # chrome.exe
            options.binary_location = _chrome_exe_path

            # chromedriver驱动
            service = webdriver.ChromeService(executable_path=_chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)

            # 设置隐式等待
            self.driver.implicitly_wait(self.implicit_wait)

        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            raise

    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

    def get_element_by_xpath(self, xpath, timeout=10):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))


# ===== 使用示例 =====
if __name__ == "__main__":
    config = SeleniumConfig(headless=False)
    try:
        # 初始化配置（切换浏览器或修改参数）
        config.init_driver()
        driver = config.driver

        # 打开网页并操作
        driver.get("https://www.baidu.com")
        search_box = driver.find_element(By.ID, "kw")
        search_box.send_keys("Selenium自动化测试")
        driver.find_element(By.ID, "su").click()
    except Exception as e:
        print(e)
    # 显式等待（推荐）
    finally:
        config.quit()