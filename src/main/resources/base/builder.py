#--> imports for mgl packaging
import moderngl
import moderngl_window as mglw
import moderngl_window.context.pyglet
import glcontext

#--> custom moderngl class
from __framebuffer import MGL_FBO

import os
import time
#import numpy as np
#import sys

MARKER = "/**========END_OF_FRAGMENT========**/"

class FragmaApp(mglw.WindowConfig):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        self.ctx = kwargs["ctx"]
        self.size = kwargs["wnd"].size
        self.window = kwargs["wnd"]
        self.timer = mglw.Timer()
        self.timer.start()

        self.pixel_density = kwargs["pixel_density"]
        self.pass_repetitions = kwargs["pass_repetitions"]

        self.editors = kwargs["editors"]
        self.editor_names = kwargs["editor_names"]

        self.timer = mglw.Timer()
        self.timer.start()
        self.prev_time = 0.0

        self.fps = kwargs["fps"]
        self.fps = max(self.fps,1)
        self.fps_limit = 1 / self.fps

        self.__fbos = []
        
        self.setup()

    def resize(self, width: int, height: int):
        self.size = self.window.size
        print("resize!!", self.size)
        # for __fbo in self.__fbos:
        #     if isinstance(__fbo, MGL_FBO):
        #         __fbo.resize(float(width), float(height))
                
        return super().resize(width, height)

    def setup(self):
        self.timer.time = 0.0
        self.prev_time = 0.0
        print("setup starting...")
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.release()
                __fbo = None

        self.__fbos = []
        has_exception = False
        for (i, editor) in enumerate(self.editors):
            print("!",self.pixel_density[i],self.pass_repetitions[i],self.size)
            try:
                new_fbo = MGL_FBO(
                    ctx = self.ctx, 
                    size = (int(self.size[0]*2*float(self.pixel_density[i])),int(self.size[1]*2*float(self.pixel_density[i]))), 
                    fragment_shader = editor, 
                    enable_backbuffer = True,
                    window = self.window,
                    name="buffer_"+editor_names[i],
                    pass_repetition=int(self.pass_repetitions[i]),
                    pixel_density=float(self.pixel_density[i]))
                self.__fbos.append(new_fbo)
            except Exception as e:
                has_exception = True
                e_mssg = str(e)
                e_mssg = e_mssg.split("===============")[1]
                print(e_mssg)
        
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

            self.do_render()
        else:
            self.window.close()
    
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

    def do_render(self):
        while not self.window.is_closing:
            time.sleep(self.fps_limit)

            current_time = self.timer.time
            time_took_to_render = current_time - self.prev_time

            if time_took_to_render >= self.fps_limit:
                self.window.clear()
                if self.has_set == True:
                    for i, __fbo in enumerate(self.__fbos):
                        if isinstance(__fbo, MGL_FBO):
                            if i == len(self.__fbos) - 1:
                                __fbo.render(time=current_time, render_to_window=True)
                            else:
                                __fbo.render(time=current_time, render_to_window=False)
                self.window.swap_buffers()
                self.prev_time = current_time



root_dir = os.path.dirname(os.path.abspath(__file__))
data = None
with open(os.path.join(root_dir+"/data","build_temp.txt"), "r") as txtfile:
    data = txtfile.read()
    print(data)

data_blocks = data.split(sep=MARKER)

compressions = []
repetitions = []
editors = []
editor_names = []

for (i, txt) in enumerate(data_blocks):
    if i > 3:
        if i % 4 == 0:
            editor_names.append(txt)
        elif i % 4 == 1:
            compressions.append(txt)
        elif i % 4 == 2:
            repetitions.append(txt)
        elif i % 4 == 3:
            editors.append(txt)

print(data_blocks[0],data_blocks[1],data_blocks[2],compressions,repetitions,editor_names,editors)

mgl_window_str = 'moderngl_window.context.pyglet.Window'
mgl_window_cls = mglw.get_window_cls(mgl_window_str)
fragma_wnd = mgl_window_cls(
    title="Fragma",
    gl_version=(3, 3),
    size=(int(data_blocks[1]), int(data_blocks[2])),
    cursor=True,
    resizable=True,
    fullscreen=False,
    vsync=True
)
fragma_ctx = moderngl.create_context(standalone=False, require=(330))
fragma_app = FragmaApp(
    ctx=fragma_ctx, 
    wnd=fragma_wnd,
    pixel_density=compressions,
    pass_repetitions=repetitions,
    fps=float(data_blocks[0]),
    editors=editors,
    editor_names=editor_names
)