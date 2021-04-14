# opencv-pyqt5
使用opencv与pyqt5实现的图像处理程序
![demo.jpg](demo.png)

# Dependency
* opencv-python
* matplotlib
* pyqt5

## 已实现功能
* 图像旋转
* 转灰度图
* 图像平滑
* 直方图均衡化
* 形态学操作
* 梯度计算
* 阈值处理
* 边缘检测
* 轮廓检测 
* 哈夫变换直线检测
* 亮度调节
* 伽马校正

## 模型检测输出结果results格式
- results = model.predict(img)
- results: [box1, box2, ..., boxn]
- box: [class_name, score, xmin, ymin, xmax, ymax]


## 使用方法
`python main.py`