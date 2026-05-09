"""
Space Shooter - Jogo de nave estilo Shoot 'em Up.

Desenvolvido em Python com PyGame para o Projeto Final de Design de Software - Insper.

Execute este arquivo para iniciar o jogo:
    python main.py
"""

import pygame
import random
import math

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
ORANGE = (255, 165, 0)
MAGENTA = (255, 0, 200)

# Jogador
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_LIVES = 3
PLAYER_INVINCIBLE_TIME = 1500

# Tiros
BULLET_SPEED = -8
BULLET_WIDTH = 4
BULLET_HEIGHT = 12
BULLET_COLOR = YELLOW
SHOOT_DELAY = 250

# Inimigos
ENEMY_MIN_SPEED = 2
ENEMY_MAX_SPEED = 5
ENEMY_WIDTH = 36
ENEMY_HEIGHT = 36
ENEMY_SPAWN_DELAY = 800
MAX_ENEMIES = 8

# Explosões
EXPLOSION_PARTICLES = 15
PARTICLE_MIN_SPEED = 1
PARTICLE_MAX_SPEED = 5
PARTICLE_LIFETIME = 500  # Milissegundos


# =============================================================================
# SPRITES
# =============================================================================

class Player(pygame.sprite.Sprite):
    """Nave controlada pelo jogador.

    A nave se move nas quatro direções usando as setas do teclado
    ou WASD, e fica limitada às bordas da tela. Atira com a barra
    de espaço. Pisca quando está invencível após levar dano.

    Attributes:
        image: Superfície com o desenho da nave.
        rect: Retângulo de posição e colisão.
        speed: Velocidade de movimentação em pixels por frame.
        last_shot: Timestamp do último tiro disparado.
        lives: Quantidade de vidas restantes.
        invincible: Flag que indica se o jogador está invencível.
        invincible_timer: Timestamp de quando ficou invencível.
    """

    def __init__(self, bullet_group, all_sprites_group):
        """Inicializa a nave no centro inferior da tela.

        Args:
            bullet_group: Grupo de sprites para adicionar os tiros.
            all_sprites_group: Grupo geral de sprites do jogo.
        """
        super().__init__()
        self.original_image = self._create_ship_image()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.bullet_group = bullet_group
        self.all_sprites_group = all_sprites_group
        self.last_shot = 0
        self.lives = PLAYER_LIVES
        self.invincible = False
        self.invincible_timer = 0

    def _create_ship_image(self):
        """Cria o sprite da nave desenhando um formato de nave.

        Returns:
            pygame.Surface: Superfície com o desenho da nave.
        """
        surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

        body_points = [
            (PLAYER_WIDTH // 2, 0),
            (0, PLAYER_HEIGHT),
            (PLAYER_WIDTH, PLAYER_HEIGHT),
        ]
        pygame.draw.polygon(surface, CYAN, body_points)

        detail_points = [
            (PLAYER_WIDTH // 2, 8),
            (PLAYER_WIDTH // 2 - 8, PLAYER_HEIGHT - 5),
            (PLAYER_WIDTH // 2 + 8, PLAYER_HEIGHT - 5),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, detail_points)

        pygame.draw.circle(surface, WHITE, (PLAYER_WIDTH // 2, 20), 5)
        pygame.draw.rect(surface, YELLOW, (PLAYER_WIDTH // 2 - 5, PLAYER_HEIGHT - 8, 10, 8))

        return surface

    def update(self):
        """Atualiza a posição da nave e o estado de invencibilidade."""
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

        self._clamp_to_screen()
        self._update_invincibility()

    def _update_invincibility(self):
        """Gerencia o tempo de invencibilidade e o efeito de piscar."""
        if self.invincible:
            elapsed = pygame.time.get_ticks() - self.invincible_timer
            if elapsed >= PLAYER_INVINCIBLE_TIME:
                self.invincible = False
                self.image = self.original_image.copy()
            else:
                if (elapsed // 100) % 2 == 0:
                    self.image = self.original_image.copy()
                else:
                    self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

    def hit(self):
        """Processa o dano recebido pelo jogador.

        Reduz uma vida e ativa o período de invencibilidade.

        Returns:
            bool: True se o jogador ainda tem vidas, False se morreu.
        """
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            return self.lives > 0
        return True

    def shoot(self):
        """Dispara um tiro se o tempo de recarga já passou."""
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOOT_DELAY:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullet_group.add(bullet)
            self.all_sprites_group.add(bullet)

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


class Bullet(pygame.sprite.Sprite):
    """Projétil disparado pela nave do jogador.

    O tiro se move para cima e é destruído ao sair da tela.

    Attributes:
        image: Superfície com o desenho do tiro.
        rect: Retângulo de posição e colisão.
        speed: Velocidade vertical do tiro (negativa = para cima).
    """

    def __init__(self, x, y):
        """Inicializa o tiro na posição especificada.

        Args:
            x: Posição horizontal do centro do tiro.
            y: Posição vertical do topo do tiro.
        """
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BULLET_COLOR, (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
        pygame.draw.rect(self.image, WHITE, (1, 1, BULLET_WIDTH - 2, BULLET_HEIGHT - 2))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED

    def update(self):
        """Move o tiro para cima e o remove se sair da tela."""
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """Nave inimiga que desce pela tela.

    Cada inimigo tem velocidade aleatória e aparece em uma posição
    horizontal aleatória no topo da tela. É destruído ao sair pela
    parte de baixo.

    Attributes:
        image: Superfície com o desenho do inimigo.
        rect: Retângulo de posição e colisão.
        speed: Velocidade vertical de descida.
    """

    COLORS = [RED, ORANGE, MAGENTA, GREEN]

    def __init__(self):
        """Inicializa o inimigo em posição aleatória acima da tela."""
        super().__init__()
        self.color = random.choice(self.COLORS)
        self.image = self._create_enemy_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = random.randint(-80, -ENEMY_HEIGHT)
        self.speed = random.uniform(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)

    def _create_enemy_image(self):
        """Cria o sprite do inimigo com formato de losango.

        Returns:
            pygame.Surface: Superfície com o desenho do inimigo.
        """
        surface = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)

        body_points = [
            (ENEMY_WIDTH // 2, 0),
            (ENEMY_WIDTH, ENEMY_HEIGHT // 2),
            (ENEMY_WIDTH // 2, ENEMY_HEIGHT),
            (0, ENEMY_HEIGHT // 2),
        ]
        pygame.draw.polygon(surface, self.color, body_points)

        inner_points = [
            (ENEMY_WIDTH // 2, 6),
            (ENEMY_WIDTH - 6, ENEMY_HEIGHT // 2),
            (ENEMY_WIDTH // 2, ENEMY_HEIGHT - 6),
            (6, ENEMY_HEIGHT // 2),
        ]
        pygame.draw.polygon(surface, DARK_GRAY, inner_points)

        pygame.draw.circle(surface, WHITE, (ENEMY_WIDTH // 2, ENEMY_HEIGHT // 2), 4)
        pygame.draw.circle(surface, RED, (ENEMY_WIDTH // 2, ENEMY_HEIGHT // 2), 2)

        return surface

    def update(self):
        """Move o inimigo para baixo e o remove se sair da tela."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    """Partícula individual de uma explosão.

    Cada partícula se move em uma direção aleatória, encolhe
    gradualmente e desaparece após um tempo de vida definido.

    Attributes:
        pos_x: Posição horizontal precisa (float).
        pos_y: Posição vertical precisa (float).
        vel_x: Velocidade horizontal.
        vel_y: Velocidade vertical.
        color: Cor da partícula.
        radius: Raio atual da partícula.
        initial_radius: Raio inicial para calcular o encolhimento.
        spawn_time: Timestamp de criação da partícula.
    """

    def __init__(self, x, y, color):
        """Inicializa a partícula na posição da explosão.

        Args:
            x: Posição horizontal do centro da explosão.
            y: Posição vertical do centro da explosão.
            color: Cor base da partícula.
        """
        super().__init__()
        self.pos_x = float(x)
        self.pos_y = float(y)

        # Direção e velocidade aleatórias
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(PARTICLE_MIN_SPEED, PARTICLE_MAX_SPEED)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed

        self.color = color
        self.initial_radius = random.randint(2, 5)
        self.radius = self.initial_radius
        self.spawn_time = pygame.time.get_ticks()

        # Cria a imagem inicial
        self._update_image()

    def _update_image(self):
        """Redesenha a imagem da partícula com o raio atual."""
        size = max(self.radius * 2, 1)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        if self.radius >= 1:
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))

    def update(self):
        """Move a partícula, encolhe e a remove quando o tempo acaba."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed >= PARTICLE_LIFETIME:
            self.kill()
            return

        # Move a partícula
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # Desacelera gradualmente
        self.vel_x *= 0.96
        self.vel_y *= 0.96

        # Encolhe proporcionalmente ao tempo de vida restante
        life_ratio = 1 - (elapsed / PARTICLE_LIFETIME)
        self.radius = max(int(self.initial_radius * life_ratio), 1)

        self._update_image()


class Explosion:
    """Gerencia a criação de uma explosão com múltiplas partículas.

    Esta classe não é um sprite, apenas serve como fábrica de partículas
    que são adicionadas ao grupo de sprites fornecido.
    """

    # Cores possíveis das partículas de explosão
    COLORS = [YELLOW, ORANGE, RED, WHITE]

    @staticmethod
    def create(x, y, all_sprites_group):
        """Cria uma explosão gerando várias partículas na posição dada.

        Args:
            x: Posição horizontal do centro da explosão.
            y: Posição vertical do centro da explosão.
            all_sprites_group: Grupo onde as partículas serão adicionadas.
        """
        for _ in range(EXPLOSION_PARTICLES):
            color = random.choice(Explosion.COLORS)
            particle = Particle(x, y, color)
            all_sprites_group.add(particle)


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
        bullets: Grupo com os tiros do jogador.
        enemies: Grupo com os inimigos.
        last_enemy_spawn: Timestamp do último spawn de inimigo.
        score: Pontuação atual do jogador.
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
        self.font_big = pygame.font.SysFont("arial", 48)

    def new_game(self):
        """Inicia uma nova partida, criando os grupos de sprites e o jogador."""
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player(self.bullets, self.all_sprites)
        self.all_sprites.add(self.player)
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.score = 0
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
                elif event.key == pygame.K_SPACE:
                    self.player.shoot()

    def update(self):
        """Atualiza todos os sprites, spawna inimigos e verifica colisões."""
        self.all_sprites.update()
        self._spawn_enemies()
        self._check_collisions()

    def _spawn_enemies(self):
        """Cria novos inimigos periodicamente, respeitando o limite máximo."""
        now = pygame.time.get_ticks()
        if now - self.last_enemy_spawn >= ENEMY_SPAWN_DELAY and len(self.enemies) < MAX_ENEMIES:
            self.last_enemy_spawn = now
            enemy = Enemy()
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def _check_collisions(self):
        """Verifica e processa todas as colisões do jogo.

        Tiro x Inimigo: destrói ambos, soma pontos e cria explosão.
        Inimigo x Jogador: o jogador perde uma vida e fica invencível.
        """
        # Tiro x Inimigo
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                self.score += 100
                Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)

        # Inimigo x Jogador
        if not self.player.invincible:
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if enemy_hits:
                for enemy in enemy_hits:
                    Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)
                alive = self.player.hit()
                if not alive:
                    Explosion.create(self.player.rect.centerx, self.player.rect.centery, self.all_sprites)
                    self._game_over()

    def _game_over(self):
        """Exibe a tela de game over temporária e encerra a partida."""
        self.screen.fill(BLACK)

        game_over_text = self.font_big.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Pontuação: {self.score}", True, WHITE)

        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3),
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2),
        )

        pygame.display.flip()
        pygame.time.wait(3000)

        self.playing = False

    def draw(self):
        """Desenha todos os elementos na tela."""
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        """Desenha o HUD com vidas, pontuação e FPS."""
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (5, 5))

        score_text = self.font.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 5))

        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 5))


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.new_game()

    while game.running:
        game.new_game()

    pygame.quit()

