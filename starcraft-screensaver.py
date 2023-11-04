import tkinter as tk
import ctypes

import time
import os
import platform

import random


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
        self.y = coords[1] + 50
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
        elif self.x_end > (self.x + 25) and self.state != "dead":
            for marine in marines:
                if (self.x+25) in range(marine.coords[0], marine.coords[0]+100) and self.y in range(marine.coords[1]+45, marine.coords[1]+56):
                    self.state = "dead"
                    marine.state = "dead"
                    marine.animate = marine.death_animation
                    break
            self.x += 25
            self.canvas.move(self.id, 25, 0)
        elif self.state != "dead":
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
    def __init__(self, *coords, canvas: tk.Canvas, move_images: list, shot_images: list, death_images: list):

        self.coords = list(coords)
        self.canvas = canvas
        self.marine_move = move_images
        self.marine_shot = shot_images
        self.marine_death = death_images
        self.id = self.canvas.create_image(coords[0], coords[1], image=self.marine_move[0], anchor='nw')

        self.highest_speed = 6
        self.lowest_speed = 3

        self.frame = 0
        self.shot_frame = 0
        self.death_frame = 0

        self.state = None

        self.animate = self.move

        self.pushed_lasers = 0

    def move(self, v_move=None):
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

        if self.coords[0] > win.winfo_screenwidth():
            self.destroy()

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

    def death_animation(self):
        try:
            frame_image = self.marine_death[self.death_frame]
            self.canvas.itemconfig(self.id, image=frame_image)
        except IndexError:
            self.destroy(leave_body=True)
            return

        self.death_frame += 1

    def destroy(self, leave_body=False):
        for shotlaser in objects['marines'][self.id]:
            shotlaser.destroy()

        if not leave_body:
            self.canvas.delete(self.id)
        else:
            win.after(20*1000, lambda event=None: self.canvas.delete(self.id))

        marines.remove(self)
        del objects['marines'][self.id]


win = tk.Tk()

win.wm_attributes('-fullscreen', True)

marine_move = [tk.PhotoImage(file=os.path.join('marine', f'marine{i}.png')) for i in range(1, 14)]
marine_shot = [tk.PhotoImage(file=os.path.join('marine_shot', f'marine_shot{i}.png')) for i in range(1, 12)]
marine_death = [tk.PhotoImage(file=os.path.join('marine_death', f'marine_death{i}.png')) for i in range(1, 13)]

floor = tk.PhotoImage(file="floor.png")

canvas = tk.Canvas(win, bg='black')
canvas.pack(expand=True, fill=tk.BOTH)

marines_count = canvas.create_text(30, 30, text="Marines: 0", anchor='nw', fill='white', font=(None, 13))
lasers_count = canvas.create_text(30, 60, text="Shot Lasers: 0", anchor='nw', fill='white', font=(None, 13))
fps = canvas.create_text(30, 90, text="FPS: 0", anchor='nw', fill='white', font=(None, 13))

stats_on = False

def show_stats():
    global stats_on

    canvas.itemconfigure(marines_count, state='normal')
    canvas.itemconfigure(lasers_count, state='normal')
    canvas.itemconfigure(fps, state='normal')

    stats_on = True

    win.bind("<F2>", lambda event: hide_stats())  



def hide_stats():
    global stats_on

    canvas.itemconfigure(marines_count, state='hidden')
    canvas.itemconfigure(lasers_count, state='hidden')
    canvas.itemconfigure(fps, state='hidden')

    stats_on = False

    win.bind("<F2>", lambda event: show_stats())  

hide_stats()  

x_start = (win.winfo_screenwidth()-2000)//2
y_start = (win.winfo_screenheight()-1200)//2
x_end = x_start + 2000
y_end = y_start + 1200

bg = canvas.create_image(x_start, y_start, image=floor, anchor='nw')

borders = [canvas.create_rectangle(0, 0, x_start, win.winfo_screenheight(), fill='black'),
          canvas.create_rectangle(0, 0, win.winfo_screenwidth(), y_start, fill='black'),
          canvas.create_rectangle(2000+x_start, 0, win.winfo_screenwidth(), win.winfo_screenheight(), fill='black'),
          canvas.create_rectangle(0, 1200+y_start, win.winfo_screenwidth(), win.winfo_screenheight(), fill='black')]

objects = {"marines":{}}

marines = []

possible_x = list(range(x_start, x_start+800))
possible_y = list(range(y_start+50, y_end-50))

for _ in range(15):
    marine = Marine(random.choice(possible_x),
                     random.choice(possible_y),
                       canvas=canvas, move_images=marine_move,
                         shot_images=marine_shot, death_images=marine_death)

    marines.append(marine)

    objects['marines'][marine.id] = []

win.update()

for rec_id in borders:
    canvas.lift(rec_id)

last_time = time.time() 
fr_count = 0

while True:
    for marine in marines[:]:
        marine: Marine
        if marine.state == None:
            marine.animate(v_move=random.choice(["up", "down", None])) # type: ignore
        elif marine.state == "shooting":
            marine.animate()
        else:
            marine.animate()
        if marine.frame == 0 and random.choice([1, 0, 0, 0, 0, 0, 0, 0]) == 1 and marine.state != "dead":
            marine.start_shooting()

    lc = 0
    for shotlasers in list(objects['marines'].values()):
        for shotlaser in shotlasers:
            if isinstance(shotlaser, ShotLaser):
                shotlaser.move()
                lc += 1
    
    if random.choice([1, 0, 0, 0, 0, 0, 0, 0, 0, 0]) == 1 and len(marines):
        marine = Marine(x_start-120,
                         random.choice(possible_y),
                           canvas=canvas, move_images=marine_move,
                             shot_images=marine_shot, death_images=marine_death)

        marines.append(marine)

        objects['marines'][marine.id] = []

    sorted_marines = sorted(marines, key=lambda m: m.coords[1])
        
    for m in sorted_marines:
        canvas.lift(m.id)

    for rec_id in borders:
        canvas.lift(rec_id)
    
    if stats_on:
        canvas.lift(marines_count)
        canvas.lift(lasers_count)
        canvas.lift(fps)

        canvas.itemconfig(marines_count, text=f"Marines: {len(marines)}")
        canvas.itemconfig(lasers_count, text=f"Lasers: {lc}")

        current_time = time.time()
        dt = current_time - last_time
        fr_count += 1

        if dt >= 0.3:
            fps_count = fr_count / dt
            canvas.itemconfig(fps, text=f"FPS: {round(fps_count)}")
            fr_count = 0
            last_time = current_time

    time.sleep(0.001)
    win.update()