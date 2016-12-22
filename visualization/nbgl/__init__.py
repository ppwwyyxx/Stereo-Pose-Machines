# -*- coding: utf-8 -*-
# $File: __init__.py
# $Date: Tue Aug 28 11:36:13 2012 +0800
# $Author: jiakai <jia.kai66@gmail.com>

from camera import Camera
from vector import Vector

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

import thread
import threading
import sys
import math
from time import time

class GLDrawer(object):
    boundary = None
    boundary_grid_size = 30
    sphere_slices = 10

    camera = None
    clip_near = 0.1
    clip_far = 10000

    prev_time = None
    simu_time = None
    fps = 0
    frame_cnt = 0
    cur_frame = None
    stop_flag = False

    win_width = None
    win_height = None

    move_accel = 0.5
    """acceleration"""
    move_velo = 0
    """current velocity"""
    move_accel_dt = 0.1
    """keypress within this time is treated as one long press"""
    prev_move_time = 0
    """previous move keypress time"""
    prev_move_key = None
    """previous moving key code"""

    mouse_left_state = GLUT_UP
    mouse_right_state = GLUT_UP
    mouse_x = 0
    mouse_y = 0
    rotate_factor = 0.00001
    x_rotate_speed = 0
    y_rotate_speed = 0
    wheel_speed = 5
    model_rot_agl_x = 0
    model_rot_agl_y = 0

    _in_fullscreen = False

    def __init__(self, win_title, boundary, win_width = 640, win_height = 480):
        """:param boundary: list<(min, max) * 3> for x, y, z; or None if no
                boundary"""
        self.boundary = boundary
        self.camera = Camera([10, 10, 180],
                [sum(boundary[i])/2 for i in range(3)],
                [0, 1, 0])
        self.win_width = win_width
        self.win_height = win_height
        def init_glut():
            glutInit(sys.argv)
            glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
            glutInitWindowSize(win_width, win_height)
            glutCreateWindow(win_title)

            glutDisplayFunc(self._gl_drawscene)
            def visible(vis):
                if vis == GLUT_VISIBLE:
                    glutIdleFunc(self._gl_drawscene)
                else:
                    glutIdleFunc(None)
            glutKeyboardFunc(self._on_keyboard)
            glutMouseFunc(self._on_mouse)
            glutMotionFunc(self._on_mouse_motion)
            glutReshapeFunc(self._on_reshape)
            glutVisibilityFunc(visible)
            glutIdleFunc(self._gl_drawscene)

        def init_gl():
            glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
            glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
            glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
            glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
            glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()					# Reset The Projection Matrix
            gluPerspective(45.0, float(win_width)/float(win_height),
                    self.clip_near, self.clip_far)

            glMatrixMode(GL_MODELVIEW)

        def init_light():
            glLightfv(GL_LIGHT0, GL_AMBIENT, GLfloat_4(0.5, 0.5, 0.5, 1.0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_4(1.0, 1.0, 1.0, 1.0))
            glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_4(1.0, 1.0, 1.0, 1.0))
            glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(1.0, 1.0, 1.0, 0.0));
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, GLfloat_4(0.2, 0.2, 0.2, 1.0))
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

        init_glut()
        init_gl()
        self._quadric = gluNewQuadric()
        #init_light()

    def start(self):
        self.prev_time = time()
        def mainloop():
            glutMainLoop()
        t = threading.Thread(target = mainloop)
        t.daemon = True
        t.start()

    def _on_keyboard(self, key, x, y):
        if key == 'q':
            self.stop_flag = True
            thread.exit()
        if key == 'f':
            if not self._in_fullscreen:
                self._orig_w = self.win_width
                self._orig_h = self.win_height
                glutFullScreen()
                self._in_fullscreen = True
            else:
                glutReshapeWindow(self._orig_w, self._orig_h)
                self._in_fullscreen = False
        if key in ('w', 's', 'a', 'd'):
            if time() - self.prev_move_time > self.move_accel_dt or \
                    key != self.prev_move_key:
                self.move_velo = 0
            self.prev_move_time = time()
            self.prev_move_key = key
            self.move_velo += self.move_accel
            if key == 'w':
                self.camera.move_forawrd(self.move_velo)
            elif key == 's':
                self.camera.move_forawrd(-self.move_velo)
            elif key == 'a':
                self.camera.move_right(-self.move_velo)
            else:
                self.camera.move_right(self.move_velo)


    def _on_mouse(self, button, state, x, y):
        self.mouse_x = x
        self.mouse_y = y
        if button == GLUT_LEFT_BUTTON:
            self.mouse_left_state = state
        elif button == GLUT_RIGHT_BUTTON:
            self.mouse_right_state = state
        if state == GLUT_UP:
            self.x_rotate_speed = 0
            self.y_rotate_speed = 0
            if button == 3:
                self.camera.move_forawrd(self.wheel_speed)
            elif button == 4:
                self.camera.move_forawrd(-self.wheel_speed)

    def _on_mouse_motion(self, x, y):
        def getv(v):
            s = False
            if v < 0:
                s = True
                v = -v
            r = self.rotate_factor * pow(v, 1.5)
            if s:
                r = -r
            return r
        if self.mouse_left_state == GLUT_DOWN or \
                self.mouse_right_state == GLUT_DOWN:
            x -= self.mouse_x
            y -= self.mouse_y
            self.x_rotate_speed = getv(y)
            self.y_rotate_speed = getv(x)

    def _on_reshape(self, w, h):
        self.win_width = w
        self.win_height = h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w)/float(h), self.clip_near, self.clip_far)
        glMatrixMode(GL_MODELVIEW)


    def draw_callback(self, frame, time):
        self.cur_frame = frame
        self.simu_time = time
        return not self.stop_flag

    def _gl_drawscene(self):
        frame = self.cur_frame
        if not frame:
            return
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # apply rotate
        if self.mouse_right_state == GLUT_DOWN:
            self.camera.rotate_right(-self.x_rotate_speed)
            self.camera.rotate_up(self.y_rotate_speed)
        self.camera.setGL()
        if self.mouse_left_state == GLUT_DOWN:
            self.model_rot_agl_x += self.x_rotate_speed * 180 / math.pi
            self.model_rot_agl_y += self.y_rotate_speed * 180 / math.pi
        glRotatef(self.model_rot_agl_x, 1, 0, 0)
        glRotatef(self.model_rot_agl_y, 0, 1, 0)
        self._draw_boundary()

        # draw bodies
        self._draw_frame(frame)

        # draw info text
        glColor3f(1, 1, 1)
        self._print_str('fps={0} time={1}'.format(self.fps, self.simu_time))

        # update fps
        cur_time = time()
        if cur_time - self.prev_time > 0.2:
            self.fps =int(self.frame_cnt / (cur_time - self.prev_time))
            self.prev_time = cur_time
            self.frame_cnt = 0
        self.frame_cnt += 1

        glutSwapBuffers()

    def _draw_frame(self, frame):
        for sph in frame.sphlist:
            glPushMatrix()
            glColor3f(*sph.color)
            glTranslatef(sph.pos[0], sph.pos[1], sph.pos[2])
            glutSolidSphere(sph.radius, self.sphere_slices, self.sphere_slices)
            glPopMatrix()

        for cyl in frame.cyllist:
            p1, p2 = cyl.p1, cyl.p2
            vec = p2 - p1
            vlen = float(np.sqrt(np.square(vec).sum()))
            angle = np.arccos(vec[2] / vlen) * 180.0 / np.pi
            if vec[2] < 0:
                angle = -angle
            glPushMatrix()
            glColor3f(*cyl.color)
            glTranslatef(p1[0], p1[1], p1[2])
            glRotatef(angle, -vec[1]*vec[2], vec[0]*vec[2], 0.0)
            gluCylinder(self._quadric, 3.0, 3.0, vlen, 10, 10)
            glPopMatrix()


    def _draw_boundary(self):
        bd = self.boundary
        if not bd:
            return
        o = Vector(*[bd[i][0] for i in range(3)])
        dx = bd[0][1] - bd[0][0]
        dy = bd[1][1] - bd[1][0]
        dz = bd[2][1] - bd[2][0]
        dxv = Vector(dx, 0, 0)
        dyv = Vector(0, dy, 0)
        dzv = Vector(0, 0, dz)

        glBegin(GL_LINES)
        self._draw_lines(o, o + dxv, dyv, (0.7, 0, 0))
        self._draw_lines(o, o + dyv, dxv, (0.7, 0, 0))
        self._draw_lines(o, o + dxv, dzv, (0, 0.7, 0))
        self._draw_lines(o, o + dzv, dxv, (0, 0.7, 0))
        self._draw_lines(o, o + dyv, dzv, (0, 0, 0.7))
        self._draw_lines(o, o + dzv, dyv, (0, 0, 0.7))
        glEnd()


    def _draw_lines(self, p0, p1, dist, color):
        """:param p0 and p1: Vector, initial line
        :param dist: Vector, total dist
        :param n: int, number of lines"""

        glColor3f(*color)
        dv = dist / self.boundary_grid_size
        for i in range(self.boundary_grid_size):
            glVertex3f(p0.x, p0.y, p0.z)
            glVertex3f(p1.x, p1.y, p1.z)
            p0 += dv
            p1 += dv

    def _print_str(self, s):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.win_width, self.win_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2f(10, 20)
        for i in s:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(i))

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

