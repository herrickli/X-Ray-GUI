import sys
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt

from custom.stackedWidget import StackedWidget
from custom.treeView import FileSystemTreeView
from custom.listWidgets import FuncListWidget, UsedListWidget
from custom.graphicsView import GraphicsView

import requests
import base64


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.tool_bar = self.addToolBar('工具栏')
        self.action_right_rotate = QAction(QIcon("icons/rotate-left.png"), "向右旋转90", self)
        self.action_left_rotate = QAction(QIcon("icons/rotate-right.png"), "向左旋转90°", self)
        self.action_histogram = QAction(QIcon("icons/histogram.png"), "直方图", self)
        self.action_play = QAction(QIcon("icons/play.png"), "播放视频", self)
        self.action_pause = QAction(QIcon("icons/pause.png"), "暂停视频", self)


        self.action_right_rotate.triggered.connect(self.right_rotate)
        self.action_left_rotate.triggered.connect(self.left_rotate)
        self.action_histogram.triggered.connect(self.histogram)
        self.action_play.triggered.connect(self.play_video)
        self.action_pause.triggered.connect(self.video_pause)
        

        self.tool_bar.addActions((self.action_left_rotate, self.action_right_rotate, self.action_histogram,
                                  self.action_play, self.action_pause))

        self.useListWidget = UsedListWidget(self)
        self.funcListWidget = FuncListWidget(self)
        self.stackedWidget = StackedWidget(self)
        self.fileSystemTreeView = FileSystemTreeView(self)
        self.graphicsView = GraphicsView(self)

        self.dock_file = QDockWidget(self)
        self.dock_file.setWidget(self.fileSystemTreeView)
        self.dock_file.setTitleBarWidget(QLabel('目录'))
        self.dock_file.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_func = QDockWidget(self)
        self.dock_func.setWidget(self.funcListWidget)
        self.dock_func.setTitleBarWidget(QLabel('图像操作'))
        self.dock_func.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_used = QDockWidget(self)
        self.dock_used.setWidget(self.useListWidget)
        self.dock_used.setTitleBarWidget(QLabel('已选操作'))
        self.dock_used.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_used.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_attr = QDockWidget(self)
        self.dock_attr.setWidget(self.stackedWidget)
        self.dock_attr.setTitleBarWidget(QLabel('属性'))
        self.dock_attr.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_attr.close()

        self.setCentralWidget(self.graphicsView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_file)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dock_func)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_used)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_attr)

        self.setWindowTitle('Opencv图像处理')
        self.setWindowIcon(QIcon('icons/main.png'))

        self.src_img = None
        self.cur_img = None

        self.pause = False

    def update_image(self):
        if self.src_img is None:
            return
        img = self.process_image()
        self.cur_img = img
        self.graphicsView.update_image(img)

    def change_image(self, img):
        self.src_img = img
        img = self.process_image()
        self.cur_img = img
        self.graphicsView.change_image(img)

    def process_image(self):
        img = self.src_img.copy()
        for i in range(self.useListWidget.count()):
            img = self.useListWidget.item(i)(img)
        return img

    def right_rotate(self):
        self.graphicsView.rotate(90)

    def left_rotate(self):
        self.graphicsView.rotate(-90)

    def histogram(self):
        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            histr = cv2.calcHist([self.cur_img], [i], None, [256], [0, 256])
            histr = histr.flatten()
            plt.plot(range(256), histr, color=col)
            plt.xlim([0, 256])
        plt.show()

    def video_pause(self):
        self.pause = True

    def play_video(self):
        self.pause = False

        video_path = r'F:/360MoveData/Users/HerrickLi/Desktop/cascade/opencv-pyqt5-master/utils/视频/00000000017000500.mp4'
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():  #VideoCaputre对象是否成功打开
            print('已经打开了视频文件')
        else:
            print('视频文件打开失败')

        while(cap.isOpened()): 
            ret, frame = cap.read() 
            self.change_image(frame)
            print(frame.shape)
            
            k = cv2.waitKey(1)
            if self.pause:
                break
            
        cap.release() 
        cv2.destroyAllWindows()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./custom/styleSheet.qss', encoding='utf-8').read())
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
