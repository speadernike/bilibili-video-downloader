# browser_manager.py

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By  # 导入定位元素的方法
from selenium.webdriver.chrome.service import Service  # 导入Chrome浏览器的Service
from selenium.webdriver.chrome.options import Options  # 导入Chrome浏览器的选项配置
from webdriver_manager.chrome import ChromeDriverManager  # 导入webdriver_manager，用于自动管理ChromeDriver
from dotenv import load_dotenv  # 导入dotenv，用于加载环境变量

# 加载 .env 文件中的环境变量，例如Bilibili的用户名、密码和UID
load_dotenv()

class BrowserManager:
    """浏览器管理类，负责初始化和登录操作"""

    def __init__(self):
        # 创建并初始化浏览器实例
        self.browser = self.create_browser_instance()

    @staticmethod
    def create_browser_instance():
        # 从环境变量中获取Bilibili的用户名、密码和UID
        USERNAME = os.getenv('BILIBILI_USERNAME')
        PASSWORD = os.getenv('BILIBILI_PASSWORD')
        UID = os.getenv('BILIBILI_UID')

        # 检查是否成功获取到必要的环境变量
        if not USERNAME or not PASSWORD or not UID:
            raise ValueError("环境变量 BILIBILI_USERNAME, BILIBILI_PASSWORD 或 BILIBILI_UID 未正确加载")

        # 设置Chrome浏览器的选项
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")  # 解决DevToolsActivePort文件不存在的报错
        chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存不足的问题

        # 自动安装并获取ChromeDriver的路径，无需手动配置驱动路径甚至环境变量，缺点是每次都会重新下载驱动
        driver_path = ChromeDriverManager().install()
        print(f"webdriver_manager下载使用的 ChromeDriver 路径: {driver_path}")

        # 创建Chrome浏览器实例
        driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        driver.implicitly_wait(10)  # 设置隐式等待时间为10秒

        print("正在打开 bilibili...")
        driver.get("https://account.bilibili.com/login")  # 打开Bilibili登录页面
        time.sleep(3)  # 等待页面加载完成

        print("正在定位账号和密码输入框...")
        # 定位用户名输入框
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder='请输入账号']")
        # 定位密码输入框
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][placeholder='请输入密码']")

        print("正在输入账号和密码...")
        # 输入用户名和密码
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        time.sleep(2)  # 等待2秒，确保输入被前端接收

        print("正在登录中...")
        # 模拟触发输入事件，确保前端验证机制能够检测到输入
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", username_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", password_input)
        # 移除登录按钮的禁用状态，以便可以点击
        driver.execute_script("document.querySelector('.btn_primary').classList.remove('disabled')")
        # 定位并点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, ".btn_primary")
        login_button.click()

        time.sleep(30)  # 等待30秒，处理可能出现的验证码，需要手动完成

        try:
            # 检查是否成功登录，通过用户头像的链接中是否包含UID来验证
            avatar_element = driver.find_element(By.CSS_SELECTOR, "a.header-entry-avatar")
            avatar_href = avatar_element.get_attribute("href")
            if UID in avatar_href:
                print("登录成功，开始加载下载界面...")
                return driver  # 返回已登录的浏览器实例
            else:
                raise ValueError("登录失败，无法验证 UID")
        except Exception as ex:
            # 如果登录失败，打印错误信息并关闭浏览器
            print(f"登录失败: {str(ex)}")
            driver.quit()
            raise ex

    def get_browser(self):
        # 提供获取浏览器实例的方法
        return self.browser