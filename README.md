# X-Rya-GUI
使用opencv与pyqt5实现的图像检测显示程序
- 本仓库基于`https://github.com/JiageWang/opencv-pyqt5.git`

# Dependency
* opencv-python
* matplotlib
* pyqt5


## 模型检测输出结果results格式
- results = model.predict(img)
- results: [box1, box2, ..., boxn]
- box: [class_name, score, xmin, ymin, xmax, ymax]


## 使用方法
`python main.py`