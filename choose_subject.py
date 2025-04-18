import json
import re
import sys

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QMessageBox


class SubjectChooser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("科目选择器")
        self.setGeometry(100, 100, 300, 200)
        self.layout = QVBoxLayout()
        self.subject_combobox = QComboBox()
        self.subject_combobox.addItem("请选择科目")
        self.load_subjects()
        self.layout.addWidget(self.subject_combobox)
        self.new_subject_input = QLineEdit()
        self.layout.addWidget(self.new_subject_input)
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_subject)
        self.layout.addWidget(self.add_button)
        self.confirm_button = QPushButton("确认")
        self.confirm_button.clicked.connect(self.confirm_and_return)  # 连接确认按钮的点击事件到新的方法
        self.layout.addWidget(self.confirm_button)
        self.setLayout(self.layout)
        self.chosen_subject = None  # 用于存储选择的科目

    def load_subjects(self):
        self.subject_combobox.clear()
        self.subject_combobox.addItem("请选择科目")
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                subjects = config.get('subjects', [])
                for subject in subjects:
                    self.subject_combobox.addItem(subject)
        except FileNotFoundError:
            QMessageBox.warning(self, "错误", "未找到 config.json 文件")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "错误", "config.json 文件格式错误")

    def add_subject(self):
        new_subject = self.new_subject_input.text()
        if new_subject:
            if True:
                try:
                    self.update_config(new_subject)
                    self.subject_combobox.addItem(new_subject)
                    self.new_subject_input.clear()
                    QMessageBox.information(self, "成功", "科目添加成功")
                except FileNotFoundError:
                    QMessageBox.warning(self, "错误", "未找到 config.json 文件")
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "错误", "config.json 文件格式错误")
            else:
                QMessageBox.warning(self, "错误", "科目名称不合法")

    def validate_subject(self, subject):
        pattern = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fa5]+$')
        if len(subject) <= 50 and pattern.match(subject):
            return True
        return False

    def update_config(self, new_subject):
        try:
            with open('config.json', 'r+', encoding='utf-8') as f:
                config = json.load(f)
                subjects = config.get('subjects', [])
                if new_subject not in subjects:
                    subjects.append(new_subject)
                    config['subjects'] = subjects
                    f.seek(0)
                    json.dump(config, f, indent=4)
                    f.truncate()
        except FileNotFoundError:
            self.create_config(new_subject)

    def create_config(self, new_subject):
        config = {"subjects": [new_subject]}
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    def confirm_and_return(self):
        selected_subject = self.subject_combobox.currentText()  # 获取当前选中的科目
        if selected_subject != "请选择科目":  # 确保不是默认选项
            self.chosen_subject = selected_subject  # 存储选择的科目
            self.close()  # 关闭窗口
        else:
            QMessageBox.warning(self, "错误", "请选择一个科目")

    def get_chosen_subject(self):
        return self.chosen_subject  # 提供一个方法来获取选择的科目


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubjectChooser()
    window.show()
    app.exec()
    chosen_subject = window.get_chosen_subject()  # 获取选择的科目
    if chosen_subject:
        print(f"你选择的科目是: {chosen_subject}")
    else:
        print("未选择科目")
    sys.exit()
