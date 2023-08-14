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
import codecs
import fileinput
import shutil
import subprocess
import sys
import socket as py_socket
import socket
import os
import platform
import threading
import zipfile
import re
from datetime import datetime
import multiprocessing
from glob import glob
from threading import Thread
from tkinter import Tk
import xml.etree.ElementTree as ET

import chardet
import psutil

from MySignal import my_signal
# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from tool.zip import zip_file
from widgets import *

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%
from tool.socket import *
import requests
from flask import Flask, request, send_file

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

global dir

# if getattr(sys, 'frozen', False):
#     # 如果是打包后的可执行文件
#     dir = sys._MEIPASS+"/env"
# else:
#     # 如果是直接运行的脚本
dir = os.getcwd() + "/env"

af = Flask(__name__)
af.config['JSON_AS_ASCII'] = False


method_info_dict = {
            'print': '用于打印输出',
            'if': '条件语句，根据条件判断执行不同的代码块',
            'else': '条件语句的附加分支，如果上面的条件不满足，则执行else块的代码',
            'for': '循环语句，用于遍历一个可迭代对象',
            'while': '循环语句，根据条件循环执行代码块',
            'def': '定义函数',
            'import': '导入其他模块',
            'from': '从某个模块中导入特定的函数或变量'
        }



class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []

        # 定义关键字的高亮格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.yellow)
        keyword_format.setFontWeight(QFont.Bold)
        keyword_format.setFontPointSize(12)

        # 定义字符串的高亮格式
        string_format = QTextCharFormat()
        string_format.setForeground(Qt.darkGreen)
        string_format.setFontPointSize(10)

        # 定义数字的高亮格式
        number_format = QTextCharFormat()
        number_format.setForeground(Qt.darkMagenta)
        number_format.setFontPointSize(10)

        # 定义注释的高亮格式
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.darkGray)
        comment_format.setFontItalic(True)
        comment_format.setFontPointSize(10)

        # 添加关键字和对应的高亮格式到规则列表

        for keyword in method_info_dict:
            pattern = QRegularExpression("\\b" + keyword + "\\b", QRegularExpression.CaseInsensitiveOption)
            rule = (pattern, keyword_format)
            self.highlighting_rules.append(rule)

        # 添加字符串的规则
        string_pattern = QRegularExpression("\".*?\"")
        string_rule = (string_pattern, string_format)
        self.highlighting_rules.append(string_rule)

        # 添加数字的规则
        number_pattern = QRegularExpression("\\b\\d+\\.?\\d*\\b")
        number_rule = (number_pattern, number_format)
        self.highlighting_rules.append(number_rule)

        # 添加注释的规则
        comment_pattern = QRegularExpression("//[^\n]*")
        comment_rule = (comment_pattern, comment_format)
        self.highlighting_rules.append(comment_rule)

        # 添加更多语法元素和相应的高亮格式
        # ...

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
class LineNumberArea(QWidget):
    def __init__(self, editor: QPlainTextEdit):
        super().__init__(editor.editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
class CodeEditor(QWidget):
    def __init__(self, editor: QPlainTextEdit,parent=None):
        super().__init__(parent)
        self.editor = editor

        self.lineNumberArea = LineNumberArea(self)

        self.editor.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.editor.updateRequest.connect(self.updateLineNumberArea)
        self.editor.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.editor.textChanged.connect(self.text_changed)
        self.updateLineNumberAreaWidth(0)

    def text_changed(self):
        # 将光标移动到文本末尾
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.editor.setTextCursor(cursor)

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.editor.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.editor.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.editor.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
        # self.editor.verticalScrollBar().setValue(self.editor.verticalScrollBar().maximum())

    def resizeEvent(self, event):
        self.editor.resizeEvent(event)
        cr = self.editor.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.editor.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1

    def highlightCurrentLine(self):
        extra_selections = []

        if not self.editor.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            style_sheet = "color: #2F4F4F;"
            line_color = QColor(style_sheet).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.editor.setExtraSelections(extra_selections)

class MainWindow(QMainWindow):
    global lognum
    lognum = 1
    global buildlognum
    buildlognum = 1

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
        print(get_ip())

        self.completion_list = []
        self.current_index = 0



        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "GUI"
        description = "MagicHands-IDE"
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
        widgets.btn_stop.clicked.connect(self.buttonClick)
        widgets.btn_start.clicked.connect(self.buttonClick)
        widgets.btn_startcopy.clicked.connect(self.buttonClick)
        widgets.btn_ui.clicked.connect(self.buttonClick)
        widgets.btn_xml.clicked.connect(self.buttonClick)
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
        my_signal.setResult2.connect(self.logd1)
        tmpCursor = self.ui.logd.textCursor()
        tmpCursor.setPosition(0)
        self.ui.logd.setTextCursor(tmpCursor)
        tmpCursor = self.ui.buidlod.textCursor()
        tmpCursor.setPosition(0)
        self.ui.buidlod.setTextCursor(tmpCursor)
        self.text_edit = self.ui.daima
        style_sheet = "color: white;"
        self.text_edit.setStyleSheet(style_sheet)

        font = QFont("SimSun", 3)  # 设置字体名称为"SimSun"，字体大小为12
        self.text_edit.setFont(font)

        self.text_edit.setGeometry(0, 0, 800, 500)
        self.text_edit.textChanged.connect(self.handle_text_changed)
        self.text_edit.installEventFilter(self)  # 安装事件过滤器以捕获按键事件

        self.list_view = self.ui.buquan
        self.list_view.setFixedSize(200, 200)
        self.list_view.hide()
        self.list_view.setSelectionMode(QListView.SingleSelection)
        self.list_view.clicked.connect(self.insert_completion)

        self.info_edit = self.ui.zhushi
        self.info_edit.setGeometry(200, 0, 600, 500)
        self.info_edit.setReadOnly(True)

        self.ui.tabWidget.setStyleSheet("QTabBar::tab { background-color: rgb(33, 37, 43); } QTabBar::tab:tab {background-color: rgb(33, 37, 43);font:13pt '宋体';color: white;};")
        # self.ui.logd.setStyleSheet("color:#00ff00;")
        启动判断(0)
        my_signal.setResult.emit("欢迎使用---当前版本1.0", 100, 184, 100)
        PythonHighlighter(self.text_edit.document())
        CodeEditor(self.ui.daima,self)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            print()
            # UIFunctions.toggleLeftBox(self, True)

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
        # 创建进程对象，同时传递参数

        thread = threading.Thread(target=copy_gradle)
        thread.start()

        thread = threading.Thread(target=self.auto_save,args=(os.getcwd()+"/备份.txt",10,))
        thread.start()



    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == QKeyEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.complete_current_word()
            return True

        if obj == self.text_edit and event.type() == QKeyEvent.KeyPress and (
                event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.text_edit.insertPlainText("\n")
            return True


        if obj == self.text_edit and event.type() == QKeyEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                self.current_index -= 1
                if self.current_index < 0:
                    self.current_index = len(self.completion_list) - 1
                self.update_completion_list()
                self.update_info_edit()
                return True
            elif key == Qt.Key_Down:
                self.current_index += 1
                if self.current_index >= len(self.completion_list):
                    self.current_index = 0
                self.update_completion_list()
                self.update_info_edit()
                return True
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                self.insert_completion(self.list_view.currentIndex())
                return True

        if obj == self.list_view and event.type() == QKeyEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Up:
                self.current_index -= 1
                if self.current_index < 0:
                    self.current_index = len(self.completion_list) - 1
                self.update_completion_list()
                self.update_info_edit()
                return True
            elif key == Qt.Key_Down:
                self.current_index += 1
                if self.current_index >= len(self.completion_list):
                    self.current_index = 0
                self.update_completion_list()
                self.update_info_edit()
                return True
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                self.insert_completion(self.list_view.currentIndex())
                return True

        return super().eventFilter(obj, event)

    def auto_save(self, file_path, interval):
         while True:
          time.sleep(interval)
          print(self.text_edit.toPlainText())
          if self.text_edit.toPlainText() != "":
            with open(file_path, 'w') as file:
                file.write(str(self.text_edit.toPlainText()))
            print("自动保存成功")

          else:
             print("未写入代码")


    def handle_text_changed(self):
        cursor = self.text_edit.textCursor()
        current_pos = cursor.position()

        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        block_number = cursor.blockNumber()
        line_text = cursor.block().text()[:current_pos - cursor.block().position()]
        words = line_text.split()

        if len(words) > 0:
            current_word = words[-1]
            completion_list = self.get_completion_list(current_word)
            self.completion_list = completion_list
            self.current_index = 0
            self.show_completion_list(completion_list)
        else:
            self.list_view.hide()
            self.info_edit.clear()

    def get_completion_list(self, prefix):
        # 根据输入前缀获取代码提示列表
        suggestions = list(method_info_dict.keys())
        return [suggestion for suggestion in suggestions if suggestion.startswith(prefix)]

    def show_completion_list(self, completion_list):
        # 显示代码提示列表
        model = QStandardItemModel()
        for completion in completion_list:
            item = QStandardItem(completion)
            item.setForeground(QBrush(Qt.black))
            model.appendRow(item)

        self.list_view.setModel(model)


        if model.rowCount() > 0:
            self.list_view.setCurrentIndex(model.index(0, 0))
            self.list_view.show()
            self.update_info_edit()
        else:
            self.list_view.hide()
            self.info_edit.clear()

    def update_completion_list(self):
        # 更新当前选中的代码提示项
        model = self.list_view.model()
        if model:
            new_index = model.index(self.current_index, 0)
            self.list_view.setCurrentIndex(new_index)
            self.update_info_edit()

    def update_info_edit(self):
        # 更新单词解释框的内容
        selected_index = self.list_view.currentIndex()
        model = self.list_view.model()
        selected_completion = model.data(selected_index)
        method_info = method_info_dict.get(selected_completion, '')
        self.info_edit.setStyleSheet("color: black;")
        self.info_edit.setPlainText(method_info)

    def insert_completion(self, index):
        # 插入选中的代码提示项到文本编辑框中

        model = self.list_view.model()
        completion_index = model.index(index.row(), 0)
        completion = model.data(completion_index)

        cursor = self.text_edit.textCursor()
        while not cursor.atBlockStart() and not cursor.block().text()[cursor.positionInBlock() - 1].isspace():
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor)

        # 向右移动光标直到遇到一个空格或者到达行末尾
        while not cursor.atBlockEnd():
            # 更新当前光标所在行的文本
            line_text = cursor.block().text()

            # 检查索引是否越界
            if cursor.positionInBlock() >= len(line_text):
                break

            # 判断当前字符是否为空格
            if line_text[cursor.positionInBlock()].isspace():
                break
            if line_text[cursor.positionInBlock()] == '(':
                break

            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        selected_text = cursor.selectedText()
        block = cursor.block()
        text = block.text()
        print("text:" + text)
        last_word_start = text.rfind(' ', 0, cursor.position()) + 1
        last_word = text[last_word_start:cursor.position()]
        if last_word == selected_text:
            # cursor.setPosition(last_word_start)
            cursor.setPosition(cursor.position() + len(last_word), QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(completion)

        self.text_edit.setTextCursor(cursor)


    def complete_current_word(self):
        # 自动完成当前单词
        cursor = self.text_edit.textCursor()
        current_pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        line_text = cursor.block().text()
        words = line_text.split()
        if len(words) > 0:
            current_word_start = cursor.position() + line_text.index(words[-1])
            current_word_end = current_word_start + len(words[-1])
            cursor.setPosition(current_word_start)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, current_word_end - current_word_start)

            selected_index = self.list_view.currentIndex()
            self.insert_completion(selected_index)

    def jc1(self):
        process = multiprocessing.Process(target=copy_gradle)
        # 启动进程
        process.start()

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        print("btnName:" + btnName)

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
            widgets.stackedWidget.setCurrentWidget(widgets.debug)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
        # btn_debug
        if btnName == "btn_serve":
            print("启动服务器")
            xintiao()
            # af = Flask(__name__)
            # af.run(host='192.168.189.128', port=8080)
            global command
            command = 0
            global pngcmd
            pngcmd = 0
            # 重置指令(0)
            # png指令(0)
            t = threading.Thread(target=start_flask_app)
            t.start()

            # ta = Thread(target=mai, args=(21566, "C:/Users/35600/Desktop/ma"))
            # ta.start()
        if btnName == "btn_start":
            self.ui.logd.clear()
            global lognum
            lognum = 1
            print("运行")
            项目 = self.ui.edit_debugfile.text()
            type_value = self.get_type_from_json(项目 + "/config.json")
            print("返回值是字符串" + type_value)
            if type_value == "1":
                print("返回值是字符串 '1'")
                my_signal.setResult.emit("运行(Js脚本项目)-下发时间取决网速(10-30s)", 100, 184, 100)

                项目 = self.ui.edit_debugfile.text()
                zip_file(项目 + "/js")
                zip_file(项目 + "/assets")
                zip_file(项目 + "/res")
                self.移动文件(项目 + "/js.zip", dir + "/debug/", "js.zip")
                self.移动文件(项目 + "/assets.zip", dir + "/debug/", "assets.zip")
                self.移动文件(项目 + "/res.zip", dir + "/debug/", "res.zip")
                time.sleep(0.1)
                os.remove(项目 + "/js.zip")
                os.remove(项目 + "/assets.zip")
                os.remove(项目 + "/res.zip")
                time.sleep(0.1)
                zip_file(dir + "/debug")
                time.sleep(0.1)
                up(dir + "/debug.zip")
                重置指令(3)
                print(command)
            elif type_value == "2":
                print("返回值是字符串 '2'")
                my_signal.setResult.emit("运行(Java插件项目)-下发时间取决网速(10-30s)", 100, 184, 100)

                t = Thread(target=self.debug_java, args=("gradlew assembleDebug", 项目,))
                t.start()

                print(command)
            elif type_value == "3":
                print("返回值是字符串 '3'")
                my_signal.setResult.emit("运行(Python插件项目)-下发时间取决网速(10-30s)", 100, 184, 100)
                t = Thread(target=self.debug_py, args=("gradlew  assembleRelease", 项目,))
                t.start()


            else:
                print("返回值不是 '1'、'2' 或 '3'")

            # print("操作指令：" + str(command))
            # 启动判断(1)
        if btnName == "btn_stop":
            print("停止")
            my_signal.setResult.emit("通知移动端停止", 100, 184, 100)
            重置指令(5)
        if btnName == "btn_startcopy":
            self.ui.logd.clear()

            lognum = 1
            print("启动剪切板")
            my_signal.setResult.emit("运行剪切板Js代码", 100, 184, 100)
            项目 = self.ui.edit_debugfile.text()
            overwrite_file(项目 + "/build/intermediates/other/js/main.js", get_selected_text())
            time.sleep(0.1)
            zip_file(项目 + "/build/intermediates/other/js")
            zip_file(项目 + "/assets")
            zip_file(项目 + "/res")
            self.移动文件(项目 + "/build/intermediates/other/js.zip", dir + "/debug/", "js.zip")
            self.移动文件(项目 + "/assets.zip", dir + "/debug/", "assets.zip")
            self.移动文件(项目 + "/res.zip", dir + "/debug/", "res.zip")
            time.sleep(0.1)
            os.remove(项目 + "/build/intermediates/other/js.zip")
            os.remove(项目 + "/assets.zip")
            os.remove(项目 + "/res.zip")
            time.sleep(0.1)
            zip_file(dir + "/debug")
            time.sleep(0.1)
            up(dir + "/debug.zip")

            # self.解压到指定(项目+"/build/intermediates/js.zip",dir+"/js")
            # self.解压到指定(项目 + "/build/intermediates/assets.zip", dir + "/assets")
            #

            # t = Thread(target=self.调试编译, args=(项目,))
            # t.start()

            # self.移动文件(项目 + "/build/intermediates/js.zip", "D:/socket/","js.zip")
            # time.sleep(0.1)
            # os.remove(项目 + "/js.zip")

            重置指令(4)
        if btnName == "btn_ui":
            print("预览ui")
            my_signal.setResult.emit("通知移动端展示Ui", 100, 184, 100)
            项目 = self.ui.edit_debugfile.text()
            zip_file(项目 + "/js")
            zip_file(项目 + "/assets")
            zip_file(项目 + "/res")
            self.移动文件(项目 + "/js.zip", dir + "/debug/", "js.zip")
            self.移动文件(项目 + "/assets.zip", dir + "/debug/", "assets.zip")
            self.移动文件(项目 + "/res.zip", dir + "/debug/", "res.zip")
            time.sleep(0.1)
            os.remove(项目 + "/js.zip")
            os.remove(项目 + "/assets.zip")
            os.remove(项目 + "/res.zip")
            time.sleep(0.1)
            zip_file(dir + "/debug")
            time.sleep(0.1)
            up(dir + "/debug.zip")
            重置指令(6)
        if btnName == "btn_xml":
            my_signal.setResult.emit("启动节点工具", 100, 184, 100)
            t = Thread(target=xml)
            t.start()

            # my_signal.setResult.emit("欢迎使用魔幻手---当前版本1.0", 100, 184, 100)
        if btnName == "btn_debugfile":
            print("选择文件夹")
            self.xzxm()
        if btnName == "btn_build":
            widgets.stackedWidget.setCurrentWidget(widgets.build)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
        if btnName == "btn_buildpro":
            # os.getcwd()[:-4] + 'new\\'
            print("选择文件夹")
            self.xzxm2()
        if btnName == "btn_buildico":
            # os.getcwd()[:-4] + 'new\\'
            print("选择文件夹")
            self.xzxm3()
        if btnName == "btn_buildyes":
            # os.getcwd()[:-4] + 'new\\'
            self.ui.buidlod.clear()
            global buildlognum
            buildlognum = 1
            print("编译")
            项目 = self.ui.edit_buildpro.text()
            图标 = self.ui.edit_buildico.text()
            名字 = self.ui.edit_buildname.text()
            pkg = self.ui.edit_buildpkg.text()
            # gradle(项目+"/build/app/1/app/build.gradle",pkg)
            # fi= pkg.replace('.', '/')
            # copy_all_files(项目+"/build/app/1/app/src/main/java/pa/magichands/host",项目+"/build/app/1/app/src/main/java/"+fi)
            # batch_modify_java_packageee("pa.magichands.host",pkg,项目+"/build/app/1/app/src/main/java/"+fi)
            # copy_all_files(项目 + "/build/app/1/app/src/androidTest/java/pa/magichands/host",
            #                项目 + "/build/app/1/app/src/androidTest/java/" + fi)
            # batch_modify_java_packageee("pa.magichands.host", pkg, 项目 + "/build/app/1/app/src/androidTest/java/" + fi)
            # copy_all_files(项目 + "/build/app/1/app/src/test/java/pa/magichands/host",
            #                项目 + "/build/app/1/app/src/test/java/" + fi)
            # batch_modify_java_packageee("pa.magichands.host", pkg, 项目 + "/build/app/1/app/src/test/java/" + fi)
            #
            # # copy_all_files(项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility",
            # #                项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility")
            # self.移动文件(图标,项目+"/build/app/1/app/src/main/res/drawable/","ico.jpg")
            # modify_string_resource(项目+"/build/app/1/app/src/main/res/values/strings.xml","app_name",名字)
            # time.sleep(10)
            # delete_folder(项目 + "/build/app/1/app/src/main/java/pa/magichands/host/")
            # delete_folder(项目 + "/build/app/1/app/src/androidTest/java/pa/")
            # delete_folder(项目 + "/build/app/1/app/src/test/java/pa/")
            # self.替换内容(项目+"/build/app/1/app/build.gradle",pkg)
            # file = open(项目+"/build/app/1/app/src/main/res/values/strings.xml", 'w');
            # file.close()
            # with open(项目+"/build/app/1/app/src/main/res/values/strings.xml", "w",encoding='utf-8') as f:
            #     f.write('<resources><string name="app_name">'+名字+'</string></resources>')
            type_value = self.get_type_from_json(项目 + "/config.json")
            if type_value == "1":
                print("返回值是字符串 '1'")
                t = Thread(target=self.cmd2, args=("gradlew assembleDebug assembleRelease", 项目, 图标, 名字, pkg,))
                t.start()

            elif type_value == "2":
                print("返回值是字符串 '2'")
                t = Thread(target=self.build_java,
                           args=("gradlew assembleDebug assembleRelease", 项目, 图标, 名字, pkg,))
                t.start()

            elif type_value == "3":
                print("返回值是字符串 '3'")
                t = Thread(target=self.build_py, args=("gradlew  assembleRelease", 项目,))
                t.start()

            else:
                print("返回值不是 '1'、'2' 或 '3'")

            # self.cmd("D:&&cd D:/magichands/demo/build/app/1&&gradlew assembleRelease")
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
            xzk = str(self.ui.comboBox_3.currentIndex())
            if xzk == "0":
                self.unzip_file(xzk)
            elif xzk == "1":
                self.unzip_file(xzk)
            elif xzk == "2":
                self.unzip_file(xzk)

        if btnName == "btn_exit":
            QMessageBox.information(self, "提示", "开发中", QMessageBox.Ok)
            # widgets.stackedWidget.setCurrentWidget(widgets.build)  # SET PAGE
            # UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            # btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    def logd(self, z: str, r: str, g: str, b: str):
        global lognum
        self.ui.logd.setStyleSheet("color:#00ff00;")
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ui.logd.appendPlainText(str(lognum) + "#(" + str(t) + ")" + z)
        lognum = lognum + 1

    def logd1(self, z: str, r: str, g: str, b: str):
        global buildlognum
        self.ui.buidlod.setStyleSheet("color:#00ff00;")
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ui.buidlod.appendPlainText(str(buildlognum) + "#(" + str(t) + ")" + z)

        buildlognum = buildlognum + 1

    def xzxm(self):
        # global wjj
        # 选择文件
        # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
        xz = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        print(xz)
        self.ui.edit_debugfile.setText(xz)

    def 调试编译(self, path):
        print(path)
        # while True:
        #  if not os.path.exists(path):
        #      print("1")
        #
        #  else:
        #       break
        #
        # t = Thread(target=self.cmd, args=("D:&&cd " + path + "/build/intermediates/app&&gradlew assembleRelease",))
        # t.start()
        self.cmd1("C:&&cd " + path + "/build/intermediates/app&&gradlew assembleDebug")
        file = open(dir + "/module/profiles.json", 'w')
        file.close()
        with open(dir + "/module/profiles.json", "w", encoding='utf-8') as f:
            f.write(
                '{"AesKey": "","ClassFilterFilePath": "","KeyAlias": "","KeyPassword": "","KeyStorePassword": "","KeyStorePath": "","NewApkPath": "' + path + '/build/intermediates/app/app/build/outputs/apk/debug/app-debug.apk","OldApkPath": "' + dir + '/apk/magichands.apk","OutputDirPath": "' + path + '/build/outputs/module","isForceColdFix": false,"isIgnoreRes": false,"isIgnoreSo": false}')

        self.cmd1("C:&&cd " + dir + "/module&&SophixPatchTool --profiles profiles.json")

    def xzxm1(self):
        # global wjj
        # 选择文件
        # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
        xz = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        print(xz)
        self.ui.edit_profile.setText(xz)

    def xzxm2(self):
        # global wjj
        # 选择文件
        # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
        xz = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        print(xz)
        self.ui.edit_buildpro.setText(xz)

    def xzxm3(self):
        # global wjj
        # 选择文件
        # folder_name = QFileDialog.getOpenFileNames(self, 'Open Images', wjj, 'Image files (*.png *.jpg)')
        xz = QFileDialog.getOpenFileName(self, "打开图片文件", "/",
                                         "PNG Files(*.png);;JPEG Files(*.jpg);;PGM Files(*.pgm)")
        lo = str(xz).split(",")
        s = lo[0].split("('")
        x = s[1].split("'")
        v = x[0]
        print(v)
        # print(xz)
        self.ui.edit_buildico.setText(str(v))

    def 创建项目(self):
        src = "C:/Users/35600/Desktop/js"
        det = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text()  # 目的文件目录
        # print("1")
        for root, _, fnames in os.walk(src):
            for fname in sorted(fnames):  # sorted函数把遍历的文件按文件名排序
                fpath = os.path.join(root, fname)
                shutil.copy(fpath, det)  # 完成文件拷贝
                print(fname + " 创建项目成功")

    def 清空日志(self):
        self.ui.logd.clear()

    def 替换内容(self, path, pkg):
        old = pkg
        new = "DSOIGVOISD"
        with open(path, 'r+', encoding='utf-8') as filetxt:
            lines = filetxt.readlines()
            filetxt.seek(0)
            for line in lines:
                if old in line:
                    lines = "".join(lines).replace(old, new)
            filetxt.write("".join(lines))

    def gradle_data(self):
        zip_src = dir + "/gradle.zip"
        dst_dir = os.path.expanduser("~")
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
        else:
            print('This is not zip')

    def extract_pip_dependencies(self, file_path):
        # 读取 JSON 配置文件
        with open(file_path, 'r') as file:
            config = json.load(file)

        # 提取 pip 参数
        pip_dependencies = config.get('pip', [])

        # 格式化输出
        dependencies_str = '\n'.join(f'install "{dependency}"' for dependency in pip_dependencies)

        return dependencies_str

    def replace_in_file(self, file_path, old_content, new_content):
        with open(file_path, 'rb') as file:
            raw_content = file.read()
            result = chardet.detect(raw_content)
            encoding = result['encoding']

        with open(file_path, 'r', encoding=encoding) as file:
            file_content = file.read()

        new_file_content = file_content.replace(old_content, new_content)

        with open(file_path, 'w', encoding=encoding) as file:
            file.write(new_file_content)

        print(f"替换完成：{old_content} 替换为 {new_content}")

    def extract_pip_dependencies(self, file_path):
        # 读取 JSON 配置文件
        with open(file_path, 'r') as file:
            config = json.load(file)

        # 提取 pip 参数
        pip_dependencies = config.get('pip', [])

        # 格式化输出
        dependencies_str = '\n'.join(f'"{dependency}"' for dependency in pip_dependencies)

        return dependencies_str

    def get_type_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            type_value = data.get('type')

            if isinstance(type_value, list):
                type_value = ' '.join(type_value)

        return type_value

    def build_py(self, command: str, 项目):
        my_signal.setResult2.emit("开始编译(python插件)-编译时间取决计算机性能(3-5分钟)", 100, 184, 100)

        delete_folder(项目 + "/build/ins/py")
        time.sleep(10)
        copy_all_files(项目 + "/build/intermediates/other/Demo py",
                       项目 + "/build/ins/py")
        time.sleep(10)

        copy_all_files(项目 + "/python",
                       项目 + "/build/ins/py/app/src/main/python")

        time.sleep(10)

        self.replace_in_file(项目 + "/build/ins/py/app/build.gradle",
                             "buildPython \"C:/Users/35600/anaconda3/python.exe\"",
                             "buildPython \"" + dir + "/py/python.exe\"")
        time.sleep(10)
        self.replace_in_file(项目 + "/build/ins/py/app/build.gradle",
                             "pip{}",
                             "pip {\n" + self.extract_pip_dependencies(项目 + "/config.json") + "\n}")

        time.sleep(10)
        try:
            with open(项目 + "/build/ins/py/local.properties", 'w') as file:
                file.write('sdk.dir=' + os.path.normpath(os.getcwd()).replace("\\", "/") + '/env/Sdk')
        except IOError:
            print(f"Failed to overwrite file ")
        time.sleep(10)
        my_signal.setResult2.emit("初始化完成", 100, 184, 100)
        # 获取系统环境变量
        env = os.environ.copy()

        # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
        env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径

        # 启动子进程，并传递更新后的 PATH 环境变量给子进程
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env,
                             cwd=项目 + "/build/ins/py")

        lines = []
        my_signal.setResult2.emit("编译中...", 100, 184, 100)
        while True:
            # 读取子进程的输出
            line = p.stdout.readline().decode("GB2312").strip()
            if not line and p.poll() is not None:
                # 如果没有新的输出且子进程已经结束，则退出循环
                break
            elif line:
                # 如果有新的输出，则打印并添加到结果列表中
                print(">>>", line)
                my_signal.setResult2.emit(">>>" + str(line), 100, 184, 100)
                lines.append(line)

        time.sleep(5)
        my_signal.setResult2.emit("编译完成", 100, 184, 100)
        p.communicate()
        p.terminate()
        time.sleep(5)
        py_file = "chaquopy"
        copy_all_files(项目 + "/build/ins/py/app/build/generated/python/assets/release/app/" + py_file,
                       项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/build/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/misc/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/requirements/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/arm64-v8a",
        #     项目 + "/build/outputs/ins/py/jniLibs/arm64-v8a")
        # time.sleep(10)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/armeabi-v7a",
        #     项目 + "/build/outputs/ins/py/jniLibs/armeabi-v7a")
        # time.sleep(10)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/x86",
        #     项目 + "/build/outputs/ins/py/jniLibs/x86")
        # time.sleep(10)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/x86_64",
        #     项目 + "/build/outputs/ins/py/jniLibs/x86_64")
        return lines

    def build_java(self, command: str, 项目, 图标, 名字, pkg):
        my_signal.setResult2.emit("开始编译(java插件)-编译时间取决计算机性能(3-5min)", 100, 184, 100)
        delete_folder(项目 + "/build/ins/java")
        time.sleep(10)
        copy_all_files(项目 + "/build/intermediates/other/Demo java",
                       项目 + "/build/ins/java")
        time.sleep(10)
        gradle(项目 + "/build/ins/java/app/build.gradle", pkg)
        fi = pkg.replace('.', '/')

        time.sleep(10)
        copy_all_files(项目 + "/build/ins/java/app/src/main/java/com/magichands/java",
                       项目 + "/build/ins/java/app/src/main/java/" + fi)
        batch_modify_java_packageee("com.magichands.java", pkg, 项目 + "/build/ins/java/app/src/main/java/" + fi)
        copy_all_files(项目 + "/build/ins/java/app/src/androidTest/java/com/magichands/java",
                       项目 + "/build/ins/java/app/src/androidTest/java/" + fi)
        batch_modify_java_packageee("com.magichands.java", pkg, 项目 + "/build/ins/java/app/src/androidTest/java/" + fi)
        copy_all_files(项目 + "/build/ins/java/app/src/test/java/com/magichands/java",
                       项目 + "/build/ins/java/app/src/test/java/" + fi)
        batch_modify_java_packageee("com.magichands.java", pkg, 项目 + "/build/ins/java/app/src/test/java/" + fi)

        # copy_all_files(项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility",
        #                项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility")
        self.移动文件(图标, 项目 + "/build/ins/java/app/src/main/res/drawable/", "ico.jpg")
        modify_string_resource(项目 + "/build/ins/java/app/src/main/res/values/strings.xml", "app_name", 名字)
        time.sleep(10)
        delete_folder(项目 + "/build/ins/java/app/src/main/java/com/magichands/")
        delete_folder(项目 + "/build/ins/java/app/src/androidTest/java/com/magichands/")
        delete_folder(项目 + "/build/ins/java/app/src/test/java/com/magichands/")
        time.sleep(10)
        copy_all_files(项目 + "/java",
                       项目 + "/build/ins/java/app/src/main/java/")
        time.sleep(10)
        try:
            with open(项目 + "/build/ins/java/local.properties", 'w') as file:
                file.write('sdk.dir=' + os.path.normpath(os.getcwd()).replace("\\", "/") + '/env/Sdk')
        except IOError:
            print(f"Failed to overwrite file ")
        time.sleep(10)
        my_signal.setResult2.emit("初始化完成", 100, 184, 100)
        # 获取系统环境变量
        env = os.environ.copy()

        # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
        env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径

        # 启动子进程，并传递更新后的 PATH 环境变量给子进程
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env,
                             cwd=项目 + "/build/ins/java")

        lines = []
        my_signal.setResult2.emit("编译中...", 100, 184, 100)
        while True:
            # 读取子进程的输出
            line = p.stdout.readline().decode("GB2312").strip()
            if not line and p.poll() is not None:
                # 如果没有新的输出且子进程已经结束，则退出循环
                break
            elif line:
                # 如果有新的输出，则打印并添加到结果列表中
                print(">>>", line)
                my_signal.setResult2.emit(">>>" + str(line), 100, 184, 100)
                lines.append(line)

        copy_all_files(项目 + "/build/ins/java/app/build/outputs/apk/release/",
                       项目 + "/build/outputs/ins/java/release/")

        copy_all_files(项目 + "/build/ins/java/app/build/outputs/apk/debug/",
                       项目 + "/build/outputs/ins/java/debug/")
        time.sleep(10)
        my_signal.setResult2.emit("编译完成", 100, 184, 100)
        p.communicate()
        p.terminate()
        return lines

    def debug_py(self, command: str, 项目):
        my_signal.setResult2.emit("开始编译(python调试插件)-编译时间取决计算机性能(3-5min)", 100, 184, 100)

        delete_folder(项目 + "/build/ins/py")
        time.sleep(10)
        copy_all_files(项目 + "/build/intermediates/other/Demo py",
                       项目 + "/build/ins/py")
        time.sleep(10)

        copy_all_files(项目 + "/python",
                       项目 + "/build/ins/py/app/src/main/python")
        time.sleep(10)

        copy_all_files(
            项目 + "/build/intermediates/other/apk",
            项目 + "/build/ins/py/apk/")

        time.sleep(10)

        self.replace_in_file(项目 + "/build/ins/py/app/build.gradle",
                             "buildPython \"C:/Users/35600/anaconda3/python.exe\"",
                             "buildPython \"" + dir + "/py/python.exe\"")
        time.sleep(10)
        self.replace_in_file(项目 + "/build/ins/py/app/build.gradle",
                             "pip{}",
                             "pip {\n" + self.extract_pip_dependencies(项目 + "/config.json") + "\n}")

        time.sleep(10)
        try:
            with open(项目 + "/build/ins/py/local.properties", 'w') as file:
                file.write('sdk.dir=' + os.path.normpath(os.getcwd()).replace("\\", "/") + '/env/Sdk')
        except IOError:
            print(f"Failed to overwrite file ")
        time.sleep(10)
        my_signal.setResult.emit("初始化完成", 100, 184, 100)
        # 获取系统环境变量
        env = os.environ.copy()

        # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
        env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径

        # 启动子进程，并传递更新后的 PATH 环境变量给子进程
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env,
                             cwd=项目 + "/build/ins/py")

        lines = []
        my_signal.setResult.emit("编译中...", 100, 184, 100)
        while True:
            # 读取子进程的输出
            line = p.stdout.readline().decode("GB2312").strip()
            if not line and p.poll() is not None:
                # 如果没有新的输出且子进程已经结束，则退出循环
                break
            elif line:
                # 如果有新的输出，则打印并添加到结果列表中
                print(">>>", line)
                my_signal.setResult.emit(">>>" + str(line), 100, 184, 100)
                lines.append(line)

        time.sleep(5)
        my_signal.setResult.emit("编译完成", 100, 184, 100)
        # 读取子进程的输出和错误输出
        p.communicate()
        p.terminate()

        # 将输出打印出来

        # 子进程执行完毕后，可以继续操作删除生成的文件
        # ...

        # 终止子进程

        py_file = "chaquopy"
        copy_all_files(项目 + "/build/ins/py/app/build/generated/python/assets/release/app/" + py_file,
                       项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/build/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/misc/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)

        copy_all_files(
            项目 + "/build/ins/py/app/build/generated/python/assets/release/requirements/" + py_file,
            项目 + "/build/outputs/ins/py/assets/" + py_file)
        time.sleep(5)
        #
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/arm64-v8a",
        #     项目 + "/build/outputs/ins/py/jniLibs/arm64-v8a")
        # time.sleep(5)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/armeabi-v7a",
        #     项目 + "/build/outputs/ins/py/jniLibs/armeabi-v7a")
        # time.sleep(5)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/x86",
        #     项目 + "/build/outputs/ins/py/jniLibs/x86")
        # time.sleep(5)
        # copy_all_files(
        #     项目 + "/build/ins/py/app/build/generated/python/jniLibs/release/x86_64",
        #     项目 + "/build/outputs/ins/py/jniLibs/x86_64")
        # zip_file(项目 +"/build/outputs/ins/py/assets/"+ py_file)
        # copy_all_files(
        #     项目 + "/build/outputs/ins/py/assets/" + py_file,
        #     项目 + "/build/ins/py/apk/assets/" + py_file)
        # time.sleep(5)
        # zip_file(项目 + "/build/ins/py/apk")
        # time.sleep(5)
        # os.rename(项目 + "/build/ins/py/apk.zip", 项目 + "/build/ins/py/new.apk")
        self.zip_folder(项目 + "/build/outputs/ins/py/assets/" + py_file, 项目 + "/build/ins/py/apk/new.apk",
                        "assets/chaquopy")
        time.sleep(5)
        uppy(项目 + "/build/ins/py/apk/new.apk")

        重置指令(30)

        return 项目 + "/build/ins/py/app/build/outputs/apk/debug/app-debug.apk"

    def debug_java(self, command: str, 项目):
        my_signal.setResult2.emit("开始编译(java调试插件)-编译时间取决计算机性能(3-5min)", 100, 184, 100)

        delete_folder(项目 + "/build/ins/java")
        time.sleep(10)
        copy_all_files(项目 + "/build/intermediates/other/Demo java",
                       项目 + "/build/ins/java")
        time.sleep(10)
        copy_all_files(项目 + "/java",
                       项目 + "/build/ins/java/app/src/main/java/")
        time.sleep(10)
        try:
            with open(项目 + "/build/ins/java/local.properties", 'w') as file:
                file.write('sdk.dir=' + os.path.normpath(os.getcwd()).replace("\\", "/") + '/env/Sdk')
        except IOError:
            print(f"Failed to overwrite file ")
        time.sleep(10)
        my_signal.setResult.emit("开始编译", 100, 184, 100)
        # 获取系统环境变量
        env = os.environ.copy()

        # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
        env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径

        # 启动子进程，并传递更新后的 PATH 环境变量给子进程
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env,
                             cwd=项目 + "/build/ins/java")

        lines = []
        my_signal.setResult.emit("初始化完成...", 100, 184, 100)
        while True:
            # 读取子进程的输出
            line = p.stdout.readline().decode("GB2312").strip()
            if not line and p.poll() is not None:
                # 如果没有新的输出且子进程已经结束，则退出循环
                break
            elif line:
                # 如果有新的输出，则打印并添加到结果列表中
                print(">>>", line)
                my_signal.setResult.emit(">>>" + str(line), 100, 184, 100)
                lines.append(line)

        time.sleep(10)
        my_signal.setResult.emit("编译完成", 100, 184, 100)
        p.communicate()
        p.terminate()
        upjava(项目 + "/build/ins/java/app/build/outputs/apk/debug/app-debug.apk")
        重置指令(31)

        return 项目 + "/build/ins/java/app/build/outputs/apk/debug/app-debug.apk"

    def zip_folder(self, folder_path, zip_path, target_path):
        with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(target_path, os.path.relpath(file_path, folder_path))
                    zip_file.write(file_path, arcname)

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    arcname = os.path.join(target_path, os.path.relpath(dir_path, folder_path))
                    zip_file.write(dir_path, arcname)

    def cmd(self, command: str):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        print(type(p))
        my_signal.setResult2.emit("开始编译", 100, 184, 100)
        lines = []
        my_signal.setResult2.emit("编译中...", 100, 184, 100)
        for line in iter(p.stdout.readline, b''):
            line = line.strip().decode("GB2312")
            print(">>>", line)
            my_signal.setResult2.emit(str(line), 100, 184, 100)
            lines.append(line)
        my_signal.setResult2.emit("编译完成", 100, 184, 100)
        return lines

    def cmd2(self, command: str, 项目, 图标, 名字, pkg):
        my_signal.setResult2.emit("开始编译(脚本)-编译时间取决计算机性能(3-5min)", 100, 184, 100)
        delete_folder(项目 + "/build/app/1/")
        time.sleep(10)
        copy_all_files(项目 + "/build/intermediates/other/Demo",
                       项目 + "/build/app/1")
        time.sleep(10)
        gradle(项目 + "/build/app/1/app/build.gradle", pkg)
        fi = pkg.replace('.', '/')
        copy_all_files(项目 + "/build/app/1/app/src/main/java/pa/magichands/demo",
                       项目 + "/build/app/1/app/src/main/java/" + fi)
        batch_modify_java_packageee("pa.magichands.demo", pkg, 项目 + "/build/app/1/app/src/main/java/" + fi)
        copy_all_files(项目 + "/build/app/1/app/src/androidTest/java/pa/magichands/demo",
                       项目 + "/build/app/1/app/src/androidTest/java/" + fi)
        batch_modify_java_packageee("pa.magichands.demo", pkg, 项目 + "/build/app/1/app/src/androidTest/java/" + fi)
        copy_all_files(项目 + "/build/app/1/app/src/test/java/pa/magichands/demo",
                       项目 + "/build/app/1/app/src/test/java/" + fi)
        batch_modify_java_packageee("pa.magichands.demo", pkg, 项目 + "/build/app/1/app/src/test/java/" + fi)

        # copy_all_files(项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility",
        #                项目 + "/build/app/1/app/src/main/java/pa/magichands/accessibility")
        self.移动文件(图标, 项目 + "/build/app/1/app/src/main/res/drawable/", "ico.jpg")
        modify_string_resource(项目 + "/build/app/1/app/src/main/res/values/strings.xml", "app_name", 名字)
        time.sleep(10)
        delete_folder(项目 + "/build/app/1/app/src/main/java/pa/magichands/demo/")
        delete_folder(项目 + "/build/app/1/app/src/androidTest/java/pa/")
        delete_folder(项目 + "/build/app/1/app/src/test/java/pa/")
        time.sleep(10)
        copy_all_files(项目 + "/js",
                       项目 + "/build/app/1/app/src/main/assets/js")
        time.sleep(10)
        copy_all_files(项目 + "/res",
                       项目 + "/build/app/1/app/src/main/assets/ui")
        time.sleep(10)

        copy_all_files(项目 + "/assets",
                       项目 + "/build/app/1/app/src/main/assets")
        time.sleep(10)
        try:
            with open(项目 + "/build/app/1/local.properties", 'w') as file:
                file.write('sdk.dir=' + os.path.normpath(os.getcwd()).replace("\\", "/") + '/env/Sdk')
        except IOError:
            print(f"Failed to overwrite file ")
        time.sleep(10)
        my_signal.setResult2.emit("初始化完成", 100, 184, 100)
        # 获取系统环境变量
        env = os.environ.copy()

        # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
        env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径

        # 启动子进程，并传递更新后的 PATH 环境变量给子进程
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env,
                             cwd=项目 + "/build/app/1")

        lines = []
        my_signal.setResult2.emit("编译中...", 100, 184, 100)
        while True:
            # 读取子进程的输出
            line = p.stdout.readline().decode("GB2312").strip()
            if not line and p.poll() is not None:
                # 如果没有新的输出且子进程已经结束，则退出循环
                break
            elif line:
                # 如果有新的输出，则打印并添加到结果列表中
                print(">>>", line)
                my_signal.setResult2.emit(">>>" + str(line), 100, 184, 100)
                lines.append(line)

        copy_all_files(项目 + "/build/app/1/app/build/outputs/apk/release/",
                       项目 + "/build/outputs/apk/release/")

        copy_all_files(项目 + "/build/app/1/app/build/outputs/apk/debug/",
                       项目 + "/build/outputs/apk/debug/")
        time.sleep(10)
        my_signal.setResult2.emit("编译完成", 100, 184, 100)
        p.terminate()
        return lines

    def modify_distribution_url(self, file_path, new_url):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith('distributionUrl='):
                modified_lines.append('distributionUrl=' + new_url + '\n')
            else:
                modified_lines.append(line)

        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

    def gradle_home(self, file_path, new_url):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith('gradle.user.home='):
                modified_lines.append('gradle.user.home=' + new_url + '\n')
            else:
                modified_lines.append(line)

        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

    def cmd1(self, command: str):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        print(type(p))
        my_signal.setResult.emit("开始编译", 100, 184, 100)
        lines = []
        my_signal.setResult.emit("编译中...", 100, 184, 100)
        for line in iter(p.stdout.readline, b''):
            line = line.strip().decode("GB2312")
            print(">>>", line)
            my_signal.setResult.emit(str(line), 100, 184, 100)
            lines.append(line)
        my_signal.setResult.emit("编译完成", 100, 184, 100)
        return lines

    @staticmethod
    def __external_cmd(cmd, code="utf8"):
        my_signal.setResult.emit("开始编译", 100, 184, 100)
        print(cmd)
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:
                print(line.decode(code, 'ignore'))
                my_signal.setResult.emit(line.decode(code, 'ignore'), 100, 184, 100)
        my_signal.setResult.emit("编译完成", 100, 184, 100)

    def convert_path_to_slash(self, path):
        # 替换双反斜杠和双斜杠为单斜杠
        path = re.sub(r'\\\\|//', '/', path)
        # 替换单反斜杠为单斜杠
        path = path.replace('\\', '/')
        return path

    def unzip_file(self, pd: str):
        path = "/"
        if pd == "0":
            path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "-js"

        elif pd == "1":
            path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "-java"

        elif pd == "2":
            path = self.ui.edit_profile.text() + "/" + self.ui.edit_proname.text() + "-python"

        if path == "/":
            QMessageBox.information(self, "提示", "请选择正确路径", QMessageBox.Ok)
            return -1
        if not os.path.exists(path):
            os.mkdir(path)
        pa = path + "/build"
        if not os.path.exists(pa):
            os.mkdir(pa)
        pa = path + "/res"
        if not os.path.exists(pa):
            os.mkdir(pa)
        pa = path + "/assets"
        if not os.path.exists(pa):
            os.mkdir(pa)
        pa = path + "/config.json"
        if not os.path.exists(pa):
            file = open(pa, 'w')
            file.close()
        #
        # if pd == "0":
        #     copy_all_files(dir+"/js",path)
        #
        # elif pd == "1":
        #     copy_all_files(dir+"/java",path)
        #
        # elif pd == "2":
        #     copy_all_files(dir+"/py",path)
        #
        # if pd == "0":
        #     zip_src = dir + "/js.zip"
        #
        # elif pd == "1":
        #     zip_src = dir + "/java.zip"
        #
        # elif pd == "2":
        #     zip_src = dir + "/py.zip"
        #
        # dst_dir = path
        # r = zipfile.is_zipfile(zip_src)
        # if r:
        #     fz = zipfile.ZipFile(zip_src, 'r')
        #     for file in fz.namelist():
        #         fz.extract(file, dst_dir)
        # else:
        #     print('This is not zip')

        gradle_bin = "file:///" + self.convert_path_to_slash(dir) + "/gradle/gradle-8.0-bin.zip"
        print(gradle_bin)

        thread = threading.Thread(target=self.copy_demo, args=(pd, path, gradle_bin,))
        thread.start()

    def jc2(self, pd, path, gradle_bin):
        process = multiprocessing.Process(target=self.copy_demo, args=(pd, path, gradle_bin,))
        # 启动进程
        process.start()

    def replace_build_python_value(self, build_gradle_path, new_build_python_value):
        with open(build_gradle_path, 'r') as file:
            lines = file.readlines()

        with open(build_gradle_path, 'w') as file:
            for line in lines:
                if line.strip().startswith('buildPython'):
                    line = f'    buildPython "{new_build_python_value}"\n'
                file.write(line)

        print(f"buildPython value replaced with: {new_build_python_value}")

    def copy_demo(self, pd, path, gradle_bin):
        if pd == "0":
            copy_all_files(os.getcwd() + "/pro/js", path)
            time.sleep(5)
            self.modify_distribution_url(
                path + "/build/intermediates/other/Demo/gradle/wrapper/gradle-wrapper.properties", gradle_bin)
            # self.gradle_home(path + "/build/intermediates/other/Demo/gradle.properties", dir + "/gradle/gradle_home")
        elif pd == "1":
            copy_all_files(os.getcwd() + "/pro/java", path)
            time.sleep(5)
            self.modify_distribution_url(
                path + "/build/intermediates/other/Demo java/gradle/wrapper/gradle-wrapper.properties", gradle_bin)
            # self.gradle_home(path + "/build/intermediates/other/Demo java/gradle.properties", dir + "/gardle/gradle_home")
        elif pd == "2":
            copy_all_files(os.getcwd() + "/pro/py", path)
            time.sleep(5)
            self.replace_build_python_value(path + "/build/intermediates/other/Demo py/app/build.gradle",
                                            self.convert_path_to_slash(dir) + "/Python38/python.exe")
            self.modify_distribution_url(
                path + "/build/intermediates/other/Demo py/gradle/wrapper/gradle-wrapper.properties",
                gradle_bin)
            # self.gradle_home(path + "/build/intermediates/other/Demo py/gradle.properties",
            #                              dir + "/gardle/gradle_home")

    def 解压到指定(self, src, dir):
        path = self.ui.edit_debugfile.text()
        if path == "/":
            QMessageBox.information(self, "提示", "请选择正确路径", QMessageBox.Ok)
            return -1
        zip_src = src
        dst_dir = dir
        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
        else:
            print('This is not zip')

    def 移动文件(self, srcfile, dstpath, fname):  # 复制函数
        if not os.path.isfile(srcfile):
            print("%s not exist!" % (srcfile))
        else:
            # fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
            if not os.path.exists(dstpath):
                os.makedirs(dstpath)  # 创建路径
            shutil.copy(srcfile, dstpath + fname)  # 复制文件
            print("copy %s -> %s" % (srcfile, dstpath + fname))

    # src_dir = './'
    # dst_dir = './copy/'  # 目的路径记得加斜杠
    # src_file_list = glob(src_dir + '*')  # glob获得路径下所有文件，可根据需要修改
    # for srcfile in src_file_list:
    #     mycopyfile(srcfile, dst_dir)  # 复制文件

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


