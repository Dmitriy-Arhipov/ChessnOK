from itertools import chain, product
from csv import DictReader, DictWriter
import pygame as pg
import chess
import chess.variant
from widgets import SButton, Figure, load_image, ParticleSystem
import stockfish
import os
import sys
import random


AI = stockfish.Stockfish(path=os.path.abspath('stockfish_ files/stockfish_app.exe'))
AI.set_depth(10)


def to_not(pos):
    '''
    перевод координат хода в шахматную нотацию
    '''
    d = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j'}
    return d[pos[0] + 1] + str(pos[1] + 1)


def from_not(uci):
    '''
    перевод шахматной нотации хода в координаты на доске
    '''
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10}
    return d[uci[0]] - 1, int(uci[1]) - 1


def no_pawn(color, pos):
    '''замена пешки на доске на последней горизонтали другой фигурой'''
    global ort, n
    fsize = (ort // 2, ort // 2)
    x, y = pos[0], n - pos[1] - 1
    screen.blit(pg.transform.scale(load_image(f'figures/{color}Q.png'), fsize), (x * ort, y * ort))
    screen.blit(pg.transform.scale(load_image(f'figures/{color}R.png'), fsize), (x * ort + ort // 2, y * ort))
    screen.blit(pg.transform.scale(load_image(f'figures/{color}B.png'), fsize), (x * ort, y * ort + ort // 2))
    screen.blit(pg.transform.scale(load_image(f'figures/{color}N.png'), fsize),
                (x * ort + ort // 2, y * ort + ort // 2))
    pg.display.update()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                x, y = (event.pos)
                x, y = ((x % ort) // (ort // 2)), ((y % ort) // (ort // 2))
                fdict = {(0, 0): chess.QUEEN, (1, 0): chess.ROOK, (0, 1): chess.BISHOP, (1, 1): chess.KNIGHT}
                return chess.Piece(fdict[(x, y)], color == 'w')
            if event.type == pg.QUIT:
                running = False
                break


def can_move(pref, cur):
    '''проверка корректности хода'''
    global b
    move = chess.Move.from_uci(to_not(pref) + to_not(cur))
    t = b.is_legal(move)
    if t:
        return True
    else:
        # проверка на пешку
        p = b.piece_at(square=move.from_square)
        if str(p) == 'p' and to_not(cur)[1] == '1':
            figure = no_pawn(color='b', pos=cur)
        elif str(p) == 'P' and to_not(cur)[1] == '8':
            figure = no_pawn(color='w', pos=cur)
        else:
            return False
        # обработка замены пешки на последней горизонтали
        b.remove_piece_at(move.from_square)
        b.set_piece_at(square=move.to_square, piece=figure)
        update_board(b, n)
        pg.display.update()


def move(pref, cur):
    '''совершение хода'''
    global b, n, lvl
    b.push_san(to_not(pref) + to_not(cur))
    notation.append(str(figures[pref]) + to_not(pref) + to_not(cur))
    if lvl != 'r':  # если не выбран ручной режим, следующий ход делает движок
        global AI
        AI.set_fen_position(b.board_fen())
        bmove = AI.get_best_move()
        b.push_san(bmove)


def from_fen(s, n):
    '''чтение текущего состояния доски из fen-нотации'''
    l = list(chain.from_iterable('-' * int(c) if c.isdigit() else c for c in s if c != '/'))
    cols = list(map(lambda x: ''.join([x[1], x[0]]), product(''.join(map(str, range(n, 0, -1))), 'abcdefgh')), )
    nt = list(map(from_not, cols))
    return dict(zip(cols, zip(l, nt)))


def update_board(b, n):
    '''отрисовка фигур на доске'''
    d = from_fen(b.board_fen(), n)
    for i in d.keys():
        if d[i][0] == '-':
            figures[d[i][1]] = 0
        else:
            img = f'w{d[i][0]}' if d[i][0].isupper() else f'b{d[i][0].upper()}'
            figures[d[i][1]] = Figure(group, image=f'figures/{img}.png', x=d[i][1][0], y=d[i][1][1],
                                      type=d[i][0].lower())


def draw_board(a, n):
    '''отрисовка доски'''
    global screen
    screen.fill(black)
    for i in range(a + 1):
        for j in range(a + 1):
            if (i + j) % 2 == n % 2:
                pg.draw.rect(surface=screen, color=white, rect=(j * ort, i * ort, ort, ort))


def draw_title(stringtxt):
    '''рисование финального окна'''
    global screen, size
    pg.display.set_caption(stringtxt)
    pg.display.set_icon(load_image('app.ico'))
    bts = pg.sprite.Group()
    prtcls = pg.sprite.Group()
    running = True
    black, white = (180, 140, 100), (240, 220, 180)
    cnt, i = 0, 0
    while running:
        screen.fill(white)
        end = SButton(bts, function=sys.exit, pos=(a // 2, 100), image='buttons/play.png')
        font = pg.font.Font(None, 60)
        text = font.render(stringtxt, True, (0, 0, 0))
        ms = font.render(stringtxt, True, (0, 0, 0))
        text_x, ms_x = a // 2 - text.get_width() // 2, a // 2 - ms.get_width() // 2
        text_y, ms_y = text.get_height(), ms.get_height() + 200
        text_w, ms_w = text.get_width(), ms.get_width()
        text_h, ms_h = text.get_height(), ms.get_height()
        pg.draw.rect(screen, black, (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
        if cnt % 1000000 == 0:
            i += 1
            if i >= len(stringtxt):
                i = 0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.MOUSEBUTTONUP:
                    for bt in bts:
                        if bt.rect.collidepoint(event.pos):
                            bt.function()
                            bt.click()
                            break
            text = font.render(stringtxt[i], True, (0, 0, 0))
            screen.blit(text, (text_x + (font.size(stringtxt[:i])[0]), text_y))
            screen.blit(ms, (ms_x, ms_y))
            bts.update(pg.event.get())
            bts.draw(screen)
            ps = ParticleSystem(prtcls, (random.randint(10, size[0] - 10), 10), 3, (-2, 2), 'figures/wP.png')
            ps.update(screen)
            pg.display.update()
    pg.display.flip()


def final(s):
    # подсчет результатов и запись их в файл
    if s == '1-0':
        res = 'Победа белых'
    elif s == '0-1':
        res = 'Победа черных'
    else:
        res = 'Ничья'
    draw_title(res)
    with open('results.csv', 'r', encoding='UTF8') as f:
        d = list(DictReader(f, delimiter=';'))
        num = int(d[-1]['num']) + 1 if d else 0
    with open('results.csv', 'a', encoding='UTF8') as f:
        dw = DictWriter(f, fieldnames=['num', 'res'], delimiter=';')
        dw.writerow({'num': num, 'res': res})
    with open(f'history/{num}.txt', 'w', encoding='UTF8') as f:
        for i in range(0, len(notation), 2):
            print(notation[i], file=f, end='')
            if i + 1 < len(notation):
                print(f' - {notation[i + 1]}', file=f)
            else:
                print('#', file=f)


def game(var='Standart', level='r'):
    '''
    осуществление самой шахматной партии
    '''
    global screen, b, size, running, ort, a, n, e, black, white, group, figures, notation, bts, lvl
    lvl = level
    if lvl != 'r':
        AI.set_skill_level(lvl * 20)
    pg.init()
    pg.display.set_caption("ChessnOK")
    pg.display.set_icon(load_image('app.ico'))
    size = 720, 720
    screen = pg.display.set_mode(size)
    cur_p, running = True, True
    a, n, e = size[0], 8, 10
    ort = a // n
    black, white = (180, 140, 100), (240, 220, 180)
    group, prtcls = pg.sprite.Group(), pg.sprite.Group()
    figures, notation = {}, []
    if var == 'Standart':
        b = chess.Board()
    elif var == 'Atomic':
        b = chess.variant.AtomicBoard()
    elif var == 'Antichess':
        b = chess.variant.AntichessBoard()
    elif var == 'Horde':
        b = chess.variant.HordeBoard()
    elif var == 'Racing':
        b = chess.variant.HordeBoard()
    draw_board(a, n)
    update_board(b, n)
    while running:
        if cur_p:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    cur_p = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pref = event.pos[0] // ort, n - 1 - (event.pos[1] // ort)
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        cur = event.pos[0] // ort, n - 1 - (event.pos[1] // ort)
                        try:
                            if can_move(pref, cur):
                                move(pref, cur)
                                group = pg.sprite.Group()
                                update_board(b, n)
                            else:
                                print(to_not(pref), to_not(cur))
                        except Exception as exc:
                            print(exc)
                        if b.is_variant_end() or b.is_game_over():
                            final(str(b.result()))
                group.update()
                draw_board(a, n)
                group.draw(screen)
                pg.display.flip()
        else:
            screen.fill((0, 0, 0))
            font = pg.font.Font(None, 50)
            text = font.render("Pause", True, black)
            text_x = a // 2 - text.get_width() // 2
            text_y = text.get_height()
            text_w = text.get_width()
            text_h = text.get_height()
            pg.draw.rect(screen, white, (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
            screen.blit(text, (text_x, text_y))
            ps = ParticleSystem(prtcls, (random.randint(10, size[0] - 10), 10), 3, (-2, 2), 'figures/wP.png')
            ps.update(screen)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    cur_p = True
