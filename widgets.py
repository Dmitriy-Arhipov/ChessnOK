import pygame as pg
import sys
import os
import random

size = 720, 720
a, n, e = size[0], 8, 10
ort = a // n


def load_image(name, colorkey=None):
    '''
    загрузка изображения из файла
    '''
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


class SButton(pg.sprite.Sprite):
    def __init__(self, *group, image, function, pos, isClicked=False):
        super().__init__(*group)
        self.image = load_image(image)
        self._image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.function = function
        self.isClicked = isClicked

    def update(self, events):
        # обновление спрайта-кнопки в группе
        if self.isClicked:
            self.image.fill((0, 0, 0, 100), special_flags=pg.BLEND_MIN)
        else:
            self.image = self._image.copy()

    def move(self, pos):
        self.rect.x, self.rect.y = pos

    def setFunction(self, function):
        self.function = function

    def click(self):
        # принудительное "нажатие" кнопки
        self.isClicked = False if self.isClicked else True
        if self.isClicked:
            self.image.fill((0, 0, 0, 100), special_flags=pg.BLEND_ADD)
        else:
            self.image = self._image


class Figure(pg.sprite.Sprite):
    def __init__(self, *group, image, x, y, type):
        super().__init__(*group)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.type = type
        self.rect.x, self.rect.y = ort * self.x + e, ort * (n - 1 - self.y) + e

    def __str__(self):
        d = {'p': '', 'r': 'Л', 'n': 'К', 'b': 'С', 'q': 'Ф', 'k': 'Кр'}
        return d[self.type]

    def update(self):
        self.rect.x, self.rect.y = ort * self.x + e, ort * (n - 1 - self.y) + e

    def setImage(self, path):
        self.image = load_image(path)

    def setPosition(self, pos):
        self.x, self.y = pos


class AnimatedSprite(pg.sprite.Sprite):
    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        '''нарезка листа спрайтов на отдельные изображения'''
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pg.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def setFrames(self, frames):
        self.frames = frames

    def setCurrentFrame(self, index):
        self.cur_frame = index


class Particle(pg.sprite.Sprite):
    def __init__(self, group, pos, dx, dy, path):
        t = load_image(path)
        self.fire = [pg.transform.scale(t, (scale, scale)) for scale in (5, 10, 20)]
        self.screen_rect = (pos[0], pos[1], pos[0] + 600, pos[1] + 600)
        super().__init__(group)
        self.group = group
        self.pos = pos
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = self.pos
        self.gravity = 10
        self.cnt = 0

    def __str__(self):
        return f'Particle(group={self.group}, velocity={self.velocity, self.gravity}, pos={self.pos})'

    def update(self):
        if self.cnt % 10 == 0:
            self.cnt = 1
            self.velocity[1] += self.gravity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        else:
            self.cnt += 1
        if not self.rect.colliderect(self.screen_rect):
            self.kill()

    def setGravity(self, gravity=-3):
        self.gravity = gravity

    def setVelocity(self, dx, dy):
        self.velocity = dx, dy

    def setPosition(self, pos):
        self.x, self.y = pos


class ParticleSystem:
    def __init__(self, group, pos, n, v_range, image_path):
        self.group = group
        for i in range(n):
            Particle(self.group, pos, random.choice(v_range), random.choice(v_range), image_path)

    def update(self, screen):
        self.group.update()
        self.group.draw(screen)