def folder_exists(folder_path):
    """
    判断指定文件夹是否存在

    参数:
    folder_path (str): 文件夹路径

    返回:
    bool: 如果文件夹存在，则返回 True；否则返回 False
    """
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def copy_gradle():
    dst_dir = os.path.expanduser("~");
    if folder_exists(dst_dir + "/.gradle"):
        print("gradle仓库存在,跳过")
    else:
        print("gradle不仓库存在,创建")
        zip_src = dir + "/gradle/.gradle.zip"

        r = zipfile.is_zipfile(zip_src)
        if r:
            fz = zipfile.ZipFile(zip_src, 'r')
            for file in fz.namelist():
                fz.extract(file, dst_dir)
        else:
            print('This is not zip')


def start_flask_app():
    # ip_port = (get_ipv4_address(), 8080)

    import socket
    ipv4s = socket.gethostbyname_ex(socket.gethostname())[2]
    if (str(ipv4s) != "no"):
        my_signal.setResult.emit("启动成功-服务地址:" + str(ipv4s) + ":['8080']", 100, 184, 100)
    af.run(host="0.0.0.0", port=8080, threaded=True)


@af.route('/log_receiver', methods=['POST'])
def receive_log():
    log = request.form['log']
    # 在这里可以处理接收到的日志数据，例如写入日志文件、发送邮件等
    log = log.strip()
    print('Received log:', log)
    if (str(log) != "no"):
        my_signal.setResult.emit(str(log), 100, 184, 100)
    return 'OK'


