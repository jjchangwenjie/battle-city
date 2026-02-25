import pygame
import random
import sys
from config import *
from entities import PlayerTank, EnemyTank, Bullet
from map_system import GameMap, PowerUp

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战 - Battle City")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.state = 'menu'
        self.current_level = 0
        self.players = []
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.game_map = None
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.max_enemies_on_screen = 4
        self.game_over = False
        self.victory = False
        self.paused = False
        self.two_players = False
        
    def run(self):
        running = True
        while running:
            if self.state == 'menu':
                running = self.run_menu()
            elif self.state == 'playing':
                running = self.run_game()
            elif self.state == 'game_over':
                running = self.run_game_over()
                
        pygame.quit()
        sys.exit()
        
    def run_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1] or keys[pygame.K_KP1]:
                self.two_players = False
                self.start_game()
                return True
            elif keys[pygame.K_2] or keys[pygame.K_KP2]:
                self.two_players = True
                self.start_game()
                return True
                        
            self.draw_menu()
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("坦克大战", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.small_font.render("BATTLE CITY", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        tank_img = self.draw_menu_tank(SCREEN_WIDTH // 2, 220)
        self.screen.blit(tank_img, tank_img.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        
        option1 = self.font.render("1 - 单人游戏", True, WHITE)
        option1_rect = option1.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(option1, option1_rect)
        
        option2 = self.font.render("2 - 双人游戏", True, WHITE)
        option2_rect = option2.get_rect(center=(SCREEN_WIDTH // 2, 360))
        self.screen.blit(option2, option2_rect)
        
        controls = self.small_font.render("玩家1: WASD移动 J射击 | 玩家2: 方向键移动 空格射击", True, GRAY)
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(controls, controls_rect)
        
        esc_text = self.small_font.render("ESC - 退出", True, GRAY)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, 490))
        self.screen.blit(esc_text, esc_rect)
        
    def draw_menu_tank(self, x, y):
        surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.rect(surface, YELLOW, (10, 10, 40, 40))
        pygame.draw.rect(surface, BLACK, (10, 10, 40, 40), 2)
        pygame.draw.rect(surface, YELLOW, (27, 0, 6, 30))
        pygame.draw.rect(surface, BLACK, (27, 0, 6, 30), 1)
        return surface
        
    def start_game(self):
        self.current_level = 0
        self.game_over = False
        self.victory = False
        self.load_level(self.current_level)
        self.state = 'playing'
        
    def load_level(self, level_num):
        if level_num >= len(LEVELS):
            self.victory = True
            self.state = 'game_over'
            return
            
        self.players = []
        self.enemies.empty()
        self.bullets.empty()
        self.powerups.empty()
        
        level_data = LEVELS[level_num]
        self.game_map = GameMap(level_data)
        
        player1 = PlayerTank(4 * TILE_SIZE + TILE_SIZE // 2, 
                            (MAP_HEIGHT - 2) * TILE_SIZE + TILE_SIZE // 2, 
                            player_id=1)
        player1.activate_shield(180)
        self.players.append(player1)
        
        if self.two_players:
            player2 = PlayerTank(8 * TILE_SIZE + TILE_SIZE // 2, 
                                (MAP_HEIGHT - 2) * TILE_SIZE + TILE_SIZE // 2, 
                                player_id=2)
            player2.activate_shield(180)
            self.players.append(player2)
            
        self.enemies_to_spawn = ENEMIES_PER_LEVEL
        self.spawn_timer = 0
        
    def run_game(self):
        while self.state == 'playing':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    else:
                        for player in self.players:
                            if player.player_id == 1:
                                if event.key == pygame.K_w:
                                    player.rotate('up')
                                elif event.key == pygame.K_s:
                                    player.rotate('down')
                                elif event.key == pygame.K_a:
                                    player.rotate('left')
                                elif event.key == pygame.K_d:
                                    player.rotate('right')
                                elif event.key == pygame.K_j:
                                    player.shoot(self.bullets)
                            elif player.player_id == 2:
                                if event.key == pygame.K_UP:
                                    player.rotate('up')
                                elif event.key == pygame.K_DOWN:
                                    player.rotate('down')
                                elif event.key == pygame.K_LEFT:
                                    player.rotate('left')
                                elif event.key == pygame.K_RIGHT:
                                    player.rotate('right')
                                elif event.key == pygame.K_SPACE:
                                    player.shoot(self.bullets)
            
            if not self.paused:
                self.update()
                
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        return True
        
    def update(self):
        if self.game_over:
            self.state = 'game_over'
            return
            
        self.handle_input()
        self.spawn_enemies()
        
        all_tanks = self.players + list(self.enemies)
        
        for player in self.players[:]:
            player.update()
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if player.player_id == 1:
                if keys[pygame.K_w]:
                    dy = -player.speed
                elif keys[pygame.K_s]:
                    dy = player.speed
                elif keys[pygame.K_a]:
                    dx = -player.speed
                elif keys[pygame.K_d]:
                    dx = player.speed
            elif player.player_id == 2:
                if keys[pygame.K_UP]:
                    dy = -player.speed
                elif keys[pygame.K_DOWN]:
                    dy = player.speed
                elif keys[pygame.K_LEFT]:
                    dx = -player.speed
                elif keys[pygame.K_RIGHT]:
                    dx = player.speed
            if dx != 0 or dy != 0:
                player.move(dx, dy, self.game_map, all_tanks)
            
        for enemy in self.enemies:
            enemy.update()
            enemy.ai_update(self.game_map, all_tanks, self.players, self.bullets)
            
        self.bullets.update()
        self.powerups.update()
        self.game_map.update()
        
        self.check_collisions(all_tanks)
        
        self.check_game_state()
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                for player in self.players:
                    if player.player_id == 1:
                        if event.key == pygame.K_j:
                            player.shoot(self.bullets)
                    elif player.player_id == 2:
                        if event.key == pygame.K_SPACE:
                            player.shoot(self.bullets)
                
    def spawn_enemies(self):
        if len(self.enemies) < self.max_enemies_on_screen and self.enemies_to_spawn > 0:
            self.spawn_timer += 1
            if self.spawn_timer >= 120:
                self.spawn_timer = 0
                
                spawn_points = [
                    (TILE_SIZE // 2, TILE_SIZE // 2),
                    (6 * TILE_SIZE + TILE_SIZE // 2, TILE_SIZE // 2),
                    (12 * TILE_SIZE + TILE_SIZE // 2, TILE_SIZE // 2)
                ]
                
                random.shuffle(spawn_points)
                
                for point in spawn_points:
                    spawn_rect = pygame.Rect(point[0] - 15, point[1] - 15, 30, 30)
                    can_spawn = True
                    for tank in self.players + list(self.enemies):
                        if spawn_rect.colliderect(tank.rect):
                            can_spawn = False
                            break
                    
                    if can_spawn:
                        enemy_type = random.choices(
                            ['basic', 'fast', 'power', 'heavy'],
                            weights=[50, 25, 15, 10]
                        )[0]
                        enemy = EnemyTank(point[0], point[1], enemy_type)
                        self.enemies.add(enemy)
                        self.enemies_to_spawn -= 1
                        break
                        
    def check_collisions(self, all_tanks):
        for bullet in self.bullets:
            tile_x = bullet.rect.centerx // TILE_SIZE
            tile_y = bullet.rect.centery // TILE_SIZE
            
            tile = self.game_map.get_tile(tile_x, tile_y)
            if tile == STEEL:
                if bullet.power >= 3:
                    self.game_map.set_tile(tile_x, tile_y, EMPTY)
                    bullet.kill()
                else:
                    bullet.kill()
                continue
            elif tile == BRICK:
                self.game_map.set_tile(tile_x, tile_y, EMPTY)
                bullet.kill()
                continue
            elif tile == BASE:
                self.game_map.base_destroyed = True
                self.game_map.set_tile(tile_x, tile_y, EMPTY)
                bullet.kill()
                continue
            elif tile == WATER:
                bullet.kill()
                continue
            
            for tank in all_tanks:
                if bullet.alive() and bullet.rect.colliderect(tank.rect):
                    if bullet.owner != tank:
                        if isinstance(tank, EnemyTank) and isinstance(bullet.owner, EnemyTank):
                            continue
                        if tank.hit():
                            if isinstance(tank, PlayerTank):
                                if not tank.lose_life():
                                    self.players.remove(tank)
                            else:
                                if tank.has_powerup:
                                    self.spawn_powerup(tank.rect.x, tank.rect.y)
                                tank.kill()
                        bullet.kill()
                        
        for player in self.players:
            for powerup in self.powerups:
                if player.rect.colliderect(powerup.rect):
                    powerup.apply(player, self, self.enemies)
                    powerup.kill()
                    
    def spawn_powerup(self, x, y):
        powerup_type = random.choice(list(POWERUP_TYPES.keys()))
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.add(powerup)
        
    def fortify_base(self):
        self.game_map.fortify_base()
        
    def check_game_state(self):
        if self.game_map.base_destroyed:
            self.game_over = True
            return
            
        alive_players = [p for p in self.players if p.lives > 0]
        if not alive_players:
            self.game_over = True
            return
            
        if len(self.enemies) == 0 and self.enemies_to_spawn == 0:
            self.current_level += 1
            self.load_level(self.current_level)
            
    def draw(self):
        self.screen.fill(BLACK)
        
        self.game_map.draw(self.screen, draw_grass=False)
        
        for player in self.players:
            player.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        self.bullets.draw(self.screen)
        
        self.game_map.draw(self.screen, draw_grass=True)
        
        self.powerups.draw(self.screen)
        
        self.draw_hud()
        
        if self.paused:
            self.draw_pause_screen()
            
    def draw_hud(self):
        lives_text = self.font.render(f"Lives: {self.players[0].lives if self.players else 0}", True, WHITE)
        self.screen.blit(lives_text, (10, SCREEN_HEIGHT - 30))
        
        level_text = self.font.render(f"Level: {self.current_level + 1}", True, WHITE)
        level_rect = level_text.get_rect(right=SCREEN_WIDTH - 10, top=SCREEN_HEIGHT - 30)
        self.screen.blit(level_text, level_rect)
        
        enemies_text = self.small_font.render(f"Enemies: {self.enemies_to_spawn + len(self.enemies)}", True, WHITE)
        enemies_rect = enemies_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        self.screen.blit(enemies_text, enemies_rect)
        
        if len(self.players) > 1:
            p2_lives = self.font.render(f"P2: {self.players[1].lives if len(self.players) > 1 else 0}", True, CYAN)
            self.screen.blit(p2_lives, (10, SCREEN_HEIGHT - 60))
            
    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.small_font.render("Press ESC or P to resume", True, GRAY)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(resume_text, resume_rect)
        
    def run_game_over(self):
        while self.state == 'game_over':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = 'menu'
                    elif event.key == pygame.K_ESCAPE:
                        return False
                        
            self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        return True
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        if self.victory:
            text = self.font.render("VICTORY!", True, GREEN)
        else:
            text = self.font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)
        
        level_text = self.font.render(f"Reached Level: {self.current_level + 1}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(level_text, level_rect)
        
        restart_text = self.small_font.render("Press ENTER to return to menu", True, GRAY)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
