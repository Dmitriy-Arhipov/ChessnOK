import pygame as pg
from widgets import SButton, AnimatedSprite, load_image
from chess_wlib import game

var, level = 'Standart', 'r'


# однотипные функции выбора варианта в словарь не объединить!
def play():
    global var, level
    if var not in ['Standart', 'Antichess', 'Atomic']:  # Stockfish поддерживает только их
        level = 'r'
    game(var, level)


def st():
    global var
    var = 'Standart'


def anti():
    global var
    var = 'Antichess'


def atom():
    global var
    var = 'Atomic'


def race():
    global var
    var = 'Racing'


def hrd():
    global var
    var = 'Horde'


def hand():
    global level
    level = 'r'


def lvl1():
    global level
    level = 1


def lvl2():
    global level
    level = 2


def main():
    '''
    стартовое окно
    '''
    global animated_bt
    pg.init()
    size = a, w = 720, 720
    screen = pg.display.set_mode(size)
    pg.display.set_icon(load_image('app.ico'))
    clock = pg.time.Clock()
    stringtxt = 'ChessnOK'
    pg.display.set_caption(stringtxt)
    running = True
    pg.mixer.init()
    pg.mixer.music.load('music/audio.ogg')
    pg.mixer.music.play()
    black, white = (180, 140, 100), (240, 220, 180)
    # Та самая анимация...
    animated_bt = pg.sprite.Group()
    anim = AnimatedSprite(animated_bt, load_image("figures/anim.png"), 3, 1, 10, 10)
    # Кнопки выбора
    bts = pg.sprite.Group()
    ps = SButton(bts, image='buttons/play.png', function=play, pos=(360, 650))
    hnd = SButton(bts, image='buttons/р.png', function=hand, pos=(300, 100))
    l1 = SButton(bts, image='buttons/1.png', function=lvl1, pos=(360, 100))
    l2 = SButton(bts, image='buttons/2.png', function=lvl2, pos=(420, 100))
    std = SButton(bts, image='buttons/st.png', function=st, pos=(310, 160))
    antic = SButton(bts, image='buttons/anti.png', function=anti, pos=(310, 260))
    atomic = SButton(bts, image='buttons/atom.png', function=atom, pos=(310, 360))
    racing = SButton(bts, image='buttons/race.png', function=race, pos=(310, 460))
    horde = SButton(bts, image='buttons/hrd.png', function=hrd, pos=(310, 560))
    # Текстовая анимация
    font = pg.font.Font(None, 50)
    text = font.render(stringtxt, True, (0, 0, 0))
    text_x = a // 2 - text.get_width() // 2
    text_y = text.get_height()
    text_w = text.get_width()
    text_h = text.get_height()
    cnt, i = 0, 0  # счетчики для смены кадров анимации
    while running:
        cnt += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break
            if event.type == pg.MOUSEBUTTONUP:
                for bt in bts:
                    if bt.rect.collidepoint(event.pos):
                        bt.function()
                        bt.click()
                        break
        if cnt % 1000 == 0:
            i += 1
            if i >= len(stringtxt):
                i = 0
            screen.fill(white)
            pg.draw.rect(screen, black, (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
            bts.draw(screen)
            bts.update(pg.event.get())
            text = font.render(stringtxt[i], True, (0, 0, 0))
            screen.blit(text, (text_x + (font.size(stringtxt[:i])[0]), text_y))
            animated_bt.draw(screen)
            animated_bt.update()
            pg.display.update()
            clock.tick(5)
    pg.display.flip()


if __name__ == '__main__':
    main()
