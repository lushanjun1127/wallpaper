#03.py (merged)
# UI: PySide6多页面应用程序（左侧导航栏 + 堆叠页面）带亚克力效果
# 凭据: 用户输入（可选择本地保存）

# 系统相关库
import os               # 文件路径操作
import re               # 正则表达式
import json             # JSON数据处理
import time             # 时间相关功能
import subprocess       # 子进程管理
import logging          # 日志记录
import sys              # 系统相关功能
from typing import List, Optional, Tuple, Any, Set  # 类型注解支持

# 第三方库
import requests         # 网络请求库

# PySide6 GUI框架
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QResizeEvent, QCloseEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QProgressBar,
    QListWidget, QListWidgetItem, QStackedWidget, QCheckBox
)

# Windows注册表访问（仅Windows平台）
try:
    import winreg
except ImportError:
    winreg = None

# 配置常量
CONFIG_FILE = "config.json"                             # 配置文件路径
LEGACY_LAST_PATH_FILE = "lastsavelocation.cfg"         # 旧版路径配置文件
DEFAULT_BG_URL = "https://i.pinimg.com/736x/72/59/79/725979e9578ff3afdfa9f74280fa0569.jpg"  # 默认背景图URL
STEAM_APP_ID = "431960"                                # Steam应用ID
DOWNLOADER_EXE = os.path.join("DepotdownloaderMod", "DepotDownloadermod.exe")  # 下载器可执行文件路径

# 样式表
STYLESHEET = """
/* 全局样式 */
QWidget {
    font-family: "Microsoft YaHei UI", "Segoe UI";      /* 字体族 */
    font-size: 10pt;                                   /* 字体大小 */
    color: #FFFFFF;                                    /* 文字颜色 */
    background-color: transparent;                     /* 背景透明 */
}

/* 主窗口背景 */
QMainWindow {
    background-color: rgba(0, 0, 0, 150);              /* 半透明黑色背景 */
}

/* 导航栏 */
QListWidget {
    background-color: rgba(255, 255, 255, 30);         /* 半透明白色背景 */
    border: 1px solid rgba(255, 255, 255, 30);         /* 边框 */
    border-radius: 10px;                               /* 圆角 */
    padding: 5px;                                      /* 内边距 */
    outline: 0;                                        /* 无轮廓 */
}

QListWidget::item {
    background-color: rgba(255, 255, 255, 20);         /* 列表项背景 */
    border-radius: 5px;                                /* 圆角 */
    padding: 10px;                                     /* 内边距 */
    margin:2px;                                        /* 外边距 */
}

QListWidget::item:selected {
    background-color: rgba(186, 104, 200, 150);        /* 选中项背景色 */
    color: white;                                      /* 选中项文字颜色 */
}

/* 卡片 */
QFrame.card {
    background-color: rgba(255, 255,255, 30);          /* 半透明白色背景 */
    border: 1px solid rgba(255, 255, 255, 30);         /* 边框 */
    border-radius: 10px;                               /* 圆角 */
    padding: 15px;                                     /* 内边距 */
}

/* 输入框 */
QLineEdit, QTextEdit {
    background-color: rgba(255, 255, 255, 50);         /* 背景色 */
    border: 1px solid rgba(255, 255, 255, 50);         /* 边框 */
    border-radius: 5px;                                /* 圆角 */
    padding: 8px;                                      /* 内边距 */
    selection-background-color: #ba68c8;               /* 选中文本背景色 */
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #ba68c8;                         /* 焦点状态边框 */
}

/* 按钮 */
QPushButton {
    background-color: #ba68c8;                         /* 背景色 */
    border: none;                                      /* 无边框 */
    border-radius: 5px;                                /* 圆角 */
    padding: 8px 16px;                                 /* 内边距 */
    color: white;                                      /* 文字颜色 */
    font-weight: bold;                                 /* 粗体 */
}

QPushButton:hover {
    background-color: #e91e63;                         /* 悬停背景色 */
}

QPushButton:pressed {
    background-color: #9c27b0;                         /* 按下背景色 */
}

QPushButton:disabled {
    background-color: rgba(186, 104, 200, 100);        /* 禁用状态背景色 */
}

/* 复选框 */
QCheckBox {
    background-color: transparent;                     /* 背景透明 */
    spacing: 5px;                                      /* 间距 */
}

QCheckBox::indicator {
    width: 18px;                                       /* 指示器宽度 */
    height: 18px;                                      /* 指示器高度 */
}

QCheckBox::indicator:unchecked {
    border: 1px solid #ba68c8;                         /* 未选中边框 */
    border-radius: 3px;                                /* 圆角 */
    background-color: rgba(255, 255, 255, 50);         /* 背景色 */
}

QCheckBox::indicator:checked {
    border: 1px solid#ba68c8;                          /* 选中边框 */
    border-radius: 3px;                                /* 圆角 */
    background-color: #ba68c8;                         /* 背景色 */
}

/* 进度条 */
QProgressBar {
    border: 1px solid rgba(255, 255, 255, 50);         /* 边框 */
    border-radius:5px;                                 /* 圆角 */
    text-align: center;                                /* 文本居中 */
    background-color: rgba(255, 255, 255, 30);         /* 背景色 */
}

QProgressBar::chunk {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                                      stop: 0 #ba68c8, stop: 1 #e91e63);  /* 渐变色块 */
    border-radius: 4px;                                /* 圆角 */
}

/* 滚动条 */
QScrollBar:vertical {
    border: none;                                      /* 无边框 */
    background: rgba(255, 255, 255, 30);               /* 背景色 */
    width: 10px;                                       /* 宽度 */
    border-radius: 5px;                                /* 圆角 */
}

QScrollBar::handle:vertical {
    background: rgba(186, 104, 200, 150);              /* 滑块背景色 */
    border-radius: 5px;                                /* 圆角 */
}

QScrollBar::handle:vertical:hover {
    background: rgba(233, 30, 99, 150);                /* 悬停背景色 */
}

/* 标题标签 */
QLabel {
    color: white;                                      /* 文字颜色 */
}
"""