@af.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']  # 获取上传的文件对象
    file.save(dir + '/debug.zip')  # 保存文件到服务器端
    # 在这里可以处理接收到的文件，例如写入文件、发送邮件等
    return 'File uploaded and saved successfully'


@af.route('/upload_py', methods=['POST'])
def upload_py():
    file = request.files['file']  # 获取上传的文件对象
    file.save(dir + '/new.apk')  # 保存文件到服务器端
    # 在这里可以处理接收到的文件，例如写入文件、发送邮件等
    return 'File uploaded and saved successfully'


@af.route('/upload_java', methods=['POST'])
def upload_java():
    file = request.files['file']  # 获取上传的文件对象
    file.save(dir + '/java.apk')  # 保存文件到服务器端
    # 在这里可以处理接收到的文件，例如写入文件、发送邮件等
    return 'File uploaded and saved successfully'


@af.route('/upload1', methods=['POST'])
def upload1():
    file = request.files['file']  # 获取上传的文件对象
    file.save(os.getcwd() + '/uix/1.png')  # 保存文件到服务器端
    # 在这里可以处理接收到的文件，例如写入文件、发送邮件等
    return 'File uploaded and saved successfully'


@af.route('/upload2', methods=['POST'])
def upload2():
    file = request.files['file']  # 获取上传的文件对象
    file.save(os.getcwd() + '/uix/1.xml')  # 保存文件到服务器端
    # 在这里可以处理接收到的文件，例如写入文件、发送邮件等
    return 'File uploaded and saved successfully'


