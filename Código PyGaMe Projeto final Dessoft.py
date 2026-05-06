"""
Space Shooter - Jogo de nave estilo Shoot 'em Up.
 
Desenvolvido em Python com PyGame para o Projeto Final de Design de Software - Insper.
 
Execute este arquivo para iniciar o jogo:
    python main.py
"""
 
import pygame
 
# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
 
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
TITLE = "Space Shooter"
FPS = 60
 
# Cores (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
DARK_GRAY = (40, 40, 40)
 
# Jogador
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
 
 
# =============================================================================
# SPRITES
# =============================================================================
 
class Player(pygame.sprite.Sprite):
    """Nave controlada pelo jogador.
 
    A nave se move nas quatro direções usando as setas do teclado
    ou WASD, e fica limitada às bordas da tela.
 
    Attributes:
        image: Superfície com o desenho da nave.
        rect: Retângulo de posição e colisão.
        speed: Velocidade de movimentação em pixels por frame.
    """
 
    def __init__(self):
        """Inicializa a nave no centro inferior da tela."""
        super().__init__()
        self.image = self._create_ship_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
 
    def _create_ship_image(self):
        """Cria o sprite da nave desenhando um formato de nave.
 
        Returns:
            pygame.Surface: Superfície com o desenho da nave.
        """
        surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
 
        # Corpo principal da nave (triângulo)
        body_points = [
            (PLAYER_WIDTH // 2, 0),          # Ponta superior (nariz)
            (0, PLAYER_HEIGHT),               # Base esquerda
            (PLAYER_WIDTH, PLAYER_HEIGHT),    # Base direita
        ]
        pygame.draw.polygon(surface, CYAN, body_points)
 
        # Detalhe central
        detail_points = [
            (PLAYER_WIDTH // 2, 8),
            (PLAYER_WIDTH // 2 - 8, PLAYER_HEIGHT - 5),
            (PLAYER_WIDTH // 2 + 8, PLAYER_HEIGHT - 5),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, detail_points)
 
        # Cabine (pequeno círculo)
        pygame.draw.circle(surface, WHITE, (PLAYER_WIDTH // 2, 20), 5)
 
        # Propulsor (retângulo na base)
        pygame.draw.rect(surface, YELLOW, (PLAYER_WIDTH // 2 - 5, PLAYER_HEIGHT - 8, 10, 8))
 
        return surface
 
    def update(self):
        """Atualiza a posição da nave com base nas teclas pressionadas."""
        keys = pygame.key.get_pressed()
 
        dx = 0
        dy = 0
 
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
 
        self.rect.x += dx
        self.rect.y += dy
 
        # Limita a nave às bordas da tela
        self._clamp_to_screen()
 
    def _clamp_to_screen(self):
        """Impede que a nave saia dos limites da tela."""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
 
 
# =============================================================================
# CLASSE PRINCIPAL DO JOGO
# =============================================================================
 
class Game:
    """Classe principal que gerencia o ciclo de vida do jogo.
 
    Attributes:
        screen: Superfície principal do PyGame.
        clock: Relógio para controle de FPS.
        running: Flag que indica se o jogo está em execução.
        playing: Flag que indica se uma partida está em andamento.
        all_sprites: Grupo com todos os sprites do jogo.
    """
 
    def __init__(self):
        """Inicializa o PyGame e cria a janela do jogo."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.font = pygame.font.SysFont("arial", 18)
 
    def new_game(self):
        """Inicia uma nova partida, criando os grupos de sprites e o jogador."""
        self.all_sprites = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.playing = True
        self.run()
 
    def run(self):
        """Loop principal da partida."""
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
 
    def events(self):
        """Processa os eventos do PyGame (teclado, mouse, fechar janela)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
 
    def update(self):
        """Atualiza todos os sprites do jogo."""
        self.all_sprites.update()
 
    def draw(self):
        """Desenha todos os elementos na tela."""
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self._draw_fps()
        pygame.display.flip()
 
    def _draw_fps(self):
        """Desenha o contador de FPS no canto superior esquerdo."""
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (5, 5))
 
 
# =============================================================================
# PONTO DE ENTRADA
# =============================================================================
 
if __name__ == "__main__":
    game = Game()
    game.new_game()
 
    while game.running:
        game.new_game()
 
    pygame.quit()
 