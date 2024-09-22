# browser_manager.py

import os
import sys
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
    """浏览器管理类，负责初始化和登录操作
注：此模块仅作为演示自动化操作的实现，实际使用时，不必一定非要使用账号密码登录，会遇到至少一层验证码（运气好就是两层）
你也可以在自动化登录触发验证码时点叉，关掉验证框进行扫码登录（但是扫码的账号的 UID 一定要是.env文件中对应账号的）
我在代码中在验证密码时设置了很长的循环等待时间，所以不必担心超时"""

    def __init__(self):
        # 创建并初始化浏览器实例
        self.browser = create_browser_instance()

    def get_browser(self):
        # 提供获取浏览器实例的方法
        return self.browser


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
    driver.implicitly_wait(10)  # 设置隐式等待时间为5秒

    print("正在打开 bilibili...")
    driver.get("https://account.bilibili.com/login")

    print("正在定位账号和密码输入框...")
    username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder='请输入账号']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][placeholder='请输入密码']")
    print("正在输入账号和密码...")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    print("正在定位登录按钮...")
    driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", username_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", password_input)
    driver.execute_script("document.querySelector('.btn_primary').classList.remove('disabled')")
    login_button = driver.find_element(By.CSS_SELECTOR, ".btn_primary")
    login_button.click()

    # 禁用标准输出缓冲
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    # 持续检测登录状态
    start_time = time.time()
    max_wait_time = 300  # 最大等待时间为 300 秒
    logged_in = False

    while not logged_in and time.time() - start_time < max_wait_time:
        try:
            # 每隔 1 秒检查一次是否登录成功
            elapsed_time = int(time.time() - start_time)
            sys.stdout.write(f"\r正在进行登录验证，程序已等待 {elapsed_time} 秒...")
            sys.stdout.flush()  # 强制刷新缓冲区，确保输出被立即显示
            avatar_element = driver.find_element(By.CSS_SELECTOR, "a.header-entry-avatar")
            avatar_href = avatar_element.get_attribute("href")
            if UID in avatar_href:
                print("\n登录成功，开始加载下载界面...")  # 使用换行符确保之前的输出不被覆盖
                logged_in = True
                return driver  # 返回已登录的浏览器实例
        except Exception:
            pass

    if not logged_in:
        print("\n登录超时，未检测到 UID。")
        driver.quit()
        raise TimeoutError("登录超时，未成功检测到登录状态。")