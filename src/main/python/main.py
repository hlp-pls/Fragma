from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import PyInstaller.__main__
import PyInstaller

#--> imports for moviepy packaging : https://github.com/Zulko/moviepy/issues/591
import imageio
import imageio_ffmpeg
import PIL
import decorator
import tqdm
import numpy
import moviepy

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex

from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

#--> imports for mgl packaging
import moderngl
import moderngl_window as mglw
import moderngl_window.context.pyglet
import glcontext

from datetime import datetime

import sys
import os
import re 
import shutil
import subprocess
from functools import partial
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

#--> custom lexer for Qscintilla
from __lexer import GLSLLexer
#--> custom moderngl window class
from __mgl_window import MGL_WINDOW
#--> custom pyqt class
from __labeled_int_field import LabelledIntField
from __labeled_float_field import LabelledFloatField
from __popup import CustomDialog, CustomProgressDialog
from __uniform_button import UniformButton

#--> LOCK FILE
from __pid_lock import FLOCK

default_code = '''#version 330
out vec4 outputColor;
in vec2 UV;

uniform sampler2D bckbuffer;
uniform vec2 resolution;
uniform vec2 mouse;
uniform vec2 mousedt;
uniform bool mousedown;
uniform float time;

void main() {
\tvec2 uv = UV;
\toutputColor = vec4(uv,1.,1.);
}
'''

MARKER = "/**========END_OF_FRAGMENT========**/"

class CustomAppCTX(ApplicationContext):
    @cached_property
    def app(self):
        return QApplication(sys.argv)

