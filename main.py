import sys
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import numpy

from custom.stackedWidget import StackedWidget
from custom.treeView import FileSystemTreeView
from custom.listWidgets import FuncListWidget, UsedListWidget
from custom.graphicsView import GraphicsView

import time
import threading

from model import detect
from model import cv2ImgAddText

FONT_FACE  = cv2.FONT_HERSHEY_COMPLEX
FONT_SIZE  = 1
FONT_THICK = 1


class signal_frame(QThread):
    _signal = pyqtSignal(dict)
    _signal_stop = pyqtSignal(int)
    def __init__(self):
        super(signal_frame, self).__init__()
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.isPause = False
        self.isCancel = False

    def pause(self):
        self.isPause = True
    
    def resume(self):
        self.isPause = False
        self.cond.wakeAll()

    def cancel(self):
        self.isCancel = True

    def run(self):
        video_path = r'/home/licheng/projects/X-Ray-GUI/utils/00000000017000500.mp4'
        cap = cv2.VideoCapture(video_path)
        show_interval = 10
        wait_key = int(1000 / cap.get(cv2.CAP_PROP_FPS))
        
        if cap.isOpened():  #VideoCaputre对象是否成功打开
            print('已经打开了视频文件')
        else:
            print('视频文件打开失败')
        count = 0
        while(cap.isOpened()):
            self.mutex.lock()
            if self.isPause:
                self.cond.wait(self.mutex)
            if self.isCancel:
                break 
            ret, frame = cap.read() 
            count += 1
            if count == show_interval:
                results = detect(frame)
                frame = self.apply_result_to_img(results, frame)
                self._signal.emit({'frame':frame})
                # self.window.update_image(frame)
                # print(frame.shape)
                count = 0
            time.sleep(wait_key*0.001)
            # cv2.waitKey(wait_key*show_interval)

    def apply_result_to_img(self, results, img):
        for result in results:
            obj, score, box = result
            FONT_BACK_SIZE = cv2.getTextSize(obj, FONT_FACE, FONT_SIZE, FONT_THICK)[0]
            if score > 0.5:
                xmin, ymin, xmax, ymax = box
                cv2.rectangle(img, (int(xmin), int(ymin)-FONT_BACK_SIZE[1]), (int(xmin)+FONT_BACK_SIZE[0], int(ymin)), (0,0,255,0.3), -1)
                #cv2.putText(img, obj + '', (int(xmin), int(ymin)), FONT_FACE, FONT_SIZE, (255, 255, 255, 0.7), FONT_THICK)
                img = cv2ImgAddText(img, obj, int(xmin), int(ymin)-FONT_BACK_SIZE[1], (255,255,255), 20)
                cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 0, 255, 0.3), 2)
        return img

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.tool_bar = self.addToolBar('工具栏')
        self.action_right_rotate = QAction(QIcon("icons/rotate-left.png"), "向右旋转90", self)
        self.action_left_rotate = QAction(QIcon("icons/rotate-right.png"), "向左旋转90°", self)
        self.action_histogram = QAction(QIcon("icons/histogram.png"), "直方图", self)
        self.action_play = QAction(QIcon("icons/play.png"), "播放视频", self)
        self.action_pause = QAction(QIcon("icons/pause.png"), "暂停视频", self)
        self.action_stop = QAction(QIcon("icons/stop.png"), "停止视频", self)
        


        self.action_right_rotate.triggered.connect(self.right_rotate)
        self.action_left_rotate.triggered.connect(self.left_rotate)
        self.action_histogram.triggered.connect(self.histogram)
        self.action_play.triggered.connect(self.video_paly)
        self.action_pause.triggered.connect(self.video_pause)
        self.action_stop.triggered.connect(self.video_stop)

        

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

        self.signal_thread = signal_frame()
        self.signal_thread._signal.connect(self.signal_update_img)

    def signal_update_img(self, data):
        frame = data['frame']
        self.change_image(frame) 

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
        self.signal_thread.pause = True

    def video_stop(self):
        self.signal_thread.cancel = True

    def video_paly(self):
        self.signal_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./custom/styleSheet.qss', encoding='utf-8').read())
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
