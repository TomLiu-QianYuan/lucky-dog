# <p align="center"> 幸运儿抽取器 </p>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-GUI框架-green?logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/YOLOv5-目标检测-red?logo=pytorch" alt="YOLOv5">
  <img src="https://img.shields.io/badge/版本-v5.5.5-orange" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-brightgreen" alt="许可证">
</div>

---
## 概述
**幸运儿抽取器** 是一个简洁高效的随机学生抽取器，专为课堂提升互动与参与感而设计。该工具基于 **YOLOv5 AI模型** 进行人脸识别，随机选中学生，配合实时加减分功能，助力教师更高质量地进行课堂管理。

## 功能特色
- 🎯 **随机学生抽取**：通过摄像头实时捕捉画面，在设定时间后随机选中学生。
- 📊 **分数管理**：快速为学生加减分，自动保存结果到对应的目录。
- 📝 **自定义科目**：支持选择或新增科目，每个科目有独立的存档和管理。
- 📂 **自动文件夹生成**：按月创建特定目录，保存学生得分情况及加减分记录。
- 🔊 **语音提示**：重要操作配有语音反馈，提升互动感。
- 💻 **现代化用户界面**：基于 **PySide6** 和 **qt_material**，界面简洁优雅。
---

## 安装指南
### **环境依赖**
1. 安装 Python 3.8 或更高版本。
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### **下载代码**
1. 克隆仓库：
   ```bash
   git clone https://github.com/TomLiu-QianYuan/lucky-dog.git
   cd lucky-dog
   ```
2. 运行主程序：
   ```bash
   python newVersionRandomStu.py
   ```
---

## 使用说明
### **启动与设置**
1. **首次运行**：
   - 程序启动后，会自动为当前月份创建文件夹。
     - 文件夹示例：`"2023年03月01日至2023年03月31日"`.
2. **选择科目**：
   - 在科目选择界面选择已存在的科目。
   - 如果需要新增科目，请按照下方 **编辑配置文件** 指南操作。
3. **开始抽取**：
   - 设定时长范围（秒）。例如：`30-60`。
   - 点击 `开始` 按钮，随机选中一名学生。
4. **实时评分**：
   - 点击 **加分** 或 **减分** 按钮，系统会自动保存加减分图片并更新学生分数。
   - 文件存储将以 **时间戳** 格式保存在对应目录下。
   - 示例：`20240315_1430_加分.png`。

### **关闭应用**
- 直接关闭应用窗口，数据和文件会自动保存，无需额外操作。

---

## 如何切换模型
程序默认使用 **YOLOv5su模型**，可根据需要更换其他预训练模型。

1. 替换模型：
   - 将新模型（如 `yolov5m.pt`）存放到 `models/` 目录下。
   - 替换原有的 `yolov5su.pt` 文件。
   - 确保模型为 **YOLOv5** 格式，并与程序兼容。
2. 重启程序后，修改后的模型会自动加载。

---

## 修改 `config.json`（新增/删除科目）
### **定位配置文件**
文件路径：`config.json`
```json
{
    "subjects": [
        "Calculus BC",
        "Calculus AB",
        "PreCalculus",
        "Economics",
        "Computer Science",
        "PreComputer"
    ]
}
```
### **编辑科目列表**
- 添加科目：在 `"subjects"` 数组中新增字符串，例如：
  ```json
  {
      "subjects": [
          "物理",
          "数学",
          "历史",
          "计算机"
      ]
  }
  ```
- 保存后 **重新启动程序** 生效。

---

## 项目结构
```
lucky-dog/
├── models/                    # YOLOv5 预训练模型存放目录
│   └── yolov5su.pt           # 默认人脸识别模型（可替换为其他YOLO模型）
│
│── endingVoice/             # 每次结束播放语音提示文件目录（新增））
│── addVoice/             # 加分播放语音提示文件目录（新增））
│── delVoice/             # 减分播放语音提示文件目录（新增））
│── processVoice/             # 过程中播放语音提示文件目录（新增））
│
├── config.json               # 配置文件（存储科目列表、默认参数等）
│
├── 2023年03月01日至2023年03月31日/  # 示例月份文件夹
│   ├── Calculus BC/      # 科目名称
│   │   ├── 1号/          # 学生学号（按识别结果命名）
│   │   │   ├── 加分/     # 加分记录目录
│   │   │   │   ├── 20230315_1430_加分.png  # 抓拍图片（带时间戳）
│   │   │   │   └── 总分.txt          # 该学生加分历史
│   │   │   │   └── 减分/     # 减分记录目录（结构同加分）
│   │   │   └── 2号/          # 其他学生目录
|   └── Economics/        # 其他科目目录
│   └── ...                   # 其他月份文件夹
│
├── newVersionRandomStu.py    # 主程序入口
├── requirements.txt          # Python依赖库列表

```

---

## 常见问题
### **1. 摄像头无法工作怎么办？**
- 确认摄像头已正确连接。
- 检查系统权限：
  ```bash
  sudo chmod 777 /dev/video0  # 适用于Linux系统
  ```
- 更换摄像头端口编号（可在代码中修改 `cv2.VideoCapture(1)` 等）。

### **2. 添加新科目后没有显示？**
- 确保在 `config.json` 文件中正确添加科目。
- 重新启动程序以加载修改后的配置。

### **3. 分数保存在哪里？**
- 本地保存路径如下：
  ```
  当前月份文件夹/科目名/学号/加分或者减分/
  ```
  示例：
  ```
  2023年03月01日至2023年03月31日/Economics/1号/加分/20230315_1430_加分.png
  ```

---

## 贡献
欢迎提出建议和贡献代码！步骤如下：
1. Fork 本项目。
2. 创建一个分支：
   ```bash
   git checkout -b feature-name
   ```
3. 提交您的修改，并发送 Pull Request。

---

## 许可证
本项目基于 [MIT许可证](LICENSE)。自由使用、修改和分发。

---

## 致谢
- 感谢 **PySide6** 提供了精美的UI框架。
- 感谢 [Ultralytics YOLO](https://github.com/ultralytics/yolov5) 提供预训练模型。

---

## 联系我们
如有疑问或建议，请在 [GitHub](https://github.com/TomLiu-QianYuan/lucky-dog) 上提交 Issue。