# ID验证正则表达式
ID_STRICT_RE = re.compile(r"^\d{8,10}$")               # 严格匹配8-10位数字
ID_LOOSE_RE = re.compile(r"\b\d{8,10}\b")              # 宽松匹配8-10位数字

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,                                # 日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 日志格式
)
logger = logging.getLogger(__name__)                   # 获取日志记录器


def load_json(path: str) -> dict[str, Any]:
    """
    从文件加载JSON数据
    
    Args:
        path: JSON文件路径
        
    Returns:
        包含JSON数据的字典，如果文件不存在或无效则返回空字典
    """
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"加载JSON文件 {path} 时出错: {e}")
    except Exception as e:
        logger.error(f"加载JSON文件 {path} 时出现意外错误: {e}")
    return {}


def save_json(path: str, data: dict[str, Any]) -> bool:
    """
    将数据保存到JSON文件
    
    Args:
        path: JSON文件路径
        data: 要保存的数据
        
    Returns:
        成功返回True，失败返回False
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (TypeError, IOError) as e:
        logger.error(f"保存JSON到 {path} 时出错: {e}")
        return False
    except Exception as e:
        logger.error(f"保存JSON到 {path} 时出现意外错误: {e}")
        return False


def migrate_legacy_path_if_needed(cfg: dict[str, Any]) -> dict[str, Any]:
    """
    如需要则迁移旧配置
    
    Args:
        cfg: 当前配置字典
        
    Returns:
        更新后的配置字典
    """
    if cfg.get("save_location"):
        return cfg
    try:
        if os.path.exists(LEGACY_LAST_PATH_FILE):
            with open(LEGACY_LAST_PATH_FILE, "r", encoding="utf-8", errors="ignore") as f:
                p = f.read().strip()
            if p:
                cfg["save_location"] = p
                cfg["migrated_from_cfg"] = True
    except Exception as e:
        logger.warning(f"迁移旧路径时出错: {e}")
    return cfg


def ensure_config_defaults(cfg: dict[str, Any]) -> dict[str, Any]:
    """
    确保配置包含所有必需的默认值
    
    Args:
        cfg: 配置字典
        
    Returns:
        包含默认值的更新后配置字典
    """
    cfg.setdefault("schema_version", 2)                 # 配置模式版本
    cfg.setdefault("nickname", "")                      # 昵称
    cfg.setdefault("save_location", "")                 # 保存位置
    cfg.setdefault("ui_last_page", "下载")              # 上次UI页面
    cfg.setdefault("bg_url", DEFAULT_BG_URL)            # 背景图片URL
    cfg.setdefault("bg_enabled", True)                  # 是否启用背景
    cfg.setdefault("auto_scroll_log", True)             # 是否自动滚动日志
    cfg.setdefault("login_username", "")                # 登录用户名
    cfg.setdefault("remember_password", False)          # 是否记住密码
    cfg.setdefault("login_password", "")                # 登录密码
    return cfg


def parse_ids_fusion(text: str) -> Tuple[List[str], List[str]]:
    """
    从文本中解析并提取有效ID
    
    Args:
        text: 包含ID的输入文本
        
    Returns:
        元组 (有效ID列表, 无效行列表)
    """
    seen: Set[str] = set()                              # 已见ID集合（去重用）
    valid: List[str] = []                               # 有效ID列表
    invalid: List[str] = []                             # 无效行列表
    for raw in text.splitlines():                       # 按行分割
        line = raw.strip()                              # 去除首尾空白
        if not line:                                    # 跳过空行
            continue
        extracted: Optional[str] = None                 # 提取到的ID
        if ID_STRICT_RE.match(line):                    # 严格匹配
            extracted = line
        else:
            m = ID_LOOSE_RE.search(line)                # 宽松匹配
            if m:
                extracted = m.group(0)
        if extracted:                                   # 如果提取到ID
            if extracted not in seen:                   # 去重
                seen.add(extracted)
                valid.append(extracted)
        else:
            invalid.append(raw)                         # 记录无效行
    return valid, invalid


def is_valid_we_root(path: str) -> bool:
    """
    检查路径是否为有效的Wallpaper Engine根目录
    
    Args:
        path: 要检查的路径
        
    Returns:
        路径有效返回True，否则返回False
    """
    if not path:                                        # 路径为空
        return False
    try:
        # 检查是否存在projects/myprojects目录
        return os.path.isdir(os.path.join(path, "projects", "myprojects"))
    except Exception as e:
        logger.error(f"检查Wallpaper Engine根路径 {path} 时出错: {e}")
        return False


def detect_steam_install_path_from_registry() -> Optional[str]:
    """
    从Windows注册表检测Steam安装路径
    
    Returns:
        找到返回Steam安装路径，否则返回None
    """
    if winreg is None:                                  # winreg不可用
        return None
    try:
        # 打开注册表键
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
            return winreg.QueryValueEx(key, "InstallPath")[0]  # 查询安装路径
    except Exception as e:
        logger.debug(f"Steam注册表检测失败: {e}")
        return None


def auto_detect_we_path() -> Optional[str]:
    """
    自动检测Wallpaper Engine安装路径
    
    Returns:
        找到返回Wallpaper Engine安装路径，否则返回None
    """
    # 首先尝试从注册表检测Steam路径
    steam_path = detect_steam_install_path_from_registry()
    if steam_path:
        # 构造候选路径
        candidate = os.path.join(steam_path, "steamapps", "common", "wallpaper_engine")
        if is_valid_we_root(candidate):                 # 验证路径有效性
            return candidate
    
    # 检查常见安装路径
    common_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine",
        r"C:\Program Files\Steam\steamapps\common\wallpaper_engine",
        r"D:\Steam\steamapps\common\wallpaper_engine",
    ]
    
    for path in common_paths:                           # 遍历候选路径
        if is_valid_we_root(path):
            return path
            
    return None


class BackgroundLoader(QThread):
    """用于加载背景图像的线程类"""
    loaded = Signal(QPixmap)                             # 图像加载完成信号
    failed = Signal(str)                                 # 图像加载失败信号
    
    def __init__(self, url: str, target_size: QSize):
        """
        初始化背景加载器
        
        Args:
            url: 要加载的图像URL
            target_size: 图像目标尺寸
        """
        super().__init__()
        self.url = url                                   # 图像URL
        self.target_size = target_size                   # 目标尺寸

    def run(self):
        """加载并缩放背景图像"""
        try:
            logger.info(f"正在从 {self.url} 加载背景图像")
            response = requests.get(self.url, timeout=8)  # 发送网络请求
            response.raise_for_status()                   # 检查响应状态
            
            pixmap = QPixmap()                            # 创建QPixmap对象
            if not pixmap.loadFromData(response.content):  # 从数据加载图像
                raise RuntimeError("无法从数据加载图像")
                
            # 缩放图像到目标尺寸
            scaled_pixmap = pixmap.scaled(
                self.target_size, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.loaded.emit(scaled_pixmap)               # 发射加载完成信号
        except requests.RequestException as e:
            error_msg = f"网络错误: {e}"
            logger.error(error_msg)
            self.failed.emit(error_msg)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"加载背景图像时出错: {error_msg}")
            self.failed.emit(error_msg)


class DownloadWorker(QThread):
    """用于下载WallpaperEngine创意工坊项目的线程类"""
    log = Signal(str)                                    # 日志信号
    queue_progress = Signal(int)                         # 队列进度信号
    item_progress = Signal(int)                          # 项目进度信号
    finished = Signal(bool, str)                         # 完成信号

    def __init__(self, ids: List[str], we_root: str, username: str, password: str):
        """
        初始化下载工作线程
        
        Args:
            ids: 要下载的项目ID列表
            we_root: Wallpaper Engine根目录
            username: Steam用户名
            password: Steam密码
        """
        super().__init__()
        self.ids = ids                                   # 项目ID列表
        self.we_root = we_root                           # WE根目录
        self.username = username                         # 用户名
        self.password = password                         # 密码
        self._stop = False                               # 停止标志
        self._proc: Optional[subprocess.Popen[Any]] = None  # 子进程对象

    def request_stop(self):
        """请求停止下载过程"""
        self._stop = True
        try:
            if self._proc and self._proc.poll() is None:  # 如果进程仍在运行
                self._proc.terminate()                    # 终止进程
        except Exception as e:
            logger.error(f"终止进程时出错: {e}")

    def _emit(self, msg: str):
        """
        发射带时间戳的日志消息
        
        Args:
            msg: 要发射的消息
        """
        self.log.emit(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def _mask_cmd(self, cmd: List[str]) -> str:
        """
        在命令中屏蔽敏感信息
        
        Args:
            cmd: 命令部分列表
            
        Returns:
            屏蔽后的命令字符串
        """
        out: List[str] = []                              # 输出列表
        skip = False                                     # 跳过标志
        for part in cmd:
            if skip:
                out.append("******")                     # 用星号替换密码
                skip = False
                continue
            # 检查是否为密码参数
            if part.lower() in ("-password", "--password"):
                out.append(part)
                skip = True
            else:
                out.append(part)
        return " ".join(out)

    def run(self):
        """运行下载过程"""
        # 验证输入参数
        if not self.ids:
            self.finished.emit(False, "没有可下载的 ID")
            return
            
        if not is_valid_we_root(self.we_root):
            self.finished.emit(False, "保存路径无效（必须包含 projects/myprojects）")
            return
            
        if not os.path.exists(DOWNLOADER_EXE):
            self.finished.emit(False, f"找不到下载器：{DOWNLOADER_EXE}")
            return
            
        if not self.username:
            self.finished.emit(False, "未填写账号")
            return
            
        if not self.password:
            self.finished.emit(False, "未填写密码")
            return

        total = len(self.ids)                            # 总项目数
        ok = 0                                           # 成功下载数
        self.queue_progress.emit(0)                      # 初始化队列进度
        self.item_progress.emit(0)                       # 初始化项目进度

        # 遍历所有项目ID
        for i, item_id in enumerate(self.ids):
            if self._stop:                               # 检查是否需要停止
                self.finished.emit(False, f"已取消：成功 {ok}/{total}")
                return

            # 创建目标目录
            target_dir = os.path.join(self.we_root, "projects", "myprojects", item_id)
            try:
                os.makedirs(target_dir, exist_ok=True)
            except OSError as e:
                self._emit(f"❌ 创建目录失败 {target_dir}: {e}")
                continue
                
            # 构建下载命令
            cmd = [
                DOWNLOADER_EXE,
                "-app", STEAM_APP_ID,
                "-pubfile", item_id,
                "-verify-all",
                "-username", self.username,
                "-password", self.password,
                "-dir", target_dir,
            ]
            
            self._emit(f"开始下载：{item_id} ({i+1}/{total})")
            self._emit(f"执行命令：{self._mask_cmd(cmd)}")

            # 启动子进程
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except Exception as e:
                self._emit(f"❌ 启动失败：{e}")
                continue

            # 读取子进程输出
            while True:
                if self._stop:                           # 检查是否需要停止
                    self._emit("⏹️已取消")
                    break
                    
                line = self._proc.stdout.readline() if self._proc.stdout else ""
                if line == "" and self._proc.poll() is not None:
                    break
                    
                if line:
                    s = line.rstrip("\n")
                    self.log.emit(s)
                    m = re.search(r"(\d+)%", s)          # 匹配进度百分比
                    if m:
                        self.item_progress.emit(max(0, min(100, int(m.group(1)))))

            rc = self._proc.poll()                       # 获取进程返回码
            if rc == 0 and not self._stop:               # 下载成功
                ok += 1
                self._emit(f"✅ {item_id} - 完成")
            elif self._stop:                             # 被取消
                self.finished.emit(False, f"已取消：成功 {ok}/{total}")
                return
            else:                                        # 下载失败
                self._emit(f"❌ {item_id} - 失败（exit={rc}）")

            self.item_progress.emit(0)                   # 重置项目进度
            self.queue_progress.emit(int(((i+1)/max(1, total))*100))  # 更新队列进度

        self.finished.emit(True, f"下载完成：成功 {ok}/{total}")  # 发射完成信号


class DownloadPage(QWidget):
    """下载页面控件类"""
    start_requested = Signal()                           # 开始下载请求信号
    stop_requested = Signal()                            # 停止下载请求信号

    def __init__(self):
        """初始化下载页面"""
        super().__init__()
        self._setup_ui()                                 # 设置界面
        
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)                       # 创建垂直布局
        layout.setSpacing(15)                            # 设置间距
        layout.setContentsMargins(10, 10, 10, 10)        # 设置内容边距
        
        # 凭据卡片
        credentials_card = QFrame()
        credentials_card.setObjectName("credentialsCard")
        credentials_card.setProperty("class", "card")
        credentials_layout = QVBoxLayout(credentials_card)
        
        credentials_form = QFormLayout()
        credentials_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)  # 修复：添加AlignmentFlag
        credentials_form.setHorizontalSpacing(15)
        credentials_form.setVerticalSpacing(10)
        
        # 用户名输入框
        self.username_input = QLineEdit()
        credentials_form.addRow("账号：", self.username_input)
        
        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # 密码模式
        credentials_form.addRow("密码：", self.password_input)
        
        # 记住密码复选框
        self.remember_pw = QCheckBox("记住密码（本机保存）")
        credentials_form.addRow("", self.remember_pw)
        
        credentials_layout.addLayout(credentials_form)
        layout.addWidget(credentials_card)
        
        # 路径卡片
        path_card = QFrame()
        path_card.setObjectName("pathCard")
        path_card.setProperty("class", "card")
        path_layout = QVBoxLayout(path_card)
        
        path_form = QFormLayout()
        path_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)  # 修复：添加AlignmentFlag
        path_form.setHorizontalSpacing(15)
        path_form.setVerticalSpacing(10)
        
        # 保存路径输入框
        self.path_input = QLineEdit()
        path_form.addRow("保存路径：", self.path_input)
        
        # 路径按钮布局
        path_buttons = QHBoxLayout()
        self.btn_auto = QPushButton("自动检测")           # 自动检测按钮
        self.btn_choose = QPushButton("手动选择")         # 手动选择按钮
        path_buttons.addWidget(self.btn_auto)
        path_buttons.addWidget(self.btn_choose)
        path_buttons.addStretch()                        # 添加弹性空间
        
        path_form.addRow("", path_buttons)
        path_layout.addLayout(path_form)
        layout.addWidget(path_card)
        
        # ID输入卡片
        id_card = QFrame()
        id_card.setObjectName("idCard")
        id_card.setProperty("class", "card")
        id_layout = QVBoxLayout(id_card)
        
        id_layout.addWidget(QLabel("输入创意工坊 ID（可每行一个，也可粘贴链接/文字）："))
        self.id_text = QTextEdit()                       # ID文本编辑器
        self.id_text.setMaximumHeight(150)               # 最大高度
        id_layout.addWidget(self.id_text)
        layout.addWidget(id_card)
        
        # 操作按钮卡片
        action_card = QFrame()
        action_card.setObjectName("actionCard")
        action_card.setProperty("class", "card")
        action_layout = QHBoxLayout(action_card)
        
        action_layout.addStretch()
        self.btn_start = QPushButton("开始下载")          # 开始下载按钮
        self.btn_stop = QPushButton("停止/取消")          # 停止/取消按钮
        self.btn_stop.setEnabled(False)                  # 初始禁用停止按钮
        action_layout.addWidget(self.btn_start)
        action_layout.addWidget(self.btn_stop)
        action_layout.addStretch()
        
        layout.addWidget(action_card)
        
        # 进度条卡片
        progress_card = QFrame()
        progress_card.setObjectName("progressCard")
        progress_card.setProperty("class", "card")
        progress_layout = QVBoxLayout(progress_card)
        
        self.progress_queue = QProgressBar()             # 队列进度条
        self.progress_queue.setFormat("队列进度：%p%")
        self.progress_item = QProgressBar()              # 当前任务进度条
        self.progress_item.setFormat("当前任务：%p%")
        progress_layout.addWidget(self.progress_queue)
        progress_layout.addWidget(self.progress_item)
        
        layout.addWidget(progress_card)
        layout.addStretch()
        
        # 连接信号
        self.btn_start.clicked.connect(self._on_start_clicked)
        self.btn_stop.clicked.connect(self._on_stop_clicked)

    def _on_start_clicked(self) -> None:
        """处理开始按钮点击事件"""
        self.start_requested.emit()
        
    def _on_stop_clicked(self) -> None:
        """处理停止按钮点击事件"""
        self.stop_requested.emit()


class LogPage(QWidget):
    """日志页面控件类"""
    def __init__(self):
        """初始化日志页面"""
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 日志卡片
        log_card = QFrame()
        log_card.setObjectName("logCard")
        log_card.setProperty("class", "card")
        log_layout = QVBoxLayout(log_card)
        
        # 顶部控制栏
        top_layout = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索日志（占位）")
        self.btn_clear = QPushButton("清空")              # 清空按钮
        top_layout.addWidget(self.search, 1)
        top_layout.addWidget(self.btn_clear)
        log_layout.addLayout(top_layout)
        
        # 日志视图
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)                  # 设置为只读
        log_layout.addWidget(self.log_view)
        
        layout.addWidget(log_card)
        layout.addStretch()
        
        # 连接信号
        self.btn_clear.clicked.connect(self.log_view.clear)


class SettingsPage(QWidget):
    """设置页面控件类"""
    bg_changed = Signal(str)                             # 背景改变信号
    bg_toggle_changed = Signal(bool)                     # 背景开关改变信号

    def __init__(self):
        """初始化设置页面"""
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 设置卡片
        settings_card = QFrame()
        settings_card.setObjectName("settingsCard")
        settings_card.setProperty("class", "card")
        settings_layout = QVBoxLayout(settings_card)
        
        settings_layout.addWidget(QLabel("设置"))
        
        # 昵称布局
        nickname_layout = QHBoxLayout()
        nickname_layout.addWidget(QLabel("昵称："))
        self.nickname = QLineEdit()
        nickname_layout.addWidget(self.nickname, 1)
        settings_layout.addLayout(nickname_layout)
        
        # 背景设置网格
        bg_grid = QGridLayout()
        self.bg_enabled = QCheckBox("启用联网背景图")      # 背景启用复选框
        self.bg_url = QLineEdit()
        self.bg_url.setPlaceholderText("背景图 URL（联网）")
        self.btn_apply_bg = QPushButton("应用背景")       # 应用背景按钮
        bg_grid.addWidget(self.bg_enabled, 0, 0, 1, 2)
        bg_grid.addWidget(QLabel("背景 URL："), 1, 0)
        bg_grid.addWidget(self.bg_url, 1, 1)
        bg_grid.addWidget(self.btn_apply_bg, 2, 1)
        settings_layout.addLayout(bg_grid)
        
        # 自动滚动设置
        self.auto_scroll = QCheckBox("日志自动滚动")       # 自动滚动复选框
        settings_layout.addWidget(self.auto_scroll)
        
        settings_layout.addStretch()
        layout.addWidget(settings_card)
        layout.addStretch()
        
        # 连接信号
        self.btn_apply_bg.clicked.connect(self._on_apply_bg_clicked)
        self.bg_enabled.toggled.connect(self._on_bg_enabled_toggled)
        
    def _on_apply_bg_clicked(self) -> None:
        """处理应用背景按钮点击事件"""
        self.bg_changed.emit(self.bg_url.text().strip())

    def _on_bg_enabled_toggled(self, checked: bool) -> None:
        """
        处理背景启用切换事件
        
        Args:
            checked: 切换状态
        """
        self.bg_toggle_changed.emit(checked)


class MainWindow(QMainWindow):
    """主应用程序窗口类"""
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self._setup_configuration()                      # 设置配置
        self._setup_ui()                                 # 设置界面
        self._restore_state()                            # 恢复状态
        self._setup_connections()                        # 设置连接
        self.bg_loader: Optional[BackgroundLoader] = None  # 背景加载器
        self.worker: Optional[DownloadWorker] = None     # 下载工作线程
        
        # 如果启用了背景则加载背景
        if self.page_settings.bg_enabled.isChecked():
            self._load_bg_async(self.page_settings.bg_url.text().strip())

    def _setup_configuration(self):
        """设置应用程序配置"""
        cfg = load_json(CONFIG_FILE)                     # 加载配置文件
        cfg = migrate_legacy_path_if_needed(cfg)         # 迁移旧配置
        cfg = ensure_config_defaults(cfg)                # 确保默认配置
        self.cfg = cfg
        save_json(CONFIG_FILE, self.cfg)                 # 保存配置

    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("Wallpaper Engine 创意工坊下载器（03.py / PySide6）")
        self.resize(1100, 720)                           # 设置窗口大小
        self.setMinimumSize(800, 600)                    # 设置最小尺寸

        # 中央控件
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # 导航栏
        self.nav = QListWidget()
        self.nav.setFixedWidth(180)
        for name in ["下载", "日志", "设置"]:
            self.nav.addItem(QListWidgetItem(name))

        # 页面
        self.stack = QStackedWidget()
        self.page_download = DownloadPage()
        self.page_log = LogPage()
        self.page_settings = SettingsPage()
        self.stack.addWidget(self.page_download)
        self.stack.addWidget(self.page_log)
        self.stack.addWidget(self.page_settings)
        
        root_layout.addWidget(self.nav)
        root_layout.addWidget(self.stack, 1)

        # 背景标签
        self.bg_label = QLabel(self)
        self.bg_label.lower()
        self.bg_label.setScaledContents(True)
        self._apply_fallback_background()

        # 导航连接
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)

    def _restore_state(self):
        """从配置恢复UI状态"""
        # 恢复上次页面
        last_page = self.cfg.get("ui_last_page", "下载")
        self.nav.setCurrentRow({"下载": 0, "日志": 1, "设置": 2}.get(last_page, 0))
        
        # 恢复下载页面字段
        self.page_download.path_input.setText(self.cfg.get("save_location", ""))
        self.page_download.username_input.setText(self.cfg.get("login_username", ""))
        self.page_download.remember_pw.setChecked(bool(self.cfg.get("remember_password", False)))
        if self.page_download.remember_pw.isChecked():
            self.page_download.password_input.setText(self.cfg.get("login_password", ""))

        # 恢复设置页面字段
        self.page_settings.nickname.setText(self.cfg.get("nickname", ""))
        self.page_settings.bg_enabled.setChecked(bool(self.cfg.get("bg_enabled", True)))
        self.page_settings.bg_url.setText(self.cfg.get("bg_url", DEFAULT_BG_URL))
        self.page_settings.auto_scroll.setChecked(bool(self.cfg.get("auto_scroll_log", True)))

    def _setup_connections(self):
        """设置信号/槽连接"""
        # 页面更改跟踪
        self.stack.currentChanged.connect(self._save_ui_last_page)
        
        # 下载页面连接
        self.page_download.btn_auto.clicked.connect(self._on_auto_detect_path)
        self.page_download.btn_choose.clicked.connect(self._on_choose_path)
        self.page_download.start_requested.connect(self._on_start_download)
        self.page_download.stop_requested.connect(self._on_stop_download)
        self.page_download.remember_pw.toggled.connect(self._on_remember_pw_toggled)
        self.page_download.username_input.textChanged.connect(self._on_login_changed)
        self.page_download.password_input.textChanged.connect(self._on_login_changed)

        # 设置页面连接
        self.page_settings.bg_changed.connect(self._on_bg_url_changed)
        self.page_settings.bg_toggle_changed.connect(self._on_bg_toggle_changed)
        self.page_settings.nickname.textChanged.connect(self._on_nickname_changed)
        self.page_settings.auto_scroll.toggled.connect(self._on_auto_scroll_toggled)

    def _cleanup_and_exit(self):
        """清理并退出应用程序"""
        QApplication.quit()

    def _apply_fallback_background(self):
        """应用备用渐变背景"""
        self.bg_label.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #3498db, stop:1 #9b59b6);")

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        处理窗口调整大小事件
        
        Args:
            event: 调整大小事件
        """
        super().resizeEvent(event)
        self.bg_label.resize(self.size())

    def _load_bg_async(self, url: str):
        """
        异步加载背景
        
        Args:
            url: 背景图像URL
        """
        if not url:
            self._apply_fallback_background()
            return
            
        if self.bg_loader and self.bg_loader.isRunning():
            self.bg_loader.terminate()
            self.bg_loader.wait(500)
            
        self.bg_loader = BackgroundLoader(url, self.size())
        self.bg_loader.loaded.connect(self._set_background_pixmap)
        self.bg_loader.failed.connect(self._on_bg_load_failed)
        self.bg_loader.start()

    def _set_background_pixmap(self, pixmap: QPixmap) -> None:
        """
        设置背景图像
        
        Args:
            pixmap: 背景图像
        """
        self.bg_label.setPixmap(pixmap)
        
    def _on_bg_load_failed(self, err: str) -> None:
        """
        处理背景加载失败
        
        Args:
            err: 错误消息
        """
        self._append_log(f"背景图加载失败，已降级：{err}")
        self._apply_fallback_background()

    def _save_ui_last_page(self, index: int):
        """
        保存最后UI页面到配置
        
        Args:
            index: 页面索引
        """
        self.cfg["ui_last_page"] = {0: "下载", 1: "日志", 2: "设置"}.get(index, "下载")
        save_json(CONFIG_FILE, self.cfg)

    def _on_nickname_changed(self, text: str):
        """
        处理昵称更改
        
        Args:
            text: 新昵称
        """
        self.cfg["nickname"] = text
        save_json(CONFIG_FILE, self.cfg)

    def _on_auto_scroll_toggled(self, checked: bool):
        """
        处理自动滚动切换
        
        Args:
            checked: 切换状态
        """
        self.cfg["auto_scroll_log"] = bool(checked)
        save_json(CONFIG_FILE, self.cfg)

    def _on_login_changed(self) -> None:
        """处理登录信息更改"""
        self.cfg["login_username"] = self.page_download.username_input.text().strip()
        if self.page_download.remember_pw.isChecked():
            self.cfg["login_password"] = self.page_download.password_input.text()
        save_json(CONFIG_FILE, self.cfg)

    def _on_remember_pw_toggled(self, checked: bool):
        """
        处理记住密码切换
        
        Args:
            checked: 切换状态
        """
        self.cfg["remember_password"] = bool(checked)
        if not checked:
            self.cfg["login_password"] = ""
        save_json(CONFIG_FILE, self.cfg)

    def _append_log(self, msg: str):
        """
        追加消息到日志
        
        Args:
            msg: 要追加的消息
        """
        self.page_log.log_view.append(msg)
        if self.page_settings.auto_scroll.isChecked():
            scrollbar = self.page_log.log_view.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _on_bg_url_changed(self, url: str):
        """
        处理背景URL更改
        
        Args:
            url: 新背景URL
        """
        self.cfg["bg_url"] = url
        save_json(CONFIG_FILE, self.cfg)
        if self.page_settings.bg_enabled.isChecked():
            self._load_bg_async(url)

    def _on_bg_toggle_changed(self, enabled: bool):
        """
        处理背景切换更改
        
        Args:
            enabled: 切换状态
        """
        self.cfg["bg_enabled"] = bool(enabled)
        save_json(CONFIG_FILE, self.cfg)
        if enabled:
            self._load_bg_async(self.page_settings.bg_url.text().strip())
        else:
            self._apply_fallback_background()

    def _on_auto_detect_path(self):
        """处理自动检测路径按钮点击"""
        path = auto_detect_we_path()
        if path and is_valid_we_root(path):
            self.page_download.path_input.setText(path)
            self.cfg["save_location"] = path
            save_json(CONFIG_FILE, self.cfg)
            QMessageBox.information(self, "自动检测", f"已检测到路径：{path}")
        else:
            QMessageBox.warning(
                self, 
                "自动检测", 
                "未检测到有效路径（需包含 projects/myprojects）。请手动选择。"
            )

    def _on_choose_path(self):
        """处理选择路径按钮点击"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择 Wallpaper Engine 根目录（需包含 projects/myprojects）"
        )
        if not folder:
            return
            
        if not is_valid_we_root(folder):
            QMessageBox.critical(
                self, 
                "路径无效", 
                "所选目录不是有效的项目目录：必须包含projects/myprojects。"
            )
            return
            
        self.page_download.path_input.setText(folder)
        self.cfg["save_location"] = folder
        save_json(CONFIG_FILE, self.cfg)

    def _on_start_download(self):
        """处理开始下载按钮点击"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "提示", "下载正在进行中。")
            return

        we_root = self.page_download.path_input.text().strip()
        if not is_valid_we_root(we_root):
            QMessageBox.critical(self, "错误", "保存路径无效：必须包含 projects/myprojects。")
            return

        username = self.page_download.username_input.text().strip()
        password = self.page_download.password_input.text()
        if not username or not password:
            QMessageBox.critical(self, "错误", "请先填写账号和密码（可选择是否记住密码）。")
            return

        self.cfg["login_username"] = username
        if self.page_download.remember_pw.isChecked():
            self.cfg["login_password"] = password
        save_json(CONFIG_FILE, self.cfg)

        ids, invalid_lines = parse_ids_fusion(self.page_download.id_text.toPlainText())
        if invalid_lines:
            self._append_log(f"⚠️ 无效行{len(invalid_lines)} 条（不会中断其它下载）")
        if not ids:
            QMessageBox.warning(self, "提示", "没有可下载的有效 ID（需要8~10 位数字）。")
            return

        # 更新UI以开始下载
        self.page_download.btn_start.setEnabled(False)
        self.page_download.btn_stop.setEnabled(True)
        self.page_download.progress_queue.setValue(0)
        self.page_download.progress_item.setValue(0)

        # 启动下载工作线程
        self.worker = DownloadWorker(ids, we_root, username, password)
        self.worker.log.connect(self._append_log)
        self.worker.queue_progress.connect(self.page_download.progress_queue.setValue)
        self.worker.item_progress.connect(self.page_download.progress_item.setValue)
        self.worker.finished.connect(self._on_download_finished)
        self.worker.start()

    def _on_stop_download(self):
        """处理停止下载按钮点击"""
        if self.worker and self.worker.isRunning():
            self.worker.request_stop()
            self._append_log("⏹️ 已请求停止（将尽快终止当前任务并停止队列）")

    def _on_download_finished(self, success: bool, message: str):
        """
        处理下载完成
        
        Args:
            success: 下载是否成功
            message: 完成消息
        """
        self.page_download.btn_start.setEnabled(True)
        self.page_download.btn_stop.setEnabled(False)
        QMessageBox.information(
            self, 
            "完成" if success else "结束", 
            message
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        处理窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        try:
            if self.worker and self.worker.isRunning():
                reply = QMessageBox.question(
                    self, 
                    '确认退出', 
                    '下载正在进行中，确定要退出吗？', 
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.worker.request_stop()
                    # 如果可用，在状态栏显示消息
                    try:
                        self.statusBar().showMessage("正在停止下载...")
                    except Exception:
                        pass  # 忽略状态栏不可用的情况
                        
                    # 在后台等待工作线程完成
                    self.worker.finished.connect(self._on_worker_finished)
                    event.ignore()
                    return
                else:
                    event.ignore()
                    return
        except Exception as e:
            logger.error(f"处理关闭事件时出错: {e}")
            
        event.accept()
        
    def _on_worker_finished(self) -> None:
        """处理工作线程完成事件"""
        self._cleanup_and_exit()


def main():
    """应用程序入口点"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setStyleSheet(STYLESHEET)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()