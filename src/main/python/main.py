from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import moderngl
import moderngl_window as mglw
import moderngl_window.context.pyglet
import glcontext
from __lexer import GLSLLexer
from __mgl_window import MGL_WINDOW
from __labeled_int_field import LabelledIntField
from __labeled_float_field import LabelledFloatField

default_code = '''#version 330
out vec4 outputColor;
in vec2 UV;

uniform sampler2D bckbuffer;
uniform vec2 resolution;
uniform vec2 mouse;
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

        self.__app.setStyleSheet(Path(self.__appctx.get_resource('__style.qss')).read_text())

        # Window setup
        # --------------

        # Define the geometry of the main window
        #self.setGeometry(300, 300, 800, 600)
        self.resize(800, 650)
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
        self.__new_editor_btn = QPushButton("Add Pass")
        #self.__new_editor_btn.setFixedWidth(50)
        #self.__new_editor_btn.setFixedHeight(50)
        self.__new_editor_btn.clicked.connect(self.__new_editor_action)
        self.__new_editor_btn.setFont(self.__myFont)
        con_layout.addWidget(self.__new_editor_btn)
        con_layout.addStretch(8)

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
        self.__editors_layout = QVBoxLayout()
        self.__editor_tabs = QTabWidget()
        self.__editors_layout.setObjectName("editor_layout")
        self.__editors_layout.addWidget(self.__editor_tabs)
        self.__lyt.addLayout(self.__editors_layout)
        self.__editors = []
        self.__editor_compressions = []
        #
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
    def saveProject(self):
        print("save file")
        texts = ""
        for editor in self.__editors:
            print(editor.text())
            texts += editor.text() + MARKER

        print(texts)
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
        print(file_data)

        fragments = file_data.split(MARKER)
        for index, editor in enumerate(self.__editors):
            if index < len(fragments):
                editor.setText(fragments[index])

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
        sys.exit()

    def __run_btn_action(self):
        print("Run Button Clicked.")
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
                title="Sketch",
                gl_version=(3, 3),
                size=(self.wdiv.getValue(), self.hdiv.getValue()),
                cursor=True,
                resizable=False,
                vsync=True
            )
            self.__runner_window.exit_key = self.__runner_window.keys.ESCAPE
            self.__runner = MGL_WINDOW(ctx=self.__runner_window.ctx, wnd=self.__runner_window, app=self, pixel_density=self.pd_div.getValue(), fps=self.fps_div.getValue())
            self.__runner.__setup__(editors=self.__editors)
        elif isinstance(self.__runner, MGL_WINDOW):
            self.__runner.close_window()
            self.__runner = None
            self.__run_btn_action()
    
    def setConsole(self, message):
         self.__console.setText(message)
             
    def printConsole(self, message):
        prev_txt = self.__console.toPlainText()
        new_txt = str(prev_txt) + "\n" + str(message)
        self.__console.setText(str(new_txt))

    def __stop_btn_action(self):
        self.setConsole("")
        if isinstance(self.__runner, MGL_WINDOW):
            self.__runner.close_window()
            self.__runner = None  
    
    def __new_editor_action(self):
        print("New Editor Button Clicked.")
        # Make instance of QsciScintilla class!
        
        editor_frame = QFrame()
        editor_frame.setObjectName("editor_frame")
        
        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0,0,0,0)

        pass_panel = QHBoxLayout()
        pass_compression_input = LabelledFloatField('Compression', self.__myFont, 1.0)
        self.__editor_compressions.append(pass_compression_input)
        
        pass_panel.addWidget(pass_compression_input.lineEdit)

        editor_layout.addLayout(pass_panel)
        
        editor = QsciScintilla()
        
        editor.setText(default_code)
        
        editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        editor.setMarginType(0, QsciScintilla.NumberMargin)
        editor.setMarginWidth(0, "000")
        editor.setMarginsForegroundColor(QColor("#8e8e8e"))
        editor.setMarginsBackgroundColor(QColor("#ffffff"))
        editor.setMarginsFont(self.__myFont)

        editor.setWrapMode(QsciScintilla.WrapWord)
        editor.setWrapIndentMode(QsciScintilla.WrapIndentSame)
        
        editor.setIndentationGuides(True)
        editor.setTabWidth(4)
        editor.setIndentationsUseTabs(False)
        editor.setAutoIndent(True)

        editor.setEolMode(QsciScintilla.EolUnix)
        editor.setEolVisibility(False)

        editor.setCaretLineVisible(True)
        editor.setLexer(None)
        editor.setUtf8(True)  # Set encoding to UTF-8
        editor.setFont(self.__myFont)  # Will be overridden by lexer!
        self.__editors.append(editor)

        # -------------------------------- #
        #          Install lexer           #
        # -------------------------------- #
        self.__lexer = GLSLLexer(editor, self.__myFont)
        editor.setLexer(self.__lexer)

         # ! Add editor to layout !
        editor_layout.addWidget(editor)
        editor_frame.setLayout(editor_layout)
        #self.__editors_layout.addWidget(editor_frame)
        self.__editor_tabs.addTab(editor_frame, "")
        #self.__editors_layout.addWidget(editor)

        
    ''''''


''' End Class '''

if __name__ == '__main__':
    appctxt = CustomAppCTX()       # 1. Instantiate ApplicationContext
    app = appctxt.app
    myGUI = CustomMainWindow(appctxt, app)

    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)