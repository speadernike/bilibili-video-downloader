# gui_app.py

import re
import queue
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from video_processor import VideoProcessor

class BilibiliDownloaderApp:
    """GUI应用类，负责界面创建和用户交互"""

    def __init__(self, browser_manager):
        self.browser = browser_manager.get_browser()  # 获取已登录的浏览器实例
        self.video_processor = VideoProcessor(self.browser)  # 创建视频处理器实例
        self.root = tk.Tk()  # 初始化Tkinter主窗口
        self.root.title("B站视频下载工具")  # 设置窗口标题
        self.create_widgets()  # 创建界面控件
        self.root.mainloop()  # 进入主循环，显示窗口

    def create_widgets(self):
        # 创建标签，提示用户输入
        video_label = tk.Label(self.root, text="输入视频分享链接：")
        video_label.grid(row=0, column=0, padx=5, pady=5)

        # 创建文本输入框，供用户输入视频链接或BV号
        self.video_entry = tk.Entry(self.root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        # 创建进度条，显示下载和合并进度
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        progress_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky=tk.EW)

        # 创建进度队列，用于在子线程与主线程之间传递进度信息
        self.progress_queue = queue.Queue()

        # 创建“下载并合并”按钮，绑定点击事件
        download_button = tk.Button(
            self.root,
            text="下载并合并",
            command=self.start_download
        )
        download_button.grid(row=2, column=1, padx=5, pady=20)

    @staticmethod
    def extract_video_id(input_string):
        # 使用正则表达式从输入字符串中提取BV号
        match = re.search(r'(BV\w+)', input_string)
        if match:
            return match.group(1)
        else:
            raise ValueError("未找到有效的视频 ID")

    def start_download(self):
        # 获取用户输入的链接或BV号
        input_string = self.video_entry.get()
        if not input_string:
            messagebox.showerror("错误", "请输入视频ID或链接。")
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

        # 创建新线程，调用视频处理器的process_video方法，开始下载和合并
        threading.Thread(target=self.video_processor.process_video, args=(video_id, headers, self.progress_queue)).start()

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