@af.route('/download', methods=['GET'])
def download():
    file_path = dir + '/debug.zip'  # 文件的服务器端保存路径
    return send_file(file_path, as_attachment=True)


@af.route('/download_java', methods=['GET'])
def download_java():
    file_path = dir + '/java.apk'  # 文件的服务器端保存路径
    return send_file(file_path, as_attachment=True)


@af.route('/download_py', methods=['GET'])
def download_py():
    file_path = dir + '/new.apk'  # 文件的服务器端保存路径
    return send_file(file_path, as_attachment=True)


@af.route('/download1', methods=['GET'])
def download1():
    file_path = os.getcwd() + '/uix/1.png'  # 文件的服务器端保存路径
    return send_file(file_path, as_attachment=True)


@af.route('/download2', methods=['GET'])
def download2():
    file_path = os.getcwd() + '/uix/1.xml'  # 文件的服务器端保存路径
    return send_file(file_path, as_attachment=True)


# @af.route('/upp', methods=['GET'])
# def upp():
#     up()
#     return "OK"

@af.route('/set', methods=['GET'])
def set():
    重置指令(0)
    return "OK"


@af.route('/cmd', methods=['GET'])
def cmds():
    return str(重置指令(0))


@af.route('/png', methods=['GET'])
def png():
    重置指令(9)
    my_signal.setResult2.emit("获取节点信息中(10s-20s)", 100, 184, 100)
    return "OK"
    # while True :
    #     if pngcmd == 1 :
    #
    #         return  "true"
    #
    #     elif  pngcmd == 2:
    #
    #         return "false"


