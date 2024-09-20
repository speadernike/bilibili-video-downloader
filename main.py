# main.py

from browser_manager import BrowserManager  # 导入浏览器管理器模块，用于自动登录Bilibili账户
from gui_app import BilibiliDownloaderApp  # 导入GUI应用程序模块，提供图形用户界面
from tkinter import messagebox  # 导入Tkinter的messagebox模块，用于显示消息提示框

if __name__ == "__main__":
    try:
        # 创建BrowserManager实例，自动初始化浏览器并登录Bilibili
        browser_manager = BrowserManager()

        # 创建BilibiliDownloaderApp实例，启动GUI界面
        # 将已登录的浏览器管理器传递给GUI应用程序
        app = BilibiliDownloaderApp(browser_manager)
    except Exception as e:
        # 如果出现异常，打印登录失败的信息
        print(f"登录失败: {str(e)}")

        # 弹出错误消息框，提示用户登录失败的原因
        messagebox.showerror("错误", f"登录失败：{e}")