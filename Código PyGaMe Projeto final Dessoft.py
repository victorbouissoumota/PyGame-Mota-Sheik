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
LIGHT_BLUE = (100, 200, 255)
 
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
ENEMY_WIDTH = 36
ENEMY_HEIGHT = 36
 
# Explosões
EXPLOSION_PARTICLES = 15
PARTICLE_MIN_SPEED = 1
PARTICLE_MAX_SPEED = 5
PARTICLE_LIFETIME = 500
 
# Power-ups
POWERUP_SPEED = 2
POWERUP_SIZE = 24
POWERUP_SPAWN_CHANCE = 25
TRIPLE_SHOT_DURATION = 5000
SHIELD_DURATION = 6000
BOMB_FLASH_DURATION = 300
 
# Waves
WAVE_TRANSITION_DURATION = 3000  # Milissegundos mostrando o texto da wave
 
 
# =============================================================================
# SISTEMA DE WAVES
# =============================================================================
 
class WaveManager:
    """Gerencia as ondas de inimigos com dificuldade progressiva.
 
    A cada nova wave, os inimigos ficam mais rápidos, aparecem em
    maior quantidade e com menos intervalo entre spawns.
 
    Attributes:
        wave_number: Número da wave atual.
        enemies_to_spawn: Quantos inimigos faltam spawnar nesta wave.
        enemies_alive: Quantos inimigos desta wave ainda estão vivos.
        spawn_delay: Intervalo entre spawns (diminui a cada wave).
        last_spawn: Timestamp do último spawn.
        enemy_min_speed: Velocidade mínima dos inimigos (aumenta a cada wave).
        enemy_max_speed: Velocidade máxima dos inimigos (aumenta a cada wave).
        max_enemies: Máximo de inimigos simultâneos na tela.
        transitioning: Flag que indica se está mostrando o texto da wave.
        transition_start: Timestamp do início da transição.
    """
 
    def __init__(self):
        """Inicializa o gerenciador na wave 0 (a primeira wave é a 1)."""
        self.wave_number = 0
        self.enemies_to_spawn = 0
        self.enemies_alive = 0
        self.spawn_delay = 0
        self.last_spawn = 0
        self.enemy_min_speed = 0
        self.enemy_max_speed = 0
        self.max_enemies = 0
        self.transitioning = False
        self.transition_start = 0
 
    def start_next_wave(self):
        """Configura e inicia a próxima wave com parâmetros mais difíceis."""
        self.wave_number += 1
        self.enemies_to_spawn = 5 + (self.wave_number * 3)
        self.enemies_alive = self.enemies_to_spawn
        self.spawn_delay = max(300, 800 - (self.wave_number * 50))
        self.enemy_min_speed = min(2 + (self.wave_number * 0.3), 6)
        self.enemy_max_speed = min(5 + (self.wave_number * 0.4), 10)
        self.max_enemies = min(8 + self.wave_number, 15)
        self.last_spawn = pygame.time.get_ticks()
        self.transitioning = True
        self.transition_start = pygame.time.get_ticks()
 
    def is_wave_complete(self):
        """Verifica se todos os inimigos da wave foram eliminados.
 
        Returns:
            bool: True se não há mais inimigos para spawnar nem vivos.
        """
        return self.enemies_to_spawn <= 0 and self.enemies_alive <= 0
 
    def is_transitioning(self):
        """Verifica se ainda está mostrando o texto de transição.
 
        Returns:
            bool: True se a transição ainda está acontecendo.
        """
        if self.transitioning:
            elapsed = pygame.time.get_ticks() - self.transition_start
            if elapsed >= WAVE_TRANSITION_DURATION:
                self.transitioning = False
        return self.transitioning
 
    def enemy_killed(self):
        """Registra que um inimigo foi eliminado."""
        self.enemies_alive -= 1
 
    def enemy_escaped(self):
        """Registra que um inimigo saiu da tela sem ser destruído."""
        self.enemies_alive -= 1
 
    def should_spawn(self, current_enemy_count):
        """Verifica se é hora de spawnar um novo inimigo.
 
        Args:
            current_enemy_count: Quantidade atual de inimigos na tela.
 
        Returns:
            bool: True se deve spawnar um novo inimigo.
        """
        if self.transitioning or self.enemies_to_spawn <= 0:
            return False
        if current_enemy_count >= self.max_enemies:
            return False
        now = pygame.time.get_ticks()
        if now - self.last_spawn >= self.spawn_delay:
            self.last_spawn = now
            self.enemies_to_spawn -= 1
            return True
        return False
 
 
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
        triple_shot: Flag que indica se o tiro triplo está ativo.
        triple_shot_timer: Timestamp de quando o tiro triplo foi ativado.
        shield: Flag que indica se o escudo está ativo.
        shield_timer: Timestamp de quando o escudo foi ativado.
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
        self.triple_shot = False
        self.triple_shot_timer = 0
        self.shield = False
        self.shield_timer = 0
 
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
        """Atualiza a posição da nave, invencibilidade e power-ups."""
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
        self._update_powerups()
 
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
 
    def _update_powerups(self):
        """Verifica se os power-ups ativos já expiraram."""
        now = pygame.time.get_ticks()
        if self.triple_shot and now - self.triple_shot_timer >= TRIPLE_SHOT_DURATION:
            self.triple_shot = False
        if self.shield and now - self.shield_timer >= SHIELD_DURATION:
            self.shield = False
 
    def activate_triple_shot(self):
        """Ativa o power-up de tiro triplo."""
        self.triple_shot = True
        self.triple_shot_timer = pygame.time.get_ticks()
 
    def activate_shield(self):
        """Ativa o power-up de escudo."""
        self.shield = True
        self.shield_timer = pygame.time.get_ticks()
 
    def hit(self):
        """Processa o dano recebido pelo jogador.
 
        Se o escudo estiver ativo, absorve o dano e desativa o escudo.
        Caso contrário, reduz uma vida e ativa invencibilidade.
 
        Returns:
            bool: True se o jogador ainda tem vidas, False se morreu.
        """
        if self.invincible:
            return True
        if self.shield:
            self.shield = False
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            return True
        self.lives -= 1
        self.invincible = True
        self.invincible_timer = pygame.time.get_ticks()
        return self.lives > 0
 
    def shoot(self):
        """Dispara tiros. Se tiro triplo ativo, dispara 3 tiros."""
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOOT_DELAY:
            self.last_shot = now
            if self.triple_shot:
                b1 = Bullet(self.rect.centerx, self.rect.top, 0)
                b2 = Bullet(self.rect.left + 5, self.rect.top + 10, -2)
                b3 = Bullet(self.rect.right - 5, self.rect.top + 10, 2)
                for b in [b1, b2, b3]:
                    self.bullet_group.add(b)
                    self.all_sprites_group.add(b)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top, 0)
                self.bullet_group.add(bullet)
                self.all_sprites_group.add(bullet)
 
    def draw_shield(self, screen):
        """Desenha o efeito visual do escudo ao redor da nave.
 
        Args:
            screen: Superfície onde o escudo será desenhado.
        """
        if self.shield:
            pulse = int(3 * math.sin(pygame.time.get_ticks() / 150))
            radius = max(PLAYER_WIDTH // 2, PLAYER_HEIGHT // 2) + 8 + pulse
            pygame.draw.circle(screen, LIGHT_BLUE, self.rect.center, radius, 2)
 
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
 
    O tiro se move para cima e pode ter um desvio horizontal
    para tiros diagonais (tiro triplo).
 
    Attributes:
        image: Superfície com o desenho do tiro.
        rect: Retângulo de posição e colisão.
        speed_y: Velocidade vertical do tiro.
        speed_x: Velocidade horizontal do tiro (0 para tiro reto).
    """
 
    def __init__(self, x, y, speed_x=0):
        """Inicializa o tiro na posição especificada.
 
        Args:
            x: Posição horizontal do centro do tiro.
            y: Posição vertical do topo do tiro.
            speed_x: Velocidade horizontal (0 = reto, negativo = esquerda).
        """
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BULLET_COLOR, (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
        pygame.draw.rect(self.image, WHITE, (1, 1, BULLET_WIDTH - 2, BULLET_HEIGHT - 2))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = BULLET_SPEED
        self.speed_x = speed_x
 
    def update(self):
        """Move o tiro e o remove se sair da tela."""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
 
 
class Enemy(pygame.sprite.Sprite):
    """Nave inimiga que desce pela tela.
 
    Cada inimigo tem velocidade definida pelo WaveManager e aparece
    em uma posição horizontal aleatória no topo da tela.
 
    Attributes:
        image: Superfície com o desenho do inimigo.
        rect: Retângulo de posição e colisão.
        speed: Velocidade vertical de descida.
        wave_manager: Referência ao gerenciador de waves.
    """
 
    COLORS = [RED, ORANGE, MAGENTA, GREEN]
 
    def __init__(self, min_speed, max_speed, wave_manager):
        """Inicializa o inimigo em posição aleatória acima da tela.
 
        Args:
            min_speed: Velocidade mínima de descida.
            max_speed: Velocidade máxima de descida.
            wave_manager: Referência ao gerenciador de waves.
        """
        super().__init__()
        self.color = random.choice(self.COLORS)
        self.image = self._create_enemy_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = random.randint(-80, -ENEMY_HEIGHT)
        self.speed = random.uniform(min_speed, max_speed)
        self.wave_manager = wave_manager
 
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
            self.wave_manager.enemy_escaped()
            self.kill()
 
 
class PowerUp(pygame.sprite.Sprite):
    """Item de power-up que cai pela tela após destruir um inimigo.
 
    Existem três tipos: tiro triplo, escudo e bomba.
 
    Attributes:
        image: Superfície com o desenho do power-up.
        rect: Retângulo de posição e colisão.
        speed: Velocidade de queda.
        kind: Tipo do power-up ('triple', 'shield' ou 'bomb').
    """
 
    TYPES = ["triple", "shield", "bomb"]
 
    def __init__(self, x, y):
        """Inicializa o power-up na posição do inimigo destruído.
 
        Args:
            x: Posição horizontal do centro.
            y: Posição vertical do centro.
        """
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.image = self._create_powerup_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = POWERUP_SPEED
        self.spawn_time = pygame.time.get_ticks()
 
    def _create_powerup_image(self):
        """Cria o sprite do power-up baseado no tipo.
 
        Returns:
            pygame.Surface: Superfície com o desenho do power-up.
        """
        surface = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
 
        if self.kind == "triple":
            pygame.draw.polygon(surface, YELLOW, [
                (POWERUP_SIZE // 2, 2),
                (2, POWERUP_SIZE - 2),
                (POWERUP_SIZE - 2, POWERUP_SIZE - 2),
            ])
            pygame.draw.polygon(surface, ORANGE, [
                (POWERUP_SIZE // 2, 6),
                (6, POWERUP_SIZE - 4),
                (POWERUP_SIZE - 6, POWERUP_SIZE - 4),
            ])
 
        elif self.kind == "shield":
            pygame.draw.circle(surface, LIGHT_BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), POWERUP_SIZE // 2 - 1)
            pygame.draw.circle(surface, BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), POWERUP_SIZE // 2 - 4)
            pygame.draw.circle(surface, LIGHT_BLUE, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), 4)
 
        elif self.kind == "bomb":
            pygame.draw.rect(surface, RED, (2, 2, POWERUP_SIZE - 4, POWERUP_SIZE - 4))
            pygame.draw.rect(surface, ORANGE, (6, 6, POWERUP_SIZE - 12, POWERUP_SIZE - 12))
            pygame.draw.rect(surface, YELLOW, (9, 9, POWERUP_SIZE - 18, POWERUP_SIZE - 18))
 
        return surface
 
    def update(self):
        """Move o power-up para baixo e o remove se sair da tela."""
        self.rect.y += self.speed
        self.rect.x += int(math.sin(pygame.time.get_ticks() / 200) * 0.8)
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
 
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(PARTICLE_MIN_SPEED, PARTICLE_MAX_SPEED)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
 
        self.color = color
        self.initial_radius = random.randint(2, 5)
        self.radius = self.initial_radius
        self.spawn_time = pygame.time.get_ticks()
 
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
 
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
 
        self.vel_x *= 0.96
        self.vel_y *= 0.96
 
        life_ratio = 1 - (elapsed / PARTICLE_LIFETIME)
        self.radius = max(int(self.initial_radius * life_ratio), 1)
 
        self._update_image()
 
 
class Explosion:
    """Gerencia a criação de uma explosão com múltiplas partículas."""
 
    COLORS = [YELLOW, ORANGE, RED, WHITE]
 
    @staticmethod
    def create(x, y, all_sprites_group, big=False):
        """Cria uma explosão gerando várias partículas na posição dada.
 
        Args:
            x: Posição horizontal do centro da explosão.
            y: Posição vertical do centro da explosão.
            all_sprites_group: Grupo onde as partículas serão adicionadas.
            big: Se True, cria uma explosão maior (para bomba).
        """
        count = EXPLOSION_PARTICLES * 3 if big else EXPLOSION_PARTICLES
        for _ in range(count):
            color = random.choice(Explosion.COLORS)
            particle = Particle(x, y, color)
            if big:
                particle.vel_x *= 2
                particle.vel_y *= 2
                particle.initial_radius = random.randint(3, 7)
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
        powerups: Grupo com os power-ups.
        wave_manager: Gerenciador de ondas de inimigos.
        score: Pontuação atual do jogador.
        bomb_flash: Timestamp do flash da bomba.
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
        self.font_medium = pygame.font.SysFont("arial", 30)
 
    def new_game(self):
        """Inicia uma nova partida, criando os grupos de sprites e o jogador."""
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player(self.bullets, self.all_sprites)
        self.all_sprites.add(self.player)
        self.wave_manager = WaveManager()
        self.wave_manager.start_next_wave()
        self.score = 0
        self.bomb_flash = 0
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
 
        # Verifica se a wave acabou para iniciar a próxima
        if self.wave_manager.is_wave_complete():
            self.wave_manager.start_next_wave()
 
        # Spawna inimigos se não está em transição
        if not self.wave_manager.is_transitioning():
            self._spawn_enemies()
 
        self._check_collisions()
        self._check_powerup_collisions()
 
    def _spawn_enemies(self):
        """Cria novos inimigos conforme as regras da wave atual."""
        if self.wave_manager.should_spawn(len(self.enemies)):
            enemy = Enemy(
                self.wave_manager.enemy_min_speed,
                self.wave_manager.enemy_max_speed,
                self.wave_manager,
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
 
    def _check_collisions(self):
        """Verifica e processa todas as colisões do jogo."""
        # Tiro x Inimigo
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                self.score += 100
                self.wave_manager.enemy_killed()
                Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)
 
                if random.randint(1, 100) <= POWERUP_SPAWN_CHANCE:
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
 
        # Inimigo x Jogador
        if not self.player.invincible:
            enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if enemy_hits:
                for enemy in enemy_hits:
                    self.wave_manager.enemy_killed()
                    Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites)
                alive = self.player.hit()
                if not alive:
                    Explosion.create(self.player.rect.centerx, self.player.rect.centery, self.all_sprites)
                    self._game_over()
 
    def _check_powerup_collisions(self):
        """Verifica se o jogador coletou algum power-up e aplica o efeito."""
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            if powerup.kind == "triple":
                self.player.activate_triple_shot()
            elif powerup.kind == "shield":
                self.player.activate_shield()
            elif powerup.kind == "bomb":
                self._activate_bomb()
 
    def _activate_bomb(self):
        """Ativa a bomba: destrói todos os inimigos na tela com explosões."""
        self.bomb_flash = pygame.time.get_ticks()
        for enemy in self.enemies:
            self.score += 100
            self.wave_manager.enemy_killed()
            Explosion.create(enemy.rect.centerx, enemy.rect.centery, self.all_sprites, big=True)
        self.enemies.empty()
 
    def _game_over(self):
        """Exibe a tela de game over temporária e encerra a partida."""
        self.screen.fill(BLACK)
 
        game_over_text = self.font_big.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Pontuação: {self.score}", True, WHITE)
        wave_text = self.font.render(f"Wave alcançada: {self.wave_manager.wave_number}", True, WHITE)
 
        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3),
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2),
        )
        self.screen.blit(
            wave_text,
            (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30),
        )
 
        pygame.display.flip()
        pygame.time.wait(3000)
 
        self.playing = False
 
    def draw(self):
        """Desenha todos os elementos na tela."""
        self.screen.fill(BLACK)
 
        # Flash branco da bomba
        if pygame.time.get_ticks() - self.bomb_flash < BOMB_FLASH_DURATION:
            alpha = 255 * (1 - (pygame.time.get_ticks() - self.bomb_flash) / BOMB_FLASH_DURATION)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(int(alpha))
            self.screen.blit(flash_surface, (0, 0))
 
        self.all_sprites.draw(self.screen)
        self.player.draw_shield(self.screen)
        self._draw_hud()
 
        # Texto de transição de wave
        if self.wave_manager.is_transitioning():
            self._draw_wave_transition()
 
        pygame.display.flip()
 
    def _draw_wave_transition(self):
        """Desenha o texto de anúncio da wave com efeito de fade."""
        elapsed = pygame.time.get_ticks() - self.wave_manager.transition_start
 
        # Calcula alpha para fade in e fade out
        if elapsed < 500:
            alpha = int(255 * (elapsed / 500))
        elif elapsed > WAVE_TRANSITION_DURATION - 500:
            alpha = int(255 * ((WAVE_TRANSITION_DURATION - elapsed) / 500))
        else:
            alpha = 255
 
        wave_text = self.font_big.render(f"WAVE {self.wave_manager.wave_number}", True, CYAN)
        wave_text.set_alpha(alpha)
 
        subtitle = self.font_medium.render("Prepare-se!", True, WHITE)
        subtitle.set_alpha(alpha)
 
        self.screen.blit(
            wave_text,
            (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 3),
        )
        self.screen.blit(
            subtitle,
            (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 3 + 55),
        )
 
    def _draw_hud(self):
        """Desenha o HUD com vidas, pontuação, wave, FPS e power-ups ativos."""
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (5, 5))
 
        score_text = self.font.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 5))
 
        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 5))
 
        # Wave atual
        wave_text = self.font.render(f"Wave: {self.wave_manager.wave_number}", True, CYAN)
        self.screen.blit(wave_text, (SCREEN_WIDTH - wave_text.get_width() - 10, 28))
 
        # Indicadores de power-ups ativos
        y_indicator = 30
        if self.player.triple_shot:
            remaining = max(0, TRIPLE_SHOT_DURATION - (pygame.time.get_ticks() - self.player.triple_shot_timer))
            text = self.font.render(f"Tiro Triplo: {remaining // 1000 + 1}s", True, YELLOW)
            self.screen.blit(text, (5, y_indicator))
            y_indicator += 20
        if self.player.shield:
            remaining = max(0, SHIELD_DURATION - (pygame.time.get_ticks() - self.player.shield_timer))
            text = self.font.render(f"Escudo: {remaining // 1000 + 1}s", True, LIGHT_BLUE)
            self.screen.blit(text, (5, y_indicator))
 
 
# =============================================================================
# PONTO DE ENTRADA
# =============================================================================
 
if __name__ == "__main__":
    game = Game()
    game.new_game()
 
    while game.running:
        game.new_game()
 
    pygame.quit()
