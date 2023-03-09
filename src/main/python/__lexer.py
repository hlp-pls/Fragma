import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import re

class GLSLLexer(QsciLexerCustom):

    def __init__(self, parent, font):
        super(GLSLLexer, self).__init__(parent)
        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#000000"))
        self.setDefaultPaper(QColor("#ffffff"))
        #

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#000000"), 0)   # Style 0: black
        self.setColor(QColor("#7f0000"), 1)   # Style 1: red
        self.setColor(QColor("#ffbf55"), 2)   # Style 2: orange
        self.setColor(QColor("#007f00"), 3)   # Style 3: green
        self.setColor(QColor("#007f00"), 4)   # Style 4: green
        self.setColor(QColor("#fa55fa"), 5)   # Style 5: pink
        self.setColor(QColor("#00bfff"), 6)   # Style 6: blue
       
        self.setColor(QColor("#000000"), 10)
        
        # Initialize paper colors per style
        # ----------------------------------
        # self.setPaper(QColor("#ffffffff"), 0)   # Style 0: white
        # self.setPaper(QColor("#ffffffff"), 1)   # Style 1: white
        # self.setPaper(QColor("#ffffffff"), 2)   # Style 2: white
        # self.setPaper(QColor("#ffffffff"), 3)   # Style 3: white

        # Initialize fonts per style
        # ---------------------------
        self.lexer_font = QFont("D2Coding", 16)
        self.lexer_font_lh = QFont("D2Coding", 18)
        self.setFont(self.lexer_font, 0) 
        self.setFont(self.lexer_font, 1)
        self.setFont(self.lexer_font, 2)
        self.setFont(self.lexer_font, 3)
        self.setFont(self.lexer_font, 4)
        self.setFont(self.lexer_font, 5)

        self.setFont(self.lexer_font_lh, 10)
        #self.setDefaultFont(self.lexer_font_lh)


    def language(self):
        return "GLSL"

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        elif style == 4:
            return "myStyle_4"
        elif style == 5:
            return "myStyle_5"
        elif style == 6:
            return "myStyle_6"
        elif style == 10:
            return "myStyle_10"
        ###
        return ""

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]
        #print(text)

        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[/]{2,}|[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        # checking singleline will cause error
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = True


        singleline_comm_flag = False
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                self.setStyling(token[1], 3)
                if token[0] == "*/":
                    multiline_comm_flag = False
            elif singleline_comm_flag:
                self.setStyling(token[1], 4)
                if "\n" in token[0]:
                    singleline_comm_flag = False
            else:
                if token[0] in []:
                    self.setStyling(token[1], 1)
                elif token[0] in ["(", ")", "{", "}", "[", "]"]:
                    self.setStyling(token[1], 6)
                elif token[0] == "/*":
                    # Green style
                    multiline_comm_flag = True
                    self.setStyling(token[1], 3)
                elif token[0] == "//":
                    # Green style
                    singleline_comm_flag = True
                    self.setStyling(token[1], 4)
                elif token[0] in ["vec4", "vec3", "vec2", "mat2", "mat3", "mat4", "float", "int", "void", "in", "out", "uniform", "sampler2D", "const", "for", "return", "if", "bool"]:
                    self.setStyling(token[1], 2)
                elif token[0] in ["bckbuffer", "mouse", "time", "resolution", "UV", "outputColor", "mousedt", "mousedown"]:
                    self.setStyling(token[1], 5)
                elif "buffer_" in token[0]:
                    self.setStyling(token[1], 5)
                elif "\n" in token[0]:
                    self.setStyling(token[1], 10)
                else:
                    # Default style
                    self.setStyling(token[1], 0)
            
            #print(singleline_comm_flag)