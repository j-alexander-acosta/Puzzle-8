import sys
import time
from collections import deque
import random
import wave
import struct
import math
import os

# Intenta importar pygame y, si no está instalado, trata de instalarlo automáticamente
try:
    import pygame
except ImportError:
    print("Pygame no está instalado. Instalándolo automáticamente...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame


# =====================================================================
# LÓGICA DEL PROBLEMA (Basada en el código fuente proporcionado)
# =====================================================================

def is_in(state, goal_list):
    return state in goal_list

class Problem:
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def goal_test(self, state):
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        return c + 1

    def value(self, state):
        raise NotImplementedError

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action, \
                         problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        return [node.action for node in self.path()[1:]]

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

def breadth_first_graph_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node, 1
    frontier = deque([node])
    explored = set()
    num_expanded_nodes = 0
    while frontier:
        node = frontier.popleft()
        num_expanded_nodes += 1
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child, num_expanded_nodes
                frontier.append(child)
    return None, num_expanded_nodes

class EightPuzzle(Problem):
    def __init__(self, initial, goal=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        super().__init__(initial, goal)

    def find_blank_square(self, state):
        return state.index(0)

    def actions(self, state):
        possible_actions = ['LEFT', 'UP', 'DOWN', 'RIGHT']
        index_blank_square = self.find_blank_square(state)

        if index_blank_square % 3 == 0:
            possible_actions.remove('LEFT')
        if index_blank_square < 3:
            possible_actions.remove('UP')
        if index_blank_square % 3 == 2:
            possible_actions.remove('RIGHT')
        if index_blank_square > 5:
            possible_actions.remove('DOWN')

        return possible_actions

    def result(self, state, action):
        blank = self.find_blank_square(state)
        new_state = list(state)
        delta = {'UP': -3, 'DOWN': 3, 'LEFT': -1, 'RIGHT': 1}
        neighbor = blank + delta[action]
        new_state[blank], new_state[neighbor] = new_state[neighbor], new_state[blank]
        return tuple(new_state)


# =====================================================================
# SINTETIZADOR DE SONIDOS (Para ser totalmente auto-contenido)
# =====================================================================
def generate_sounds():
    """Genera archivos de sonido .wav básicos usando matemáticas puras si no existen"""
    def make_wav(name, freqs, duration, vol=0.3, wave_type='sine'):
        if os.path.exists(name): return
        sample_rate = 44100
        with wave.open(name, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                # Envolvente básica para evitar 'clics' al inicio/fin
                env = 1.0
                if t < 0.05: env = t / 0.05
                elif t > duration - 0.05: env = (duration - t) / 0.05
                
                freq = freqs(t) if callable(freqs) else freqs
                
                if wave_type == 'sine':
                    val = math.sin(2 * math.pi * freq * t)
                elif wave_type == 'square':
                    val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
                
                value = int(vol * env * 32767.0 * val)
                value = max(-32768, min(32767, value))
                wav_file.writeframesraw(struct.pack('<h', value))

    print("Generando efectos de sonido...")
    # Movimiento: 'Pop' suave (tono que desciende rápidamente)
    make_wav('sfx_move.wav', lambda t: 600 - 4000*t if t < 0.1 else 200, 0.08, 0.5, 'sine')
    # Error: 'Bop' grave 
    make_wav('sfx_error.wav', 150, 0.2, 0.4, 'square')
    # Victoria: Arpegio alegre
    def win_freq(t):
        if t < 0.1: return 523.25 # C5
        elif t < 0.2: return 659.25 # E5
        elif t < 0.3: return 783.99 # G5
        else: return 1046.50 # C6
    make_wav('sfx_win.wav', win_freq, 0.6, 0.3, 'sine')


# =====================================================================
# UI Y MOTOR GRÁFICO (PYGAME)
# =====================================================================

def is_solvable(state):
    """ Verifica si el estado del puzzle tiene solución comprobando el número de inversiones """
    inversions = 0
    state_list = [n for n in state if n != 0]
    for i in range(len(state_list)):
        for j in range(i + 1, len(state_list)):
            if state_list[i] > state_list[j]:
                inversions += 1
    return inversions % 2 == 0

def get_random_solvable_state():
    """ Devuelve un estado barajado que esté garantizado a ser resoluble """
    while True:
        state = list(range(9))
        random.shuffle(state)
        if is_solvable(state) and tuple(state) != (1, 2, 3, 4, 5, 6, 7, 8, 0):
            return tuple(state)

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

generate_sounds()
snd_move = pygame.mixer.Sound('sfx_move.wav')
snd_error = pygame.mixer.Sound('sfx_error.wav')
snd_win = pygame.mixer.Sound('sfx_win.wav')

WIDTH, HEIGHT = 640, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle Espacial")

# Colores (Tema Espacial / Neón)
BG_COLOR = (15, 15, 30)        # Fondo azul noche oscuro
GRID_BG = (25, 25, 45)         # Fondo de la cuadrícula
EMPTY_CELL = (10, 10, 20)      # Hueco
TEXT_COLOR = (240, 240, 255)
BUTTON_COLOR = (60, 90, 170)
BUTTON_HOVER = (90, 130, 220)

# Fuentes
font_large = pygame.font.SysFont('Helvetica', 60, bold=True)
font_medium = pygame.font.SysFont('Helvetica', 22, bold=True)
font_small = pygame.font.SysFont('Helvetica', 16)

TILE_SIZE = 130
GAP = 12
GRID_ORIGIN_X = (WIDTH - (TILE_SIZE * 3 + GAP * 2)) // 2
GRID_ORIGIN_Y = 160

# Paleta vibrante para las fichas
TILE_COLORS = {
    1: (255, 89, 94),   # Rojo Coral
    2: (255, 146, 76),  # Naranja
    3: (255, 202, 58),  # Amarillo
    4: (138, 201, 38),  # Verde
    5: (25, 130, 196),  # Azul
    6: (106, 76, 147),  # Morado
    7: (237, 106, 176), # Rosa
    8: (0, 204, 204),   # Cian
}

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        # Borde ligero para destacar el botón
        pygame.draw.rect(surface, (255, 255, 255), self.rect, width=2, border_radius=12)
        
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.action()

class Particle:
    """ Clase simple para el confeti/chispas de celebración """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-10, 2)
        self.color = random.choice(list(TILE_COLORS.values()))
        self.life = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravedad
        self.life -= 0.015

    def draw(self, surface):
        if self.life > 0:
            size = int(6 * self.life)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

def get_tile_rect(index):
    row = index // 3
    col = index % 3
    x = GRID_ORIGIN_X + col * (TILE_SIZE + GAP)
    y = GRID_ORIGIN_Y + row * (TILE_SIZE + GAP)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

def draw_tile(surface, rect, val):
    if val == 0:
        return
    
    color = TILE_COLORS.get(val, (100, 100, 100))
    pygame.draw.rect(surface, color, rect, border_radius=15)
    # Borde iluminado sutil
    pygame.draw.rect(surface, (255, 255, 255), rect, width=3, border_radius=15)
    
    text_surf = font_large.render(str(val), True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


class Game:
    def __init__(self):
        self.state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.moves = 0
        self.is_solved = True
        
        # Animación de movimiento
        self.animating = False
        self.anim_val = 0
        self.anim_start = (0, 0)
        self.anim_end = (0, 0)
        self.anim_progress = 0.0
        self.anim_target_state = None
        
        # Auto-resolución
        self.auto_solving = False
        self.solution_path = []
        self.last_auto_move_time = 0
        
        self.sound_enabled = True
        self.particles = []
        
        # Estado manual
        self.input_mode = False
        self.input_text = ""
        self.input_error = ""

        # Layout de botones
        b_width = 180
        self.buttons = [
            Button(30, 620, b_width, 45, "Nuevo Juego", self.new_game),
            Button(WIDTH//2 - b_width//2, 620, b_width, 45, "Resolver Auto", self.solve_auto),
            Button(WIDTH - 30 - b_width, 620, b_width, 45, "Estado Manual", self.toggle_input_mode),
            Button(WIDTH//2 - 70, 690, 140, 35, "Sonido: ON", self.toggle_sound)
        ]

    def new_game(self):
        self.state = get_random_solvable_state()
        self.moves = 0
        self.is_solved = False
        self.auto_solving = False
        self.solution_path = []
        self.particles = []

    def solve_auto(self):
        if self.is_solved or self.auto_solving or self.animating:
            return
        
        problem = EightPuzzle(self.state)
        
        # Pantalla de carga
        screen.fill(BG_COLOR)
        calc_surf = font_medium.render("Calculando la ruta óptima...", True, (255,200,0))
        screen.blit(calc_surf, calc_surf.get_rect(center=(WIDTH//2, 100)))
        pygame.display.flip()
        
        # Ejecutamos el algoritmo BFS que proporcionó el usuario
        solution_node, _ = breadth_first_graph_search(problem)
        
        if solution_node and solution_node.solution():
            self.solution_path = solution_node.solution()
            self.auto_solving = True
            self.last_auto_move_time = pygame.time.get_ticks()
        else:
            if self.sound_enabled: snd_error.play()

    def toggle_input_mode(self):
        self.input_mode = not self.input_mode
        self.input_text = ""
        self.input_error = ""
        self.auto_solving = False

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.buttons[3].text = "Sonido: ON" if self.sound_enabled else "Sonido: OFF"

    def play_sound(self, snd):
        if self.sound_enabled:
            snd.play()

    def handle_click(self, pos):
        if self.input_mode or self.auto_solving or self.animating or self.is_solved:
            return

        clicked_idx = -1
        for i in range(9):
            if get_tile_rect(i).collidepoint(pos):
                clicked_idx = i
                break

        if clicked_idx != -1:
            self.try_move(clicked_idx)

    def try_move(self, idx):
        empty_idx = self.state.index(0)
        
        row1, col1 = idx // 3, idx % 3
        row2, col2 = empty_idx // 3, empty_idx % 3
        
        # Si la celda clickeada es adyacente (diferencia de 1 en manhattan distance)
        if abs(row1 - row2) + abs(col1 - col2) == 1:
            val = self.state[idx]
            
            # Setup de la animación
            self.animating = True
            self.anim_val = val
            self.anim_start = get_tile_rect(idx).topleft
            self.anim_end = get_tile_rect(empty_idx).topleft
            self.anim_progress = 0.0
            
            new_state = list(self.state)
            new_state[empty_idx], new_state[idx] = new_state[idx], new_state[empty_idx]
            self.anim_target_state = tuple(new_state)
            
            self.play_sound(snd_move)
            self.moves += 1
        else:
            if idx != empty_idx:
                self.play_sound(snd_error)

    def update(self):
        # Actualizar animación de movimiento
        if self.animating:
            self.anim_progress += 0.15 # Velocidad del deslizamiento
            if self.anim_progress >= 1.0:
                self.animating = False
                self.state = self.anim_target_state
                
                # Comprobar estado de victoria
                if self.state == (1, 2, 3, 4, 5, 6, 7, 8, 0):
                    self.is_solved = True
                    self.auto_solving = False
                    self.play_sound(snd_win)
                    # Lluvia de confeti
                    for _ in range(120):
                        self.particles.append(Particle(WIDTH//2 + random.randint(-200, 200), HEIGHT//2 - 100))

        # Motor de auto-resolución paso a paso
        elif self.auto_solving:
            now = pygame.time.get_ticks()
            if now - self.last_auto_move_time > 350: # ms de pausa entre movimientos
                if self.solution_path:
                    action = self.solution_path.pop(0)
                    empty_idx = self.state.index(0)
                    delta = {'UP': -3, 'DOWN': 3, 'LEFT': -1, 'RIGHT': 1}
                    target_idx = empty_idx + delta[action]
                    self.try_move(target_idx)
                    self.last_auto_move_time = now
                else:
                    self.auto_solving = False

        # Actualizar física del confeti
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        
        title_surf = font_large.render("8-Puzzle Espacial", True, (200, 220, 255))
        surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 60)))
        
        moves_surf = font_medium.render(f"Movimientos: {self.moves}", True, TEXT_COLOR)
        surface.blit(moves_surf, (30, 110))
        
        if self.is_solved and self.moves > 0:
            sol_surf = font_medium.render("¡Completado!", True, (100, 255, 150))
            surface.blit(sol_surf, (WIDTH - 170, 110))
        
        # Fondo de la Cuadrícula
        grid_rect = pygame.Rect(GRID_ORIGIN_X - GAP, GRID_ORIGIN_Y - GAP, 
                                TILE_SIZE * 3 + GAP * 4, TILE_SIZE * 3 + GAP * 4)
        pygame.draw.rect(surface, GRID_BG, grid_rect, border_radius=20)
        
        # Dibujar Huecos (0)
        for i in range(9):
            rect = get_tile_rect(i)
            pygame.draw.rect(surface, EMPTY_CELL, rect, border_radius=15)
            pygame.draw.rect(surface, (15, 15, 25), rect, width=4, border_radius=15)

        # Dibujar Fichas en su posición actual
        for i in range(9):
            val = self.state[i]
            if val == 0: continue
            
            # Ocultamos la ficha que se está moviendo (se dibuja aparte para la animación)
            if self.animating and val == self.anim_val:
                continue
                
            draw_tile(surface, get_tile_rect(i), val)

        # Dibujar Ficha Animada Interpolada
        if self.animating:
            # Interpolación Lineal (Lerp) para el deslizamiento suave
            x = self.anim_start[0] + (self.anim_end[0] - self.anim_start[0]) * self.anim_progress
            y = self.anim_start[1] + (self.anim_end[1] - self.anim_start[1]) * self.anim_progress
            anim_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            draw_tile(surface, anim_rect, self.anim_val)

        # Confeti
        for p in self.particles:
            p.draw(surface)

        # Interfaz Inferior
        for b in self.buttons:
            b.draw(surface)

        # Overlay Modal: Ingreso de Estado Manual
        if self.input_mode:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            surface.blit(overlay, (0,0))
            
            box = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 120, 440, 240)
            pygame.draw.rect(surface, GRID_BG, box, border_radius=20)
            pygame.draw.rect(surface, BUTTON_COLOR, box, width=4, border_radius=20)
            
            msg1 = font_medium.render("Ingresa 9 dígitos (0-8 sin repetir)", True, TEXT_COLOR)
            surface.blit(msg1, msg1.get_rect(center=(WIDTH//2, HEIGHT//2 - 70)))
            
            msg2 = font_medium.render("El '0' representa el hueco vacío", True, (180,180,200))
            surface.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
            
            # Formatear y mostrar el texto ingresado
            display_text = " ".join(self.input_text) + (" _" if len(self.input_text) < 9 else "")
            txt_surf = font_large.render(display_text, True, (255, 220, 100))
            surface.blit(txt_surf, txt_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))
            
            if self.input_error:
                err_surf = font_small.render(self.input_error, True, (255, 100, 100))
                surface.blit(err_surf, err_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 75)))
                
            inst_surf = font_small.render("ENTER para Jugar | ESC para Cancelar", True, (150,150,150))
            surface.blit(inst_surf, inst_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 105)))


def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if game.input_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.toggle_input_mode()
                    elif event.key == pygame.K_RETURN:
                        # Validaciones al intentar crear el estado
                        if len(game.input_text) == 9:
                            if set(game.input_text) == set("012345678"):
                                new_st = tuple(int(c) for c in game.input_text)
                                if is_solvable(new_st):
                                    game.state = new_st
                                    game.moves = 0
                                    game.is_solved = (game.state == (1,2,3,4,5,6,7,8,0))
                                    game.toggle_input_mode()
                                else:
                                    game.input_error = "El puzzle ingresado NO tiene solución (por inversiones)."
                            else:
                                game.input_error = "Debe usar únicamente dígitos del 0 al 8 sin repetirlos."
                        else:
                            game.input_error = "Debe ingresar exactamente los 9 dígitos."
                    elif event.key == pygame.K_BACKSPACE:
                        game.input_text = game.input_text[:-1]
                        game.input_error = ""
                    elif event.unicode.isdigit() and len(game.input_text) < 9:
                        game.input_text += event.unicode
                        game.input_error = ""
            else:
                for b in game.buttons:
                    b.check_event(event)
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    game.handle_click(event.pos)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60) # 60 FPS fijos

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
