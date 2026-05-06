
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
        """Inicia uma nova partida, criando os grupos de sprites."""
        self.all_sprites = pygame.sprite.Group()
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