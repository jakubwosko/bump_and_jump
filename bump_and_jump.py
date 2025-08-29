#################################################################################################
# Bump n Jump - Modern Homage to the 1982 Arcade Classic
# 
# August 2025
#################################################################################################

import pygame, sys, time, random, math
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((600, 800))
pygame.display.set_caption('BUMP N JUMP')

# Create car icon for the window
def create_car_icon():
    icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    icon_surface.fill((0, 0, 0, 0))
    
    # F1 car icon design
    # Front wing
    pygame.draw.rect(icon_surface, (100, 100, 100), (4, 8, 24, 2))
    
    # Nose cone
    pygame.draw.polygon(icon_surface, (255, 0, 0), [(16, 10), (12, 14), (20, 14)])
    
    # Main body
    pygame.draw.rect(icon_surface, (255, 0, 0), (12, 14, 8, 10))
    
    # Side pods
    pygame.draw.polygon(icon_surface, (255, 0, 0), [(8, 16), (12, 14), (12, 20), (10, 22)])
    pygame.draw.polygon(icon_surface, (255, 0, 0), [(24, 16), (20, 14), (20, 20), (22, 22)])
    
    # Cockpit
    pygame.draw.rect(icon_surface, (0, 0, 0), (14, 16, 4, 4))
    
    # Wheels (exposed)
    pygame.draw.rect(icon_surface, (50, 50, 50), (6, 12, 4, 6))  # Front left
    pygame.draw.rect(icon_surface, (50, 50, 50), (22, 12, 4, 6))  # Front right
    pygame.draw.rect(icon_surface, (50, 50, 50), (6, 20, 4, 6))  # Rear left
    pygame.draw.rect(icon_surface, (50, 50, 50), (22, 20, 4, 6))  # Rear right
    
    # Rear wing
    pygame.draw.rect(icon_surface, (100, 100, 100), (6, 26, 20, 2))
    
    return icon_surface

# Set the window icon
car_icon = create_car_icon()
pygame.display.set_icon(car_icon)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
SILVER = (192, 192, 192)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)

# Road and environment colors
ROAD_COLOR = (80, 80, 80)
ROAD_LINE_COLOR = (255, 255, 0)
GRASS_COLOR = (34, 139, 34)
WATER_COLOR = (0, 100, 200)
GUARDRAIL_COLOR = (150, 150, 150)

