from __framebuffer import MGL_FBO
import moderngl_window as mglw
import moderngl_window.screenshot
import time
import numpy as np
import moviepy.editor as mvp
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from __popup import CustomDialog

class MGL_WINDOW(mglw.WindowConfig):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__kwargs = kwargs
        print(self.__kwargs)
        self.__fbos = []
        self.has_set = False
        self.ctx = kwargs["ctx"]
        self.size = kwargs["wnd"].size
        self.window = kwargs["wnd"]
        self.app = kwargs["app"]
        self.qfont = kwargs["qfont"]
        self.pixel_density = kwargs["pixel_density"]
        self.pass_repetitions = kwargs["pass_repetitions"]
        self.timer = mglw.Timer()
        self.timer.start()
        self.fps = kwargs["fps"]
        self.fps_limit = 1 / self.fps
        self.has_closed = False
        self.recording = kwargs["recording"]

        #self.__stop_btn_action = self.app.__stop_btn_action
        #print("app", kwargs["app"].__stop_btn_action)
        #pyglet.app.run()
        #self.window = pyglet.app.window
        print(self.window)
        

    def __setup__(self, editors):
        self.timer.time = 0.0
        self.prev_time = 0.0
        print("setup starting...")
        self.time = 0.0
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.release()
                __fbo = None

        self.__fbos = []
        #print(self.ctx)
        print("EDITORS LENGTH", len(editors))
        has_exception = False
        for i, editor in enumerate(editors):
            print(editor.text(), "PD!!!",self.pixel_density[i].text())
            try:
                new_fbo = MGL_FBO(
                    ctx = self.ctx, 
                    size = (int(self.size[0]*2*float(self.pixel_density[i].text())),int(self.size[1]*2*float(self.pixel_density[i].text()))), 
                    fragment_shader = editor.text(), 
                    enable_backbuffer = True,
                    window = self.window,
                    name="buffer_"+str(editor.objectName()),
                    pass_repetition=int(self.pass_repetitions[i].text()))
                self.__fbos.append(new_fbo)
                #self.app.clearConsole()
                self.app.setConsole("")
            except Exception as e:
                has_exception = True
                e_mssg = str(e)
                e_mssg = e_mssg.split("===============")[1]
                print(e_mssg)
                self.app.setConsole(e_mssg)
        
        if has_exception == False:
            print(len(self.__fbos))
            self.has_set = True
            print("setup complete")
            print(self.has_set)

            # set each pass texture as buffer in each other passes
            for fbo in self.__fbos:
                for _fbo in self.__fbos:
                    if fbo.pass_name != _fbo.pass_name:
                        fbo.set_texture_uniform_auto(_fbo.texture, _fbo.pass_name)

            if self.recording is None:
                self.do_render(0.0)
            else:
                clip = mvp.VideoClip(self.do_render, duration=self.recording["duration"])
                clip.write_videofile(self.recording["filename"], fps=self.fps)
                print("recording completed")
                # --> error : window opens for a second time
                # use lock file --> done
                # --> checks closed time and stops restarting if time elapsed is shorter than a given time
                record_done_mssg = CustomDialog(
                    parent=self.app, 
                    flags=Qt.FramelessWindowHint, 
                    title="record", 
                    message="Recording finished!",
                    font=self.qfont,
                    type="MESSAGE"
                )
                record_done_mssg.exec()
        else:
            self.window.close()

    def close_window(self):
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.release()
        self.window.close()
        self.ctx.release()

    def capture(self, path):
        moderngl_window.screenshot.create(source=self.__fbos[len(self.__fbos)-1].fbo,name=path)

    def mouse_position_event(self, x, y, dx, dy):
        mx = x / self.size[0]
        my = 1.0 - y / self.size[1]
        #dtx =  dx / self.size[0]
        #dty = 1.0 - dy / self.size[1]
        #print(dtx, dty)
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                #print(x, y)
                __fbo.set_uniform("mouse", [mx, my])
                __fbo.set_uniform("mousedt", [0.0, 0.0])

    def mouse_drag_event(self, x, y, dx, dy):
        mx = x / self.size[0]
        my = 1.0 - y / self.size[1]
        dtx = dx / self.size[0]
        dty = - dy / self.size[1]
        #print(dtx, dty)
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                #print(x, y)
                __fbo.set_uniform("mouse", [mx, my])
                __fbo.set_uniform("mousedt", [dtx, dty])

    def mouse_release_event(self, x, y, button):
        print("mouse released!")
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.set_uniform("mousedown", False)
    
    def mouse_press_event(self, x, y, button):
        print("mouse pressed!")
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.set_uniform("mousedown", True)

    def close(self):
        #print(self.window.is_closing)
        duration = self.timer.time
        print(self.window.frames / duration)
        if self.window.is_closing == False:
            self.window.close()

    def do_render(self, t):
        while not self.window.is_closing:

            if self.recording is None:
                time.sleep(self.fps_limit)
            #else:
                #self.timer.time = t
            
            if self.recording is None:
                current_time = self.timer.time
            else:
                current_time = t
            
            if self.recording is None:
                time_took_to_render = current_time - self.prev_time
            else:
                time_took_to_render = self.fps_limit

            if time_took_to_render >= self.fps_limit:
                self.window.clear()
                last_fbo_ref = None
                if self.has_set == True:
                    for i, __fbo in enumerate(self.__fbos):
                        if isinstance(__fbo, MGL_FBO):
                            if i == len(self.__fbos) - 1:
                                last_fbo_ref = __fbo
                                __fbo.render(time=current_time, render_to_window=True)
                            else:
                                __fbo.render(time=current_time, render_to_window=False)
                self.window.swap_buffers()
                self.prev_time = current_time

                if self.recording is not None:
                    img_buf = last_fbo_ref.fbo.read()
                    img_width = last_fbo_ref.size[0]
                    img_height = last_fbo_ref.size[1]
                    img = np.frombuffer(img_buf, np.uint8).reshape(img_height, img_width, 3)[::-1]
                    return img   