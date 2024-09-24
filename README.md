# 基于selenium 的 Bilibili 视频下载测试
## 一、 此项目为一个 B 站视频下载的 python 自动化测试程序
### 1. 终端运行:`pip install -r requirements.txt`

**这个指令会在本项目文件当前使用的 python 环境中运行，用于安装所需要的依赖。**

### 2. 在项目目录新建一个.env文件并填写入你自己的 B 站账号密码（用于登录）和 UID（用于验证登录）
示例：
```
BILIBILI_USERNAME=1234567890（一般就是手机号）
BILIBILI_PASSWORD=1234567890（若经常使用验证码登录，很可能没有设置，需要在手机端的设置-安全隐私-账号安全中心进行设置）
BILIBILI_UID=1234567890（手机端的设置-账户资料-UID查看）
```
### 3. 最关键的，由于多数视频网站都是将视频与音频分开存储的，bilibili也不例外，所以获取到视频流和音频流后需要合并
**本项目需要下载 FFmpeg 这个视频处理工具，后面会讲到如何安装。**

### 4. 上述工作完成后，在终端导航到项目根目录，执行以下命令运行程序：`python main.py` 
*如果提示没有找到 python，使用 python3 main.py*

---
## 二、 概括：在 Windows、Mac、Linux 上安装和使用 FFmpeg
*看不懂可以移步三、四、五查看详细安装教程*

	1. Windows：
	•从受信任的第三方下载 FFmpeg 的预编译版本。
	•解压并将 FFmpeg 的 bin 目录添加到系统 PATH 环境变量中。

	2. macOS：
	•使用 Homebrew 安装 FFmpeg，命令为 brew install ffmpeg。

	3. Linux：
	•使用系统的包管理器安装 FFmpeg，例如在 Ubuntu 上使用 sudo apt-get install ffmpeg。

	4. 验证安装：
	•在命令行中运行 ffmpeg -version，确保 FFmpeg 已正确安装并可用。

	5. 在项目中使用：
	•确保 FFmpeg 在系统 PATH 中，Python 的 subprocess 模块能够找到并调用 FFmpeg。

	6. 注意事项：
	•处理路径时，使用 os.path 模块，确保跨平台兼容。
	•处理权限和依赖问题，确保程序在不同操作系统上都能正常运行。

---
## **三、在 Windows 上安装和使用 FFmpeg**

### **步骤 1：下载 FFmpeg**

1. **访问 FFmpeg 官网或受信任的第三方网站：**

   - FFmpeg 官方并未直接提供 Windows 的可执行安装程序，但您可以从以下受信任的第三方获取预编译的 Windows 版本：

     - **gyan.dev** 提供了最新的 FFmpeg Windows 版本：[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

2. **下载适合的版本：**

   - 在 `gyan.dev` 网站上，选择 **"FFmpeg release full"** 版本，以确保包含所有的编解码器。

   - 点击链接下载 ZIP 压缩包，例如：`ffmpeg-6.0-full_build.zip`

### **步骤 2：解压并配置 FFmpeg**

1. **解压 ZIP 文件：**

   - 将下载的 ZIP 文件解压到您希望安装的位置，例如 `C:\ffmpeg\`

2. **配置环境变量：**

   - **打开系统环境变量设置：**

     - 右键点击 **"此电脑"** 或 **"计算机"**，选择 **"属性"**
     - 点击 **"高级系统设置"**
     - 点击 **"环境变量"**

   - **编辑系统变量 Path：**

     - 在 **"系统变量"** 中，找到 **"Path"**，然后点击 **"编辑"**
     - 点击 **"新建"**，添加 FFmpeg 的 `bin` 目录路径，例如：

       ```
       C:\ffmpeg\ffmpeg-6.0-full_build\bin
       ```

     - 点击 **"确定"** 保存设置

### **步骤 3：验证安装**

1. **打开命令提示符：**

   - 按 **Win + R**，输入 **`cmd`**，按回车

2. **输入以下命令检查 FFmpeg 是否安装成功：**

   ```bash
   ffmpeg -version
   ```

   - 如果正确安装，您将看到 FFmpeg 的版本信息。

### **在项目中使用 FFmpeg**

- 您的 Python 脚本通过 `subprocess` 模块调用 FFmpeg 命令，因此只要 FFmpeg 在系统的 `PATH` 中，您的程序就可以正常调用它。

---
## **四、在 macOS 上安装和使用 FFmpeg**

### **步骤 1：安装 Homebrew（如果尚未安装）**

- **Homebrew** 是 macOS 的包管理器，方便您安装各种软件。

1. **打开终端：**

   - 您可以通过 **Spotlight** 搜索 **"终端"**，或者在 **"应用程序"** -> **"实用工具"** 中找到。

2. **安装 Homebrew：**

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   - 按提示完成安装。

### **步骤 2：使用 Homebrew 安装 FFmpeg**

1. **在终端中运行以下命令：**

   ```bash
   brew install ffmpeg
   ```

2. **等待安装完成。**

### **步骤 3：验证安装**

1. **在终端中输入以下命令：**

   ```bash
   ffmpeg -version
   ```

   - 如果正确安装，您将看到 FFmpeg 的版本信息。

### **在项目中使用 FFmpeg**

- macOS 的终端默认会搜索 `/usr/local/bin`，Homebrew 安装的 FFmpeg 会自动添加到系统路径中，您的 Python 程序可以直接调用 FFmpeg。

---
## **五、在 Linux 上安装和使用 FFmpeg**

不同的 Linux 发行版可能有不同的包管理器，以下以 Ubuntu/Debian 和 CentOS/Fedora 为例。

### **1. 对于 Ubuntu/Debian 系统**

#### **步骤 1：更新包列表**

```bash
sudo apt-get update
```

#### **步骤 2：安装 FFmpeg**

```bash
sudo apt-get install ffmpeg
```

#### **步骤 3：验证安装**

```bash
ffmpeg -version
```

- 如果正确安装，您将看到 FFmpeg 的版本信息。

### **2. 对于 CentOS/Fedora 系统**

#### **步骤 1：启用 EPEL 和 RPM Fusion 仓库**

```bash
sudo dnf install epel-release
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```

#### **步骤 2：安装 FFmpeg**

```bash
sudo dnf install ffmpeg ffmpeg-devel
```

#### **步骤 3：验证安装**

```bash
ffmpeg -version
```

- 如果正确安装，您将看到 FFmpeg 的版本信息。
### **3. 在项目中使用 FFmpeg**

- 在 Linux 系统上，FFmpeg 安装后通常位于 `/usr/bin` 或 `/usr/local/bin`，默认在系统路径中，Python 程序可以直接调用。

---