@af.route('/pngis', methods=['GET'])
def pngis():
    return str(png指令(0))


xt = 0
# 记录最后一次心跳时间的字典，以客户端的IP地址作为键
last_heartbeat = {}
# 线程锁
heartbeat_lock = threading.Lock()


def 心跳(num: int):
    global xt
    xt = num
    return xt


def xintiao():
    heartbeat_monitor_thread = threading.Thread(target=heartbeat_monitor)
    heartbeat_monitor_thread.daemon = True
    heartbeat_monitor_thread.start()


# 心跳监听函数
def heartbeat_monitor():
    while True:
        current_time = datetime.now()
        print("Current time:", current_time)  # 调试语句，用于查看当前时间

        # 锁定心跳记录
        with heartbeat_lock:
            to_be_deleted = []  # 初始化删除列表
            # 遍历所有的心跳记录
            for client_ip, timestamp in last_heartbeat.items():
                # 计算当前时间与最后一次心跳时间的差值
                time_diff = (current_time - timestamp).total_seconds()
                if time_diff > 3:
                    print(f"Heartbeat disconnected from client: {client_ip}")
                    心跳(0)
                    my_signal.setResult.emit("心跳中断", 100, 184, 100)
                    # 将需要删除的心跳记录添加到删除列表中
                    to_be_deleted.append(client_ip)

            # 删除断开的心跳记录
            for client_ip in to_be_deleted:
                del last_heartbeat[client_ip]

        # 等待一秒
        threading.Event().wait(1)


