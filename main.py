#!/usr/bin/env python3

import os
import sys
import traceback

from math import (
    acos,
    cos,
    pi,
    sin,
)

with open(os.devnull, "w") as f:
    oldstdout = sys.stdout
    sys.stdout = f
    import pygame
    sys.stdout = oldstdout

from pygame import locals as pgloc

from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_DEPTH_BUFFER_BIT,
    GL_MODELVIEW,
    GL_NICEST,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PERSPECTIVE_CORRECTION_HINT,
    GL_PROJECTION,
    GL_QUADS,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    glBegin,
    glBlendFunc,
    glClear,
    glEnable,
    glEnd,
    glHint,
    glMatrixMode,
    glLoadIdentity,
    glTexCoord2f,
    glVertex2f,
    glViewport,
)
from OpenGL.GLU import (
    gluOrtho2D,
)

import gl_shader as mod_program
import gl_texture as mod_texture
from math_helpers import (
    cross,
    dot,
    qq_mult,
    axisangle_to_q,
)


if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()


screen_size = [1000, 500]
multisample = 0
icon = pygame.Surface((1, 1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Off-Center Map Projections - Ian Mallett - v.1.1.0 - 2019")
if multisample:
    pygame.display.gl_set_attribute(pgloc.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pgloc.GL_MULTISAMPLESAMPLES, multisample)
pygame.display.set_mode(screen_size, pgloc.OPENGL | pgloc.DOUBLEBUF)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

glEnable(GL_TEXTURE_2D)
#glTexEnvi(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE)
#glTexEnvi(GL_POINT_SPRITE,GL_COORD_REPLACE,GL_TRUE)

glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
glEnable(GL_DEPTH_TEST)

program = mod_program.Program(
    [
        mod_program.ShaderFragment("""
uniform sampler2D tex2D_1;
uniform vec4 rotation;

const float tau = 6.2831853071795864769;

//a + bi + cj + dk
//w + xi + yj + zk

vec4 q_conjugate(vec4 q) {
  return vec4(q.x,-q.yzw);
}
vec4 qq_mult(vec4 q1, vec4 q2) {
  return vec4(
    q1.x*q2.x - q1.y*q2.y - q1.z*q2.z - q1.w*q2.w,
    q1.x*q2.y + q1.y*q2.x + q1.z*q2.w - q1.w*q2.z,
    q1.x*q2.z - q1.y*q2.w + q1.z*q2.x + q1.w*q2.y,
    q1.x*q2.w + q1.y*q2.z - q1.z*q2.y + q1.w*q2.x
  );
}

vec3 qv_mult(vec4 q1, vec3 v1) {
  vec4 q2 = vec4(0.0,v1);
  return qq_mult( qq_mult(q1,q2), q_conjugate(q1) ).yzw;
}

void main(void) {
  //2D texture coordinates
  float s = gl_TexCoord[0].x;
  float t = gl_TexCoord[0].y;

  //Convert to 3D world space vector
  vec3 world = vec3(
    cos(tau * s) * cos(0.5*tau*(t-0.5)),
                       sin(0.5*tau*(t-0.5)),
    sin(tau * s) * cos(0.5*tau*(t-0.5))
  );

  //Rotate world-space vector
  world = qv_mult(rotation,world);

  //Convert back to 2D texture coordinates
  s = (1.0/tau)*atan(world.z,world.x);
  t = 0.5 + (1.0/(0.5*tau))*asin(world.y);

  //Sample map at updated location
  gl_FragData[0] = texture2D(tex2D_1,vec2(s,t));
}
""")
    ]
)
program.print_errors()

texture = mod_texture.Texture2D.from_path("equirectangular.jpg")
texture.set_nicest()

rotation = [1.0, 0.0, 0.0, 0.0]


def get_st_mouse(mouse_position):
    s = float(mouse_position[0]) / float(screen_size[0])
    t = float(screen_size[1] - 1 - mouse_position[1]) / float(screen_size[1])
    return (s, t)


def get_input():
    global rotation

    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = pygame.mouse.get_pos()
    mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if event.type == pgloc.QUIT:
            return False
        elif event.type == pgloc.KEYDOWN:
            if event.key == pgloc.K_ESCAPE:
                return False

    sc = 0.01
    if keys_pressed[pgloc.K_a] or keys_pressed[pgloc.K_LEFT]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (0.0, 1.0, 0.0),
                sc,
            ),
        )
    if keys_pressed[pgloc.K_d] or keys_pressed[pgloc.K_RIGHT]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (0.0, 1.0, 0.0),
                -sc,
            ),
        )
    if keys_pressed[pgloc.K_s] or keys_pressed[pgloc.K_DOWN]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (0.0, 0.0, 1.0),
                sc,
            ),
        )
    if keys_pressed[pgloc.K_w] or keys_pressed[pgloc.K_UP]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (0.0, 0.0, 1.0),
                -sc,
            ),
        )
    if keys_pressed[pgloc.K_q]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (1.0, 0.0, 0.0),
                -sc,
            ),
        )
    if keys_pressed[pgloc.K_e]:
        rotation = qq_mult(
            rotation,
            axisangle_to_q(
                (1.0, 0.0, 0.0),
                sc,
            ),
        )

    if mouse_buttons[0]:
        mouse_position0 = (
            mouse_position[0] - mouse_rel[0],
            mouse_position[1] - mouse_rel[1],
        )
        mouse_position1 = mouse_position

        if mouse_position0 != mouse_position1:
            s0, t0 = get_st_mouse(mouse_position0)
            s1, t1 = get_st_mouse(mouse_position1)

            def to_world(s, t):
                return (
                    cos(2.0 * pi * s) * cos(pi * (t - 0.5)),
                    sin(pi * (t - 0.5)),
                    sin(2.0 * pi * s) * cos(pi * (t - 0.5))
                )
            xyz0 = to_world(s0, t0)
            xyz1 = to_world(s1, t1)

            axis = cross(xyz0, xyz1)
            angle = acos(dot(xyz0, xyz1))
            rotation = qq_mult(rotation, axisangle_to_q(axis, -angle))

    return True


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glViewport(0, 0, screen_size[0], screen_size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, screen_size[0], 0, screen_size[1])
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    mod_program.Program.use(program)
    program.pass_texture(texture, 1)
    program.pass_vec4("rotation", rotation)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0, 0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(screen_size[0], 0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(screen_size[0], screen_size[1])
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0, screen_size[1])
    glEnd()

    mod_program.Program.use(None)

    pygame.display.flip()


def main():
    global program, texture

    clock = pygame.time.Clock()
    while True:
        if not get_input():
            break
        draw()
        clock.tick(60)

    del program, texture

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
        pygame.quit()
        input()
