from __framebuffer import MGL_FBO
import moderngl_window as mglw
import time

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
        self.pixel_density = kwargs["pixel_density"]
        self.timer = mglw.Timer()
        self.timer.start()
        self.fps = kwargs["fps"]
        self.fps_limit = 1 / self.fps
        self.has_closed = False
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
                    size = (int(self.size[0]*float(self.pixel_density[i].text())),int(self.size[1]*float(self.pixel_density[i].text()))), 
                    fragment_shader = editor.text(), 
                    enable_backbuffer = True,
                    window = self.window,
                    name="buffer_"+str(editor.objectName()))
                self.__fbos.append(new_fbo)
                #self.app.clearConsole()
            except Exception as e:
                has_exception = True
                e_mssg = str(e)
                e_mssg = e_mssg.split("===============")[1]
                print(e_mssg)
                self.app.printConsole(e_mssg)
        
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

    def close_window(self):
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                __fbo.release()
        self.window.close()
        self.ctx.release()

    def mouse_position_event(self, x, y, dx, dy):
        for __fbo in self.__fbos:
            if isinstance(__fbo, MGL_FBO):
                mx = x / self.size[0]
                my = 1.0 - y / self.size[1]
                #print(x, y)
                __fbo.set_uniform("mouse", [mx, my])   

    def close(self):
        #print(self.window.is_closing)
        duration = self.timer.time
        print(self.window.frames / duration)
        if self.window.is_closing == False:
            self.window.close()

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
                                __fbo.render(time=self.timer.time, render_to_window=True)
                            else:
                                __fbo.render(time=self.timer.time, render_to_window=False)
                self.window.swap_buffers()
                self.prev_time = current_time   