# 心跳接口
@af.route('/heartbeat', methods=['GET'])
def heartbeat():
    client_ip = request.remote_addr
    # 更新客户端的最后心跳时间为当前时间
    if xt == 0:
        my_signal.setResult.emit("心跳建立成功", 100, 184, 100)
        心跳(1)

    with heartbeat_lock:
        last_heartbeat[client_ip] = datetime.now()
    return "OK"


@af.route('/pngset', methods=['GET'])
def pngset():
    png指令(1)
    return "OK"


@af.route('/pngin', methods=['GET'])
def pngin():
    png指令(0)
    return "OK"


def up(file):
    # 读取本地文件
    file_path = file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    # 发送文件给 Flask 服务器
    url = 'http://' + get_ip() + ':8080/upload'  # Flask 服务器端的上传接口
    files = {'file': ('debug.zip', file_data)}
    response = requests.post(url, files=files)
    print(response.text)


def uppy(file):
    # 读取本地文件
    file_path = file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    # 发送文件给 Flask 服务器
    url = 'http://' + get_ip() + ':8080/upload_py'  # Flask 服务器端的上传接口
    files = {'file': ('new.apk', file_data)}
    response = requests.post(url, files=files)
    print(response.text)


def upjava(file):
    # 读取本地文件
    file_path = file
    with open(file_path, 'rb') as file:
        file_data = file.read()
    # 发送文件给 Flask 服务器
    url = 'http://' + get_ip() + ':8080/upload_java'  # Flask 服务器端的上传接口
    print("url:" + url)
    files = {'file': ('app-debug.zip', file_data)}
    response = requests.post(url, files=files)
    print(response.text)