class CustomMainWindow(QMainWindow):
    def __init__(self, AppCTX, App):
        super(CustomMainWindow, self).__init__()
        
        #project manager
        self.__file_dialog = QFileDialog()
        #self.__file_dialog.setNameFilter("Fragma file (*.fragma)")
        #self.__file_dialog.setViewMode(QFileDialog::Detail)

        # Resource path
        
        self.__appctx = AppCTX
        self.__app = App
        print(self.__app)

        # rootdir = self.__appctx.get_resource()
        # rootdir = Path(os.path.dirname(rootdir)).as_posix()
        # print(rootdir)

        #---> FBS does not allow this --> this will work with run, but not when freezing or releasing
        # https://stackoverflow.com/questions/55930797/how-to-reference-resource-file-in-pyqt-stylesheet-using-fbs
        #QDir.addSearchPath('resource',os.path.join(rootdir,"resources/base"))
        #cssfile = QFile('resource:__style.qss')
        #cssfile.open(QFile.ReadOnly | QFile.Text)
        #self.__app.setStyleSheet(str(cssfile.readAll(), 'utf-8'))

        close_tab = Path(self.__appctx.get_resource("close-tab.png")).as_posix()
        close_tab_hover = Path(self.__appctx.get_resource("close-tab-hover.png")).as_posix()

        print(close_tab, close_tab_hover)
        QSS_text = Path(self.__appctx.get_resource('__style.qss')).read_text()
        QSS_text = QSS_text % {"close_tab": close_tab, "close_tab_hover" : close_tab_hover}
        #print(QSS_text)
        self.__app.setStyleSheet(QSS_text)
        
        # Window setup
        # --------------

        # Define the geometry of the main window
        #self.setGeometry(300, 300, 800, 600)
        self.resize(800, 750)
        self.center()
        self.setWindowTitle("Fragma")

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.__effect = QGraphicsDropShadowEffect()
        self.__effect.setBlurRadius(9)
        self.__effect.setOffset(0)
        self.setGraphicsEffect(self.__effect)

        # Create toolbar
        #self.__toolbar = QToolBar("Main Toolbar")
        #self.addToolBar(self.__toolbar)

        # Create Menubar
        self.__menu = self.menuBar()

        file_save_action = QAction(QIcon(), "&Save", self)
        file_save_action.setStatusTip("Save Fragments")
        file_save_action.triggered.connect(self.saveProject)
        self._shortcut_save = QShortcut(QKeySequence('Ctrl+S'), self)
        self._shortcut_save.activated.connect(self.saveProject)
        #file_action.setCheckable(True)
        #self.__toolbar.addAction(button_action)

        file_open_action = QAction(QIcon(), "&Open", self)
        file_open_action.setStatusTip("Open Fragments")
        file_open_action.triggered.connect(self.openProject)
        self._shortcut_open = QShortcut(QKeySequence('Ctrl+O'), self)
        self._shortcut_open.activated.connect(self.openProject)

        self.__file_menu = self.__menu.addMenu("&File")
        self.__file_menu.addAction(file_save_action)
        self.__file_menu.addAction(file_open_action)

        file_fontsize_action = QAction(QIcon(), "&Font Size", self)
        file_fontsize_action.setStatusTip("Font Size")
        file_fontsize_action.triggered.connect(self.setFontSize)
        
        
        file_lineheight_action = QAction(QIcon(), "&Line Height", self)
        file_lineheight_action.setStatusTip("Line Height")
        file_lineheight_action.triggered.connect(self.setLineHeight)

        self.__file_menu = self.__menu.addMenu("&Editor")
        self.__file_menu.addAction(file_fontsize_action)
        self.__file_menu.addAction(file_lineheight_action)

        # Create frame and layout
        self.__frm = QFrame(self)
        #self.__frm.setStyleSheet("")
        self.__lyt = QVBoxLayout()
        #self.__lyt.setContentsMargins(0,0,0,0)
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        fontId = QFontDatabase.addApplicationFont(self.__appctx.get_resource("D2Coding-Ver1.3.2-20180524.ttf"))
        families = QFontDatabase.applicationFontFamilies(fontId)
        print(families[0])
        self.__myFont = QFont(families[0])#QFont(self.__appctx.get_resource("D2CodingBold-Ver1.3.2-20180524.ttf"))
        #self.__myIconFont = QFont(self.__appctx.get_resource('MaterialIcons-Regular.ttf'))
        self.__myFont.setPointSize(14)

        # loading images for icons
        #self.__aspect_icon = QPixmap(self.__appctx.get_resource('aspect_ratio_2.png'))
        #self.__VER_CURSOR = QCursor(QPixmap(self.__appctx.get_resource('cursor_V_45.png')))
        #self.__HOR_CURSOR = QCursor(QPixmap(self.__appctx.get_resource('cursor_H_45.png')))
        #self.__CLOSE_ICON = QIcon(self.__appctx.get_resource('close.png'))
        #self.__MAX_ICON = QIcon(self.__appctx.get_resource('max.png'))
        #self.__PLAY_ICON = QPixmap(self.__appctx.get_resource('play.png'))
        #self.__STOP_ICON = QPixmap(self.__appctx.get_resource('stop.png'))
        
        # Window title Bar
        win_btns_lyt = QHBoxLayout()
        win_btns_lyt.setContentsMargins(0,0,0,0)

        self.__quit_btn = QPushButton("")
        self.__quit_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('close.png') + ")")
        #self.__quit_btn.setIcon(self.__CLOSE_ICON)
        #self.__quit_btn.setIconSize(QSize(10,10))
        self.__quit_btn.setObjectName("quit_btn")
        self.__quit_btn.setFixedWidth(12)
        self.__quit_btn.setFixedHeight(12)
        self.__quit_btn.clicked.connect(self.__quit_btn_action)

        self.__max_btn = QPushButton("")
        self.__max_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('max.png') + ")")
        #self.__max_btn.setIcon(self.__MAX_ICON)
        #self.__max_btn.setIconSize(QSize(10,10))
        self.__max_btn.setObjectName("max_btn")
        self.__max_btn.setFixedWidth(12)
        self.__max_btn.setFixedHeight(12)
        self.__max_btn.clicked.connect(self.__max_btn_action)
        
        win_btns_lyt.addWidget(self.__quit_btn)
        win_btns_lyt.addWidget(self.__max_btn)
        
        win_btns_lyt.addStretch(9)
        #win_btns_lyt.setContentsMargins(0,0,0,0)
        self.__lyt.addLayout(win_btns_lyt)

        panel_layout = QVBoxLayout()

        mgl_ctx_tester = moderngl.create_context(standalone=True, require=(330))
        self.__mgl_max_size = mgl_ctx_tester.info["GL_MAX_VIEWPORT_DIMS"]
        #self.__mgl_max_size = (min(self.__mgl_max_size[0], 1080), min(self.__mgl_max_size[0], 1080))
        mgl_ctx_tester.release()
        print(self.__mgl_max_size) 

        # Create widgets to control framebuffer size
        whlayout = QHBoxLayout()
        self.wdiv = LabelledIntField('', self.__myFont, 400)
        self.hdiv = LabelledIntField('', self.__myFont, 400)
        self.pd_div = LabelledFloatField('', self.__myFont, 2.0)
        self.fps_div = LabelledFloatField('', self.__myFont, 60)
        #self.wdiv.label.setPixmap(self.__aspect_icon)
        #self.wdiv.label.resize(int(self.__aspect_icon.width() * 0.5),int(self.__aspect_icon.height() * 0.5))
       
        whlayout.addWidget(self.wdiv)
        whlayout.setSpacing(10)
        whlayout.addWidget(self.hdiv)
        #whlayout.setSpacing(10)
        #whlayout.addWidget(self.pd_div)
        whlayout.setSpacing(10)
        whlayout.addWidget(self.fps_div)
        whlayout.addStretch(9)
        
        panel_layout.addLayout(whlayout)

        con_layout = QHBoxLayout()

        # Place Run button
        self.__run_btn = QPushButton("")
        self.__run_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('play.png') + ")")
        self.__run_btn.setFixedWidth(24)
        self.__run_btn.setFixedHeight(24)
        self.__run_btn.clicked.connect(self.__run_btn_action)
        self.__run_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__run_btn)
        con_layout.setSpacing(10)

        # Place Stop button
        self.__stop_btn = QPushButton("")
        self.__stop_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('stop.png') + ")")
        self.__stop_btn.setFixedWidth(24)
        self.__stop_btn.setFixedHeight(24)
        self.__stop_btn.clicked.connect(self.__stop_btn_action)
        self.__stop_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__stop_btn)
        con_layout.setSpacing(10)

        

        # Place New Editor button
        self.__new_editor_btn = QPushButton("")
        self.__new_editor_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('add.png') + ")")
        self.__new_editor_btn.setFixedWidth(24)
        self.__new_editor_btn.setFixedHeight(24)
        self.__new_editor_btn.clicked.connect(self.__new_editor_action)
        self.__new_editor_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__new_editor_btn)
        con_layout.addStretch(8)

        # Place Build
        self.__build_btn = QPushButton("")
        #self.__build_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('play_once.png') + ")")
        self.__build_btn.setFixedWidth(24)
        self.__build_btn.setFixedHeight(24)
        self.__build_btn.clicked.connect(self.__build_btn_action)
        self.__build_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__build_btn)
        con_layout.setSpacing(10)

        # Place Compile / Play Once
        self.__compile_btn = QPushButton("")
        self.__compile_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('play_once.png') + ")")
        self.__compile_btn.setFixedWidth(24)
        self.__compile_btn.setFixedHeight(24)
        self.__compile_btn.clicked.connect(self.__compile_btn_action)
        self.__compile_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__compile_btn)
        con_layout.setSpacing(10)

        # Place Capture button
        self.__capture_btn = QPushButton("")
        self.__capture_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('capture.png') + ")")
        self.__capture_btn.setFixedWidth(24)
        self.__capture_btn.setFixedHeight(24)
        self.__capture_btn.clicked.connect(self.__capture_btn_action)
        self.__capture_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__capture_btn)
        con_layout.setSpacing(10)
        
        # Place Rec button
        self.__rec_btn = QPushButton("")
        self.__rec_btn.setStyleSheet("border-image: url(" + self.__appctx.get_resource('rec.png') + ")")
        self.__rec_btn.setFixedWidth(24)
        self.__rec_btn.setFixedHeight(24)
        self.__rec_btn.clicked.connect(self.__rec_btn_action)
        self.__rec_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__rec_btn)
        
        self.__rec_popup = CustomDialog(
            parent=self, 
            flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint, 
            title="record", 
            message="Set recording duration (seconds)",
            font=self.__myFont,
            type="FLOAT_INPUT",
            initial_value=1.0
            )
        
        # self.__rec_progress_popup = CustomProgressDialog(
        #     parent=self, 
        #     flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint, 
        #     title="record", 
        #     message="Recording Progress",
        #     font=self.__myFont,
        #     type="PROGRESS",
        #     initial_value=0.0
        #     )
        
        self.__fontsize_popup = CustomDialog(
            parent=self, 
            flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint, 
            title="Font Size", 
            message="Font Size",
            font=self.__myFont,
            type="INT_INPUT",
            initial_value = 18
            )
        
        self.__lineheight_popup = CustomDialog(
            parent=self, 
            flags=Qt.FramelessWindowHint, 
            title="Line Height", 
            message="Line Height",
            font=self.__myFont,
            type="FLOAT_INPUT",
            initial_value=1.2
            )
        
        # self.__projnm_btn = QLineEdit()
        # self.__projnm_btn.setMaximumWidth(200)
        # con_layout.addWidget(self.__projnm_btn)
        # self.__projnm_btn.setText("Fragment Name")

         
        panel_layout.addLayout(con_layout)
        self.__lyt.addLayout(panel_layout)
        
        whlayout.setContentsMargins(0,20,0,0)
        con_layout.setContentsMargins(0,0,0,0)
        panel_layout.setContentsMargins(20,0,20,5)

        # QScintilla editor setup
        # ------------------------
        self.__editor_tabs = QTabWidget()
        self.__editor_tabs.setFont(self.__myFont)
        self.__editor_tabs.setTabsClosable(True)
        self.__editor_tabs.setMovable(True)
        self.__editor_tabs.tabCloseRequested.connect(self.__remove_editor_action)
        self.__editor_tab_count = 0
        #self.__editor_tabs.setTabsE

        self.__editors_layout = QVBoxLayout()
        self.__editors_layout.setObjectName("editor_layout")
        self.__editors_layout.addWidget(self.__editor_tabs)
        self.__lyt.addLayout(self.__editors_layout)
        #self.__editors = []
        #self.__editor_compressions = []

        self.__uniform_panel = QHBoxLayout()
        self.__lyt.addLayout(self.__uniform_panel)
        self.__uniform_panel.addStretch(9)
       
        self.__new_editor_action()

        self.__console = QTextEdit()
        self.__console.setFixedHeight(100)
        self.__console.setReadOnly(True)
        self.__lyt.addWidget(self.__console)

        self.show()

        self.__mgl_window_str = 'moderngl_window.context.pyglet.Window'
        self.__mgl_window_cls = mglw.get_window_cls(self.__mgl_window_str)
        self.__runner_window = None
        self.__runner = None

        # Mouse position
        self.__mpos = [0, 0]
        self.__prev_mpos = [0, 0]
        self.__m_state = None

    ''''''
    def setFontSize(self):
        print("set font size")
        if self.__fontsize_popup.exec():
            font_size = self.__fontsize_popup.getValue()
            editors = self.__editor_tabs.findChildren(QsciScintilla)
            for editor in editors:
                lexer = editor.lexer()
                lexer.setFontSize(font_size)
            

    def setLineHeight(self):
        print("set line height")
        if self.__lineheight_popup.exec():
            line_size = self.__lineheight_popup.getValue()
            editors = self.__editor_tabs.findChildren(QsciScintilla)
            for editor in editors:
                lexer = editor.lexer()
                lexer.setLineHeight(line_size)

    def saveProject(self):
        print("save file")
        texts = ""
        editors = self.__editor_tabs.findChildren(QsciScintilla)
        for editor in editors:
            if editor.parent != None:
            #print(editor.text())
                texts += editor.text() + MARKER

        #print(texts)
        filename = self.__file_dialog.getSaveFileName(self, '', '', "Fragma file (*.fragma)")
        print(filename)
        with open(filename[0], 'w') as f:
            f.write(texts)

    def openProject(self):
        print("open project")
        file = QStringListModel()
        filename = self.__file_dialog.getOpenFileName(self, '', '', "Fragma file (*.fragma)")
        file = open(filename[0], 'r')
        file_data = file.read()
        #print(file_data)
        # for index in range(self.__editor_tabs.count()):
        #     self.__remove_editor_action(index)

        while self.__editor_tabs.count() >= 1:
            self.__remove_editor_action(0)

        # editors = self.__editor_tabs.findChildren(QsciScintilla)
        # for editor in editors:
        #     editor.setParent(None)
        #     editor.deleteLater()
        
        self.__editor_tabs.clear()
        self.__editor_tab_count = 0
        fragments = file_data.split(MARKER)
        for i, fragment in enumerate(fragments):
            if i < len(fragments)-1:
                self.__new_editor_action(text=fragment)

        # for index, editor in enumerate(self.__editors):
        #     if index < len(fragments):
        #         editor.setText(fragments[index])

        # check available projects
        # projects = self.__project_manager.searchDirectory(self.__appctx.get_resource("projects/"))
        # print(projects)
        # prompt a dialog

        #f = open(projects[0], "r")
        #print(f.read())

    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton:
            print('LEFT')
        if buttons & Qt.MidButton:
            print('MIDDLE')
        if buttons & Qt.RightButton:
            print('RIGHT')
    
    def mousePressEvent(self, e):  # e ; QMouseEvent
        if e.buttons() == Qt.LeftButton:
            self.__m_state = self.checkMouseArea(e)
            self.__prev_mpos[0] = e.x()
            self.__prev_mpos[1] = e.y()

    def mouseReleaseEvent(self, e):  # e ; QMouseEvent
        if e.buttons() == Qt.LeftButton:
            self.__m_state = None
            #self.__prev_mpos[0] = e.x()
            #self.__prev_mpos[1] = e.y()
        self.restoreCursor()

    def mouseMoveEvent(self, e):  # e ; QMouseEvent
        #print('(%d %d)' % (e.x(), e.y()))
        if not self.isFullScreen():
            if e.buttons() == Qt.LeftButton:
                dtx = e.x() - self.__prev_mpos[0]
                dty = e.y() - self.__prev_mpos[1]
                if self.__m_state == "WindowBar":
                    #print(dtx, dty, e.x(), e.y(), self.__prev_mpos[0], self.__prev_mpos[1])
                    self.setGeometry(self.x()+dtx, self.y()+dty, self.width(), self.height())
                elif self.__m_state == "Left":
                    self.setGeometry(self.x()+dtx, self.y(), self.width()-dtx, self.height())
                elif self.__m_state == "Right":
                    self.setGeometry(self.x(), self.y(), self.width()+dtx, self.height())
                    self.__prev_mpos[0] = e.x()
                    self.__prev_mpos[1] = e.y()
                elif self.__m_state == "Top":
                    self.setGeometry(self.x(), self.y()+dty, self.width(), self.height()-dty)
                elif self.__m_state == "Bottom":
                    self.setGeometry(self.x(), self.y(), self.width(), self.height()+dty)
                    self.__prev_mpos[0] = e.x()
                    self.__prev_mpos[1] = e.y()

        #self.checkMouseArea(e)
    
    def restoreCursor(self):
        while self.__app.overrideCursor() is not None:
            self.__app.restoreOverrideCursor()

    def checkMouseArea(self, e):
        pos = e.screenPos()
        position = QPointF(pos)
        
        appx = self.x()
        appy = self.y()
        appw = self.width()
        apph = self.height()

        rectTop = QRectF(appx + 9, appy, appw - 18, 7)
        rectBottom = QRectF(appx + 9, appy + apph - 7, appw - 18, 7)
        rectLeft = QRectF(appx, appy + 9, 7, apph - 18)
        rectRight = QRectF(appx + appw - 7, appy + 9, 7, apph - 18)
        rectWindowBar = QRectF(appx + 9, appy + 9, appw - 18, 30)

        if rectTop.contains(position):
            #self.__app.setOverrideCursor(self.__VER_CURSOR)
            return "Top"
        elif rectBottom.contains(position):
            #self.__app.setOverrideCursor(self.__VER_CURSOR)
            return "Bottom"
        elif rectLeft.contains(position):
            #self.__app.setOverrideCursor(self.__HOR_CURSOR)
            return "Left"
        elif rectRight.contains(position):
            #self.__app.setOverrideCursor(self.__HOR_CURSOR)
            return "Right"
        elif rectWindowBar.contains(position):
            #self.restoreCursor()
            return "WindowBar"
        else:
            #self.restoreCursor()
            return None

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        print("centered!")

    def __max_btn_action(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def __quit_btn_action(self):
        current_start_time = datetime.now()
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        with open(ROOT_DIR+'/fragma_time_rec.txt', 'w') as f:
            f.truncate(0) # emptying texts
            f.seek(0)
            f.write(str(current_start_time.strftime('%Y-%m-%d %H:%M:%S')))
        #lock.unlock()
        self.__stop_btn_action()
        self.__app.quit()
        #sys.exit()

    def __run_btn_action(self, **kwargs):
        print("Run Button Clicked.")

        recording = None
        if "recording" in kwargs:
            recording = kwargs["recording"]
            #print(kwargs["recording"])
        
        compile = False
        if "compile" in kwargs:
            compile = kwargs["compile"]
        
        # if recording == None:
        #     if self.__runner is not None:
        #         if self.__runner.paused == True:
        #             self.__runner.play()

        #print(self.__editor_tabs.findChildren(QsciScintilla))
        #print("TEST", len(self.__editor_tabs.findChildren(QLineEdit)))
        compressions = self.__editor_tabs.findChildren(QLineEdit, 'compression')
        for compression in compressions:
            if float(compression.text()) <= 0.1:
                compression.setText(str(0.1))
            elif float(compression.text()) > 1.0:
                compression.setText(str(1.0))

        repetitions = self.__editor_tabs.findChildren(QLineEdit, 'repetition')
        for repetition in repetitions:
            if int(repetition.text()) <= 1:
                repetition.setText(str(1))
            elif int(repetition.text()) > 50:
                repetition.setText(str(50))

        editors = self.__editor_tabs.findChildren(QsciScintilla)

        max_size = int(self.__mgl_max_size[0] / self.pd_div.getValue())
        window_dimension_changed = False
        if self.wdiv.getValue() < 2 or self.wdiv.getValue() > max_size or self.hdiv.getValue() < 2 or self.hdiv.getValue() > max_size:
            window_width = min(max(self.wdiv.getValue(), 2),max_size)
            window_height = min(max(self.hdiv.getValue(), 2),max_size)
            self.printConsole(f"Window dimension ({self.wdiv.getValue()},{self.hdiv.getValue()}) out of range.\nWindow dimension set to ({window_width},{window_height})")
            self.wdiv.lineEdit.setText(str(window_width))
            self.hdiv.lineEdit.setText(str(window_height))
            window_dimension_changed = True

        if self.__runner is None:
            self.__runner_window = self.__mgl_window_cls(
                title="Fragma",
                gl_version=(3, 3),
                size=(self.wdiv.getValue(), self.hdiv.getValue()),
                cursor=True,
                resizable=False,
                vsync=True
            )
            self.__runner_window.exit_key = self.__runner_window.keys.ESCAPE
            self.__runner = MGL_WINDOW(
                ctx=self.__runner_window.ctx, 
                wnd=self.__runner_window, 
                app=self, 
                pixel_density=compressions,#self.pd_div.getValue(),
                pass_repetitions=repetitions,
                fps=self.fps_div.getValue(),
                recording=recording,
                qfont=self.__myFont,
                compile=compile)
            self.__runner.__setup__(editors=editors)
        elif isinstance(self.__runner, MGL_WINDOW):
            self.__runner.close_window()
            self.__runner = None
            self.__run_btn_action(compile=compile)
    
    def setConsole(self, message):
         self.__console.setText(message)
         self.__console.verticalScrollBar().setValue(self.__console.verticalScrollBar().maximum())
             
    def printConsole(self, message):
        prev_txt = self.__console.toPlainText()
        new_txt = str(prev_txt) + "\n" + str(message)
        self.__console.setText(str(new_txt))
        self.__console.verticalScrollBar().setValue(self.__console.verticalScrollBar().maximum())
    
    def __build_btn_action(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        print(root_dir)
        
        #--> delete previously created .spec files
        dir_name = root_dir
        del_specs = os.listdir(dir_name)
        for item in del_specs:
            if item.endswith(".spec"):
                os.remove(os.path.join(dir_name, item))

        #--> delete previously create build files and txt files in data folder
        del_folder = root_dir+"/data"
        for item in os.listdir(del_folder):
            file_path = os.path.join(del_folder, item)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e)) 

        try:
            filename = self.__file_dialog.getSaveFileName(self, 'Save App', '', "")
            file_path = filename[0].rsplit(sep="/",maxsplit=1)[0]
            file_name = filename[0].rsplit(sep="/",maxsplit=1)[1]
            print(file_path, file_name)
            print("bulid test")
            
            self.__file_dialog.hide()

            compressions = self.__editor_tabs.findChildren(QLineEdit, 'compression')
            for compression in compressions:
                if float(compression.text()) <= 0.1:
                    compression.setText(str(0.1))
                elif float(compression.text()) > 1.0:
                    compression.setText(str(1.0))

            repetitions = self.__editor_tabs.findChildren(QLineEdit, 'repetition')
            for repetition in repetitions:
                if int(repetition.text()) <= 1:
                    repetition.setText(str(1))
                elif int(repetition.text()) > 50:
                    repetition.setText(str(50))
            
            max_size = int(self.__mgl_max_size[0] / self.pd_div.getValue())
            if self.wdiv.getValue() < 2 or self.wdiv.getValue() > max_size or self.hdiv.getValue() < 2 or self.hdiv.getValue() > max_size:
                window_width = min(max(self.wdiv.getValue(), 2),max_size)
                window_height = min(max(self.hdiv.getValue(), 2),max_size)
                self.printConsole(f"Window dimension ({self.wdiv.getValue()},{self.hdiv.getValue()}) out of range.\nWindow dimension set to ({window_width},{window_height})")
                self.wdiv.lineEdit.setText(str(window_width))
                self.hdiv.lineEdit.setText(str(window_height))

            texts = ""
            texts += str(self.fps_div.getValue()) + MARKER
            texts += str(self.wdiv.getValue()) + MARKER + str(self.hdiv.getValue()) + MARKER
            texts += "empty" + MARKER
            editors = self.__editor_tabs.findChildren(QsciScintilla)
            for (i, editor) in enumerate(editors):
                if editor.parent != None:
                    texts += str(editor.objectName()) + MARKER
                    texts += compressions[i].text() + MARKER
                    texts += repetitions[i].text() + MARKER
                    texts += editor.text() + MARKER
            
            if os.path.exists(root_dir+"/data"):
                pass
            else:
                os.makedirs(root_dir+"/data")

            with open(os.path.join(root_dir+"/data","build_temp.txt"), "w") as txtfile:
                txtfile.write(texts)

            #print(os.path.abspath(self.__appctx.get_resource('icon.ico')))
            
            work_path = "--workpath="+root_dir+"/data"
            spec_path = "--specpath="+root_dir
            dist_path = "--distpath="+file_path
            app_name = "--name="+file_name
            app_icon = "--icon="+os.path.abspath(self.__appctx.get_resource('icon.ico'))
            app_data = "--add-data="+root_dir+"/data:data"
            build_script = os.path.abspath(self.__appctx.get_resource('builder.py'))
            
            #Broken Pipe error when freezed
            # build_process = [
            #     build_script, 
            #     #'--onefile', 
            #     '--windowed',
            #     #'--noconsole',
            #     '--clean', 
            #     '-y',
            #     #work_path, 
            #     dist_path, spec_path,
            #     app_name, app_icon, app_data]
            
            # PyInstaller.__main__.run(build_process,)

            build_process = [
                'pyinstaller', 
                #'--onefile', 
                '--windowed',
                #'--noconsole',
                '--clean', 
                '-y',
                work_path, 
                dist_path, spec_path,
                app_name, app_icon, app_data,
                build_script]
            subprocess.run(build_process,stdout=subprocess.PIPE).stdout.decode('utf-8')
        except Exception as e:
            self.printConsole(str(e))
            print("build failed", e)

    def __compile_btn_action(self):
        self.__run_btn_action(compile=True)
    
    def __stop_btn_action(self):
        self.setConsole("")
        if isinstance(self.__runner, MGL_WINDOW):
            self.__runner.close_window()
            self.__runner = None  

    def __rec_btn_action(self):
        print("record button clicked!")
        self.__stop_btn_action()
        #custom qdialog popup
        if self.__rec_popup.exec():
            duration = self.__rec_popup.getValue()
            
            try:
                filename = self.__file_dialog.getSaveFileName(self, 'Save File', '', "(*.mp4)")
                print(filename[0])
                self.__run_btn_action(recording={
                    "filename": filename[0],
                    "duration": duration
                    #"progress": self.__rec_progress_popup
                })

                self.__stop_btn_action()
            except:
                print("recording error")
        else:
            print("recording canceled")
        
        # duration, ok = QInputDialog.getDouble(self, 'Record Video', 'Recording Duration:', flags=Qt.FramelessWindowHint)
        # if ok:
        #     print(float(duration))
        #     filename = self.__file_dialog.getSaveFileName(self, '', '', "(*.mp4)")
        #     print(filename)
        #     self.__run_btn_action(recording={
        #         "filename": filename[0],
        #         "duration": duration
        #     })
        # else:
        #     print("recording canceled")

    def __capture_btn_action(self):
        print("capture button clicked!")
        if self.__runner is not None:
            filename = self.__file_dialog.getSaveFileName(self, '', '', "(*.png)")
            self.__runner.capture(filename[0])
            self.__stop_btn_action()

    def __set_uniform_btns(self):
        editors = self.__editor_tabs.findChildren(QsciScintilla)
        
        buffer_btn_index = self.__uniform_panel.count() - 1
        print("buffer buttons length", buffer_btn_index)
        while buffer_btn_index >= 0:
            buffer_btn = self.__uniform_panel.itemAt(buffer_btn_index).widget()
            if buffer_btn is not None:
                try:
                    buffer_btn.clicked.disconnect(partial(self.__uniform_btn_action, buffer_btn))
                except:
                    pass
                buffer_btn.setParent(None)
                buffer_btn.deleteLater()
            buffer_btn_index -=1

        for editor in reversed(editors):
            buffer_button_name = "buffer_"+str(editor.objectName())
            buffer_button_id = str(editor.objectName())
            buffer_button = UniformButton(title=buffer_button_name, name='buffer', font=self.__myFont, id=buffer_button_id)
            buffer_button.clicked.connect(partial(self.__uniform_btn_action, buffer_button))
            self.__uniform_panel.insertWidget(self.__uniform_panel.count() - 1, buffer_button)

    def __uniform_btn_action(self, button):
        print("uniform button clicked", button.ID)

        editors = self.__editor_tabs.findChildren(QsciScintilla)
        active_editor = editors[len(editors)-1]
        active_editor_text = active_editor.text()
        uniform_code = "uniform sampler2D buffer_" + str(button.ID) + ";"

        if uniform_code in active_editor_text or button.ID == active_editor.objectName():
            print("unable to add uniform", button.ID, active_editor.objectName())
        else:
            if button.ID != active_editor.objectName():
                split_text = active_editor_text.split('uniform', 1)
                active_editor_text = ""
                for (i, text) in enumerate(split_text):
                    if i == 0:
                        active_editor_text += text + uniform_code + " \n" + "uniform"
                    else:
                        active_editor_text += text
                
                active_editor.setText(active_editor_text)


    def __remove_editor_action(self, index):
        print("remove editor", index)
        #self.__editor_tabs.removeTab(index)
        tab = self.__editor_tabs.widget(index)
        #--> check if tab exists before using it
        if tab is not None:
            print("deleting tab")
            editors = tab.findChildren(QsciScintilla)
            for editor in editors:
                editor.setParent(None)
                editor.deleteLater()

            tab.setParent(None)
            tab.deleteLater()
            if self.__editor_tabs.count() == 0:
                self.__editor_tab_count = 0

            # if self.__editor_tabs.count() > 1:
            #     print("remove editor", index)
            #     self.__editor_tabs.removeTab(index)
            # else:
            #     print("just one left")
        
        self.__set_uniform_btns()

    def __new_editor_action(self, **kwargs):
        print("New Editor Button Clicked.")
        # Make instance of QsciScintilla class!
        if self.__editor_tabs.count() < 5:
            editor_frame = QFrame()
            editor_frame.setObjectName("editor_frame")
            
            editor_layout = QVBoxLayout()
            editor_layout.setContentsMargins(0,0,0,0)

            pass_panel = QHBoxLayout()
            pass_compression_input = LabelledFloatField('', self.__myFont, 1.0)
            pass_compression_input.lineEdit.setObjectName('compression')

            pass_repetition_input = LabelledIntField('', self.__myFont, 1)
            pass_repetition_input.lineEdit.setObjectName('repetition')
            pass_repetition_input.lineEdit.setFixedWidth(50)
            #self.__editor_compressions.append(pass_compression_input)
            
            pass_panel.addSpacing(13)
            pass_panel.addWidget(pass_compression_input.lineEdit)
            #pass_panel.addLayout(pass_compression_input.layout)
            pass_panel.addSpacing(0)
            pass_panel.addWidget(pass_repetition_input.lineEdit)
            pass_panel.addStretch(9)
            
            editor_layout.addLayout(pass_panel)
            
            editor = QsciScintilla()
            self.__editor_tab_count += 1
            editor.setObjectName(str(self.__editor_tab_count))
            
            if "text" in kwargs:
                editor_text = kwargs["text"]
                #editor_text = re.sub("buffer_.","buffer_"+str(editor.objectName),editor_text)
                editor.setText(editor_text)
            else:
                editor.setText(default_code)

            editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)

            editor.setMarginType(0, QsciScintilla.NumberMargin)
            editor.setMarginWidth(0, "000")
            editor.setMarginsForegroundColor(QColor("#8e8e8e"))
            editor.setMarginsBackgroundColor(QColor("#ffffff"))
            editor.setMarginsFont(self.__myFont)

            #editor.setWrapMode(QsciScintilla.WrapWord)
            #editor.setWrapIndentMode(QsciScintilla.WrapIndentSame)
            
            #editor.setIndentationGuides(True)
            editor.setTabWidth(4)
            editor.setIndentationsUseTabs(False)
            #editor.setAutoIndent(True)

            editor.setEolMode(QsciScintilla.EolUnix)
            editor.setEolVisibility(False)

            editor.setCaretLineVisible(True)
            editor.setLexer(None)
            editor.setUtf8(True)  # Set encoding to UTF-8
            editor.setFont(self.__myFont)  # Will be overridden by lexer!
            #self.__editors.append(editor)

            # -------------------------------- #
            #          Install lexer           #
            # -------------------------------- #
            self.__lexer = GLSLLexer(editor, self.__myFont)
            editor.setLexer(self.__lexer)

            # ! Add editor to layout !
            editor_layout.addWidget(editor)
            editor_frame.setLayout(editor_layout)
            #self.__editors_layout.addWidget(editor_frame)
            
            self.__editor_tabs.addTab(editor_frame, str(self.__editor_tab_count) + "")
            #self.__editors_layout.addWidget(editor)
        else:
            print("too many tabs")

        self.__set_uniform_btns()
        

    

        
    ''''''


