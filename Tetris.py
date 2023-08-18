import pygame
import random
import os
import datetime

pygame.init()

TOTAL_TIME = 7200  # 总的游戏时间上限，单位秒
GRID_WIDTH = 30
GRID_NUM_WIDTH = 15
GRID_NUM_HEIGHT = 25
WIDTH = GRID_WIDTH * GRID_NUM_WIDTH
HEIGHT = GRID_WIDTH * GRID_NUM_HEIGHT
SIDE_WIDTH = 200
SCREEN_WIDTH = WIDTH + SIDE_WIDTH
WHITE = (0xff, 0xff, 0xff)
BLACK = (0, 0, 0)
LINE_COLOR = (0x33, 0x33, 0x33)

CUBE_COLORS = [
    (0xcc, 0x99, 0x99), (0xff, 0xff, 0x99), (0x66, 0x66, 0x99),
    (0x99, 0x00, 0x66), (0xff, 0xcc, 0x00), (0xcc, 0x00, 0x33),
    (0xff, 0x00, 0x33), (0x00, 0x66, 0x99), (0xff, 0xff, 0x33),
    (0x99, 0x00, 0x33), (0xcc, 0xff, 0x66), (0xff, 0x99, 0x00)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
FPS = 30

score = 0
cumulated_score = 0
level = 1

screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]

# 设置游戏的根目录为当前文件夹
base_folder = os.path.dirname(__file__)


