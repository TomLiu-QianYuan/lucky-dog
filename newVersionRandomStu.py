import json
import logging
import os
import random
from datetime import date
from datetime import datetime
from os import getcwd, path, mkdir
from random import randint
from sys import argv, exit
from threading import Thread
from time import time, sleep

import cv2
import playsound
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QSizePolicy, QComboBox
)
from qt_material import apply_stylesheet

import choose_subject

# 配置日志记录基本设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建 logger 对象
logger = logging.getLogger(__name__)
HELP = r"""
版本v5.5.5
-作者:TomLiu
-识别模型:yolov5su(小型模型)
"""
VERSION = '''
项目地址:https://github.com/TomLiu-QianYuan/lucky-dog
📚 使用指南
    1️⃣ 首次启动自动生成本月专属文件夹
    📁 名称示例："3月1日-3月31日"
    2️⃣ 科目设置（两步完成）
    🎯 第一步：点击选择当前授课科目
    ➕ 第二步：如需新增科目，点击"添加"添加
二、开始抽选
    ⏰ 设置倒计时区间（如设30-60秒，系统自动随机计时）
    🔄 点击【开始抽选】启动随机轮盘
    🎉 倒计时结束时，头像框高亮显示被选同学
三、即时评分（三选一操作）➡️ 自动更新总分：本月文件夹/当前科目/学号/总分.txt
    👍 加分：点击【加分】按钮
    ➡️ 自动保存至：本月文件夹/当前科目/学号/加分/时间+加分.png
    📸 示例：20240315_1430_加分.png
    👎 减分：点击【减分】按钮
    ➡️ 自动保存至：本月文件夹/当前科目/学号/减分/时间+减分.png
    ⏭️ 跳过：不点击任何按钮，直接进入下一轮抽选
注：
    千万别学It，特别是这种软件！
    如果写出代码不难，改bug就会很难! 特别是小bug、不报错的bug。
    如果改bug不难，调试环境最难! 没有资料全靠菩萨保佑!
'''
subject = ''
playing_sound = Thread()


def get_month_range():
    today = date.today()
    # 获取本月的第一天
    start_of_month = date(today.year, today.month, 1)
    # 获取下个月的第一天
    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1)
    else:
        end_of_month = date(today.year, today.month + 1, 1)
    # 由于 end_of_month 是下个月的第一天，所以要减去一天，得到本月的最后一天
    end_of_month = end_of_month - date.resolution
    # 修改为完整的 ISO 8601 日期格式
    month_range = f"{start_of_month.isoformat()}至{end_of_month.isoformat()}"
    return month_range


def is_today_in_month_range():
    global chinese_date
    global subject

    if not os.path.exists(get_month_range()) and not os.path.isdir(get_month_range()):
        logger.info(f"不存在{get_month_range()}")
        os.mkdir(str(get_month_range()))
    chinese_date = get_month_range()
    print(get_month_range() + "\\" + subject)
    return os.path.join(os.getcwd(), get_month_range()) + "\\" + subject


logger.info("库加载完毕")
now = datetime.now()
chinese_date = is_today_in_month_range()
# 全局变量，用于保存最后绘制且处理完成的帧数据（包含准确的人头框选等情况）
last_drawn_frame = None
# 全局变量，用于保存最后选中的人头框坐标
last_selected_head_box = None


def get_chinese_date():
    return is_today_in_month_range()


def get_color_dict():
    return {
        "红色": QColor("#FF0000"),
        "绿色": QColor("#00FF00"),
        "蓝色": QColor("#0000FF"),
        "黄色": QColor("#FFFF00"),
        "品红": QColor("#FF00FF"),
        "青色": QColor("#00FFFF"),
        "黑色": QColor("#000000"),
        "白色": QColor("#FFFFFF"),
        "橙色": QColor("#FFA500"),
        "紫色": QColor("#800080"),
        "棕色": QColor("#A52A2A"),
        "黑色2": QColor("#808080")
    }


# 加载预训练的YOLOv5模型
def load_model():
    from ultralytics import YOLO
    model_path = path.join("models", "yolov5su.pt")
    model = YOLO(model_path)
    model.fuse()
    model.half()

    logger.info("yolov5su.pt模型导入完毕")
    return model