''' End Class '''

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(ROOT_DIR)
lock = FLOCK(ROOT_DIR+'/fragma.lock', True).acquire()
# lock = QLockFile(ROOT_DIR + '/fragma.lock')
# lock.setStaleLockTime(5000)

current_start_time = datetime.now()
#now.strftime('%Y-%m-%d %H:%M:%S')
minimum_restart_time = 2
too_soon_to_restart = False

try:
    with open(ROOT_DIR+'/fragma_time_rec.txt', 'r+') as f:
        f_data = f.read()
        print(f_data)
        try:
            previous_start_time = datetime.strptime(f_data, '%Y-%m-%d %H:%M:%S')
            time_taken_to_restart = current_start_time - previous_start_time
            print(time_taken_to_restart.seconds)
            if int(time_taken_to_restart.seconds) < minimum_restart_time:
                print('too soon to restart')
                too_soon_to_restart = True
        except Exception as e:
            print("no start time record or something wrong", e)
        f.truncate(0) # emptying texts
        f.seek(0) # needed when rewriting after emptying
        f.write(str(current_start_time.strftime('%Y-%m-%d %H:%M:%S')))
except:
    with open(ROOT_DIR+'/fragma_time_rec.txt', 'w') as f:
        f.truncate(0) # emptying texts
        f.seek(0)
        f.write(str(current_start_time.strftime('%Y-%m-%d %H:%M:%S')))

if lock and too_soon_to_restart == False:
#if lock.tryLock(100):
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    if __name__ == '__main__':
        appctxt = CustomAppCTX()       # 1. Instantiate ApplicationContext
        app = appctxt.app
        print(f"Using AA_EnableHighDpiScaling > {QApplication.testAttribute(Qt.AA_EnableHighDpiScaling)}")
        print(f"Using AA_UseHighDpiPixmaps    > {QApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)}")
        
        myGUI = CustomMainWindow(appctxt, app)

        exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
        sys.exit(exit_code)
else:
    print("locked!")
    sys.exit()

# if __name__ == '__main__':
#     appctxt = CustomAppCTX()       # 1. Instantiate ApplicationContext
#     lock = FLOCK(appctxt.get_resource('fragma.lock'), True).acquire()
#     if lock:
#         app = appctxt.app
#         print(f"Using AA_EnableHighDpiScaling > {QApplication.testAttribute(Qt.AA_EnableHighDpiScaling)}")
#         print(f"Using AA_UseHighDpiPixmaps    > {QApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)}")
        
#         myGUI = CustomMainWindow(appctxt, app)

#         exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
#         sys.exit(exit_code)
#     else:
#         print("locked!")
#         sys.exit()
        