# Car colors for variety
CAR_COLORS = [
    (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
    (0, 255, 255), (255, 128, 0), (128, 255, 0), (255, 255, 255),
    (128, 0, 128), (0, 128, 255)
]

screen.fill(BLACK)

def print_hud(score, fuel, stage, hiscore, speed, lives, jump_cooldown=0, jump_cooldown_max=300):
    # Clear top area
    pygame.draw.rect(screen, BLACK, (0, 0, 600, 80))
    
    font = pygame.font.SysFont("monospace", 14, bold=True)
    # First row
    scoretext = font.render("SCORE: " + str(score), 1, WHITE)
    screen.blit(scoretext, (10, 10))
    
    hiscoretext = font.render("HI SCORE: " + str(hiscore), 1, YELLOW)
    screen.blit(hiscoretext, (200, 10))
    
    stagetext = font.render("STAGE: " + str(stage), 1, CYAN)
    screen.blit(stagetext, (400, 10))
    
    # Second row
    fuel_display = max(0, round(fuel))  # Ensure fuel display matches game logic
    fueltext = font.render("FUEL: " + str(fuel_display), 1, GREEN if fuel > 20 else RED)
    screen.blit(fueltext, (10, 35))
    
    livestext = font.render("LIVES: " + str(lives), 1, RED if lives <= 2 else WHITE)
    screen.blit(livestext, (200, 35))
    
    speedtext = font.render("SPEED: " + str(int(speed)), 1, WHITE)
    screen.blit(speedtext, (400, 35))
    
    # Jump countdown display
    if jump_cooldown > 0:
        countdown_seconds = (jump_cooldown // 60) + 1  # Convert frames to seconds, round up
        if countdown_seconds > 1:
            jumptext = font.render("JUMP: " + str(countdown_seconds), 1, ORANGE)
        else:
            jumptext = font.render("JUMP: READY", 1, GREEN)
        screen.blit(jumptext, (10, 60))
    else:
        # Draw "JUMP" with small car icon
        jumptext = font.render("JUMP:", 1, GREEN)
        screen.blit(jumptext, (10, 60))
        
        # Draw small car icon
        car_x = 70
        car_y = 62
        pygame.draw.rect(screen, RED, (car_x, car_y, 12, 8))  # Car body
        pygame.draw.circle(screen, BLACK, (car_x + 2, car_y + 8), 2)  # Left wheel
        pygame.draw.circle(screen, BLACK, (car_x + 10, car_y + 8), 2)  # Right wheel

def print_stage_message(stage):
    # Create transparent background surface
    banner_surface = pygame.Surface((300, 70), pygame.SRCALPHA)
    banner_surface.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(banner_surface, (150, 365))
    
    # Stage message with smaller font
    font = pygame.font.SysFont("monospace", 28, bold=True)
    stage_msg = font.render("STAGE " + str(stage), 1, YELLOW)
    msg_width = stage_msg.get_width()
    screen.blit(stage_msg, ((600 - msg_width) // 2, 375))
    
    # Stage description with smaller font
    descriptions = ["SUBURBAN HIGHWAY", "RIVERSIDE ROAD", "INDUSTRIAL ZONE", "CANYON PASS", "DEATH VALLEY"]
    desc = descriptions[min(stage - 1, len(descriptions) - 1)]
    font = pygame.font.SysFont("monospace", 12)
    desc_msg = font.render(desc, 1, WHITE)
    msg_width = desc_msg.get_width()
    screen.blit(desc_msg, ((600 - msg_width) // 2, 405))

def print_pause_message():
    # Clear center area for pause message
    pygame.draw.rect(screen, BLACK, (150, 350, 300, 100))
    
    # Pause message
    font = pygame.font.SysFont("monospace", 50, bold=True)
    pause_msg = font.render("PAUSED", 1, CYAN)
    msg_width = pause_msg.get_width()
    screen.blit(pause_msg, ((600 - msg_width) // 2, 380))
    
    # Instructions
    font = pygame.font.SysFont("monospace", 16)
    inst_msg = font.render("Press P to resume", 1, WHITE)
    msg_width = inst_msg.get_width()
    screen.blit(inst_msg, ((600 - msg_width) // 2, 420))

def print_gameover(score, reason="OUT OF FUEL", is_new_hiscore=False):
    # Clear center area for game over message
    pygame.draw.rect(screen, BLACK, (100, 300, 400, 200))
    
    font = pygame.font.SysFont("monospace", 40, bold=True)
    textgm = font.render("GAME OVER", 1, RED)
    msg_width = textgm.get_width()
    screen.blit(textgm, ((600 - msg_width) // 2, 340))
    
    font = pygame.font.SysFont("monospace", 14)
    reason_text = font.render(reason, 1, WHITE)
    msg_width = reason_text.get_width()
    screen.blit(reason_text, ((600 - msg_width) // 2, 380))
    
    # Show new high score message if applicable
    if is_new_hiscore:
        font = pygame.font.SysFont("monospace", 18, bold=True)
        hiscore_text = font.render("NEW HIGH SCORE!", 1, YELLOW)
        msg_width = hiscore_text.get_width()
        screen.blit(hiscore_text, ((600 - msg_width) // 2, 400))
        y_offset = 20
    else:
        y_offset = 0
    
    font = pygame.font.SysFont("monospace", 16)
    textgm = font.render("FINAL SCORE: " + str(score), 1, WHITE)
    msg_width = textgm.get_width()
    screen.blit(textgm, ((600 - msg_width) // 2, 420 + y_offset))
    
    font = pygame.font.SysFont("monospace", 14, bold=True)
    textgm = font.render("Press SPACE to play again", 1, YELLOW)
    msg_width = textgm.get_width()
    screen.blit(textgm, ((600 - msg_width) // 2, 460 + y_offset))
    
    font = pygame.font.SysFont("monospace", 12)
    textgm = font.render("Press ESC to quit", 1, WHITE)
    msg_width = textgm.get_width()
    screen.blit(textgm, ((600 - msg_width) // 2, 480 + y_offset))

def print_startgame(hiscore=0):
    screen.fill(BLACK)
    
    # Draw road background (50% wider)
    pygame.draw.rect(screen, ROAD_COLOR, (150, 0, 300, 800))
    
    # Draw road lines
    for y in range(0, 800, 40):
        pygame.draw.rect(screen, ROAD_LINE_COLOR, (295, y, 10, 20))
    
    # Draw grass on sides
    pygame.draw.rect(screen, GRASS_COLOR, (0, 0, 150, 800))
    pygame.draw.rect(screen, GRASS_COLOR, (450, 0, 150, 800))
    
    # Rainbow colors for title
    letter_colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE, SILVER, RED, ORANGE, YELLOW]
    
    font = pygame.font.SysFont("monospace", 80, bold=True)
    title = "BUMP N JUMP"
    
    # Calculate total width to center the title
    total_width = 0
    letter_widths = []
    for letter in title:
        letter_surface = font.render(letter, 1, WHITE)
        letter_width = letter_surface.get_width()
        letter_widths.append(letter_width)
        total_width += letter_width
    
    # Starting x position to center the title
    start_x = (600 - total_width) // 2
    current_x = start_x
    
    # Draw each letter in different color
    for i, letter in enumerate(title):
        if letter != ' ':
            color = letter_colors[i % len(letter_colors)]
            letter_surface = font.render(letter, 1, color)
            screen.blit(letter_surface, (current_x, 180))
        current_x += letter_widths[i]
    
    # Subtitle
    font_small = pygame.font.SysFont("monospace", 12)
    subtitle = font_small.render("Modern Homage to the 1982 Arcade Classic", 1, SILVER)
    subtitle_width = subtitle.get_width()
    screen.blit(subtitle, ((600 - subtitle_width) // 2, 280))
    
    # Instructions
    font = pygame.font.SysFont("monospace", 18)
    instructions = [
        "ARROWS: Steer and accelerate",
        "SPACE: Jump over obstacles",
        "",
        "Press any key to start"
    ]
    
    for i, instruction in enumerate(instructions):
        color = WHITE if instruction != "Press any key to start" else YELLOW
        text = font.render(instruction, 1, color)
        text_width = text.get_width()
        screen.blit(text, ((600 - text_width) // 2, 320 + i * 25))
    
    # Display high score if it exists
    if hiscore > 0:
        font_hiscore = pygame.font.SysFont("monospace", 18, bold=True)
        hiscore_text = font_hiscore.render("HIGH SCORE: " + str(hiscore), 1, YELLOW)
        msg_width = hiscore_text.get_width()
        screen.blit(hiscore_text, ((600 - msg_width) // 2, 550))
    
    pygame.display.update()

# Game entity classes
class Car:
    def __init__(self, x, y, color, car_type="player"):
        self.x = x
        self.y = y
        self.color = color
        self.width = 36  # Wider
        self.height = 42  # Shorter
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.deceleration = 0.2
        self.turn_speed = 0
        self.max_turn_speed = 4
        self.car_type = car_type
        self.jumping = False
        self.jump_height = 0
        self.jump_velocity = 0
        self.shadow_y = y
        
    def update(self):
        # Only update enemy cars - player car is handled separately
        if self.car_type == "enemy":
            # Update position
            self.x += self.turn_speed
            self.y += self.speed
            
            # Handle jumping physics
            if self.jumping:
                self.jump_velocity += 0.5  # gravity
                self.jump_height += self.jump_velocity
                if self.jump_height <= 0:
                    self.jump_height = 0
                    self.jumping = False
                    self.jump_velocity = 0
            
            # Keep car on screen horizontally
            if self.x < 150:
                self.x = 150
            elif self.x > 420:
                self.x = 420
    
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_velocity = 0  # Will be controlled by timer system
            self.jump_height = 0
    
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        
        # Draw shadow when jumping
        if self.jumping:
            shadow_y = self.shadow_y - camera_y
            pygame.draw.ellipse(screen, (50, 50, 50), (self.x + 5, shadow_y + 34, 26, 10))
        
        # Draw car (elevated when jumping)
        car_y = draw_y - self.jump_height
        center_x = self.x + self.width // 2
        
        # Calculate scale factor based on jump height for perspective effect
        # Scale increases as car jumps higher (1.0 to 1.3)
        scale_factor = 1.0 + (self.jump_height / 100.0) * 0.3
        
        # Modern F1 car design - aerodynamic and iconic
        
        # Front wheels (large, exposed, positioned outside main body)
        wheel_width = int(10 * scale_factor)
        wheel_height = int(14 * scale_factor)
        wheel_offset = int(4 * scale_factor)
        wheel_y_offset = int(8 * scale_factor)
        pygame.draw.rect(screen, BLACK, (center_x - 18 - wheel_offset, car_y + wheel_y_offset, wheel_width, wheel_height))
        pygame.draw.rect(screen, BLACK, (center_x + 12 + wheel_offset, car_y + wheel_y_offset, wheel_width, wheel_height))
        
        # Front wing (wide, multi-element aerodynamic wing)
        wing_width = int(40 * scale_factor)
        wing_height = int(3 * scale_factor)
        wing_y_offset = int(2 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - wing_width//2 - 2, car_y + wing_y_offset, wing_width, wing_height))
        pygame.draw.rect(screen, SILVER, (center_x - int(36 * scale_factor)//2, car_y + int(5 * scale_factor), int(36 * scale_factor), int(2 * scale_factor)))
        
        # Nose cone (sharp, aerodynamic point)
        nose_color = (min(255, self.color[0] + 30), min(255, self.color[1] + 30), min(255, self.color[2] + 30))
        nose_width = int(6 * scale_factor)
        nose_y_offset = int(7 * scale_factor)
        nose_height = int(5 * scale_factor)
        pygame.draw.polygon(screen, nose_color, [
            (center_x, car_y + nose_y_offset),
            (center_x - nose_width, car_y + nose_y_offset + nose_height),
            (center_x + nose_width, car_y + nose_y_offset + nose_height)
        ])
        
        # Main monocoque (narrow central survival cell)
        mono_width = int(8 * scale_factor)
        mono_height = int(18 * scale_factor)
        mono_y_offset = int(12 * scale_factor)
        pygame.draw.rect(screen, self.color, (center_x - mono_width//2, car_y + mono_y_offset, mono_width, mono_height))
        
        # Side pods (large aerodynamic air intakes)
        pod_offset = int(12 * scale_factor)
        pod_width = int(6 * scale_factor)
        pygame.draw.polygon(screen, self.color, [
            (center_x - pod_offset - pod_width, car_y + int(14 * scale_factor)),
            (center_x - pod_width, car_y + int(12 * scale_factor)),
            (center_x - pod_width, car_y + int(26 * scale_factor)),
            (center_x - pod_offset - int(4 * scale_factor), car_y + int(30 * scale_factor))
        ])
        pygame.draw.polygon(screen, self.color, [
            (center_x + pod_offset + pod_width, car_y + int(14 * scale_factor)),
            (center_x + pod_width, car_y + int(12 * scale_factor)),
            (center_x + pod_width, car_y + int(26 * scale_factor)),
            (center_x + pod_offset + int(4 * scale_factor), car_y + int(30 * scale_factor))
        ])
        
        # Cockpit opening (driver area)
        cockpit_color = BLACK
        cockpit_width = int(6 * scale_factor)
        cockpit_height = int(8 * scale_factor)
        pygame.draw.rect(screen, cockpit_color, (center_x - cockpit_width//2, car_y + int(14 * scale_factor), cockpit_width, cockpit_height))
        
        # Driver helmet (visible in cockpit)
        helmet_radius = int(2 * scale_factor)
        if self.car_type == "player":
            pygame.draw.circle(screen, WHITE, (center_x, car_y + int(18 * scale_factor)), helmet_radius)
        else:
            pygame.draw.circle(screen, YELLOW, (center_x, car_y + int(18 * scale_factor)), helmet_radius)
        
        # Rear wheels (large, exposed)
        rear_wheel_y = int(26 * scale_factor)
        pygame.draw.rect(screen, BLACK, (center_x - 18 - wheel_offset, car_y + rear_wheel_y, wheel_width, wheel_height))
        pygame.draw.rect(screen, BLACK, (center_x + 12 + wheel_offset, car_y + rear_wheel_y, wheel_width, wheel_height))
        
        # Engine cover (tapered, aerodynamic rear)
        engine_width = int(8 * scale_factor)
        engine_taper = int(4 * scale_factor)
        pygame.draw.polygon(screen, self.color, [
            (center_x - engine_width//2, car_y + int(30 * scale_factor)),
            (center_x + engine_width//2, car_y + int(30 * scale_factor)),
            (center_x + engine_taper//2, car_y + int(38 * scale_factor)),
            (center_x - engine_taper//2, car_y + int(38 * scale_factor))
        ])
        
        # Large rear wing (most prominent F1 feature)
        wing_main_width = int(32 * scale_factor)
        wing_main_height = int(3 * scale_factor)
        wing_sub_width = int(28 * scale_factor)
        wing_sub_height = int(2 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - wing_main_width//2, car_y + int(40 * scale_factor), wing_main_width, wing_main_height))
        pygame.draw.rect(screen, SILVER, (center_x - wing_sub_width//2, car_y + int(43 * scale_factor), wing_sub_width, wing_sub_height))
        # Wing endplates
        endplate_width = int(3 * scale_factor)
        endplate_height = int(7 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - wing_main_width//2, car_y + int(38 * scale_factor), endplate_width, endplate_height))
        pygame.draw.rect(screen, DARK_GRAY, (center_x + wing_main_width//2 - endplate_width, car_y + int(38 * scale_factor), endplate_width, endplate_height))
        # Wing supports
        support_width = int(2 * scale_factor)
        support_height = int(5 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - support_width, car_y + int(38 * scale_factor), support_width, support_height))
        pygame.draw.rect(screen, DARK_GRAY, (center_x, car_y + int(38 * scale_factor), support_width, support_height))
        
        # Air intakes (prominent on side pods)
        intake_width = int(3 * scale_factor)
        intake_height = int(6 * scale_factor)
        intake_offset = int(10 * scale_factor)
        pygame.draw.rect(screen, BLACK, (center_x - intake_offset, car_y + int(16 * scale_factor), intake_width, intake_height))
        pygame.draw.rect(screen, BLACK, (center_x + intake_offset - intake_width, car_y + int(16 * scale_factor), intake_width, intake_height))
        
        # Racing number for player car
        if self.car_type == "player":
            stripe_color = WHITE if sum(self.color) < 400 else BLACK
            stripe_width = int(2 * scale_factor)
            stripe_height = int(12 * scale_factor)
            pygame.draw.rect(screen, stripe_color, (center_x - stripe_width//2, car_y + int(14 * scale_factor), stripe_width, stripe_height))
    
    def draw_at_screen_position(self, screen, screen_y):
        # Draw player car at fixed screen position (not affected by camera)
        
        # Draw shadow when jumping
        if self.jumping:
            pygame.draw.ellipse(screen, (50, 50, 50), (self.x + 5, screen_y + 34, 26, 10))
        
        # Draw car (elevated when jumping)
        car_y = screen_y - self.jump_height
        center_x = self.x + self.width // 2
        
        # Calculate scale factor based on jump height for perspective effect
        # Scale increases as car jumps higher (1.0 to 1.3)
        scale_factor = 1.0 + (self.jump_height / 100.0) * 0.3
        
        # Modern F1 car design - rotated 180 degrees for player (facing forward)
        
        # Large rear wing (now at front - most prominent F1 feature)
        wing_main_width = int(32 * scale_factor)
        wing_main_height = int(3 * scale_factor)
        wing_sub_width = int(28 * scale_factor)
        wing_sub_height = int(2 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - wing_main_width//2, car_y + int(2 * scale_factor), wing_main_width, wing_main_height))
        pygame.draw.rect(screen, SILVER, (center_x - wing_sub_width//2, car_y + int(-1 * scale_factor), wing_sub_width, wing_sub_height))
        # Wing endplates
        endplate_width = int(3 * scale_factor)
        endplate_height = int(7 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - wing_main_width//2, car_y + int(2 * scale_factor), endplate_width, endplate_height))
        pygame.draw.rect(screen, DARK_GRAY, (center_x + wing_main_width//2 - endplate_width, car_y + int(2 * scale_factor), endplate_width, endplate_height))
        # Wing supports
        support_width = int(2 * scale_factor)
        support_height = int(5 * scale_factor)
        pygame.draw.rect(screen, DARK_GRAY, (center_x - support_width, car_y + int(2 * scale_factor), support_width, support_height))
        pygame.draw.rect(screen, DARK_GRAY, (center_x, car_y + int(2 * scale_factor), support_width, support_height))
        
        # Engine cover (now at front, tapered aerodynamic front)
        engine_width = int(4 * scale_factor)
        engine_taper = int(8 * scale_factor)
        pygame.draw.polygon(screen, self.color, [
            (center_x - engine_width//2, car_y + int(4 * scale_factor)),
            (center_x + engine_width//2, car_y + int(4 * scale_factor)),
            (center_x + engine_taper//2, car_y + int(12 * scale_factor)),
            (center_x - engine_taper//2, car_y + int(12 * scale_factor))
        ])
        
        # Front wheels (now rear wheels after rotation - large, exposed, positioned outside main body)
        wheel_width = int(10 * scale_factor)
        wheel_height = int(14 * scale_factor)
        wheel_offset = int(4 * scale_factor)
        pygame.draw.rect(screen, BLACK, (center_x - 18 - wheel_offset, car_y + int(5 * scale_factor), wheel_width, wheel_height))
        pygame.draw.rect(screen, BLACK, (center_x + 12 + wheel_offset, car_y + int(5 * scale_factor), wheel_width, wheel_height))
        
        # Side pods (large aerodynamic air intakes) - rotated
        pod_offset = int(12 * scale_factor)
        pod_width = int(6 * scale_factor)
        pygame.draw.polygon(screen, self.color, [
            (center_x - pod_offset - int(4 * scale_factor), car_y + int(12 * scale_factor)),
            (center_x - pod_width, car_y + int(16 * scale_factor)),
            (center_x - pod_width, car_y + int(30 * scale_factor)),
            (center_x - pod_offset - pod_width, car_y + int(28 * scale_factor))
        ])
        pygame.draw.polygon(screen, self.color, [
            (center_x + pod_offset + int(4 * scale_factor), car_y + int(12 * scale_factor)),
            (center_x + pod_width, car_y + int(16 * scale_factor)),
            (center_x + pod_width, car_y + int(30 * scale_factor)),
            (center_x + pod_offset + pod_width, car_y + int(28 * scale_factor))
        ])
        
        # Main monocoque (narrow central survival cell)
        mono_width = int(8 * scale_factor)
        mono_height = int(18 * scale_factor)
        pygame.draw.rect(screen, self.color, (center_x - mono_width//2, car_y + int(12 * scale_factor), mono_width, mono_height))
        
        # Air intakes (prominent on side pods)
        intake_width = int(3 * scale_factor)
        intake_height = int(6 * scale_factor)
        intake_offset = int(10 * scale_factor)
        pygame.draw.rect(screen, BLACK, (center_x - intake_offset, car_y + int(20 * scale_factor), intake_width, intake_height))
        pygame.draw.rect(screen, BLACK, (center_x + intake_offset - intake_width, car_y + int(20 * scale_factor), intake_width, intake_height))
        
        # Cockpit opening (driver area)
        cockpit_color = BLACK
        cockpit_width = int(6 * scale_factor)
        cockpit_height = int(8 * scale_factor)
        pygame.draw.rect(screen, cockpit_color, (center_x - cockpit_width//2, car_y + int(20 * scale_factor), cockpit_width, cockpit_height))
        
        # Driver helmet (visible in cockpit)
        helmet_radius = int(2 * scale_factor)
        if self.car_type == "player":
            pygame.draw.circle(screen, WHITE, (center_x, car_y + int(24 * scale_factor)), helmet_radius)
        else:
            pygame.draw.circle(screen, YELLOW, (center_x, car_y + int(24 * scale_factor)), helmet_radius)
        
        # Rear wheels (now front wheels after rotation - large, exposed)
        pygame.draw.rect(screen, BLACK, (center_x - 18 - wheel_offset, car_y + int(23 * scale_factor), wheel_width, wheel_height))
        pygame.draw.rect(screen, BLACK, (center_x + 12 + wheel_offset, car_y + int(23 * scale_factor), wheel_width, wheel_height))
        
        # Nose cone (sharp, aerodynamic point - now pointing down/forward)
        nose_color = (min(255, self.color[0] + 30), min(255, self.color[1] + 30), min(255, self.color[2] + 30))
        nose_width = int(6 * scale_factor)
        pygame.draw.polygon(screen, nose_color, [
            (center_x, car_y + int(35 * scale_factor)),
            (center_x - nose_width, car_y + int(30 * scale_factor)),
            (center_x + nose_width, car_y + int(30 * scale_factor))
        ])
        
        # Front wing (now rear wing - wide, multi-element aerodynamic wing)
        pygame.draw.rect(screen, SILVER, (self.x, car_y + 37, 36, 2))
        pygame.draw.rect(screen, DARK_GRAY, (self.x - 2, car_y + 39, 40, 3))
        
        # Racing number for player car
        if self.car_type == "player":
            stripe_color = WHITE if sum(self.color) < 400 else BLACK
            pygame.draw.rect(screen, stripe_color, (center_x - 1, car_y + 20, 2, 12))
    

        
class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.width = 40
        self.height = 20
        
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        if self.type == "barrel":
            pygame.draw.ellipse(screen, BROWN, (self.x, draw_y, self.width, self.height))
            pygame.draw.ellipse(screen, DARK_GRAY, (self.x + 5, draw_y + 5, 30, 10))
        elif self.type == "water":
            pygame.draw.rect(screen, WATER_COLOR, (self.x, draw_y, self.width * 3, self.height))

class Bridge:
    def __init__(self, y, stage):
        self.y = y
        self.stage = stage
        self.height = 40  # Bridge height
        self.bridge_clearance = 25  # Height cars need to jump to clear
        # Randomly choose bridge type
        import random
        self.bridge_type = random.choice(["roman", "steel", "medieval"])
        # Note: x and width are calculated dynamically in draw() and check_collision() 
        # to follow road curves properly
        
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        
        # Draw bridge if it's anywhere near the screen (expanded range)
        if draw_y > -100 and draw_y < 900:
            
            # Draw bridge in segments to follow road curves
            # Bridge spans from self.y to self.y + self.height
            bridge_segments = 8  # Number of segments to draw
            segment_height = self.height // bridge_segments
            
            # Store road bounds for each segment
            segment_bounds = []
            for i in range(bridge_segments + 1):
                segment_y = self.y + (i * segment_height)
                road_left, road_right, road_width = get_road_bounds(segment_y, self.stage)
                segment_bounds.append((road_left, road_right, road_width))
            
            # Draw bridge based on type
            if self.bridge_type == "roman":
                self.draw_roman_bridge(screen, draw_y, segment_bounds, bridge_segments, segment_height)
            elif self.bridge_type == "steel":
                self.draw_steel_bridge(screen, draw_y, segment_bounds, bridge_segments, segment_height)
            else:  # medieval bridge
                self.draw_medieval_bridge(screen, draw_y, segment_bounds, bridge_segments, segment_height)

    
    def draw_roman_bridge(self, screen, draw_y, segment_bounds, bridge_segments, segment_height):
        """Draw a Roman-style stone bridge with arches"""
        # Roman bridge colors
        stone_color = (180, 160, 140)
        stone_dark = (140, 120, 100)
        mortar_color = (220, 220, 200)
        
        # Draw bridge pillars at the start and end positions
        start_road_left, start_road_right, start_road_width = segment_bounds[0]
        end_road_left, end_road_right, end_road_width = segment_bounds[-1]
        
        pillar_width = 25
        pillar_height = self.height + 25
        
        # Left pillar - positioned at average of start and end positions
        avg_left = (start_road_left + end_road_left) // 2
        left_pillar_x = avg_left - 20
        pygame.draw.rect(screen, stone_color, (left_pillar_x, draw_y - 15, pillar_width, pillar_height))
        
        # Right pillar - positioned at average of start and end positions  
        avg_right = (start_road_right + end_road_right) // 2
        right_pillar_x = avg_right - 5
        pygame.draw.rect(screen, stone_color, (right_pillar_x, draw_y - 15, pillar_width, pillar_height))
        
        # Draw stone block pattern on pillars
        block_width = 12
        block_height = 8
        for pillar_x in [left_pillar_x, right_pillar_x]:
            for row in range(0, pillar_height, block_height):
                y_pos = draw_y - 15 + row
                # Alternate block offset for realistic pattern
                offset = (block_width // 2) if (row // block_height) % 2 else 0
                for col in range(-offset, pillar_width + offset, block_width):
                    if col + block_width <= pillar_width and col >= 0:
                        # Individual stone block
                        pygame.draw.rect(screen, stone_color, (pillar_x + col, y_pos, block_width - 1, block_height - 1))
                        # Add shadow for depth
                        pygame.draw.rect(screen, stone_dark, (pillar_x + col + block_width - 2, y_pos, 2, block_height - 1))
                        # Mortar lines
                        pygame.draw.rect(screen, mortar_color, (pillar_x + col + block_width - 1, y_pos, 1, block_height))
                        pygame.draw.rect(screen, mortar_color, (pillar_x + col, y_pos + block_height - 1, block_width, 1))
        
        # Draw Roman arch segments
        for i in range(bridge_segments):
            segment_y_offset = i * segment_height
            road_left, road_right, road_width = segment_bounds[i]
            
            # Roman bridge spans road width with adaptive extensions based on road width
            extension = min(15, road_width * 0.1)  # Smaller extension for narrow roads
            bridge_left = road_left - extension
            bridge_width = road_width + (2 * extension)
            
            # Draw main arch structure
            pygame.draw.rect(screen, stone_color, (bridge_left, draw_y + segment_y_offset, bridge_width, segment_height))
            
            # Add stone block pattern
            for row in range(0, segment_height, block_height):
                y_pos = draw_y + segment_y_offset + row
                offset = (block_width // 2) if ((segment_y_offset + row) // block_height) % 2 else 0
                for col in range(-offset, bridge_width + offset, block_width):
                    if col + block_width <= bridge_width and col >= 0:
                        # Stone block with shadow
                        pygame.draw.rect(screen, stone_color, (bridge_left + col, y_pos, block_width - 1, block_height - 1))
                        pygame.draw.rect(screen, stone_dark, (bridge_left + col + block_width - 2, y_pos, 2, block_height - 1))
                        # Mortar lines
                        pygame.draw.rect(screen, mortar_color, (bridge_left + col + block_width - 1, y_pos, 1, block_height))
                        pygame.draw.rect(screen, mortar_color, (bridge_left + col, y_pos + block_height - 1, block_width, 1))
        
        # Roman arch decoration at the center
        center_road_left, center_road_right, center_road_width = segment_bounds[bridge_segments // 2]
        arch_center_x = center_road_left + center_road_width // 2
        arch_y = draw_y + self.height // 2
        
        # Draw decorative arch opening
        pygame.draw.ellipse(screen, (50, 50, 50), (arch_center_x - 15, arch_y - 8, 30, 16))
        pygame.draw.ellipse(screen, stone_dark, (arch_center_x - 13, arch_y - 6, 26, 12))
        
        # Stone capstone on top
        top_road_left, top_road_right, top_road_width = segment_bounds[0]
        extension = min(15, top_road_width * 0.1)
        capstone_left = top_road_left - extension
        capstone_width = top_road_width + (2 * extension)
        pygame.draw.rect(screen, mortar_color, (capstone_left, draw_y - 3, capstone_width, 3))
        
        # Bridge shadow
        shadow_road_left, shadow_road_right, shadow_road_width = get_road_bounds(self.y + 18, self.stage)
        shadow_left = shadow_road_left + 8
        shadow_width = shadow_road_width - 16
        pygame.draw.rect(screen, (30, 30, 30), (shadow_left, draw_y + 18, shadow_width, 25))
        
        # Warning signs
        if draw_y > 60 and draw_y < 150:
            sign_road_left, sign_road_right, sign_road_width = get_road_bounds(self.y + 50, self.stage)
            sign_x = sign_road_left + sign_road_width // 2 - 15
            sign_y = draw_y + 50
            
            # Sign post
            pygame.draw.rect(screen, BROWN, (sign_x + 13, sign_y + 20, 4, 25))
            
            # Warning sign - diamond shape
            pygame.draw.polygon(screen, YELLOW, [
                (sign_x + 15, sign_y),      # top
                (sign_x + 30, sign_y + 10), # right  
                (sign_x + 15, sign_y + 20), # bottom
                (sign_x, sign_y + 10)       # left
            ])
            pygame.draw.polygon(screen, BLACK, [
                (sign_x + 15, sign_y),
                (sign_x + 30, sign_y + 10),
                (sign_x + 15, sign_y + 20),
                (sign_x, sign_y + 10)
            ], 2)
            
            # Roman arch symbol
            pygame.draw.arc(screen, BLACK, (sign_x + 8, sign_y + 8, 14, 8), 0, 3.14159, 2)
            pygame.draw.rect(screen, BLACK, (sign_x + 7, sign_y + 12, 2, 4))
            pygame.draw.rect(screen, BLACK, (sign_x + 21, sign_y + 12, 2, 4))
    
    def draw_steel_bridge(self, screen, draw_y, segment_bounds, bridge_segments, segment_height):
        """Draw a modern steel truss bridge"""
        # Steel bridge colors
        steel_color = (120, 120, 140)
        steel_dark = (80, 80, 100)
        steel_light = (160, 160, 180)
        
        # Draw steel support towers
        start_road_left, start_road_right, start_road_width = segment_bounds[0]
        end_road_left, end_road_right, end_road_width = segment_bounds[-1]
        
        tower_width = 8
        tower_height = self.height + 30
        
        # Left tower
        avg_left = (start_road_left + end_road_left) // 2
        left_tower_x = avg_left - 15
        pygame.draw.rect(screen, steel_color, (left_tower_x, draw_y - 20, tower_width, tower_height))
        pygame.draw.rect(screen, steel_light, (left_tower_x, draw_y - 20, 2, tower_height))  # Highlight
        
        # Right tower
        avg_right = (start_road_right + end_road_right) // 2
        right_tower_x = avg_right + 7
        pygame.draw.rect(screen, steel_color, (right_tower_x, draw_y - 20, tower_width, tower_height))
        pygame.draw.rect(screen, steel_light, (right_tower_x, draw_y - 20, 2, tower_height))  # Highlight
        
        # Draw steel deck segments
        for i in range(bridge_segments):
            segment_y_offset = i * segment_height
            road_left, road_right, road_width = segment_bounds[i]
            
            # Steel bridge spans road width with adaptive extensions
            extension = min(8, road_width * 0.08)  # Smaller extension for steel bridges
            bridge_left = road_left - extension
            bridge_width = road_width + (2 * extension)
            
            # Main steel deck
            pygame.draw.rect(screen, steel_color, (bridge_left, draw_y + segment_y_offset, bridge_width, segment_height))
            
            # Steel beam pattern
            beam_spacing = 15
            for beam_x in range(bridge_left, bridge_left + bridge_width, beam_spacing):
                # Vertical beams
                pygame.draw.rect(screen, steel_dark, (beam_x, draw_y + segment_y_offset, 2, segment_height))
                # Horizontal reinforcement
                if segment_y_offset % 10 == 0:
                    pygame.draw.rect(screen, steel_light, (bridge_left, draw_y + segment_y_offset + segment_height // 2, bridge_width, 1))
        
        # Draw truss structure
        truss_segments = 6
        truss_width = abs(right_tower_x - left_tower_x)
        truss_segment_width = truss_width // truss_segments
        
        for i in range(truss_segments):
            truss_x = left_tower_x + (i * truss_segment_width)
            truss_y_top = draw_y - 5
            truss_y_bottom = draw_y + self.height // 2
            
            # Diagonal truss members
            pygame.draw.line(screen, steel_color, 
                           (truss_x, truss_y_top), 
                           (truss_x + truss_segment_width, truss_y_bottom), 3)
            pygame.draw.line(screen, steel_color, 
                           (truss_x + truss_segment_width, truss_y_top), 
                           (truss_x, truss_y_bottom), 3)
        
        # Top and bottom chords
        pygame.draw.rect(screen, steel_color, (left_tower_x, draw_y - 5, truss_width, 3))
        pygame.draw.rect(screen, steel_color, (left_tower_x, draw_y + self.height // 2, truss_width, 3))
        
        # Steel bridge shadow
        shadow_road_left, shadow_road_right, shadow_road_width = get_road_bounds(self.y + 18, self.stage)
        shadow_left = shadow_road_left + 8
        shadow_width = shadow_road_width - 16
        pygame.draw.rect(screen, (20, 20, 20), (shadow_left, draw_y + 18, shadow_width, 25))
        
        # Warning signs for steel bridge
        if draw_y > 60 and draw_y < 150:
            sign_road_left, sign_road_right, sign_road_width = get_road_bounds(self.y + 50, self.stage)
            sign_x = sign_road_left + sign_road_width // 2 - 15
            sign_y = draw_y + 50
            
            # Sign post
            pygame.draw.rect(screen, steel_color, (sign_x + 13, sign_y + 20, 4, 25))
            
            # Warning sign - diamond shape
            pygame.draw.polygon(screen, ORANGE, [
                (sign_x + 15, sign_y),      # top
                (sign_x + 30, sign_y + 10), # right  
                (sign_x + 15, sign_y + 20), # bottom
                (sign_x, sign_y + 10)       # left
            ])
            pygame.draw.polygon(screen, BLACK, [
                (sign_x + 15, sign_y),
                (sign_x + 30, sign_y + 10),
                (sign_x + 15, sign_y + 20),
                (sign_x, sign_y + 10)
            ], 2)
            
            # Steel truss symbol
            pygame.draw.line(screen, BLACK, (sign_x + 8, sign_y + 8), (sign_x + 22, sign_y + 16), 2)
            pygame.draw.line(screen, BLACK, (sign_x + 22, sign_y + 8), (sign_x + 8, sign_y + 16), 2)
            pygame.draw.rect(screen, BLACK, (sign_x + 7, sign_y + 12, 2, 4))
            pygame.draw.rect(screen, BLACK, (sign_x + 21, sign_y + 12, 2, 4))

    def draw_medieval_bridge(self, screen, draw_y, segment_bounds, bridge_segments, segment_height):
        """Draw a medieval brick bridge with battlements"""
        # Medieval bridge colors
        brick_red = (160, 80, 60)
        brick_dark = (120, 60, 40)
        mortar_color = (200, 190, 170)
        battlement_color = (140, 70, 50)
        
        # Draw medieval towers at the start and end positions
        start_road_left, start_road_right, start_road_width = segment_bounds[0]
        end_road_left, end_road_right, end_road_width = segment_bounds[-1]
        
        tower_width = 30
        tower_height = self.height + 35
        
        # Left tower with battlements
        avg_left = (start_road_left + end_road_left) // 2
        left_tower_x = avg_left - 25
        pygame.draw.rect(screen, brick_red, (left_tower_x, draw_y - 20, tower_width, tower_height))
        
        # Right tower with battlements
        avg_right = (start_road_right + end_road_right) // 2
        right_tower_x = avg_right - 5
        pygame.draw.rect(screen, brick_red, (right_tower_x, draw_y - 20, tower_width, tower_height))
        
        # Draw battlements on towers
        for tower_x in [left_tower_x, right_tower_x]:
            battlement_y = draw_y - 20
            for i in range(0, tower_width, 8):
                if i % 16 < 8:  # Alternating pattern
                    pygame.draw.rect(screen, battlement_color, (tower_x + i, battlement_y, 8, 8))
        
        # Draw brick pattern on towers
        brick_width = 10
        brick_height = 6
        for tower_x in [left_tower_x, right_tower_x]:
            for row in range(0, tower_height, brick_height):
                y_pos = draw_y - 20 + row
                # Alternate brick offset for realistic pattern
                offset = (brick_width // 2) if (row // brick_height) % 2 else 0
                for col in range(-offset, tower_width + offset, brick_width):
                    if col + brick_width <= tower_width and col >= 0:
                        # Individual brick
                        pygame.draw.rect(screen, brick_red, (tower_x + col, y_pos, brick_width - 1, brick_height - 1))
                        # Add variation in brick color
                        if (col + row) % 4 == 0:
                            pygame.draw.rect(screen, brick_dark, (tower_x + col, y_pos, brick_width - 1, brick_height - 1))
                        # Mortar lines
                        pygame.draw.rect(screen, mortar_color, (tower_x + col + brick_width - 1, y_pos, 1, brick_height))
                        pygame.draw.rect(screen, mortar_color, (tower_x + col, y_pos + brick_height - 1, brick_width, 1))
        
        # Draw medieval bridge arch segments
        for i in range(bridge_segments):
            segment_y_offset = i * segment_height
            road_left, road_right, road_width = segment_bounds[i]
            
            # Medieval bridge spans road width with moderate extensions
            extension = min(12, road_width * 0.09)
            bridge_left = road_left - extension
            bridge_width = road_width + (2 * extension)
            
            # Draw main bridge structure
            pygame.draw.rect(screen, brick_red, (bridge_left, draw_y + segment_y_offset, bridge_width, segment_height))
            
            # Add brick pattern to bridge
            for row in range(0, segment_height, brick_height):
                y_pos = draw_y + segment_y_offset + row
                offset = (brick_width // 2) if ((segment_y_offset + row) // brick_height) % 2 else 0
                for col in range(-offset, bridge_width + offset, brick_width):
                    if col + brick_width <= bridge_width and col >= 0:
                        # Brick with variation
                        pygame.draw.rect(screen, brick_red, (bridge_left + col, y_pos, brick_width - 1, brick_height - 1))
                        if (col + row + i) % 5 == 0:
                            pygame.draw.rect(screen, brick_dark, (bridge_left + col, y_pos, brick_width - 1, brick_height - 1))
                        # Mortar lines
                        pygame.draw.rect(screen, mortar_color, (bridge_left + col + brick_width - 1, y_pos, 1, brick_height))
                        pygame.draw.rect(screen, mortar_color, (bridge_left + col, y_pos + brick_height - 1, brick_width, 1))
        
        # Medieval arch decoration
        center_road_left, center_road_right, center_road_width = segment_bounds[bridge_segments // 2]
        arch_center_x = center_road_left + center_road_width // 2
        arch_y = draw_y + self.height // 2
        
        # Draw pointed gothic arch
        pygame.draw.polygon(screen, (40, 40, 40), [
            (arch_center_x - 12, arch_y + 6),
            (arch_center_x, arch_y - 8),
            (arch_center_x + 12, arch_y + 6)
        ])
        pygame.draw.polygon(screen, brick_dark, [
            (arch_center_x - 10, arch_y + 4),
            (arch_center_x, arch_y - 6),
            (arch_center_x + 10, arch_y + 4)
        ])
        
        # Crenellated parapet on top
        top_road_left, top_road_right, top_road_width = segment_bounds[0]
        extension = min(12, top_road_width * 0.09)
        parapet_left = top_road_left - extension
        parapet_width = top_road_width + (2 * extension)
        
        # Base parapet
        pygame.draw.rect(screen, battlement_color, (parapet_left, draw_y - 5, parapet_width, 5))
        
        # Crenellations (battlements)
        for i in range(0, parapet_width, 12):
            if i % 24 < 12:  # Alternating pattern
                pygame.draw.rect(screen, battlement_color, (parapet_left + i, draw_y - 8, 12, 3))
        
        # Bridge shadow
        shadow_road_left, shadow_road_right, shadow_road_width = get_road_bounds(self.y + 18, self.stage)
        shadow_left = shadow_road_left + 8
        shadow_width = shadow_road_width - 16
        pygame.draw.rect(screen, (25, 25, 25), (shadow_left, draw_y + 18, shadow_width, 25))
        
        # Warning signs for medieval bridge
        if draw_y > 60 and draw_y < 150:
            sign_road_left, sign_road_right, sign_road_width = get_road_bounds(self.y + 50, self.stage)
            sign_x = sign_road_left + sign_road_width // 2 - 15
            sign_y = draw_y + 50
            
            # Sign post
            pygame.draw.rect(screen, battlement_color, (sign_x + 13, sign_y + 20, 4, 25))
            
            # Warning sign - diamond shape
            pygame.draw.polygon(screen, (200, 50, 50), [  # Dark red for medieval
                (sign_x + 15, sign_y),      # top
                (sign_x + 30, sign_y + 10), # right  
                (sign_x + 15, sign_y + 20), # bottom
                (sign_x, sign_y + 10)       # left
            ])
            pygame.draw.polygon(screen, BLACK, [
                (sign_x + 15, sign_y),
                (sign_x + 30, sign_y + 10),
                (sign_x + 15, sign_y + 20),
                (sign_x, sign_y + 10)
            ], 2)
            
            # Medieval castle symbol
            pygame.draw.rect(screen, BLACK, (sign_x + 8, sign_y + 12, 14, 6))
            # Battlements
            for i in range(0, 14, 4):
                if i % 8 < 4:
                    pygame.draw.rect(screen, BLACK, (sign_x + 8 + i, sign_y + 10, 4, 2))

    def check_collision(self, car):
        """Check if car collides with bridge (fails to jump over it)"""
        # Get current road bounds to follow road curves
        bridge_left, bridge_right, bridge_width = get_road_bounds(self.y, self.stage)
        
        # Check if car is in bridge area
        car_left = car.x
        car_right = car.x + car.width
        car_top = car.y - car.jump_height
        car_bottom = car.y + car.height - car.jump_height
        
        bridge_top = self.y
        bridge_bottom = self.y + self.bridge_clearance
        
        # Check horizontal overlap
        if car_right > bridge_left and car_left < bridge_right:
            # Check if car is at bridge level and not high enough
            if car_bottom > bridge_top and car_top < bridge_bottom:
                # Car is not jumping high enough to clear the bridge
                if car.jump_height < self.bridge_clearance:
                    return True
        
        return False

class Pickup:
    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.type = pickup_type
        self.width = 20
        self.height = 20
        
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        if self.type == "fuel":
            # Make fuel pickups more visible with a gas can design
            pygame.draw.rect(screen, RED, (self.x, draw_y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (self.x + 3, draw_y + 3, 14, 14))
            pygame.draw.rect(screen, RED, (self.x + 6, draw_y + 6, 8, 8))
            # Add "F" for fuel
            pygame.draw.rect(screen, WHITE, (self.x + 8, draw_y + 8, 2, 6))
            pygame.draw.rect(screen, WHITE, (self.x + 8, draw_y + 8, 4, 2))
            pygame.draw.rect(screen, WHITE, (self.x + 8, draw_y + 11, 3, 2))

class Scenery:
    def __init__(self, x, y, scenery_type, stage):
        self.x = x
        self.y = y
        self.type = scenery_type
        self.stage = stage
        self.width = 30
        self.height = 40
        
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        
        # Only draw if on screen
        if draw_y > -60 and draw_y < 860:
            if self.type == "tree":
                # Tree trunk (50% bigger)
                pygame.draw.rect(screen, BROWN, (self.x + 7, draw_y + 18, 12, 22))
                # Tree foliage (green circle) - 50% bigger
                pygame.draw.circle(screen, DARK_GREEN, (self.x + 13, draw_y + 15), 18)
                # Tree highlights - 50% bigger
                pygame.draw.circle(screen, GREEN, (self.x + 8, draw_y + 10), 6)
                
            elif self.type == "house":
                # House base (50% bigger)
                pygame.draw.rect(screen, BROWN, (self.x - 6, draw_y + 8, 38, 30))
                # Roof (50% bigger)
                pygame.draw.polygon(screen, RED, [
                    (self.x - 9, draw_y + 8),
                    (self.x + 12, draw_y - 7),
                    (self.x + 33, draw_y + 8)
                ])
                # Door (50% bigger)
                pygame.draw.rect(screen, DARK_GRAY, (self.x + 6, draw_y + 23, 9, 15))
                # Window (50% bigger)
                pygame.draw.rect(screen, YELLOW, (self.x + 18, draw_y + 15, 8, 8))
                
            elif self.type == "water_feature":
                # Water lily pad or small pond (50% bigger)
                pygame.draw.ellipse(screen, WATER_COLOR, (self.x - 5, draw_y + 15, 30, 22))
                pygame.draw.ellipse(screen, DARK_GREEN, (self.x + 3, draw_y + 18, 12, 9))
                
            elif self.type == "cactus":
                # Desert cactus (50% bigger)
                pygame.draw.rect(screen, DARK_GREEN, (self.x + 9, draw_y + 2, 9, 38))
                # Cactus arms (50% bigger)
                pygame.draw.rect(screen, DARK_GREEN, (self.x + 1, draw_y + 10, 12, 6))
                pygame.draw.rect(screen, DARK_GREEN, (self.x + 18, draw_y + 17, 12, 6))
                # Cactus spines (50% bigger spacing)
                for i in range(3):
                    pygame.draw.circle(screen, WHITE, (self.x + 13, draw_y + 10 + i * 12), 1)
                    
            elif self.type == "rock":
                # Desert rock formation (50% bigger)
                pygame.draw.ellipse(screen, GRAY, (self.x - 6, draw_y + 18, 38, 18))
                pygame.draw.ellipse(screen, LIGHT_GRAY, (self.x - 1, draw_y + 10, 22, 15))

class FuelPump:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 40
        
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y
        
        # Only draw if on screen
        if draw_y > -50 and draw_y < 850:
            # Fuel pump base (gray)
            pygame.draw.rect(screen, GRAY, (self.x, draw_y + 20, self.width, 20))
        
        # Fuel pump top (red)
        pygame.draw.rect(screen, RED, (self.x + 3, draw_y + 10, 19, 15))
        
        # Pump handle (black)
        pygame.draw.rect(screen, BLACK, (self.x + 20, draw_y + 15, 8, 3))
        
        # Display screen (green)
        pygame.draw.rect(screen, GREEN, (self.x + 6, draw_y + 12, 8, 6))
        
        # Fuel nozzle (silver)
        pygame.draw.rect(screen, SILVER, (self.x + 22, draw_y + 18, 6, 2))
        
        # Base details
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 2, draw_y + 35, 21, 3))
        
        # "FUEL" text
        font = pygame.font.SysFont("monospace", 8, bold=True)
        fuel_text = font.render("FUEL", 1, WHITE)
        screen.blit(fuel_text, (self.x + 4, draw_y + 2))

def get_road_curve(y, stage):
    """Calculate road curve offset based on y position and stage"""
    # Gentle curves for all stages - gradual progression
    if stage == 1:
        # Gentle S-curves
        return math.sin(y * 0.003) * 30
    elif stage == 2:
        # Slightly more curves but still gentle
        return math.sin(y * 0.0032) * 35
    elif stage == 3:
        # Moderate curves
        return math.sin(y * 0.0035) * 40
    elif stage == 4:
        # More winding curves
        return math.sin(y * 0.004) * 45
    else:
        # Challenging curves for high stages
        return math.sin(y * 0.004) * 50

def get_road_bounds(y, stage):
    """Get the left and right boundaries of the road at a given y position"""
    base_road_width = 300  # 50% wider than original 200px
    road_width = max(base_road_width - (stage - 1) * 20, 180)  # Minimum 180px width
    
    curve_offset = get_road_curve(y, stage)
    road_center = 300 + curve_offset  # Screen center (600/2) + curve
    
    road_left = road_center - road_width // 2
    road_right = road_center + road_width // 2
    
    # Keep road on screen
    if road_left < 50:
        road_right += 50 - road_left
        road_left = 50
    elif road_right > 550:
        road_left -= road_right - 550
        road_right = 550
    
    return int(road_left), int(road_right), int(road_width)

def draw_road(screen, camera_y, stage):
    # Draw themed background based on stage - alternating green and sandy yellow
    if stage % 2 == 1:
        # Odd stages (1, 3, 5, etc.) - Green theme
        screen.fill(GRASS_COLOR)  # Green background
    else:
        # Even stages (2, 4, 6, etc.) - Sandy yellow theme
        screen.fill((200, 180, 100))  # Sandy yellow background
    
    # Draw road segments with curves
    for y in range(0, 800, 10):  # Draw in 10px segments for smooth curves
        world_y = camera_y + y
        road_left, road_right, road_width = get_road_bounds(world_y, stage)
        

        
        # Draw road segment
        pygame.draw.rect(screen, ROAD_COLOR, (road_left, y, road_width, 10))
        
        # Draw guardrails for later stages
        if stage >= 3:
            if y % 20 == 0:  # Every 20 pixels
                pygame.draw.rect(screen, GUARDRAIL_COLOR, (road_left - 10, y, 5, 15))
                pygame.draw.rect(screen, GUARDRAIL_COLOR, (road_right + 5, y, 5, 15))
    
    # Draw road center lines
    line_y_offset = int(camera_y) % 40
    for y in range(-line_y_offset, 800, 40):
        world_y = camera_y + y
        road_left, road_right, road_width = get_road_bounds(world_y, stage)
        road_center = road_left + road_width // 2
        pygame.draw.rect(screen, ROAD_LINE_COLOR, (road_center - 5, y, 10, 20))
        road_center = road_left + road_width // 2
        pygame.draw.rect(screen, ROAD_LINE_COLOR, (road_center - 5, y, 10, 20))

def main_game(hiscore_in):
    # Game variables
    player = Car(300, 500, RED, "player")
    camera_y = 0
    player_screen_y = 600  # Fixed screen position for player car
    
    enemy_cars = []
    obstacles = []
    pickups = []
    fuel_pumps = []
    bridges = []
    scenery = []
    
    score = 0
    fuel = 100
    lives = 5
    gameover = False
    gameover_reason = "OUT OF FUEL"
    hiscore = hiscore_in
    
    # Stage system variables
    current_stage = 1
    stage_message_active = True
    stage_message_timer = 0
    stage_message_duration = 120  # 2 seconds at 60 FPS
    distance_traveled = 0
    stage_distance = 2000  # Distance to complete each stage
    
    # Explosion effect variables
    explosion_active = False
    explosion_particles = []
    explosion_timer = 0
    
    # Pause system variables
    paused = False
    
    # Collision animation variables
    collision_active = False
    collision_particles = []
    collision_timer = 0
    player_invulnerable = False
    invulnerable_timer = 0
    
    # Jump system variables
    jump_cooldown = 0  # Frames until next jump is available
    jump_cooldown_max = 300  # 5 seconds at 60 FPS
    jump_duration = 180  # 3 seconds at 60 FPS
    jump_timer = 0
    
    # Score display for crushed cars
    score_displays = []  # List of [x, y, score, timer] for floating score text
    
    # High score tracking
    hiscore_beaten_this_game = False
    
    # Spawn timers
    enemy_spawn_timer = 0
    obstacle_spawn_timer = 0
    pickup_spawn_timer = 0
    fuel_pump_spawn_timer = 0
    bridge_spawn_timer = 0
    scenery_spawn_timer = 0
    
    # Spawn delays (decrease with stage)
    enemy_spawn_delay = max(60 - (current_stage - 1) * 10, 20)
    obstacle_spawn_delay = max(120 - (current_stage - 1) * 15, 40)
    pickup_spawn_delay = 120  # Reduced to 120 (2 seconds)
    fuel_pump_spawn_delay = 300  # Fuel pumps spawn every 5 seconds (balanced for new fuel system)
    bridge_spawn_delay = 480  # Bridges spawn every 8 seconds (480 frames at 60 FPS) - allows 3 seconds buffer after 5-second jump cooldown
    scenery_spawn_delay = 90   # Scenery spawns every 1.5 seconds (more frequent)
    
    # Create initial enemy cars
    for i in range(3):
        enemy_y = random.randint(100, 300)
        road_left, road_right, _ = get_road_bounds(enemy_y, current_stage)
        enemy_x = random.randint(road_left + 10, road_right - 40)
        enemy_color = random.choice(CAR_COLORS)
        enemy_speed = random.uniform(1, 3)
        enemy = Car(enemy_x, enemy_y, enemy_color, "enemy")
        enemy.speed = enemy_speed
        enemy_cars.append(enemy)
    
    # Create initial bridge for testing
    initial_bridge = Bridge(200, current_stage)
    bridges.append(initial_bridge)
    
    #################################################################################################
    # Main game loop
    #################################################################################################
    clock = pygame.time.Clock()
    
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                elif event.key == K_SPACE and not paused and jump_cooldown <= 0:
                    player.jump()
                    jump_timer = jump_duration
        
        # Game over check moved to end of loop after all collision detection
        
        # If paused, show pause message and skip game logic
        if paused:
            print_pause_message()
            pygame.display.update()
            clock.tick(60)
            continue
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Player movement
        if keys[K_LEFT]:
            player.turn_speed = max(player.turn_speed - 0.5, -player.max_turn_speed)
        elif keys[K_RIGHT]:
            player.turn_speed = min(player.turn_speed + 0.5, player.max_turn_speed)
        else:
            player.turn_speed *= 0.8  # Gradual stop
        
        if keys[K_UP]:
            player.speed = min(player.speed + player.acceleration, player.max_speed)
        elif keys[K_DOWN]:
            player.speed = max(player.speed - player.deceleration, 1)
        else:
            player.speed = max(player.speed - 0.1, 2)  # Minimum speed
        
        # Update camera (world moves past player)
        camera_y += player.speed
        distance_traveled += player.speed
        
        # Add speed-based scoring (higher speed = more points)
        # Base points = speed, bonus points for high speed
        speed_multiplier = 1.0
        if player.speed >= 6:
            speed_multiplier = 2.0  # Double points at high speed
        elif player.speed >= 4:
            speed_multiplier = 1.5  # 50% bonus at medium-high speed
        
        points_earned = int(player.speed * speed_multiplier)
        score += points_earned
        if score > hiscore:
            if not hiscore_beaten_this_game:
                hiscore_beaten_this_game = True
                # Add congratulations message to score displays
                score_displays.append([250, 300, "NEW HI-SCORE!", 180])
            hiscore = score
        
        # Update player (only horizontal movement, not forward)
        player.x += player.turn_speed
        
        # Handle jumping physics for player
        if player.jumping:
            # Calculate jump height based on timer (parabolic arc over 3 seconds)
            if jump_timer > 0:
                jump_progress = 1.0 - (jump_timer / jump_duration)  # 0 to 1
                # Parabolic jump: height peaks at middle of jump
                player.jump_height = 40 * math.sin(jump_progress * math.pi)
                jump_timer -= 1
            else:
                # Player has landed - start the cooldown now
                player.jump_height = 0
                player.jumping = False
                player.jump_velocity = 0
                jump_cooldown = jump_cooldown_max  # Start cooldown when landing
        
        # Keep player car within road boundaries
        player_world_y = camera_y + player_screen_y
        road_left, road_right, _ = get_road_bounds(player_world_y, current_stage)
        if player.x < road_left + 10:
            player.x = road_left + 10
        elif player.x > road_right - 36:  # Account for car width
            player.x = road_right - 36
            
        player.shadow_y = player.y
        
        # Update fuel consumption (balanced for fuel pump system)
        fuel -= 0.1  # 6 units per second at 60 FPS - missing 3 pumps (~10 sec) uses ~60 fuel
        
        # Clamp fuel to prevent floating point precision issues
        fuel = max(0, fuel)
        
        # Check for game over when fuel reaches 0 or below
        if fuel <= 0 and not gameover:
            gameover = True
            gameover_reason = "OUT OF FUEL"
        
        # Stage progression
        if distance_traveled >= stage_distance:
            current_stage += 1
            distance_traveled = 0
            stage_message_active = True
            stage_message_timer = 0
            # No fuel bonus for stage completion - only fuel pumps refill fuel
        
        # Update stage message timer
        if stage_message_active:
            stage_message_timer += 1
            if stage_message_timer >= stage_message_duration:
                stage_message_active = False
        
        # Spawn timers
        enemy_spawn_timer += 1
        obstacle_spawn_timer += 1
        pickup_spawn_timer += 1
        fuel_pump_spawn_timer += 1
        bridge_spawn_timer += 1
        scenery_spawn_timer += 1
        
        # Spawn enemies
        if enemy_spawn_timer >= enemy_spawn_delay:
            spawn_y = camera_y - random.randint(100, 300)
            road_left, road_right, _ = get_road_bounds(spawn_y, current_stage)
            enemy_x = random.randint(road_left + 10, road_right - 40)
            enemy_color = random.choice(CAR_COLORS)
            enemy_speed = random.uniform(1, 4)
            enemy = Car(enemy_x, spawn_y, enemy_color, "enemy")
            enemy.speed = enemy_speed
            enemy_cars.append(enemy)
            enemy_spawn_timer = 0
        
        # Spawn obstacles
        if obstacle_spawn_timer >= obstacle_spawn_delay:
            spawn_y = camera_y - random.randint(200, 400)
            road_left, road_right, _ = get_road_bounds(spawn_y, current_stage)
            obstacle_x = random.randint(road_left + 20, road_right - 60)
            obstacle_type = random.choice(["barrel", "water"])
            obstacles.append(Obstacle(obstacle_x, spawn_y, obstacle_type))
            obstacle_spawn_timer = 0
        
        # Spawn pickups
        if pickup_spawn_timer >= pickup_spawn_delay:
            spawn_y = camera_y - random.randint(150, 300)
            road_left, road_right, _ = get_road_bounds(spawn_y, current_stage)
            pickup_x = random.randint(road_left + 15, road_right - 35)
            pickups.append(Pickup(pickup_x, spawn_y, "fuel"))
            pickup_spawn_timer = 0
        
        # Spawn fuel pumps (occasionally instead of enemy cars)
        if fuel_pump_spawn_timer >= fuel_pump_spawn_delay:
            spawn_y = camera_y + random.randint(200, 400)  # Spawn behind player, not ahead
            road_left, road_right, _ = get_road_bounds(spawn_y, current_stage)
            pump_x = random.randint(road_left + 20, road_right - 45)
            fuel_pumps.append(FuelPump(pump_x, spawn_y))
            print(f"DEBUG: Spawned fuel pump at ({pump_x}, {spawn_y}), camera_y: {camera_y}")
            fuel_pump_spawn_timer = 0
        
        # Spawn bridges (dangerous obstacles that require jumping)
        if bridge_spawn_timer >= bridge_spawn_delay:
            spawn_y = camera_y - random.randint(300, 500)  # Spawn bridges ahead of player
            new_bridge = Bridge(spawn_y, current_stage)
            bridges.append(new_bridge)
            bridge_spawn_timer = 0

            # Reduce bridge spawn delay slightly each time for increasing difficulty
            bridge_spawn_delay = max(bridge_spawn_delay - 10, 360)  # Minimum 6 seconds between bridges (5s jump cooldown + 1s buffer)
        
        # Spawn scenery elements (trees, houses, themed elements)
        if scenery_spawn_timer >= scenery_spawn_delay:
            spawn_y = camera_y + random.randint(200, 500)  # Spawn behind player
            road_left, road_right, _ = get_road_bounds(spawn_y, current_stage)
            
            # Choose scenery type based on stage theme
            if current_stage == 1:
                # Green/suburban theme - trees and houses
                scenery_types = ["tree", "tree", "house"]  # More trees than houses
            elif current_stage == 2:
                # Water theme - only water-related scenery
                scenery_types = ["water_feature", "water_feature", "water_feature"]  # Only water features
            elif current_stage == 3:
                # Industrial/water theme - trees and water features
                scenery_types = ["tree", "water_feature", "house"]
            else:
                # Desert theme for higher stages - cacti and rocks
                scenery_types = ["cactus", "cactus", "rock"]  # More cacti than rocks
            
            scenery_type = random.choice(scenery_types)
            
            # Place scenery on the sides of the road (not on the road itself)
            side = random.choice(["left", "right"])
            scenery_x = None
            
            if side == "left":
                # Left side of road - ensure minimum distance from road edge
                max_left_x = max(10, road_left - 50)  # At least 50 pixels from road
                if max_left_x > 10:
                    scenery_x = random.randint(10, max_left_x)
            else:
                # Right side of road - ensure minimum distance from road edge  
                min_right_x = min(550, road_right + 50)  # At least 50 pixels from road
                if min_right_x < 550:
                    scenery_x = random.randint(min_right_x, 550)
            
            # Only spawn if there's a valid position
            if scenery_x is not None and scenery_x > 0 and scenery_x < 570:
                scenery.append(Scenery(scenery_x, spawn_y, scenery_type, current_stage))
            
            scenery_spawn_timer = 0
        
        # Update enemy cars
        for enemy in enemy_cars[:]:
            # Move enemy cars relative to player speed (they should appear to move toward player)
            enemy.y += player.speed + enemy.speed
            enemy.x += enemy.turn_speed
            
            # Handle enemy jumping physics
            if enemy.jumping:
                enemy.jump_velocity += 0.5
                enemy.jump_height += enemy.jump_velocity
                if enemy.jump_height <= 0:
                    enemy.jump_height = 0
                    enemy.jumping = False
                    enemy.jump_velocity = 0
            
            # Keep enemy cars within road boundaries
            road_left, road_right, _ = get_road_bounds(enemy.y, current_stage)
            if enemy.x < road_left + 10:
                enemy.x = road_left + 10
                enemy.turn_speed = abs(enemy.turn_speed)  # Bounce off left edge
            elif enemy.x > road_right - 36:  # Account for car width
                enemy.x = road_right - 36
                enemy.turn_speed = -abs(enemy.turn_speed)  # Bounce off right edge
            
            # Remove cars that have passed the player
            if enemy.y > camera_y + 700:
                enemy_cars.remove(enemy)
        
        # Update fuel pumps (move them toward player)
        for pump in fuel_pumps[:]:
            # Move fuel pumps relative to player speed (they should appear to move toward player)
            pump.y += player.speed
            
            # Remove fuel pumps that have passed the player
            if pump.y > camera_y + 700:
                fuel_pumps.remove(pump)
        
        # Update scenery (move them toward player)
        for scene in scenery[:]:
            # Move scenery relative to player speed + base speed (they should appear to move toward player)
            scene.y += player.speed + 2  # Same as bridges - stationary objects that approach player
            
            # Remove scenery that has passed the player
            if scene.y > camera_y + 800:
                scenery.remove(scene)
        
        # Collision detection (use screen position for player)
        player_rect = pygame.Rect(player.x, player_screen_y, player.width, player.height)
        
        # Enemy car collisions
        for enemy in enemy_cars[:]:
            # Convert enemy world coordinates to screen coordinates for collision detection
            enemy_screen_y = enemy.y - camera_y
            enemy_rect = pygame.Rect(enemy.x, enemy_screen_y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect):
                if player.jumping and player.jump_height > 10:
                    # Crush the enemy car when jumping on it
                    score += 200
                    if score > hiscore:
                        hiscore = score
                    
                    # Add floating score display
                    score_displays.append([enemy.x + 15, enemy_screen_y, 200, 60])  # x, y, score, timer
                    
                    # Remove the crushed enemy
                    enemy_cars.remove(enemy)
                    continue
                elif not player_invulnerable:
                    # Collision! Lose a life
                    lives -= 1
                    player_invulnerable = True
                    invulnerable_timer = 0
                    
                    # Create collision animation
                    collision_active = True
                    collision_timer = 0
                    collision_particles = []
                    
                    # Create explosion particles
                    center_x = (player.x + enemy.x) // 2 + 15
                    center_y = player_screen_y + 25
                    explosion_colors = [RED, ORANGE, YELLOW, WHITE, SILVER, player.color, enemy.color]
                    
                    for i in range(30):
                        particle_x = center_x + random.randint(-20, 20)
                        particle_y = center_y + random.randint(-15, 15)
                        vel_x = random.randint(-8, 8)
                        vel_y = random.randint(-8, 8)
                        color = random.choice(explosion_colors)
                        size = random.randint(2, 6)
                        collision_particles.append([particle_x, particle_y, vel_x, vel_y, color, size])
                    
                    # Bump enemy off road
                    if player.x < enemy.x:
                        enemy.turn_speed = 8
                    else:
                        enemy.turn_speed = -8
                    
                    # Check game over
                    if lives <= 0 and not gameover:
                        gameover = True
                        gameover_reason = "NO LIVES REMAINING"
        
        # Obstacle collisions
        for obstacle in obstacles[:]:
            # Convert obstacle world coordinates to screen coordinates
            obstacle_screen_y = obstacle.y - camera_y
            obstacle_rect = pygame.Rect(obstacle.x, obstacle_screen_y, obstacle.width, obstacle.height)
            if player_rect.colliderect(obstacle_rect) and not player.jumping:
                if obstacle.type == "barrel" and not gameover:
                    # Crash into barrel
                    gameover = True
                    gameover_reason = "CRASHED INTO OBSTACLE"
                elif obstacle.type == "water" and not gameover:
                    # Fall into water
                    gameover = True
                    gameover_reason = "FELL INTO WATER"
        
        # Pickup collisions
        for pickup in pickups[:]:
            # Convert pickup world coordinates to screen coordinates
            pickup_screen_y = pickup.y - camera_y
            pickup_rect = pygame.Rect(pickup.x, pickup_screen_y, pickup.width, pickup.height)
            if player_rect.colliderect(pickup_rect):
                if pickup.type == "fuel":
                    # Fuel pickups no longer refill fuel - only fuel pumps do
                    score += 25
                    if score > hiscore:
                        hiscore = score
                pickups.remove(pickup)
        
        # Fuel pump collisions
        for pump in fuel_pumps[:]:
            # Convert fuel pump world coordinates to screen coordinates
            pump_screen_y = pump.y - camera_y
            pump_rect = pygame.Rect(pump.x, pump_screen_y, pump.width, pump.height)
            if player_rect.colliderect(pump_rect):
                fuel = min(fuel + 60, 100)  # Refill 60 fuel (enough for ~10 seconds of driving)
                score += 100  # Bonus points for fuel pump
                if score > hiscore:
                    hiscore = score
                fuel_pumps.remove(pump)
        
        # Bridge collisions (GAME OVER if hit)
        # Bridge collisions (GAME OVER if hit)
        for bridge in bridges[:]:
            # Get current road bounds to follow road curves
            bridge_left, bridge_right, bridge_width = get_road_bounds(bridge.y, bridge.stage)
            # Convert bridge world coordinates to screen coordinates
            bridge_screen_y = bridge.y - camera_y
            bridge_rect = pygame.Rect(bridge_left, bridge_screen_y, bridge_width, bridge.bridge_clearance)
            if player_rect.colliderect(bridge_rect):
                # Check if player is jumping high enough to clear the bridge
                if not player.jumping or player.jump_height < bridge.bridge_clearance:
                    gameover = True
                    gameover_reason = "CRASHED INTO BRIDGE"  # Override any previous reason
                    break
        
        # Update invulnerability timer
        if player_invulnerable:
            invulnerable_timer += 1
            if invulnerable_timer >= 120:  # 2 seconds of invulnerability
                player_invulnerable = False
                invulnerable_timer = 0
        
        # Update jump cooldown
        if jump_cooldown > 0:
            jump_cooldown -= 1
        
        # Update score displays
        for score_display in score_displays[:]:
            score_display[3] -= 1  # Decrease timer
            score_display[1] -= 1  # Float upward
            if score_display[3] <= 0:
                score_displays.remove(score_display)
        
        # Update collision animation
        if collision_active:
            collision_timer += 1
            # Update particle positions
            for particle in collision_particles:
                particle[0] += particle[2]  # x += vel_x
                particle[1] += particle[3]  # y += vel_y
                particle[3] += 0.3  # Add gravity to vel_y
                particle[5] = max(1, particle[5] - 0.1)  # Shrink particle size
            
            # Remove particles that are too small or off screen
            collision_particles = [p for p in collision_particles if p[5] > 1 and p[1] < 750 and p[0] > 0 and p[0] < 800]
            
            # End collision animation after 90 frames or no particles left
            if collision_timer > 90 or len(collision_particles) == 0:
                collision_active = False
        
        # Update obstacles, pickups, fuel pumps, and bridges to move with player speed
        for obstacle in obstacles:
            obstacle.y += player.speed
        
        for pickup in pickups:
            pickup.y += player.speed
            
        for pump in fuel_pumps:
            pump.y += player.speed
            
        for bridge in bridges:
            bridge.y += player.speed + 2  # Bridges approach player like other objects
        
        # Remove old objects that have passed the player
        obstacles = [obs for obs in obstacles if obs.y < camera_y + 900]
        pickups = [pickup for pickup in pickups if pickup.y < camera_y + 900]
        fuel_pumps = [pump for pump in fuel_pumps if pump.y < camera_y + 900]
        bridges = [bridge for bridge in bridges if bridge.y < camera_y + 900]
        scenery = [scene for scene in scenery if scene.y < camera_y + 900]
        
        # Draw everything
        draw_road(screen, camera_y, current_stage)
        
        # Draw scenery (background elements, before other objects)
        for scene in scenery:
            scene.draw(screen, camera_y)
        
        # Draw game objects (after road and scenery so they appear on top)
        for enemy in enemy_cars:
            enemy.draw(screen, camera_y)
        
        for obstacle in obstacles:
            obstacle.draw(screen, camera_y)
        
        for pickup in pickups:
            pickup.draw(screen, camera_y)
        
        for pump in fuel_pumps:
            pump.draw(screen, camera_y)
        
        for bridge in bridges:
            bridge.draw(screen, camera_y)
        
        # Draw floating score displays
        font = pygame.font.SysFont("monospace", 16, bold=True)
        for score_display in score_displays:
            if isinstance(score_display[2], str):
                # Special text message (like "NEW HI-SCORE!")
                score_text = font.render(score_display[2], 1, CYAN)
            else:
                # Regular score number
                score_text = font.render("+" + str(score_display[2]), 1, YELLOW)
            screen.blit(score_text, (score_display[0], score_display[1]))
        
        # Draw player car at fixed screen position (with invulnerability flashing)
        if not player_invulnerable or (invulnerable_timer // 5) % 2 == 0:  # Flash every 5 frames
            player.draw_at_screen_position(screen, player_screen_y)
        
        # Draw collision particles
        if collision_active:
            for particle in collision_particles:
                pygame.draw.circle(screen, particle[4], (int(particle[0]), int(particle[1])), int(particle[5]))
        
        # Draw stage message if active
        if stage_message_active:
            print_stage_message(current_stage)
        
        # Update HUD
        print_hud(score, int(fuel), current_stage, hiscore, player.speed, lives, jump_cooldown, jump_cooldown_max)
        
        pygame.display.update()
        clock.tick(60)
        
        # Return score and hiscore when game over
        if gameover:
            # Save high score if it was beaten
            is_new_hiscore = False
            if score > hiscore:
                hiscore = score
                is_new_hiscore = True
            return score, hiscore, gameover_reason

######################################################################################
# MAIN GAME LOOP
######################################################################################

game_state = "start"  # "start", "playing", "gameover"
final_score = 0
final_reason = "OUT OF FUEL"
hiscore = 0  # High score persists only during runtime

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_state == "start":
                # Start the game
                screen.fill(BLACK)
                game_state = "playing"
                final_score, hiscore, final_reason = main_game(hiscore)
                game_state = "gameover"
            elif game_state == "gameover":
                if event.key == K_SPACE:
                    # Restart the game
                    screen.fill(BLACK)
                    game_state = "playing"
                    final_score, hiscore, final_reason = main_game(hiscore)
                    game_state = "gameover"
                elif event.key == K_ESCAPE:
                    # Quit the game
                    pygame.quit()
                    sys.exit()
    
    # Display appropriate screen based on game state
    if game_state == "start":
        print_startgame(hiscore)
    elif game_state == "gameover":
        print_gameover(final_score, final_reason)
        pygame.display.update()
    
    time.sleep(0.016)  # Small delay to prevent excessive CPU usage
