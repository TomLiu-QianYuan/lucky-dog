# 🎯 幸运儿抽取器 - 课堂互动系统 🎯
<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-GUI框架-green?logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/YOLOv5-目标检测-red?logo=pytorch" alt="YOLOv5">
  <img src="https://img.shields.io/badge/版本-v5.5.5-orange" alt="版本">
  <img src="https://img.shields.io/badge/许可证-MIT-brightgreen" alt="许可证">
</div>

## 🌟 项目简介
一款基于**YOLOv5目标检测**的课堂随机点名系统，具有以下炫酷功能：
- 🎲 随机抽取学生（带倒计时动画）
- 📊 自动记录加减分（按科目/学号分类）
- 🎨 动态高亮显示选中学生
- 🔊 趣味音效反馈
- 📅 自动按月创建归档文件夹

## 🚀 快速开始

```bash
git clone https://github.com/TomLiu-QianYuan/lucky-dog.git
cd lucky-dog
pip install -r requirements.txt
python newVersionRandomStu.py
```

## 🛠️ 功能演示
| 功能 | 截图 |
|------|--------|
| 选择科目 | screenshot/start.png |
| 抽取截图 | screenshot/running.png |
## 📂 文件结构
```
lucky-dog/
├── models/               # YOLOv5模型
├── processVoice/         # 过程音效
├── endingVoice/          # 结束音效
├── config.json           # 科目配置文件
└── newVersionRandomStu.py # 主程序

## 🔧 配置说明
1. 编辑`config.json`添加科目：
```json
{
  "subjects": ["数学", "语文", "英语"]
}
```
## 🎮 使用指南
1. **首次启动**：自动创建当月文件夹（如`3月1日-3月31日`）
2. **科目设置**：
   - 点击选择当前授课科目
   - 通过"添加"按钮新增科目
3. **随机抽取**：
   - 设置倒计时区间（如30-60秒）
   - 点击【开始抽选】启动随机轮盘
4. **即时评分**：
   - 👍 加分：自动保存到`当月文件夹/科目/学号/加分/`
   - 👎 减分：自动保存到`当月文件夹/科目/学号/减分/`
   - ⏭️ 跳过：不操作直接进入下一轮
## 📌 注意事项
```diff
! 开发警告：
- 千万别学It，特别是这种软件！
- 如果写出代码不难，改bug就会很难!
- 特别是小bug、不报错的bug。
- 如果改bug不难，调试环境最难!
+ 没有资料全靠菩萨保佑!
```
## 🤝 参与贡献
欢迎提交PR或Issue！请遵循以下流程：
1. Fork项目
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request
## 📜 许可证
[MIT License](LICENSE) © TomLiu
---
<div align="center">
  💖 如果喜欢这个项目，请给它一个Star！ 💖
</div>
