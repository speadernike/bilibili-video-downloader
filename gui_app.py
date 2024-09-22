import re
import queue
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from video_processor import VideoProcessor
from bs4 import BeautifulSoup

class BilibiliDownloaderApp:
    """GUI应用类，负责界面创建和用户交互"""

    def __init__(self, browser_manager):
        self.browser = browser_manager.get_browser()  # 获取已登录的浏览器实例
        self.video_processor = VideoProcessor(self.browser)  # 创建视频处理器实例
        self.root = tk.Tk()  # 初始化Tkinter主窗口
        self.root.title("B站视频下载工具")  # 设置窗口标题
        self.stop_download = False  # 标志位，控制下载过程是否中断
        self.create_widgets()  # 创建界面控件
        self.root.mainloop()  # 进入主循环，显示窗口

    def create_widgets(self):
        # 创建标签，提示用户输入
        video_label = tk.Label(self.root, text="输入视频分享链接：")
        video_label.grid(row=0, column=0, padx=5, pady=5)

        # 创建文本输入框，供用户输入视频链接或BV号
        self.video_entry = tk.Entry(self.root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        # 创建“查找”按钮，点击后查找视频信息
        search_button = tk.Button(self.root, text="查找", command=self.search_video_info)
        search_button.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)

        # 创建标签来显示视频标题
        self.video_title_label = tk.Label(self.root, text="视频标题：", anchor="w")
        self.video_title_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # 创建进度条，显示下载和合并进度
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky=tk.EW)

        # 创建进度队列，用于在子线程与主线程之间传递进度信息
        self.progress_queue = queue.Queue()

        # 创建“下载并合并”按钮，绑定点击事件
        download_button = tk.Button(self.root, text="下载并合并", command=self.start_download)
        download_button.grid(row=4, column=1, padx=5, pady=20)

        # 创建“暂停下载”按钮
        pause_button = tk.Button(self.root, text="暂停下载", command=self.pause_download)
        pause_button.grid(row=4, column=0, padx=5, pady=20)

    def pause_download(self):
        """暂停下载按钮的回调函数"""
        self.stop_download = True
        messagebox.showinfo("暂停", "下载已暂停！")

    def search_video_info(self):
        """查找并显示视频信息（标题）"""
        input_string = self.video_entry.get()
        if not input_string:
            messagebox.showerror("错误", "请输入视频ID或链接。")
            return

        # 如果输入的是短链接，则解析为完整链接
        if 'b23.tv' in input_string:
            try:
                input_string = self.resolve_short_link(input_string)
            except ValueError as ex:
                messagebox.showerror("错误", str(ex))
                return

        try:
            # 提取视频ID
            video_id = self.extract_video_id(input_string)
        except ValueError as ex:
            messagebox.showerror("错误", str(ex))
            return

        try:
            # 使用已登录的浏览器访问视频页面
            self.browser.get(f'https://www.bilibili.com/video/{video_id}/')
            self.browser.implicitly_wait(3)  # 等待页面加载

            # 解析页面内容，获取视频标题
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            title = soup.find('meta', attrs={'name': 'title'})['content']
            title = re.sub(r'[_\-–—]*哔哩哔哩.*$', '', title)  # 去除标题中的后缀

            # 显示视频标题
            self.video_title_label.config(text=f"视频标题：{title}")
        except Exception as ex:
            messagebox.showerror("错误", f"获取视频信息失败: {ex}")
            print(f"获取视频信息失败: {ex}")

    def start_download(self):
        # 获取用户输入的链接或BV号
        input_string = self.video_entry.get()
        if not input_string:
            messagebox.showerror("错误", "请输入视频ID或链接。")
            return

        # 如果输入的是短链接，则解析为完整链接
        if 'b23.tv' in input_string:
            try:
                input_string = self.resolve_short_link(input_string)
            except ValueError as ex:
                messagebox.showerror("错误", str(ex))
                return

        try:
            # 提取视频ID
            video_id = self.extract_video_id(input_string)
        except ValueError as ex:
            messagebox.showerror("错误", str(ex))
            return

        # 设置请求头，模拟浏览器访问
        headers = {
            "referer": "https://www.bilibili.com",
            "origin": "https://www.bilibili.com",
            "User-Agent": 'Mozilla/5.0'
        }

        # 重置停止下载的标志位
        self.stop_download = False

        # 创建新线程，调用视频处理器的 process_video 方法，开始下载和合并
        threading.Thread(target=self.video_processor.process_video, args=(video_id, headers, self.progress_queue, self)).start()

        # 开始更新进度条
        self.update_progress()

    def update_progress(self):
        try:
            # 从进度队列中获取当前进度
            progress = self.progress_queue.get_nowait()
            if isinstance(progress, str) and progress.startswith("error"):
                # 如果收到错误信息，弹出错误提示
                messagebox.showerror("错误", progress)
            elif progress == 'done':
                # 下载和合并完成，弹出成功提示
                messagebox.showinfo("成功", "下载与合并完成！")
            else:
                # 更新进度条的值
                self.progress_var.set(progress)
            # 定时器，继续检查进度队列
            self.root.after(100, self.update_progress)
        except queue.Empty:
            # 如果队列为空，稍后再次检查
            self.root.after(100, self.update_progress)

    @staticmethod
    def resolve_short_link(input_string):
        """从输入中提取并解析b站手机端短链接"""
        short_link_pattern = re.compile(r'(b23.tv/\S+)')
        match = short_link_pattern.search(input_string)
        if match:
            short_link = match.group(1)
            short_link_url = f"https://{short_link}"
            try:
                response = requests.head(short_link_url, allow_redirects=True)
                return response.url
            except requests.exceptions.RequestException as e:
                print(f"短链接解析失败: {e}")
                return None
        else:
            raise ValueError("未找到有效的短链接")

    @staticmethod
    def extract_video_id(input_string):
        """从输入的链接中提取 BV 号"""
        bv_pattern = re.compile(r'BV[0-9A-Za-z]+')
        match = bv_pattern.search(input_string)
        if match:
            return match.group(0)
        else:
            raise ValueError("未找到有效的视频 ID")