def create_subject_folder():
    config = json.loads(open("config.json", 'r', encoding="utf-8").read())
    subjects = config.get('subjects', [])
    for i in subjects:
        try:
            os.mkdir(get_month_range() + "\\" + i)
        except:
            ...


def update_score_file(index_path):
    total_score_file = os.path.join(index_path, "总分.txt")
    if not os.path.exists(total_score_file):
        with open(total_score_file, 'w', encoding='utf-8') as f:
            f.write('0\n')
    red_score, add_score = 0, 0
    try:
        red_score = len(os.listdir(os.path.join(index_path, "减分")))
    except:
        ...
    try:
        add_score = len(os.listdir(os.path.join(index_path, "加分")))
    except:
        ...
    total_score = add_score - red_score
    with open(total_score_file, 'w', encoding='utf-8') as f:
        f.write(f'总分统计为:{total_score}\n')


# 主窗口类，包含整个应用的界面布局及核心功能逻辑（使用PySide6构建）
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        global last_drawn_frame, last_selected_head_box
        self.random_time = None  # 随机时长变量
        self.version_info_button = None  # “信息”按钮
        self.start_button = None  # 开始抽取按钮
        self.add_score_button = None  # 新增加分按钮
        self.subtract_score_button = None  # 新增减分按钮
        self.final_frame_label = None  # 最终显示的画面变量
        self.time_c_label = None  # 显示“5-10时长...”的文字
        self.time_c_entry = None  # 输入随机时长区间文字框
        self.color_label = None  # 提示颜色选择文字
        self.color_combobox = None  # 选择颜色下拉框
        self.selected_index = None  # 新增：保存选中的序号
        self.init_ui()

        self.current_index = 0
        self.cap = cv2.VideoCapture(0)  # 序号为0的摄像头对象
        if not self.cap.isOpened():
            self.cap = None
            logger.error("无法获取摄像头画面，可能摄像头未正确连接或出现故障。")

        self.detection_thread = None  # 抽取的线程变量
        self.final_frame = None  # 最终画框变量
        self.is_running = False  # 是否正在运行变量
        self.model = load_model()  # 加载模型
        self.remaining_time = 0  # 剩余时长变量

        self.folder_path = path.join(getcwd(), get_chinese_date())  # 保存图片的文件路径

        if not path.exists(self.folder_path):
            if not os.path.exists(self.folder_path):
                mkdir(self.folder_path)  # 创建父文件夹文件夹
                logger.info(f"创建文件夹完毕{self.folder_path}")

            logger.info(f"创建文件夹完毕{self.folder_path}")

        if not path.exists(self.folder_path + "\\加分"):
            try:
                mkdir(self.folder_path + "\\加分")  # 在父文件夹下创建“加分”文件夹
                logger.info(f"创建文件夹完毕{self.folder_path}\\加分")
            except:
                ...
            try:
                mkdir(self.folder_path + "\\减分")  # 在父文件夹下创建“减分”文件夹
                logger.info(f"创建文件夹完毕{self.folder_path}\\减分")
            except:
                ...

        self.pre_load_model()

    def init_ui(self):
        # 设置布局
        main_layout = QVBoxLayout()

        # 设置为宋体
        # font = QFont("SimSun")
        # Qapp = QApplication.instance()
        # Qapp.setFont(font)

        # 摄像头画面布局
        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(0, 0, 0, 0)
        camera_layout.setSpacing(0)
        self.final_frame_label = QLabel()
        size_policy = self.final_frame_label.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        self.final_frame_label.setSizePolicy(size_policy)
        self.final_frame_label.setScaledContents(True)
        camera_layout.addWidget(self.final_frame_label)
        camera_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(camera_layout)

        # 创建布局
        config_layout = QHBoxLayout()

        # 时长区间输入框布局
        left_layout = QVBoxLayout()
        self.time_c_label = QLabel("设置抽取时长跨度（格式：开始时长-结束时长，单位：s）")
        self.time_c_entry = QLineEdit()
        self.time_c_entry.setEnabled(False)
        self.time_c_entry.setText('7-10')
        left_layout.addWidget(self.time_c_label)
        left_layout.addWidget(self.time_c_entry)

        # 开始按钮布局
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_detection)
        left_layout.addWidget(self.start_button)

        # 新增下拉框布局
        self.index_combo = QComboBox()
        self.index_combo.addItems([str(i) + "号" for i in range(1, 41)])
        self.index_combo.currentIndexChanged.connect(self.update_button_status)
        self.index_combo.setCurrentIndex(0)
        self.index_combo.setEnabled(False)
        left_layout.addWidget(self.index_combo)

        # 新增加分按钮
        self.add_score_button = QPushButton("加分")
        self.add_score_button.clicked.connect(self.handle_add_score)
        self.add_score_button.setEnabled(False)  # 初始设置为不可点击
        left_layout.addWidget(self.add_score_button)

        # 新增减分按钮
        self.subtract_score_button = QPushButton("减分")
        self.subtract_score_button.clicked.connect(self.handle_subtract_score)
        self.subtract_score_button.setEnabled(False)  # 初始设置为不可点击
        left_layout.addWidget(self.subtract_score_button)

        left_layout.setAlignment(Qt.AlignCenter)
        config_layout.addLayout(left_layout)

        # 查看信息按钮布局
        self.version_info_button = QPushButton("使用说明以及版本信息")
        self.version_info_button.clicked.connect(self.show_version_info)
        left_layout.addWidget(self.version_info_button)

        # 配置进总布局
        main_layout.addLayout(config_layout)
        self.setLayout(main_layout)

    def update_button_status(self):
        self.selected_index = self.index_combo.currentText()
        self.add_score_button.setEnabled(bool(self.selected_index))
        self.subtract_score_button.setEnabled(bool(self.selected_index))

    def play_sound(self):
        if random.randint(0,10) == 1:
            self.paly_sound_dir("processVoice")

    def play_ending_sound(self):
        try:
            self.paly_sound_dir("endingVoice")
        except:
            sleep(3)
            self.paly_sound_dir("endingVoice", False)

    def start_detection(self):
        logger.info("开始检测")

        # 开始抽取函数
        if not self.is_running:
            # 不允许再次点击“开始”按钮
            self.index_combo.setEnabled(False)
            self.start_button.setEnabled(False)
            # 获取时间区间
            time_span_str = self.time_c_entry.text()
            time_span_parts = time_span_str.split('-')
            # 判断区间填写是否合规
            if len(time_span_parts) == 2:
                # 切片获取时长区间，以及计算随机的时间
                start_time = int(time_span_parts[0].strip())
                end_time = int(time_span_parts[1].strip())
                self.random_time = randint(start_time, end_time)
            else:
                # 区间填写不合格时，弹窗
                QMessageBox.warning(self, "提示", "输入的抽取时长格式不正确，请按正确格式输入。")
                self.index_combo.setEnabled(True)
                self.start_button.setEnabled(True)

                return
            color_str = '青色'
            # 启动抽取线程
            self.detection_thread = Thread(target=self._run_detection_thread,
                                           args=(
                                               start_time,
                                               end_time,
                                               color_str
                                           )
                                           )
            self.detection_thread.start()

            self.is_running = True
            Thread(target=self.play_sound).run()

        else:
            QMessageBox.warning(self, "提示", "当前正在进行检测操作，不能再次点击开始按钮。")

    def _run_detection_thread(self, start_time, end_time, color_str):
        """
        在独立线程中执行检测逻辑，不阻塞主线程
        """
        logger.info("启动抽取线程")
        self.add_score_button.setEnabled(False)
        self.subtract_score_button.setEnabled(False)
        self.cropped_pixmap = None

        self.random_time = randint(start_time, end_time)
        start_time = time()
        frame_count = 0
        x1, x2, y1, y2 = 0, 0, 0, 0
        color = get_color_dict()[color_str]  # 框颜色

        while True:
            detect_interval = randint(5, 15)
            global last_drawn_frame, last_selected_head_box
            elapsed_time = int(time() - start_time)  # 已消耗时间
            self.remaining_time = self.random_time - elapsed_time  # 剩余时长计算
            if self.cap is None or not self.cap.isOpened():
                break
            ret, frame = self.cap.read()
            if not ret:
                break
            if self.remaining_time <= 1:  # 结束了
                cv2.putText(frame,
                            random.choice(["", "good luck"]),
                            (int(x1), int(y1)),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1.0,
                            color.getRgb()[:3],
                            2)

            if frame_count % detect_interval == 0:
                # 加载模型检测
                results = self.model(frame)
                heads = []
                for result in results:
                    for box in result.boxes:
                        cls = int(box.cls)
                        if cls == 0:
                            # 获取所有人物坐标
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            heads.append([x1, y1, x2, y2])
                if len(heads) > 0:
                    if self.current_index >= len(heads):
                        self.current_index = 0
                    x1, y1, x2, y2 = heads[self.current_index]
                    self.current_index += 1
            if self.remaining_time > 1:
                # 有剩余时间时，展示剩余时间
                cv2.putText(frame,
                            str(self.remaining_time),
                            (
                                int(x1), int(y1)
                            ),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1.0,
                            color.getRgb()[:3],
                            2)
            # 绘制矩形
            cv2.rectangle(frame,
                          (int(x1), int(y1)),
                          (int(x2), int(y2)),
                          color.getRgb()[:3],
                          2)  # 绘制矩形
            try:
                # 将最后一张照片加载进final_frame_label
                height, width, channel = frame.shape
                q_image = QImage(frame.data, frame.shape[1], frame.shape[0],
                                 frame.strides[0], QImage.Format_BGR888)
                pixmap = QPixmap.fromImage(q_image)
                self.final_frame_label.setPixmap(pixmap)
                self.final_frame_label.setAlignment(Qt.AlignCenter)
                sleep(0.01)
            except Exception as e:
                logger.error(f"图像更新显示出现异常: {e}")

            frame_count += 1
            if self.remaining_time <= 1:  # 结束了
                try:

                    last_drawn_frame = frame.copy()  # 保存最后绘制的帧数据
                    last_selected_head_box = [x1, y1, x2, y2]  # 保存最后选中的人头框坐标
                    img = Image.fromarray(cv2.cvtColor(last_drawn_frame, cv2.COLOR_BGR2RGB))  # 保存
                    self.cropped_pixmap = img  # 保存，后续使用这个保存图片

                    logger.info("结束啦")
                except Exception as e:
                    logger.warning(f"图像更新显示出现异常: {e}")
                finally:
                    break
        self.play_ending_sound()
        self.add_score_button.setEnabled(True)
        self.subtract_score_button.setEnabled(True)

        # 抽取结束后，根据是否有选中的框来设置加分、减分按钮是否可点击
        self.index_combo.setEnabled(True)

        self.start_button.setEnabled(True)
        self.is_running = False

    def handle_add_score(self):
        """
        处理加分按钮点击事件的函数，通过实例变量self.cropped_pixmap的save方法保存对应图片
        """
        if not self.selected_index:
            QMessageBox.warning(self, "提示", "请先选择序号/学号")
            return
        if self.cropped_pixmap:
            # logger.info("播放音频:", voice)
            logger.info("add score")
            now2 = datetime.now()
            chinese_date2 = now2.strftime('%Y年%m月%d日%H时%M分%S秒').replace(':', '-')
            logger.warning(self.selected_index)
            index_folder = os.path.join(is_today_in_month_range(), self.selected_index)
            logger.warning(index_folder)
            if not os.path.exists(index_folder):
                os.mkdir(index_folder)
            score_folder = os.path.join(index_folder, "加分")
            if not os.path.exists(score_folder):
                print(score_folder)
                os.mkdir(score_folder)
            self.cropped_pixmap.save(f"{score_folder}\\{chinese_date2}加分.png", "PNG")
            logger.info(f"保存图片完毕{score_folder}\\{chinese_date2}加分.png")
            update_score_file(os.path.join(os.getcwd(), index_folder))  # 更新总分文件，加1分
            self.paly_sound_dir("addvoice")
            QMessageBox.information(self, "操作完成", f'学号为...加一分'.replace('...', score_folder.split('\\')[-2]))

            # self.add_score_button.setEnabled(False)  # 点击后设置为不可点击，可根据实际需求调整
            # self.subtract_score_button.setEnabled(False)  # 同步设置减分按钮不可点击，可调整
            # self.index_combo.setEnabled(False)

    def paly_sound_dir(self, dir: str, thread: bool = Thread):
        try:
            path = os.path.join(dir, random.choice(os.listdir(dir)))
            if thread:
                Thread(target=playsound.playsound, args=(path,)).start()
                return
            else:
                Thread(target=playsound.playsound, args=(path,)).run()

        except:
            ...

    def handle_subtract_score(self):
        """
        处理减分按钮点击事件的函数，通过实例变量self.cropped_pixmap的save方法保存对应图片
        """
        if not self.selected_index:
            QMessageBox.warning(self, "提示", "请先选择序号/学号")
            return

        if self.cropped_pixmap:
            # logger.info("播放音频:", voice)
            # playsound.playsound(voice)
            logger.info("sub score")

            now2 = datetime.now()
            chinese_date2 = now2.strftime('%Y年%m月%d日%H时%M分%S秒').replace(':', '-')
            index_folder = os.path.join(is_today_in_month_range(), self.selected_index)
            # print(index_folder)
            if not os.path.exists(index_folder):
                os.mkdir(index_folder)
            score_folder = os.path.join(index_folder, "减分")
            print(score_folder)
            if not os.path.exists(score_folder):
                os.mkdir(score_folder)
            self.cropped_pixmap.save(f"{score_folder}\\{chinese_date2}减分.png", "PNG")
            logger.info(f"保存图片完毕{score_folder}\\{chinese_date2}减分.png")
            update_score_file(os.path.join(os.getcwd(), index_folder))  # 更新总分文件，减1分
            self.paly_sound_dir("delvoice")
            QMessageBox.information(self, "操作完成", f'学号为...减一分'.replace('...', score_folder.split('\\')[-2]))
            # self.add_score_button.setEnabled(False)  # 点击后设置为不可点击，可根据实际需求调整
            # self.subtract_score_button.setEnabled(False)  # 同步设置减分按钮不可点击，可调整
            # self.index_combo.setEnabled(False)

    def pre_load_model(self):
        ret, frame = self.cap.read()  # 读取这一帧画面

        if ret:
            results = self.model(frame)  # 调用模型识别
            heads = []
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls)
                    if cls == 0:
                        # 将所有人坐标依次for循环添加到heads list
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        heads.append([x1, y1, x2, y2])
            color_str = '青色'
            color = get_color_dict()[color_str]  # 获取指定颜色

            for x1, y1, x2, y2 in heads:
                # 为每一个人坐标绘制矩形
                cv2.rectangle(frame,
                              (int(x1), int(y1)),
                              (int(x2), int(y2)),
                              color.getRgb()[:3],
                              2)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data,
                             width,
                             height,
                             bytes_per_line,
                             QImage.Format_RGB888
                             ).rgbSwapped()

            pixmap = QPixmap.fromImage(q_image)
            self.final_frame_label.setPixmap(pixmap)
            self.final_frame_label.setAlignment(Qt.AlignCenter)

    def show_version_info(self):
        info_text = f"{HELP}{VERSION}"
        QMessageBox.information(self, "版本信息", info_text)


if __name__ == "__main__":
    app = QApplication(argv)
    font = QFont("SimSun")
    app.setFont(font)
    apply_stylesheet(app, "dark_amber.xml")
    window = choose_subject.SubjectChooser()
    window.show()
    app.exec()

    chosen_subject = window.get_chosen_subject()  # 获取选择的科目
    subject = str(chosen_subject)
    if chosen_subject:
        logger.info(f"你选择的科目是: {chosen_subject}")
        window2 = MainWindow()

        window2.setWindowTitle(f"幸运儿抽取器{chosen_subject}{get_month_range()}")
        window2.resize(300, 190)
        window2.show()
        logger.info("窗口绘制完毕")
    else:
        logger.warning("未选择科目")
    exit(app.exec())
