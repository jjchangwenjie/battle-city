import pygame
import random
import math
from config import *

class GameMap:
    def __init__(self, level_data):
        self.tiles = [row[:] for row in level_data]
        self.base_destroyed = False
        self.fortified = False
        self.fortify_timer = 0
        
    def get_tile(self, x, y):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            return self.tiles[y][x]
        return EMPTY
    
    def set_tile(self, x, y, tile_type):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            self.tiles[y][x] = tile_type
            
    def destroy_tile(self, x, y, power=1):
        tile = self.get_tile(x, y)
        if tile == BRICK:
            self.set_tile(x, y, EMPTY)
            return True
        elif tile == STEEL and power >= 3:
            self.set_tile(x, y, EMPTY)
            return True
        elif tile == BASE:
            self.base_destroyed = True
            self.set_tile(x, y, EMPTY)
            return True
        return False
    
    def fortify_base(self):
        self.fortified = True
        self.fortify_timer = 600
        
        for y in range(MAP_HEIGHT - 2, MAP_HEIGHT):
            for x in range(MAP_WIDTH // 2 - 2, MAP_WIDTH // 2 + 3):
                if self.get_tile(x, y) == BRICK:
                    self.set_tile(x, y, STEEL)
                    
    def update(self):
        if self.fortified:
            self.fortify_timer -= 1
            if self.fortify_timer <= 0:
                self.fortified = False
                for y in range(MAP_HEIGHT - 2, MAP_HEIGHT):
                    for x in range(MAP_WIDTH // 2 - 2, MAP_WIDTH // 2 + 3):
                        if self.get_tile(x, y) == STEEL:
                            self.set_tile(x, y, BRICK)
    
    def draw(self, screen, draw_grass=True):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.tiles[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if tile == BRICK:
                    self.draw_brick(screen, rect)
                elif tile == STEEL:
                    self.draw_steel(screen, rect)
                elif tile == WATER:
                    self.draw_water(screen, rect)
                elif tile == ICE:
                    self.draw_ice(screen, rect)
                elif tile == BASE:
                    self.draw_base(screen, rect)
                elif tile == GRASS:
                    pass
                    
        if draw_grass:
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    tile = self.tiles[y][x]
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if tile == GRASS:
                        self.draw_grass(screen, rect)
                        
    def draw_brick(self, screen, rect):
        pygame.draw.rect(screen, BROWN, rect)
        brick_width = TILE_SIZE // 4
        brick_height = TILE_SIZE // 4
        for row in range(4):
            for col in range(4):
                bx = rect.x + col * brick_width
                by = rect.y + row * brick_height
                pygame.draw.rect(screen, DARK_GRAY, (bx, by, brick_width, brick_height), 1)
                
    def draw_steel(self, screen, rect):
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, WHITE, rect, 3)
        pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomright, 2)
        pygame.draw.line(screen, WHITE, rect.topright, rect.bottomleft, 2)
        
    def draw_water(self, screen, rect):
        pygame.draw.rect(screen, BLUE, rect)
        for i in range(4):
            wave_y = rect.y + 10 + i * 8
            for j in range(3):
                wave_x = rect.x + j * 15 + (i % 2) * 7
                pygame.draw.arc(screen, CYAN, (wave_x, wave_y, 15, 8), 0, 3.14, 2)
                
    def draw_ice(self, screen, rect):
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, CYAN, rect, 2)
        for i in range(3):
            for j in range(3):
                sparkle_x = rect.x + 10 + i * 12
                sparkle_y = rect.y + 10 + j * 12
                pygame.draw.circle(screen, CYAN, (sparkle_x, sparkle_y), 2)
                
    def draw_grass(self, screen, rect):
        grass_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(grass_surface, (0, 100, 0, 180), (0, 0, TILE_SIZE, TILE_SIZE))
        for i in range(8):
            gx = random.randint(0, TILE_SIZE - 4)
            gy = random.randint(0, TILE_SIZE - 4)
            pygame.draw.line(grass_surface, GREEN, (gx, gy), (gx, gy - 5), 2)
        screen.blit(grass_surface, rect)
        
    def draw_base(self, screen, rect):
        pygame.draw.rect(screen, BLACK, rect)
        eagle_points = [
            (rect.centerx, rect.y + 5),
            (rect.x + 5, rect.centery),
            (rect.centerx, rect.bottom - 5),
            (rect.right - 5, rect.centery)
        ]
        pygame.draw.polygon(screen, YELLOW, eagle_points)
        pygame.draw.polygon(screen, ORANGE, eagle_points, 2)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.type = powerup_type
        self.color = POWERUP_TYPES[powerup_type]['color']
        self.effect = POWERUP_TYPES[powerup_type]['effect']
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.draw_powerup()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 600
        
    def draw_powerup(self):
        pygame.draw.rect(self.image, self.color, (4, 4, TILE_SIZE - 8, TILE_SIZE - 8))
        pygame.draw.rect(self.image, WHITE, (4, 4, TILE_SIZE - 8, TILE_SIZE - 8), 2)
        
        if self.type == 'star':
            self.draw_star()
        elif self.type == 'grenade':
            self.draw_grenade()
        elif self.type == 'helmet':
            self.draw_helmet()
        elif self.type == 'shovel':
            self.draw_shovel()
        elif self.type == 'tank':
            self.draw_tank_icon()
        elif self.type == 'clock':
            self.draw_clock()
            
    def draw_star(self):
        center = TILE_SIZE // 2
        points = []
        for i in range(5):
            angle = i * 72 - 90
            x = center + 12 * math.cos(math.radians(angle))
            y = center + 12 * math.sin(math.radians(angle))
            points.append((x, y))
            angle += 36
            x = center + 6 * math.cos(math.radians(angle))
            y = center + 6 * math.sin(math.radians(angle))
            points.append((x, y))
        pygame.draw.polygon(self.image, BLACK, points)
        
    def draw_grenade(self):
        center = TILE_SIZE // 2
        pygame.draw.circle(self.image, BLACK, (center, center), 8)
        pygame.draw.line(self.image, BLACK, (center, center - 8), (center + 4, center - 12), 2)
        
    def draw_helmet(self):
        pygame.draw.arc(self.image, BLACK, (8, 8, TILE_SIZE - 16, TILE_SIZE - 16), 0, 3.14, 3)
        pygame.draw.line(self.image, BLACK, (8, TILE_SIZE // 2), (TILE_SIZE - 8, TILE_SIZE // 2), 3)
        
    def draw_shovel(self):
        center = TILE_SIZE // 2
        pygame.draw.line(self.image, BLACK, (center, 8), (center, TILE_SIZE - 8), 3)
        pygame.draw.ellipse(self.image, BLACK, (center - 8, TILE_SIZE - 16, 16, 10))
        
    def draw_tank_icon(self):
        pygame.draw.rect(self.image, BLACK, (12, 10, TILE_SIZE - 24, TILE_SIZE - 20))
        pygame.draw.rect(self.image, BLACK, (TILE_SIZE // 2 - 3, 4, 6, 10))
        
    def draw_clock(self):
        center = TILE_SIZE // 2
        pygame.draw.circle(self.image, BLACK, (center, center), 12, 2)
        pygame.draw.line(self.image, BLACK, (center, center), (center, center - 8), 2)
        pygame.draw.line(self.image, BLACK, (center, center), (center + 6, center), 2)
        
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            
    def apply(self, player, game, enemies):
        if self.effect == 'upgrade':
            player.upgrade()
        elif self.effect == 'destroy_all':
            for enemy in enemies:
                enemy.kill()
        elif self.effect == 'shield':
            player.activate_shield()
        elif self.effect == 'fortify':
            game.fortify_base()
        elif self.effect == 'extra_life':
            player.lives += 1
        elif self.effect == 'freeze':
            for enemy in enemies:
                enemy.freeze()
