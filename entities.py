import pygame
import math
import random
from config import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, owner, power=1):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = speed
        self.owner = owner
        self.power = power
        
    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed
            
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
    
    def can_pass_water(self):
        return True
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed, bullet_speed, health=1, is_player=False, player_id=1):
        super().__init__()
        self.size = TILE_SIZE - 4
        self.color = color
        self.speed = speed
        self.bullet_speed = bullet_speed
        self.health = health
        self.max_health = health
        self.is_player = is_player
        self.player_id = player_id
        self.direction = 'up'
        self.level = 1
        self.shield = False
        self.shield_timer = 0
        self.frozen = False
        self.frozen_timer = 0
        
        self.image = self.create_tank_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.bullet = None
        self.can_shoot = True
        self.shoot_cooldown = 0
        
        self.on_ice = False
        self.ice_velocity = [0, 0]
        
    def create_tank_image(self):
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color, (0, 0, self.size, self.size))
        pygame.draw.rect(surface, BLACK, (0, 0, self.size, self.size), 2)
        
        barrel_width = 8
        barrel_length = self.size // 2 + 6
        
        if self.direction == 'up':
            pygame.draw.rect(surface, self.color, 
                           (self.size//2 - barrel_width//2, -4, barrel_width, barrel_length))
            pygame.draw.rect(surface, BLACK, 
                           (self.size//2 - barrel_width//2, -4, barrel_width, barrel_length), 1)
            pygame.draw.circle(surface, self.color, (self.size//2, barrel_length - 6), barrel_width//2 + 1)
            pygame.draw.circle(surface, BLACK, (self.size//2, barrel_length - 6), barrel_width//2 + 1, 1)
        elif self.direction == 'down':
            pygame.draw.rect(surface, self.color, 
                           (self.size//2 - barrel_width//2, self.size - barrel_length + 4, barrel_width, barrel_length))
            pygame.draw.rect(surface, BLACK, 
                           (self.size//2 - barrel_width//2, self.size - barrel_length + 4, barrel_width, barrel_length), 1)
            pygame.draw.circle(surface, self.color, (self.size//2, self.size - barrel_length + 6), barrel_width//2 + 1)
            pygame.draw.circle(surface, BLACK, (self.size//2, self.size - barrel_length + 6), barrel_width//2 + 1, 1)
        elif self.direction == 'left':
            pygame.draw.rect(surface, self.color, 
                           (-4, self.size//2 - barrel_width//2, barrel_length, barrel_width))
            pygame.draw.rect(surface, BLACK, 
                           (-4, self.size//2 - barrel_width//2, barrel_length, barrel_width), 1)
            pygame.draw.circle(surface, self.color, (barrel_length - 6, self.size//2), barrel_width//2 + 1)
            pygame.draw.circle(surface, BLACK, (barrel_length - 6, self.size//2), barrel_width//2 + 1, 1)
        elif self.direction == 'right':
            pygame.draw.rect(surface, self.color, 
                           (self.size - barrel_length + 4, self.size//2 - barrel_width//2, barrel_length, barrel_width))
            pygame.draw.rect(surface, BLACK, 
                           (self.size - barrel_length + 4, self.size//2 - barrel_width//2, barrel_length, barrel_width), 1)
            pygame.draw.circle(surface, self.color, (self.size - barrel_length + 6, self.size//2), barrel_width//2 + 1)
            pygame.draw.circle(surface, BLACK, (self.size - barrel_length + 6, self.size//2), barrel_width//2 + 1, 1)
        
        return surface
    
    def rotate(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.image = self.create_tank_image()
            
    def move(self, dx, dy, game_map, tanks):
        if self.frozen:
            return False
            
        new_rect = self.rect.copy()
        new_rect.x += dx
        new_rect.y += dy
        
        if new_rect.left < 0 or new_rect.right > SCREEN_WIDTH:
            return False
        if new_rect.top < 0 or new_rect.bottom > SCREEN_HEIGHT:
            return False
            
        tile_x = new_rect.centerx // TILE_SIZE
        tile_y = new_rect.centery // TILE_SIZE
        
        for check_y in range(max(0, tile_y - 1), min(MAP_HEIGHT, tile_y + 2)):
            for check_x in range(max(0, tile_x - 1), min(MAP_WIDTH, tile_x + 2)):
                tile = game_map.get_tile(check_x, check_y)
                if tile in [BRICK, STEEL, BASE]:
                    tile_rect = pygame.Rect(check_x * TILE_SIZE, check_y * TILE_SIZE, 
                                          TILE_SIZE, TILE_SIZE)
                    if new_rect.colliderect(tile_rect):
                        return False
        
        for tank in tanks:
            if tank != self and new_rect.colliderect(tank.rect):
                return False
                
        self.rect = new_rect
        return True
    
    def shoot(self, bullets_group):
        if self.bullet is None and self.can_shoot and not self.frozen:
            bullet_x, bullet_y = self.rect.center
            if self.direction == 'up':
                bullet_y = self.rect.top
            elif self.direction == 'down':
                bullet_y = self.rect.bottom
            elif self.direction == 'left':
                bullet_x = self.rect.left
            elif self.direction == 'right':
                bullet_x = self.rect.right
                
            power = self.level if self.is_player else 1
            self.bullet = Bullet(bullet_x, bullet_y, self.direction, 
                               self.bullet_speed, self, power)
            bullets_group.add(self.bullet)
            self.can_shoot = False
            self.shoot_cooldown = 15 if self.is_player else 30
            return True
        return False
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown == 0:
                self.can_shoot = True
                
        if self.bullet is not None and not self.bullet.alive():
            self.bullet = None
            
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False
                
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
                
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.shield:
            shield_surface = pygame.Surface((self.size + 8, self.size + 8), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (255, 255, 255, 128), 
                             (self.size // 2 + 4, self.size // 2 + 4), self.size // 2 + 4, 2)
            screen.blit(shield_surface, (self.rect.x - 4, self.rect.y - 4))
            
    def hit(self, damage=1):
        if self.shield:
            return False
        self.health -= damage
        return self.health <= 0
    
    def upgrade(self):
        if self.level < 4:
            self.level += 1
            self.bullet_speed = PLAYER_BULLET_SPEED + self.level
            
    def activate_shield(self, duration=300):
        self.shield = True
        self.shield_timer = duration
        
    def freeze(self, duration=300):
        self.frozen = True
        self.frozen_timer = duration


class PlayerTank(Tank):
    def __init__(self, x, y, player_id=1):
        super().__init__(x, y, YELLOW, PLAYER_SPEED, PLAYER_BULLET_SPEED, 
                        health=1, is_player=True, player_id=player_id)
        self.lives = 3
        self.spawn_x = x
        self.spawn_y = y
        
    def respawn(self):
        self.rect.center = (self.spawn_x, self.spawn_y)
        self.direction = 'up'
        self.image = self.create_tank_image()
        self.level = 1
        self.bullet_speed = PLAYER_BULLET_SPEED
        self.activate_shield(180)
        
    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            self.respawn()
            return True
        return False


class EnemyTank(Tank):
    def __init__(self, x, y, enemy_type='basic'):
        stats = ENEMY_TYPES[enemy_type]
        super().__init__(x, y, stats['color'], stats['speed'], 
                        stats['bullet_speed'], stats['health'])
        self.enemy_type = enemy_type
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.image = self.create_tank_image()
        self.move_timer = 0
        self.move_direction = self.direction
        self.has_powerup = random.random() < 0.2
        self.ai_timer = 0
        self.target_direction = None
        
    def ai_update(self, game_map, tanks, player_tanks, bullets_group):
        if self.frozen:
            return
            
        self.ai_timer += 1
        
        if self.ai_timer >= 120 and self.target_direction is None:
            self.ai_timer = 0
            self.choose_direction(player_tanks)
            
        dx, dy = 0, 0
        if self.move_direction == 'up':
            dy = -self.speed
        elif self.move_direction == 'down':
            dy = self.speed
        elif self.move_direction == 'left':
            dx = -self.speed
        elif self.move_direction == 'right':
            dx = self.speed
            
        if self.direction != self.move_direction:
            self.rotate(self.move_direction)
            
        moved = self.move(dx, dy, game_map, tanks)
        
        if not moved:
            self.ai_timer = 0
            self.choose_direction(player_tanks)
        elif random.random() < 0.005:
            self.ai_timer = 0
            self.choose_direction(player_tanks)
            
        if random.random() < 0.02:
            self.shoot(bullets_group)
            
    def choose_direction(self, player_tanks):
        if player_tanks and random.random() < 0.5:
            nearest_player = min(player_tanks, 
                               key=lambda p: math.hypot(p.rect.centerx - self.rect.centerx,
                                                       p.rect.centery - self.rect.centery))
            dx = nearest_player.rect.centerx - self.rect.centerx
            dy = nearest_player.rect.centery - self.rect.centery
            
            if abs(dx) > abs(dy):
                self.move_direction = 'right' if dx > 0 else 'left'
            else:
                self.move_direction = 'down' if dy > 0 else 'up'
        else:
            self.move_direction = random.choice(['up', 'down', 'left', 'right'])