def get_ip():
    try:
        # 创建一个socket对象
        sock = py_socket.socket(py_socket.AF_INET, py_socket.SOCK_DGRAM)

        # 连接到外部服务器（此处使用谷歌的DNS服务器）
        sock.connect(("8.8.8.8", 80))

        # 获取本地IP地址
        ip_address = sock.getsockname()[0]

        # 关闭socket连接
        sock.close()

        return ip_address
    except Exception as e:
        print(e)
        return None


def 重置指令(num: int):
    global command
    lo = command
    command = num
    return lo


def png指令(num: int):
    global pngcmd
    lo = pngcmd
    pngcmd = num
    return lo


def get_selected_text():
    # # 模拟按下Ctrl键
    # pyautogui.keyDown('ctrl')
    # # 模拟按下C键
    # pyautogui.press('c')
    # # 释放C键
    # pyautogui.keyUp('ctrl')
    # # 获取剪贴板内容
    root = Tk()
    selected_text = root.clipboard_get()
    root.destroy()
    print("剪切板：" + selected_text)
    return selected_text


def create_file(file_path):
    try:
        with open(file_path, 'w') as f:
            # 在这里可以写入文件的内容
            # 如果不需要写入内容，可以省略这一步
            # 示例：写入一行文本
            f.write("Hello, world!")
        print(f"文件 '{file_path}' 创建成功。")
    except Exception as e:
        print(f"创建文件 '{file_path}' 失败：{e}")


