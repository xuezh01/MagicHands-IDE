# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////
import shutil
import subprocess
import sys
import os
import platform
import zipfile
from datetime import datetime
from glob import glob
from threading import Thread

from MySignal import my_signal
# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%
from tool.socket import *
# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    global lognum
    lognum = 1
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(1800, 1400)
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyDracula - Modern GUI"
        description = "PyDracula APP - Theme with colors based on Dracula for Python."
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        # widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_debug.clicked.connect(self.buttonClick)
        widgets.btn_build.clicked.connect(self.buttonClick)
        widgets.btn_serve.clicked.connect(self.buttonClick)
        widgets.btn_start.clicked.connect(self.buttonClick)
        widgets.btn_stop.clicked.connect(self.buttonClick)
        widgets.btn_debugfile.clicked.connect(self.buttonClick)
        widgets.btn_pro.clicked.connect(self.buttonClick)
        widgets.btn_profile.clicked.connect(self.buttonClick)
        widgets.btn_proopen.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        widgets.btn_buildico.clicked.connect(self.buttonClick)
        widgets.btn_buildpro.clicked.connect(self.buttonClick)
        widgets.btn_buildyes.clicked.connect(self.buttonClick)
        # widgets.edit_buildv.clicked.connect(self.buttonClick)
        # widgets.edit_buildico.clicked.connect(self.buttonClick)
        # widgets.edit_buildpkg.clicked.connect(self.buttonClick)
        # widgets.edit_buildpro.clicked.connect(self.buttonClick)
        # widgets.edit_buildname.clicked.connect(self.buttonClick)
        my_signal.setResult.connect(self.logd)
        tmpCursor = self.ui.logd.textCursor()
        tmpCursor.setPosition(0)
        self.ui.logd.setTextCursor(tmpCursor)
        # self.ui.logd.setStyleSheet("color:#00ff00;")
        my_signal.setResult.emit("欢迎使用---当前版本1.0", 100, 184, 100)
        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        # if btnName == "btn_widgets":
        #     widgets.stackedWidget.setCurrentWidget(widgets.widgets)
        #     UIFunctions.resetStyle(self, btnName)
        #     btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_debug":
            widgets.stackedWidget.setCurrentWidget(widgets.debug) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU
        # btn_debug
        if btnName == "btn_serve":
            print("启动服务器")
            ta = Thread(target=mai, args=(21566, "D:/socket/"))
            ta.start()
        if btnName == "btn_start":
            print("运行")
            重置指令(3)

        if btnName == "btn_stop":
            print("停止")
            重置指令(5)
            # my_signal.setResult.emit("欢迎使用魔幻手---当前版本1.0", 100, 184, 100)
        if btnName == "btn_debugfile":
            print("选择文件夹")
            self.xzxm()


        if btnName == "btn_build":
            widgets.stackedWidget.setCurrentWidget(widgets.build)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        if btnName == "btn_buidpro":
            # os.getcwd()[:-4] + 'new\\'
            print("选择文件夹")
            self.xzxm2()
        if btnName == "btn_buidico":
            # os.getcwd()[:-4] + 'new\\'
            print("选择文件夹")
            self.xzxm2()


        if btnName == "btn_pro":
            widgets.stackedWidget.setCurrentWidget(widgets.pro)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
        if btnName == "btn_profile":
            print("选择文件夹")
            self.xzxm1()
        if btnName == "btn_proopen":
            # os.getcwd()[:-4] + 'new\\'
            print("创建")
            self.unzip_file()


        if btnName == "btn_exit":
            QMessageBox.information(self,"提示","开发中",QMessageBox.Ok)
            # widgets.stackedWidget.setCurrentWidget(widgets.build)  # SET PAGE
            # UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            # btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    def logd(self, z:str,r:str,g:str,b:str):
        global lognum
        self.ui.logd.setStyleSheet("color:#00ff00;")
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ui.logd.appendPlainText(str(lognum)+"#("+str(t)+")"+z)

        lognum=lognum+1

    def xzxm(self):
         # global wjj
         # 选择文件
         # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
         xz= QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
         print(xz)
         self.ui.edit_debugfile.setText(xz)

    def xzxm1(self):
         # global wjj
         # 选择文件
         # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
         xz= QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
         print(xz)
         self.ui.edit_profile.setText(xz)
    def xzxm2(self):
         # global wjj
         # 选择文件
         # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
         xz= QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
         print(xz)
         self.ui.edit_buildpro.setText(xz)
    def xzxm3(self):
         # global wjj
         # 选择文件
         # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
         xz= QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
         print(xz)
         self.ui.edit_buildico.setText(xz)
    def 创建项目(self):
        src = "C:/Users/35600/Desktop/js"
        det = self.ui.edit_profile.text()+"/"+self.ui.edit_proname.text()  # 目的文件目录
        # print("1")
        for root, _, fnames in os.walk(src):
            for fname in sorted(fnames):  # sorted函数把遍历的文件按文件名排序
                fpath = os.path.join(root, fname)
                shutil.copy(fpath, det)  # 完成文件拷贝
                print(fname + " 创建项目成功")
    def cmd(self, command):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        print(type(p))
        lines = []
        for line in iter(p.stdout.readline, b''):
            line = line.strip().decode("GB2312")
            print(">>>", line)
            lines.append(line)
        return lines
    def unzip_file(self):
        path = self.ui.edit_profile.text()+"/"+self.ui.edit_proname.text()
        if path=="/":
            QMessageBox.information(self, "提示", "请选择正确路径", QMessageBox.Ok)
            return -1
        if not os.path.exists(path):
            os.mkdir(path)
        path =  self.ui.edit_profile.text()+"/"+self.ui.edit_proname.text() + "/build"
        if not os.path.exists(path):
            os.mkdir(path)
        path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "/res"
        if not os.path.exists(path):
            os.mkdir(path)
        path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "/assets"
        if not os.path.exists(path):
            os.mkdir(path)
        path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "/config.json"
        file = open(path, 'w')
        file.close()
        zip_src = "C:/Users/35600/Desktop/demo.zip"
        dst_dir =  self.ui.edit_profile.text()+"/"+self.ui.edit_proname.text()
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
        else:
            print('This is not zip')

    def mycopyfile(srcfile, dstpath):  # 复制函数
        if not os.path.isfile(srcfile):
            print("%s not exist!" % (srcfile))
        else:
            fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
            if not os.path.exists(dstpath):
                os.makedirs(dstpath)  # 创建路径
            shutil.copy(srcfile, dstpath + fname)  # 复制文件
            print("copy %s -> %s" % (srcfile, dstpath + fname))

    src_dir = './'
    dst_dir = './copy/'  # 目的路径记得加斜杠
    src_file_list = glob(src_dir + '*')  # glob获得路径下所有文件，可根据需要修改
    for srcfile in src_file_list:
        mycopyfile(srcfile, dst_dir)  # 复制文件

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        p = event.globalPosition()
        globalPos = p.toPoint()
        self.dragPos = globalPos
        # self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