def show_text(surf, text, size, x, y, color=WHITE):
    font_name = os.path.join(base_folder, 'c:/Windows/Fonts/arial.ttf')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class CubeShape(object):
    SHAPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    I = [[(0, -1), (0, 0), (0, 1), (0, 2)],
         [(-1, 0), (0, 0), (1, 0), (2, 0)]]
    J = [[(-2, 0), (-1, 0), (0, 0), (0, -1)],
         [(-1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, 1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (1, 0)]]
    L = [[(-2, 0), (-1, 0), (0, 0), (0, 1)],
         [(1, 0), (0, 0), (0, 1), (0, 2)],
         [(0, -1), (0, 0), (1, 0), (2, 0)],
         [(0, -2), (0, -1), (0, 0), (-1, 0)]]
    O = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    S = [[(-1, 0), (0, 0), (0, 1), (1, 1)],
         [(1, -1), (1, 0), (0, 0), (0, 1)]]
    T = [[(0, -1), (0, 0), (0, 1), (-1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, 1)],
         [(0, -1), (0, 0), (0, 1), (1, 0)],
         [(-1, 0), (0, 0), (1, 0), (0, -1)]]
    Z = [[(0, -1), (0, 0), (1, 0), (1, 1)],
         [(-1, 0), (0, 0), (0, -1), (1, -1)]]
    SHAPES_WITH_DIR = {
        'I': I, 'J': J, 'L': L, 'O': O, 'S': S, 'T': T, 'Z': Z
    }

    def __init__(self):
        self.shape = self.SHAPES[random.randint(0, len(self.SHAPES) - 1)]
        # 骨牌所在的行列
        self.center = (2, GRID_NUM_WIDTH // 2)
        self.dir = random.randint(0, len(self.SHAPES_WITH_DIR[self.shape]) - 1)
        self.color = CUBE_COLORS[random.randint(0, len(CUBE_COLORS) - 1)]

    def get_all_gridpos(self, center=None):
        curr_shape = self.SHAPES_WITH_DIR[self.shape][self.dir]
        if center is None:
            center = [self.center[0], self.center[1]]

        return [(cube[0] + center[0], cube[1] + center[1])
                for cube in curr_shape]

    def conflict(self, center):
        for cube in self.get_all_gridpos(center):
            # 超出屏幕之外，说明不合法
            if cube[0] < 0 or cube[1] < 0 or cube[0] >= GRID_NUM_HEIGHT or \
                    cube[1] >= GRID_NUM_WIDTH:
                return True

            # 不为None，说明之前已经有小方块存在了，也不合法
            if screen_color_matrix[cube[0]][cube[1]] is not None:
                return True

        return False

    def rotate(self):
        new_dir = self.dir + 1
        new_dir %= len(self.SHAPES_WITH_DIR[self.shape])
        old_dir = self.dir
        self.dir = new_dir
        if self.conflict(self.center):
            self.dir = old_dir
            return False

    def down(self):
        # import pdb; pdb.set_trace()
        center = (self.center[0] + 1, self.center[1])
        if self.conflict(center):
            return False

        self.center = center
        return True

    def left(self):
        center = (self.center[0], self.center[1] - 1)
        if self.conflict(center):
            return False
        self.center = center
        return True

    def right(self):
        center = (self.center[0], self.center[1] + 1)
        if self.conflict(center):
            return False
        self.center = center
        return True

    def draw(self):
        for cube in self.get_all_gridpos():
            pygame.draw.rect(screen, self.color,
                             (cube[1] * GRID_WIDTH, cube[0] * GRID_WIDTH,
                              GRID_WIDTH, GRID_WIDTH))
            pygame.draw.rect(screen, WHITE,
                             (cube[1] * GRID_WIDTH, cube[0] * GRID_WIDTH,
                              GRID_WIDTH, GRID_WIDTH),
                             1)


def draw_grids():
    for i in range(GRID_NUM_WIDTH):
        pygame.draw.line(screen, LINE_COLOR,
                         (i * GRID_WIDTH, 0), (i * GRID_WIDTH, HEIGHT))

    for i in range(GRID_NUM_HEIGHT):
        pygame.draw.line(screen, LINE_COLOR,
                         (0, i * GRID_WIDTH), (WIDTH, i * GRID_WIDTH))

    pygame.draw.line(screen, WHITE,
                     (GRID_WIDTH * GRID_NUM_WIDTH, 0),
                     (GRID_WIDTH * GRID_NUM_WIDTH, GRID_WIDTH * GRID_NUM_HEIGHT))


def draw_matrix():
    for i, row in zip(range(GRID_NUM_HEIGHT), screen_color_matrix):
        for j, color in zip(range(GRID_NUM_WIDTH), row):
            if color is not None:
                pygame.draw.rect(screen, color,
                                 (j * GRID_WIDTH, i * GRID_WIDTH,
                                  GRID_WIDTH, GRID_WIDTH))
                pygame.draw.rect(screen, WHITE,
                                 (j * GRID_WIDTH, i * GRID_WIDTH,
                                  GRID_WIDTH, GRID_WIDTH), 2)


def draw_score():
    show_text(screen, u'current score: {}'.format(score), 20, WIDTH + SIDE_WIDTH // 2, 500)

def draw_cumulated_score():
    show_text(screen, u'Score: {}'.format(cumulated_score), 20, WIDTH + SIDE_WIDTH // 2, 300)
    show_text(screen, u'Press p to toggle', 20, WIDTH + SIDE_WIDTH // 2, 400)
    show_text(screen, u'PAUSE / RESUME', 20, WIDTH + SIDE_WIDTH // 2, 430)

def draw_timer():
    hh = countdown // 60 // 60
    mm = countdown // 60 % 60
    ss = countdown % 60
    show_text(screen, u'Countdown Time', 20, WIDTH + SIDE_WIDTH // 2, 100)
    show_text(screen, u'{}:{}:{}'.format(hh,mm,ss), 20, WIDTH + SIDE_WIDTH // 2, 130)

    hh = (TOTAL_TIME-countdown) // 60 // 60
    mm = (TOTAL_TIME-countdown) // 60 % 60
    ss = (TOTAL_TIME-countdown) % 60
    show_text(screen, u'Time Elapsed', 20, WIDTH + SIDE_WIDTH // 2, 200)
    show_text(screen, u'{}:{}:{}'.format(hh,mm,ss), 20, WIDTH + SIDE_WIDTH // 2, 230)

def save_score_time():
    file = open('./Tetris_result.txt', 'a')
    now_time = datetime.datetime.now()
    now_time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')
    file.write('current time is '+ now_time_str + '\n' +
               'your final score is: '+ str(cumulated_score) + '\n' +
               'time consumption is: '+ str( TOTAL_TIME-countdown ) + ' seconds \n\n' )
    file.close()

def remove_full_line():
    global screen_color_matrix     # screen_color_matrix 是当前帧的俄罗斯方块矩阵
    global score
    global cumulated_score
    global level
    new_matrix = [ [None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT) ]   # 下一帧的俄罗斯方块矩阵
    index = GRID_NUM_HEIGHT - 1
    n_full_line = 0
    for i in range(GRID_NUM_HEIGHT - 1, -1, -1):  # 从最顶上扫描到最底下，判定消除满行
        is_full = True
        for j in range(GRID_NUM_WIDTH):
            if screen_color_matrix[i][j] is None:  # 当前小格子为空，则表明当前行没有满，不消除
                is_full = False
                continue
        if is_full == False:
            new_matrix[index] = screen_color_matrix[i]
            index -= 1
        else:
            n_full_line += 1

    if n_full_line == 4:      # 单次消的行越多，加的分数越多，累进加分
        score = score + 10
        cumulated_score = cumulated_score + 20
    elif n_full_line == 3:
        score = score + 6
        cumulated_score = cumulated_score + 10
    elif n_full_line == 2:
        score = score + 3
        cumulated_score = cumulated_score + 5
    elif n_full_line == 1:
        score = score + 1
        cumulated_score = cumulated_score + 1
    # score += n_full_line

    level = score // 20 + 1            # 根据当前得分加快积木下降速度
    screen_color_matrix = new_matrix

def show_welcome(screen):
    show_text(screen, u'Tetris', 50, WIDTH / 2, HEIGHT / 2 - 30)
    show_text(screen, u'Press any key to start game', 20, WIDTH / 2, HEIGHT / 2 + 30)

def show_pause(screen):
    show_text(screen, u'PAUSE', 30, WIDTH / 2, HEIGHT / 2 )

countdown = TOTAL_TIME  # 游戏时间最长为2个小时，7200秒
timer_event = pygame.USEREVENT+1
pygame.time.set_timer(timer_event, 1000)

running = True
gameover = True
counter = 0
live_cube = None
pause = True
pause_text = pygame.font.SysFont('Consolas', 32).render('Pause', True, pygame.color.Color('White'))

while running == True and countdown > 0:  # 倒计时结束 或者 不运行了， 游戏结束
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break  # 中断 这个 for 循环
        elif event.type == timer_event and pause == False:
            countdown = countdown - 1
            if countdown == 0: pygame.time.set_timer(timer_event, 0)
        elif event.type == pygame.KEYDOWN:
            if gameover == True:
                gameover = False
                live_cube = CubeShape()
                break
            if event.key == pygame.K_p: pause = not pause
            elif event.key == pygame.K_LEFT and pause == False: live_cube.left()
            elif event.key == pygame.K_RIGHT and pause == False: live_cube.right()
            elif event.key == pygame.K_DOWN and pause == False: live_cube.down()
            elif event.key == pygame.K_UP and pause == False: live_cube.rotate()
            elif event.key == pygame.K_SPACE and pause == False:   # 按空格键，积木快速下落
                while live_cube.down() == True:
                    pass
            if pause == False: remove_full_line()

    # level 是为了方便游戏的难度，level 越高 FPS // level 的值越小
    # 这样屏幕刷新的就越快，难度就越大
    if pause == False:
        if gameover is False and counter % (FPS // level) == 0:
            # down 表示下移骨牌，返回False表示下移不成功，可能超过了屏幕或者和之前固定的
            # 小方块冲突了
            if live_cube.down() == False:
                for cube in live_cube.get_all_gridpos():
                    screen_color_matrix[cube[0]][cube[1]] = live_cube.color
                live_cube = CubeShape()
                if live_cube.conflict(live_cube.center):
                    gameover = True
                    score = 0
                    live_cube = None
                    screen_color_matrix = [[None] * GRID_NUM_WIDTH for i in range(GRID_NUM_HEIGHT)]
            # 消除满行
            remove_full_line()
        counter += 1

        # 更新屏幕
    screen.fill(BLACK)
    draw_grids()
    draw_matrix()
    # draw_score()
    draw_cumulated_score()
    draw_timer()
    if live_cube is not None:
        live_cube.draw()

    if gameover == True and pause == True:
        show_welcome(screen)
    elif gameover == True and pause == False:
        show_welcome(screen)
    elif gameover == False and pause == True:
        show_pause(screen)
    else: pass

    pygame.display.update()


save_score_time()