import tkinter as tk
import ctypes

import time
import os
import platform

import secrets

import pygame


pygame.init()


if platform.system() == 'Windows':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


class Empty:
    def __init__(self):
        self.state = ""
    def move(self, x_move=None):
        pass
    def __bool__(self):
        return False
    def __str__(self) -> str:
        return ""


class ShotLaser:
    def __init__(self, coords: list, marine, canvas: tk.Canvas, x_end: int):
        self.shot_laser = tk.PhotoImage(file=os.path.join('marine_shot', 'shot.png'))
        self.laser_collision = [tk.PhotoImage(file=os.path.join('marine_shot', f'shot{i}.png')) for i in range(2, 7)]


        self.parent_marine = marine
        self.canvas = canvas
        self.id = self.canvas.create_image(coords[0], coords[1], image=self.shot_laser, anchor='nw')

        self.x = coords[0]
        self.x_end = x_end

        self.frame = 0

        self.state = "not free"

    def move(self):
        x_move = 0

        if self.x_end > (self.x + 25) and self.state != "free":
            if self.parent_marine.shot_frame > 3 and self.parent_marine.shot_frame < 8:
                self.x += 2
                self.canvas.move(self.id, 2, 0)
            else:
                self.state = "free"
        elif self.x_end > (self.x + 25):
            self.x += 25
            self.canvas.move(self.id, 25, 0)
        else:
            if self.frame == len(self.laser_collision):
                self.destroy()
                return
            self.canvas.itemconfig(self.id, image=self.laser_collision[self.frame])
            self.frame += 1

    def destroy(self):
        self.canvas.delete(self.id)
        objects['marines'][self.parent_marine.id].pop(0)
        self.parent_marine.pushed_lasers -= 1

    def __str__(self) -> str:
        return f"ShotLaser ![id={self.id}]!   [state={self.state}][x={self.x}]"


class Marine:
    def __init__(self, *coords, canvas: tk.Canvas, move_images: list, shot_images: list):

        self.coords = list(coords)
        self.canvas = canvas
        self.marine_move = move_images
        self.marine_shot = shot_images
        self.id = self.canvas.create_image(coords[0], coords[1], image=self.marine_move[0], anchor='nw')

        self.highest_speed = 6
        self.lowest_speed = 3

        self.frame = 0
        self.shot_frame = 0
        
        self.pause = 0
        self.pause_end = 2

        self.state = None

        self.animate = self.move

        self.pushed_lasers = 0

    def move(self, v_move=None):

        if self.pause == self.pause_end:
            self.pause = 0
        else:
            self.pause += 1
            return

        self.frame += 1
        frame_image = self.marine_move[self.frame]
        self.canvas.itemconfig(self.id, image=frame_image)

        h_speed = 0
        v_speed = 0

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
        

        self.coords[0] += h_speed

        if v_move == 'up':
            self.canvas.move(self.id, h_speed, -1*v_speed)
            self.coords[1] -= v_speed
        elif v_move == 'down':
            self.canvas.move(self.id, h_speed, v_speed)
            self.coords[1] += v_speed
        else:
            self.canvas.move(self.id, h_speed, 0)

    def stop(self):
        self.frame = 0
        self.canvas.itemconfig(self.id, image=self.marine_move[0])

    def start_shooting(self):
        self.animate = self.shot
        self.state = "shooting"

        self.pushed_lasers += 1


    def shot(self):

        shot_lasers = objects['marines'][self.id]

        if (not shot_lasers) and self.shot_frame > 4:
            self.state = None
            self.shot_frame = 0
            self.animate = self.move
            self.stop()
            return

        def create_laser_shot():
            x, y = self.coords
            x += 90
            x_end = (win.winfo_screenwidth()-2000)//2 + 2000

            return ShotLaser([x, y], self, self.canvas, x_end)
        
        try:
            shot_laser = shot_lasers[self.pushed_lasers-1]
        except IndexError:
            shot_laser = Empty()

        if self.shot_frame == 3 and not shot_laser:
            shot_laser = create_laser_shot()
            objects['marines'][self.id].append(shot_laser)

        frame_image = self.marine_shot[self.shot_frame]
        self.canvas.itemconfig(self.id, image=frame_image)

        self.shot_frame += 1

        if self.shot_frame == len(self.marine_shot):
            self.shot_frame = 0
            self.state = None
            self.animate = self.move


win = tk.Tk()

win.wm_attributes('-fullscreen', True)

marine_move = [tk.PhotoImage(file=os.path.join('marine', f'marine{i}.png')) for i in range(1, 14)]
marine_shot = [tk.PhotoImage(file=os.path.join('marine_shot', f'marine_shot{i}.png')) for i in range(1, 12)]

floor = tk.PhotoImage(file="floor.png")

canvas = tk.Canvas(win, bg='black')
canvas.pack(expand=True, fill=tk.BOTH)

canvas.create_image((win.winfo_screenwidth()-2000)//2, (win.winfo_screenheight()-1200)//2, image=floor, anchor='nw')

frames = [canvas.create_rectangle(0, 0, (win.winfo_screenwidth()-2000)//2, win.winfo_screenheight(), fill='black'),
          canvas.create_rectangle(0, 0, win.winfo_screenwidth(), (win.winfo_screenheight()-1200)//2, fill='black'),
          canvas.create_rectangle(2000+((win.winfo_screenwidth()-2000)//2), 0, win.winfo_screenwidth(), win.winfo_screenheight(), fill='black'),
          canvas.create_rectangle(0, 1200+((win.winfo_screenheight()-1200)//2), win.winfo_screenwidth(), win.winfo_screenheight(), fill='black')]

objects = {"marines":{}}

marines = []

marine = Marine(677, 1220, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

marines.append(marine)

objects['marines'][marine.id] = []

marine = Marine(357, 740, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

marines.append(marine)

objects['marines'][marine.id] = []

marine = Marine(357, 540, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

marines.append(marine)

objects['marines'][marine.id] = []

marine = Marine(987, 940, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

marines.append(marine)

objects['marines'][marine.id] = []

marine = Marine(857, 540, canvas=canvas, move_images=marine_move, shot_images=marine_shot)

marines.append(marine)

objects['marines'][marine.id] = []

for rec_id in frames:
    canvas.lift(rec_id)

win.update()

channel = pygame.mixer.Channel(0)

music = pygame.mixer.Sound("proshanie_slavyanki.mp3")

channel.play(music)

while True:
    for marine in marines:
        marine: Marine
        if marine.state == None:
            marine.animate(v_move=secrets.choice(["up", "down", None])) # type: ignore
        elif marine.state == "shooting":
            marine.animate()
        if marine.frame == 0 and secrets.choice([1, 0, 0, 0, 0, 0, 0, 0]) == 1:
            marine.start_shooting()

        
    for shotlasers in list(objects['marines'].values()):
        for shotlaser in shotlasers:
            if isinstance(shotlaser, ShotLaser):
                shotlaser.move()

    time.sleep(0.01)
    win.update()