# video_processor.py

import os
import re
import time
import json
import threading
import subprocess  # 在本程序中，它的最关键用处是调用 FFmpeg 这个外部工具，实现音视频的成功合并
import requests
from bs4 import BeautifulSoup
from sanitize_filename import sanitize


class VideoProcessor:
    """视频处理类，负责视频信息获取、下载和合并"""

    def __init__(self, browser):
        self.browser = browser  # 已登录的浏览器实例

    @staticmethod
    def sanitize_filename(filename, max_length=255):
        # 清理文件名，移除非法字符，确保文件名合法
        filename = sanitize(filename)
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        if not filename:
            filename = 'unnamed'
        return filename

    def download_file(self, url, dest_path, headers, gui_app, max_retries=5, retry_delay=2):
        """下载文件，支持中途中断"""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        attempt = 0
        while attempt < max_retries:
            try:
                print(f"正在尝试下载（尝试 {attempt + 1}/{max_retries}）：{url}")
                with requests.get(url, headers=headers, stream=True, timeout=10) as r:
                    r.raise_for_status()
                    with open(dest_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if gui_app.stop_download:  # 检查是否中断下载
                                print("下载已暂停")
                                return False  # 下载被暂停，返回 False
                            if chunk:  # 检查是否有内容，避免空块
                                f.write(chunk)
                print(f"下载完成：{os.path.basename(dest_path)}")
                return True  # 成功下载
            except requests.exceptions.RequestException as ex:
                print(f"下载失败：{ex}")
                attempt += 1
                if attempt < max_retries:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    print("最大重试次数已达到，下载失败。")
                    raise ex

    @staticmethod
    def get_highest_quality_video(video_info):
        # 获取最高质量的视频流的 URL
        highest_quality = max(
            video_info['data']['dash']['video'], key=lambda x: x.get('height', 0))
        return highest_quality['base_url']

    @staticmethod
    def get_video_duration(video_file):
        # 使用 ffprobe 获取视频时长
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v',
            '-show_entries', 'format=duration',
            '-of', 'json',
            video_file
        ]
        try:
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            info = json.loads(result.stdout)
            return float(info['format']['duration'])
        except subprocess.CalledProcessError as ex:
            print(f"发生异常：{ex}")
            return None

    def merge_audio_video(self, video_file, audio_file, output_folder, output_filename, progress_queue):
        # 合并音频和视频文件，使用 FFmpeg
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, output_filename)

        total_duration = self.get_video_duration(video_file)
        if total_duration is None:
            return

        command = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'error',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',   # 直接复制视频流，不重新编码
            '-c:a', 'copy',   # 直接复制音频流，不重新编码
            '-map', '0:v:0',  # 指定使用第一个输入文件的视频流
            '-map', '1:a:0',  # 指定使用第二个输入文件的音频流
            '-shortest',      # 以最短地输入文件长度为输出长度
            '-progress', 'pipe:1',  # 输出进度信息到标准输出
            output_file
        ]

        def run_ffmpeg():
            try:
                # 启动 FFmpeg 进程，开始合并音视频
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while True:
                    line = process.stdout.readline()
                    if line == '':
                        if process.poll() is not None:
                            break
                    else:
                        if line.startswith('out_time_ms='):
                            # 读取输出时间，计算进度
                            out_time_ms = int(line.strip().split('=')[1])
                            progress = out_time_ms / (total_duration * 1000000) * 100
                            progress_queue.put(progress)  # 将进度信息放入队列
                if process.returncode == 0:
                    progress_queue.put(100)    # 合并完成，进度 100%
                    progress_queue.put('done')  # 发送完成信号
                else:
                    progress_queue.put(f"error: {process.stderr.read()}")  # 发送错误信息
            except Exception as ex:
                progress_queue.put(f"error: {ex}")  # 捕获异常，发送错误信息

        # 使用线程启动 FFmpeg 合并，避免阻塞主线程
        threading.Thread(target=run_ffmpeg).start()

    def process_video(self, video_id, headers, progress_queue, gui_app):
        try:
            # 使用已登录的浏览器访问视频页面
            self.browser.get(f'https://www.bilibili.com/video/{video_id}/')
            time.sleep(3)  # 等待页面加载

            # 解析页面内容，获取视频标题
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')

            title = soup.find('meta', attrs={'name': 'title'})['content']
            title = re.sub(r'[_\-–—]*哔哩哔哩.*$', '', title)  # 去除标题中的后缀
            title = re.sub(r'\s+', ' ', title).strip()
            filename = self.sanitize_filename(title)  # 清理文件名

            # 提取视频的播放信息
            video_info = json.loads(
                re.search(r'window\.__playinfo__=({.*?})\s*</script>', self.browser.page_source).group(1))

            # 获取最高质量的视频和音频流的 URL
            video_url = self.get_highest_quality_video(video_info)
            audio_url = video_info['data']['dash']['audio'][0]['base_url']

            # 下载视频文件，传递 gui_app 参数
            if not self.download_file(video_url, os.path.join('download', f"{filename}.mp4"), headers, gui_app):
                progress_queue.put("error: 下载已暂停")
                return  # 下载被暂停，直接退出

            # 下载音频文件，传递 gui_app 参数
            if not self.download_file(audio_url, os.path.join('download', f"{filename}.mp3"), headers, gui_app):
                progress_queue.put("error: 下载已暂停")
                return  # 下载被暂停，直接退出

            # 合并音视频文件
            self.merge_audio_video(
                os.path.join('download', f"{filename}.mp4"),
                os.path.join('download', f"{filename}.mp3"),
                'output',
                f"{filename}.mp4",
                progress_queue
            )

        except Exception as ex:
            # 捕获异常，放入进度队列供 GUI 显示
            progress_queue.put(f"error: {ex}")
            print(f"处理视频时出错: {ex}")