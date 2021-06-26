#!/usr/bin/env python3

from OpenGL.GL import *

from OpenGL.GL.ARB.shader_objects import *
from OpenGL.GL.ARB.vertex_shader import *
from OpenGL.GL.ARB.fragment_shader import *


class ShaderBase(object):
    def __init__(self, source, type):
        self.source = source

        self.shader = glCreateShaderObjectARB(type)

        # Crucial for AMD compatibility to have `[]`
        glShaderSourceARB(self.shader, [source])
        glCompileShaderARB(self.shader)

        self.errors = glGetInfoLogARB(self.shader)
        if isinstance(self.errors, bytes):
            self.errors = self.errors.decode()

    def __del__(self):
        glDeleteObjectARB(self.shader)

    def print_errors(self):
        for line in self.errors.split("\n"):
            print(line)


class ShaderVertex(ShaderBase):
    def __init__(self, source):
        ShaderBase.__init__(self, source, GL_VERTEX_SHADER_ARB)


class ShaderFragment(ShaderBase):
    def __init__(self, source):
        ShaderBase.__init__(self, source, GL_FRAGMENT_SHADER_ARB)


class Program(object):
    def __init__(self, shaders):
        self.program = glCreateProgramObjectARB()

        for shader in shaders:
            glAttachObjectARB(self.program, shader.shader)

        glValidateProgramARB(self.program)
        glLinkProgramARB(self.program)

        self.errors = glGetInfoLogARB(self.program)
        if isinstance(self.errors, bytes):
            self.errors = self.errors.decode()

        self.symbol_locations = {}

    def __del__(self):
        glDeleteObjectARB(self.program)

    def get_location(self, symbol):
        if not symbol in self.symbol_locations.keys():
            self.symbol_locations[symbol] = glGetUniformLocation(self.program, symbol.encode())
            if self.symbol_locations[symbol] == -1:
                print("Cannot get the location of symbol \""+symbol+"\"!")
        return self.symbol_locations[symbol]

    def pass_int(self, symbol, i):
        glUniform1i(self.get_location(symbol), i)

    def pass_float(self, symbol, f):
        glUniform1f(self.get_location(symbol), f)

    def pass_bool(self, symbol, b):
        glUniform1i(self.get_location(symbol), b)

    def pass_vec2(self, symbol, v):
        glUniform2f(self.get_location(symbol), v[0], v[1])

    def pass_vec3(self, symbol, v):
        glUniform3f(self.get_location(symbol), v[0], v[1], v[2])

    def pass_vec4(self, symbol, v):
        glUniform4f(self.get_location(symbol), v[0], v[1], v[2], v[3])

    def pass_texture(self, texture, number):
        glActiveTexture(GL_TEXTURE0 + number-1)
        active_texture = glGetIntegerv(GL_ACTIVE_TEXTURE) - GL_TEXTURE0
        if texture is None:
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            texture.bind()
            glUniform1i(self.get_location("tex2D_"+str(number)), active_texture)
        glActiveTexture(GL_TEXTURE0)

    def print_errors(self):
        for line in self.errors.split("\n"):
            print(line)

    @staticmethod
    def use(program=None):
        if program is None:
            glUseProgramObjectARB(0)
        else:
            glUseProgramObjectARB(program.program)