def overwrite_file(file_path, content):
    """覆盖写入文件内容"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"文件 '{file_path}' 已成功覆盖写入内容。")
    except Exception as e:
        print(f"写入文件 '{file_path}' 时出现错误: {e}")


# # 使用示例
# file_path = 'example.txt'  # 文件路径
# content = '这是新的文件内容。'  # 要写入的内容
# overwrite_file(file_path, content)

def gradle(gradle_file_path, pkg):
    # 要修改的applicationId的新值

    replacement_dict = {
        "applicationId": pkg,
        "namespace": pkg

        # 添加更多的键值对，表示要查找和替换的其他键值对
    }

    with fileinput.FileInput(gradle_file_path, inplace=True) as file:
        for line in file:
            # 遍历字典中的键值对，查找并替换对应的参数值
            for key, value in replacement_dict.items():
                if key in line:
                    line = line.split(key)[0] + key + " " + '"' + value + '"'
            print(line.rstrip())


def batch_modify_java_package(old_package_name, new_package_name, java_folder_path):
    """
    批量修改 Java 文件中的包名和导入包的名

    参数：
    old_package_name（str）：原包名
    new_package_name（str）：新包名
    java_folder_path（str）：Java 文件所在的文件夹路径

    """

    # 遍历指定文件夹下的所有 Java 文件
    for dirpath, dirnames, filenames in os.walk(java_folder_path):
        for filename in filenames:
            if filename.endswith(".kt"):
                file_path = os.path.join(dirpath, filename)
                with fileinput.FileInput(file_path, inplace=True) as file:
                    for line in file:
                        # 修改包名
                        if line.strip().startswith("package " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        # 修改导入包的名
                        elif line.strip().startswith("import " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        print(line.rstrip())  # 使用rstrip()方法移除行末尾的换行符，并打印替换后的行


def batch_modify_java_packagee(old_package_name, new_package_name, java_folder_path):
    for dirpath, dirnames, filenames in os.walk(java_folder_path):
        for filename in filenames:
            if filename.endswith(".kt"):
                file_path = os.path.join(dirpath, filename)
                with codecs.open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                with codecs.open(file_path, 'w', encoding='utf-8') as file:
                    for line in lines:
                        # 修改包名
                        if line.strip().startswith("package " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        # 修改导入包名
                        elif line.strip().startswith("import " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        file.write(line.rstrip() + '\n')  # 使用rstrip()方法移除行末尾的换行符，并写入替换后的行


def batch_modify_java_packageee(old_package_name, new_package_name, java_folder_path):
    for dirpath, dirnames, filenames in os.walk(java_folder_path):
        for filename in filenames:
            if filename.endswith(".kt"):
                file_path = os.path.join(dirpath, filename)
                with codecs.open(file_path, 'r+', encoding='utf-8') as file:
                    lines = file.readlines()
                    file.seek(0)  # 将文件指针移动到文件开头
                    file.truncate()  # 清空文件内容
                    for line in lines:
                        # 修改包名
                        if line.strip().startswith("package " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        # 修改导入包名
                        elif line.strip().startswith("import " + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        elif line.strip().startswith('assertEquals("' + old_package_name):
                            line = line.replace(old_package_name, new_package_name)
                        file.write(line.rstrip() + '\n')  # 使用rstrip()方法移除行末尾的换行符，并写入替换后的行
            else:
                if filename.endswith(".java"):
                    file_path = os.path.join(dirpath, filename)
                    with codecs.open(file_path, 'r+', encoding='utf-8') as file:
                        lines = file.readlines()
                        file.seek(0)  # 将文件指针移动到文件开头
                        file.truncate()  # 清空文件内容
                        for line in lines:
                            # 修改包名
                            if line.strip().startswith("package " + old_package_name):
                                line = line.replace(old_package_name, new_package_name)
                            # 修改导入包名
                            elif line.strip().startswith("import " + old_package_name):
                                line = line.replace(old_package_name, new_package_name)
                            elif line.strip().startswith('assertEquals("' + old_package_name):
                                line = line.replace(old_package_name, new_package_name)
                            file.write(line.rstrip() + '\n')  # 使用rstrip()方法移除行末尾的换行符，并写入替换后的行


def copy_all_files(src_folder, dest_folder):
    """
    复制源文件夹中的所有文件到目标文件夹

    参数：
    src_folder（str）：源文件夹路径
    dest_folder（str）：目标文件夹路径

    """

    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 遍历源文件夹下的所有文件和文件夹
    for item in os.listdir(src_folder):
        item_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)

        # 判断是否为文件
        if os.path.isfile(item_path):
            # 复制文件到目标文件夹
            shutil.copy2(item_path, dest_path)
        elif os.path.isdir(item_path):
            # 如果是文件夹，则递归复制文件夹中的文件
            copy_all_files(item_path, dest_path)


def delete_folder(folder_path):
    """
    删除文件夹

    参数：
    folder_path（str）：文件夹路径

    """

    # 使用 shutil.rmtree 删除文件夹及其内容
    try:
        shutil.rmtree(folder_path)
        print("Folder deleted successfully.")
    except OSError as e:
        print(f"报错: {e}")
        try:
            shutil.rmtree(folder_path)
            print("Folder deleted successfully.")
        except OSError as e:
            error_message = str(e)
            pattern = r'进程无法访问。: (.+)'
            match = re.search(pattern, error_message)
            if match:
                file_path = match.group(1).replace("'", "")
                print("Error deleting folder:", file_path)

                thread = threading.Thread(target=close_file, args=(file_path,))
                thread.start()

                # 在这里可以添加其他处理逻辑，比如记录日志或执行其他操作
            else:
                print("Error message format does not match the expected pattern.")
        my_signal.setResult.emit("编译出错-清理缓存中-请等几分钟再试", 100, 184, 100)


def jc3(file_path):
    process = multiprocessing.Process(target=close_file, args=(file_path,))
    process.start()


def xml():
    env = os.environ.copy()

    # 将 Java 安装路径下的 bin 目录添加到 PATH 环境变量
    env["PATH"] = dir + "/jbr/bin;" + env["PATH"]  # 替换为您的 Java 安装路径
    # 启动子进程，并传递更新后的 PATH 环境变量给子进程
    print(dir + "/jar")
    p = subprocess.Popen('java -jar "MagicHands Viewer.jar"', shell=True, stdout=subprocess.PIPE, env=env,
                         cwd=dir + "/jar")

    if p.returncode != 0:
        # 打印错误信息
        print(sys.getdefaultencoding())
    else:
        # 打印命令的标准输出
        print(sys.getdefaultencoding())

    lines = []
    my_signal.setResult.emit("启动MagicHands Viewer完成", 100, 184, 100)
    while True:
        # 读取子进程的输出
        line = p.stdout.readline().decode("GB2312").strip()
        if not line and p.poll() is not None:
            # 如果没有新的输出且子进程已经结束，则退出循环
            break
        elif line:
            # 如果有新的输出，则打印并添加到结果列表中
            print(">>>", line)
            my_signal.setResult.emit(">>>" + str(line), 100, 184, 100)
            lines.append(line)


def convert_path(path):
    # 替换双反斜杠和双斜杠为单斜杠
    path = re.sub(r'\\\\|//', '/', path)
    # 替换单反斜杠为单斜杠
    path = path.replace('\\', '/')
    return path


def kill_process(process_id):
    try:
        process = psutil.Process(process_id)
        process.terminate()
        process.wait(timeout=5)
    except psutil.NoSuchProcess:
        pass
    except psutil.AccessDenied:
        # 提示用户获取管理员权限
        print("需要管理员权限来终止进程。")


def close_file(file):
    # 获取占用文件的进程信息
    # filename= re.sub(r'\\{2,}', '/', file)
    filename = convert_path(file)
    print("关闭路径:" + filename)
    for process in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            for file in process.open_files():
                if file.path == filename:
                    print(file.path)
                    print(f"找到占用文件的进程：{process.name()} (PID: {process.pid})")
                    # 终止占用文件的进程
                    kill_process(process.pid)

                    # 在管理员权限下尝试删除文件
                    # try:
                    #     subprocess.run(['cmd', '/c', 'del', filename], check=True, shell=True, capture_output=True)
                    #     print("文件删除成功。")
                    # except subprocess.CalledProcessError as e:
                    #     print(f"删除文件失败：{e.stderr.decode()}")
                    return

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # 未找到占用文件的进程
    print("未找到占用文件的进程。")


def modify_string_resource(xml_file, resource_name, new_value):
    """
    修改 Android string 资源文件中的值

    参数：
    xml_file（str）：XML 文件路径
    resource_name（str）：要修改的资源名称
    new_value（str）：新的资源值

    """

    # 解析 XML 文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 遍历 <string> 元素
    for string_elem in root.findall(".//string"):
        # 获取 string 元素的 name 属性值
        name = string_elem.get("name")
        # 如果 name 属性值匹配到要修改的资源名称
        if name == resource_name:
            # 修改 string 元素的文本值
            string_elem.text = new_value

    # 将修改后的 XML 写入文件
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("ico.ico"))
    window = MainWindow()
    sys.exit(app.exec())
