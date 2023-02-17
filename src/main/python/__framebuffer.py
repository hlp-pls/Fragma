import numpy as np
from PIL import Image
from array import array
import moderngl

#--> WARNING : when uniforms are unused inside the shader program, an error occurs
#https://github.com/moderngl/moderngl/issues/149  
class FakeUniform:
    value = None

class MGL_FBO:

    quad_vertex_shader = '''
    #version 330
    in vec2 in_vert;
    in vec2 in_uv;
    out vec2 UV;
    void main() {
        gl_Position = vec4(in_vert, .0, 1.0);
        UV = in_uv;
    }
    '''
    copier_fragment_shader = '''
    #version 330
    out vec4 outputColor;
    in vec2 UV;

    uniform sampler2D copy_target;

    void main() {
        vec4 copy = texture(copy_target,UV);
        outputColor = copy;
    }
    '''

    def __init__(self,**kwargs):
        self.kwargs = kwargs

        self.ctx = kwargs["ctx"]
        self.size = kwargs["size"]
        self.enable_backbuffer = kwargs["enable_backbuffer"]
        self.window = kwargs["window"]
        #print(self.window)

        self.pass_name = kwargs["name"]
    
        self.texture = self.ctx.texture(self.size, components=4, dtype="f4")
        self.fbo = self.ctx.framebuffer(self.texture)
        self.prog = self.ctx.program(vertex_shader=self.quad_vertex_shader,fragment_shader=kwargs["fragment_shader"])
    

        # vertex_data = np.array([
        #     # x,    y,   z,    u,   v
        #     -1.0, -1.0, 0.0,  0.0, 0.0, #upper left
        #     +1.0, -1.0, 0.0,  1.0, 0.0,
        #     -1.0, +1.0, 0.0,  0.0, 1.0,
        #     +1.0, +1.0, 0.0,  1.0, 1.0,
        # ]).astype(np.float32)

        # content = [(
        #     self.ctx.buffer(vertex_data),
        #     '3f 2f',
        #     'in_vert', 'in_uv'
        # )]
        #self.vao = self.ctx.vertex_array(self.prog, content)

        self.vertices = self.ctx.buffer(
        array(
            'f',
            [
            # Triangle strip creating a fullscreen quad
            # x, y, u, v
            -1,  1, 0, 1,  # upper left
            -1, -1, 0, 0, # lower left
            1,  1, 1, 1, # upper right
            1, -1, 1, 0, # lower right
            ]
        )
        )
        self.content = [(self.vertices, '2f 2f', 'in_vert', 'in_uv'),]
        self.vao = self.ctx.vertex_array(self.prog,self.content)

        self.rndr_prog = self.ctx.program(vertex_shader=self.quad_vertex_shader, fragment_shader=self.copier_fragment_shader)
        self.rndr_vao = self.ctx.vertex_array(self.rndr_prog,self.content)
        self.rndr_target_uniform = self.rndr_prog.get('copy_target', FakeUniform())
        self.rndr_target_uniform.value = 0

        #https://github.com/moderngl/moderngl/issues/459
        #https://realpython.com/python-keyerror/
        self.time = self.prog.get('time', FakeUniform())
        self.resolution = self.prog.get('resolution', FakeUniform())

        if self.resolution:
            self.resolution.value = self.size
        else:
            print(f'unable to set resolution uniform resolution')

        if self.enable_backbuffer == True:
            self.bck_texture = self.ctx.texture(self.size, components=4, dtype="f4")
            self.bck_fbo = self.ctx.framebuffer(self.bck_texture)
            self.bck_prog = self.ctx.program(vertex_shader=self.quad_vertex_shader, fragment_shader=self.copier_fragment_shader)
            self.bck_vao = self.ctx.vertex_array(self.bck_prog, self.content)

            self.backbuffer_uniform = self.prog.get('backbuffer', FakeUniform())
            self.copy_target_uniform = self.bck_prog.get('copy_target', FakeUniform())

            self.backbuffer_uniform.value = 0
            self.copy_target_uniform.value = 0
            
            
    
        self.textures = {}
        self.texture_buffers = {}
        self.texture_uniforms = {}
        self.init_texture = None
        self.texture_counter = 3

  
    def set_uniform(self, name, value):
        uniform = self.prog.get(name, FakeUniform())
        uniform.value = value
  
    def set_texture_uniform(self, texture, name, id):
        if name not in self.textures:
            self.texture_uniforms[name] = self.prog.get(name, FakeUniform())
            self.textures[name] = texture
        self.texture_uniforms[name].value = id
    
    def set_texture_uniform_auto(self, texture, name):
        if name not in self.textures:
            self.texture_uniforms[name] = self.prog.get(name, FakeUniform())
            self.textures[name] = texture
        self.texture_uniforms[name].value = self.texture_counter
        self.texture_counter += 1

    #https://stackoverflow.com/questions/64074990/using-pillow-image-tobytes-to-flip-the-image-and-swap-the-color-channels
    def set_init_img(self, path):
        im = Image.open(path)
        im_WIDTH, im_HEIGHT, im_DATA = im.size[0], im.size[1], im.convert('RGBA').tobytes("raw", "RGBA", 0, -1)
        self.init_texture = self.ctx.texture((im.size[0], im.size[1]), components=4, data=im_DATA)
        self.init_texture_uniform = self.prog.get('init_texture', FakeUniform())
        self.init_texture_uniform.value = 1
    
    def clear(self):
        self.fbo.clear()
        if self.bck_fbo:
            self.bck_fbo.clear()
    
    def release(self):
        self.fbo.release()
        self.bck_fbo.release()

    def extract_img(self, path):
        image = Image.frombytes('RGBA', self.size, self.fbo.read(components=4))
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(path, format='png')

    def render(self,**kwargs):
        # if "render_to_window" in kwargs:
        #     if kwargs["render_to_window"] == True:
        #         #print("using window")
        #         self.window.use()
        #     else:
        #         self.fbo.use()
        #self.fbo.clear()
        self.fbo.use()

        for (name, texture) in self.textures.items():
            #print(str(name), self.texture_uniforms[name].value)
            textureid = self.texture_uniforms[name].value
            self.textures[name].use(location=textureid)
    
        if "time" in kwargs:
            self.time.value = kwargs['time']
        
        if self.enable_backbuffer == True:
            self.bck_texture.use(location=0)
            # not sure why, but this does not work properly when using multipass if location is 2
            # for some reason location 0 seems to works okay, even though it is same as copy_target     
        
        if self.init_texture:
            self.init_texture.use(location=1)
        
        self.vao.render(moderngl.TRIANGLE_STRIP)
        #self.bck_fbo.clear()

        if self.enable_backbuffer == True:
            self.bck_fbo.use()

            self.texture.use(location=0)
        
            self.bck_vao.render(moderngl.TRIANGLE_STRIP)

        if "render_to_window" in kwargs:
            if kwargs["render_to_window"] == True:
                self.window.use()

                self.texture.use(location=0)

                self.rndr_vao.render(moderngl.TRIANGLE_STRIP)
                #self.clear()
                
        
