import pygame
import cv2
import mediapipe as mp
import os
import random


#Inicializa o rastreio de mão pelo mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

#Captura a entrada da webcam
cam = cv2.VideoCapture(0)

#Posição da janela na tela 
os.environ['SDL_VIDEO_WINDOW_POS'] ="560,30"

#Inicializa o uso de fontes
pygame.font.init()

#Dimensões da tela e a posição de onde o jogo será desenhado
s_width = 800
s_height = 690
play_width = 300   # largura vai ser de 10 blocos
play_height = 600  # altura vai ser de 20 blocos
block_size = 30    
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 10

#Rotações possíveis para cada peça
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

#index 0-6 para cada forma e as cores possíveis 
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 230, 115), (255, 51, 51), (0, 204, 255), (255, 255, 128), (0, 102, 255), (255, 140, 26), (204, 51, 255)]

#Classe que representa as forma
class Piece(object):  
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

#Cria a matriz que representa a área de jogo 10x20
def create_grid(locked_pos={}):  # *
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid

#Converte a forma da peça atual para coordenadas no grid
def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

#Verifica se a posição é válida para colocar a peça
def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

#Verifica se as peças atingiram o topo, dessa forma, o jogador perde
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

#Pega uma forma aleatória
def get_shape():
    return Piece(5, 0, random.choice(shapes))

#Texto no meio da tela
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("britannic", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))

#linhas que separam os blocos, formando o grid
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))

#Remove linhas completas e ajusta a posição das peças restantes
def clear_rows(grid, locked):

    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j,i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc

#Mostra a próxima peça a entrar
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('britannic', 30)
    label = font.render('Próximo', 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 40))

#Janela principal
def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('britannic', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 15))

    #Score atual 
    font = pygame.font.SysFont('britannic', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (215, 215, 215), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)

#Score aumenta quando as linhas são limpas
def add_score(rows):
    conversion = {
        0: 0,
        1: 40,
        2: 100,
        3: 300,
        4: 1200
    }
    return conversion.get(rows)

#Função que roda o jogo
def main(win):
    # Dicionário que armazena onde as peças já estão fixas no grid
    locked_positions = {}
    #Cria o grid do jogo com base nas posições bloqueadas
    grid = create_grid(locked_positions)

    change_piece = False 
    run = True # O loop principal do jogo está em execução

    current_piece = get_shape()
    next_piece = get_shape()

    clock = pygame.time.Clock() #Controle do tempo
    # Variáveis para controlar o tempo de queda e a velocidade da peça
    fall_time = 0
    fall_speed_real = 0.45
    fall_speed = fall_speed_real
    level_time = 0

    score = 0

    # Variáveis que controlam o tempo de espera para os movimentos
    left_wait = 0
    right_wait = 0
    rotate_wait = 0
    down_wait = 0
    fall_speed_down = 0.05 

    #Loop principal
    while run:
        grid = create_grid(locked_positions) # Atualiza a grade do jogo com as posições bloqueadas

        # Atualiza o tempo de queda e o tempo do nível
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()




        ##### RASTREIO DE MÃO #####

        success, img = cam.read()
        #imgg = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Converte o frame da câmera de BGR para RGB
        results = hands.process(imgRGB)

        # Se as landmarks forem detectadas:
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    if id == 0:
                        x = []  # Lista que armazena as coordenadas x dos pontos
                        y = []  # Lista que armazena as coordenadas y dos pontos

                    # Converte as coordenadas normalizadas dos pontos da mão para coordenadas da imagem
                    x.append(int((lm.x) * w))
                    y.append(int((1 - lm.y) * h))

                    #Gestos:
                    if len(y) > 20:
                        #Se o polegar aponta para a esquerda e o mindinho está abaixado. (ESQUERDA)
                        if (x[0] > x[3] > x[4]) and not(y[20] > y[17]):
                           left_wait += 1

                        #Se o polegar está "fechado" e o mindinho levantado. (DIREITA)
                        if not(x[0] > x[3] > x[4]) and (y[20] > y[17]):
                            right_wait += 1

                        #Se o polegar aponta para a esquerda e o mindinho levantado. (ROTAÇÃO)
                        if (x[0] > x[3] > x[4]) and (y[20] > y[17]):
                            rotate_wait += 1

                #Desenha os pontos e as ligações da mão
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        else:
            down_wait += 1 #Sem detecção da mão, a peça cai

        # Exibe a janela da câmera com o rastreamento de mãos
        cv2.namedWindow("WebCam")
        cv2.moveWindow("WebCam", 20, 121)
        cv2.imshow("WebCam", img)
        cv2.waitKey(1)


        # Controle de queda e velocidade #
        #A cada 10 segundos, a velocidade de queda das peças aumenta em 0.03 segundos, com um limite de 0.25
        if level_time/1000 > 10:
            level_time = 0
            if fall_speed_real > 0.25:
                fall_speed_real -= 0.03

        #Se o tempo de queda passou, a peça cai um bloco
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        #Houve detecção por pelo menos 4 quadros, a peça se move para a esquerda
        if left_wait >= 4:
            current_piece.x -= 1
            if not (valid_space(current_piece, grid)):
                current_piece.x += 1
            left_wait = 0
            right_wait = 0
            rotate_wait = 0
            down_wait = 0

        # Houve detecção por pelo menos 4 quadros, a peça se move para a direita
        if right_wait >= 4:
            current_piece.x += 1
            if not (valid_space(current_piece, grid)):
                current_piece.x -= 1
            left_wait = 0
            right_wait = 0
            rotate_wait = 0
            down_wait = 0

        # Houve detecção por pelo menos 4 quadros, a peça rotaciona
        if rotate_wait >= 4:
            current_piece.rotation += 1
            if not (valid_space(current_piece, grid)):
                current_piece.rotation -= 1
            left_wait = 0
            right_wait = 0
            rotate_wait = 0
            down_wait = 0

        #Se não houver mão detectada por 5 quadros, a peça desce rapidamente
        if down_wait >= 5:
            fall_speed = fall_speed_down
            left_wait = 0
            right_wait = 0
            rotate_wait = 0
            down_wait = 0

        shape_pos = convert_shape_format(current_piece)

        # Pinta o grid onde a peça está localizada
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color # A peça é bloqueada no grid
            current_piece = next_piece  # A próxima peça se torna a peça atual
            next_piece = get_shape()   #Gera uma nova próxima peça
            change_piece = False
            score += add_score(clear_rows(grid, locked_positions)) #Atualiza a pontuação
            fall_speed = fall_speed_real
            down_wait = 0

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Verifica se o jogador perdeu e aparece a mensagem
        if check_lost(locked_positions):
            draw_text_middle(win, "VOCÊ PERDEU", 80, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

#Menu do jogo e a inicialização do main
def main_menu(win):
    run = True # Controla se o menu está em execução
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Pressione qualquer tecla', 60, (255,255,255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                
                main(win)

    pygame.display.quit()


#Janela configurada e a inicialização do menu
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('TETRIS')
main_menu(win)