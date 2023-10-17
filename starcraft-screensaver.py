import tkinter as tk
import ctypes

import time

import os
import platform

import secrets


if platform.system() == 'Windows':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class Marine:
    def __init__(self, *coords, canvas: tk.Canvas, move_images: list, shot_images: list):

        self.coords = list(coords)
        self.canvas = canvas
        self.marine_move = move_images
        self.marine_shot = shot_images
        self.shot_laser = tk.PhotoImage(file=os.path.join('marine_shot', 'shot.png'))
        self.laser_collision = [tk.PhotoImage(file=os.path.join('marine_shot', f'shot{i}.png')) for i in range(2, 7)]
        self.id = self.canvas.create_image(coords[0], coords[1], image=self.marine_move[0], anchor='nw')

        self.highest_speed = 6
        self.lowest_speed = 3

        self.frame = 0

        self.pause = 0.04

    def move(self, v_move=None): 
        for _ in range(0, len(self.marine_move)):

            self.frame += 1
            frame_image = self.marine_move[self.frame]

            self.canvas.itemconfig(self.id, image=frame_image)
            if self.frame < 3:
                h_speed = 0
                v_speed = 0
            elif self.frame < 6:
                h_speed = self.highest_speed
                v_speed = self.highest_speed
            elif self.frame < 8:
                h_speed = 0
                v_speed = 0
            elif self.frame == 8:
                h_speed = self.highest_speed
                v_speed = self.highest_speed
            elif self.frame == 9:
                h_speed = 0
                v_speed = 0
            elif self.frame < 12:
                h_speed = self.lowest_speed
                v_speed = self.lowest_speed
            elif self.frame == 12:
                h_speed = self.highest_speed - self.lowest_speed
                v_speed = self.highest_speed - self.lowest_speed
                self.frame = 0

            time.sleep(self.pause)

            self.coords[0] += h_speed

            if v_move == 'up':
                self.canvas.move(self.id, h_speed, -1*v_speed)
                self.coords[1] -= v_speed
            elif v_move == 'down':
                self.canvas.move(self.id, h_speed, v_speed)
                self.coords[1] += v_speed
            else:
                self.canvas.move(self.id, h_speed, 0)
            win.update()

    def stop(self):
        self.frame = 0
        self.canvas.itemconfig(self.id, image=self.marine_move[0])
        win.update()

    def shot(self):

        shot_id = None


        def create_laser_shot():
            x, y = self.coords
            shot_id = self.canvas.create_image(x+90, y, image=self.shot_laser, anchor='nw')
            return shot_id
        
        
        for i in range(0, len(self.marine_shot)):
            if i == 3:
                shot_id = create_laser_shot()
            elif i > 3 and i < 8:
                self.canvas.move(shot_id, 2, 0)
            elif i > 8:
                self.canvas.move(shot_id, 25, 0)
            frame_image = self.marine_shot[i]
            self.canvas.itemconfig(self.id, image=frame_image)
            if not shot_id:
                time.sleep(self.pause)
            else:
                time.sleep(0.01)
            win.update()
        
        x_end = (win.winfo_screenwidth()-2000)//2 + 2000
        laser_x = self.coords[0]+148

        while laser_x + 25 < x_end:
            laser_x += 25
            self.canvas.move(shot_id, 25, 0)
            time.sleep(0.01)
            win.update()
        
        for image in self.laser_collision:
            self.canvas.itemconfig(shot_id, image=image)
            time.sleep(0.01)
            win.update()

        self.canvas.delete(shot_id)


win = tk.Tk()

win.wm_attributes('-fullscreen', True)

marine_move = [tk.PhotoImage(file=os.path.join('marine', f'marine{i}.png')) for i in range(1, 14)]
marine_shot = [tk.PhotoImage(file=os.path.join('marine_shot', f'marine_shot{i}.png')) for i in range(1, 12)]

floor = tk.PhotoImage(file="floor.png")

canvas = tk.Canvas(win, bg='black')
canvas.pack(expand=True, fill=tk.BOTH)

canvas.create_image((win.winfo_screenwidth()-2000)//2, (win.winfo_screenheight()-1200)//2, image=floor, anchor='nw')

marine = Marine(357, 540, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

for _ in range(0, 10):
    c = secrets.choice([None, 'up', 'down'])
    c2 = secrets.choice([True, False, True, True, True])
    if c2:
        marine.shot()
    for _ in range(0, 5):
        marine.move(v_move=c)

marine.stop()

win.mainloop()