import threading
import queue
import time
import random
import pygame
import math
from player1 import player_script as player_script_left
from player2 import player_script as player_script_right

# Initialize pygame
pygame.init()

# Load cannon sprites
cannon1_img = pygame.image.load("cannon.png")
cannon2_img = pygame.image.load("cannon.png")

# Scale cannon sprites (if necessary)
cannon1_img = pygame.transform.scale(cannon1_img, (60, 20))  # Adjust size as needed
cannon2_img = pygame.transform.scale(cannon2_img, (60, 20))  # Adjust size as needed
cannon2_img = pygame.transform.flip(cannon2_img, False, True)  # Flip the cannon sprite


# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Football Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Clock
game_time = 60 #seconds
clock = pygame.time.Clock()
FPS = 60
counter, text = game_time, f"{game_time}".rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)

# Ball
BALL_RADIUS = 20
positions = [(WIDTH // 2, HEIGHT // 2), (WIDTH // 2 , HEIGHT // 2 + 50), (WIDTH // 2 , HEIGHT // 2 - 50), (WIDTH // 2 , HEIGHT // 2 + 100), (WIDTH // 2 - 50, HEIGHT // 2 - 100)]
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [0, 0]
FRICTION = 0.995  # Friction factor

# Cannon settings
cannon1_pos = (50, HEIGHT // 2)
cannon2_pos = (WIDTH - 50, HEIGHT // 2)
CANNON_RADIUS = 30
BULLET_RADIUS = 5
cannon1_angle, cannon1_power = 45, 0
cannon2_angle, cannon2_power = 45, 0
bullets = []

# Bullet type counts
powerbulletscount = 5
precisionbulletscount = 10
powerbullets1 = powerbulletscount
powerbullets2 = powerbulletscount
precisionbullets1 = precisionbulletscount
precisionbullets2 = precisionbulletscount
bullets_used1 = 0
bullets_used2 = 0

# params for bullets
powerbullet_angle_error = 5
powerbullet_multiplier = 1.5

# Power settings
MAX_POWER = 30  # Maximum power for a shot
BULLET_SPEED = 15
power_increment = 0.13
charging_power = False  # Whether a player is charging power

# Score
player1_score, player2_score = 0, 0
winning_score = 5

# Variables used for turns
# current_turn = 1  # 1 for Player 1, 2 for Player 2
turn_delay = 0.6  # Delay between turns
can_shoot1 = True
can_shoot2 = True
last_shot_time1 = 0
last_shot_time2 = 0

player1_ready = False
player2_ready = False

player1_executing = None
player2_executing = None

# Font
font = pygame.font.Font(None, 36)
font_bulletcount = pygame.font.Font(None, 24)

def draw_field():
    # Green background for the field
    screen.fill((34, 139, 34))  # Dark green color for the field

    # Field border
    pygame.draw.rect(screen, WHITE, (50, 50, WIDTH - 100, HEIGHT - 100), 5)

    # Halfway line
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 50), (WIDTH // 2, HEIGHT - 50), 5)

    # Center circle
    pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), 70, 5)

    # Goal areas
    goal_width = 200
    pygame.draw.rect(screen, WHITE, (50, HEIGHT // 2 - 75, 50, 150), 5)  # Left goal area
    pygame.draw.rect(screen, WHITE, (WIDTH - 100, HEIGHT // 2 - 75, 50, 150), 5)  # Right goal area

def draw_cannon(x, y, img):
    # Get ball position
    ball_x, ball_y = ball_pos
    
    # Calculate angle to point the cannon at the ball
    angle = math.degrees(math.atan2(y - ball_y, ball_x - x))
    
    # Rotate the cannon sprite
    rotated_img = pygame.transform.rotate(img, angle)
    img_rect = rotated_img.get_rect(center=(x, y))
    
    # Draw the cannon
    screen.blit(rotated_img, img_rect.topleft)
    
    return angle  # Return the calculated angle

def draw_power_bar(x, y, power, color):
    # Power bar rectangle
    pygame.draw.rect(screen, GRAY, (x - 25, y + 40, 50, 10))  # Background bar
    pygame.draw.rect(screen, color, (x - 25, y + 40, int(50 * (power / MAX_POWER)), 10))  # Charging bar

def draw_ball():
    pygame.draw.circle(screen, GREEN, ball_pos, BALL_RADIUS)

def draw_bullets():
    for bullet in bullets:
        if bullet[4] == "power":
            pygame.draw.circle(screen, RED, (int(bullet[0]), int(bullet[1])), BULLET_RADIUS)
        else:
            pygame.draw.circle(screen, BLACK, (int(bullet[0]), int(bullet[1])), BULLET_RADIUS)

def update_ball():
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Apply friction
    ball_vel[0] *= FRICTION
    ball_vel[1] *= FRICTION

    # Stop the ball if velocity is very low
    if abs(ball_vel[0]) < 0.1:
        ball_vel[0] = 0
    if abs(ball_vel[1]) < 0.1:
        ball_vel[1] = 0

    # Wall collision
    if ball_pos[1] - BALL_RADIUS <= 0 or ball_pos[1] + BALL_RADIUS >= HEIGHT:
        ball_vel[1] = -ball_vel[1]
    if ball_pos[0] - BALL_RADIUS <= 0:
        global player2_score
        player2_score += 1
        reset_ball()
    elif ball_pos[0] + BALL_RADIUS >= WIDTH:
        global player1_score
        player1_score += 1
        reset_ball()
round_counter = 0
def reset_ball():
    global round_counter, player1_executing, player2_executing, cannon1_power, cannon2_power
    round_counter += 1
    global ball_pos, ball_vel, powerbullets1, powerbullets2, precisionbullets1, precisionbullets2, bullets
    ball_pos[:] = [positions[round_counter%5][0] + random.randint(-5,5), positions[round_counter%5][1] + random.randint(-5,5)]
    ball_vel[:] = [0, 0]
    powerbullets1, powerbullets2 = powerbulletscount, powerbulletscount
    precisionbullets1, precisionbullets2 = precisionbulletscount, precisionbulletscount
    bullets.clear()
    player1_executing = None
    player2_executing = None
    cannon1_power, cannon2_power = 0, 0

def handle_bullets():
    global bullets, ball_vel
    for bullet in bullets[:]:
        bullet[0] += math.cos(math.radians(bullet[2])) * BULLET_SPEED
        bullet[1] -= math.sin(math.radians(bullet[2])) * BULLET_SPEED
        if (bullet[0] < 0 or bullet[0] > WIDTH or
                bullet[1] < 0 or bullet[1] > HEIGHT):
            bullets.remove(bullet)

        # Check collision with the ball
        dist = math.hypot(bullet[0] - ball_pos[0], bullet[1] - ball_pos[1])
        if dist <= BALL_RADIUS + BULLET_RADIUS:
            angle = math.atan2(ball_pos[1] - bullet[1], ball_pos[0] - bullet[0])
            ball_vel[0] += math.cos(angle) * bullet[3] * power_increment * (powerbullet_multiplier if bullet[4] == "power" else 1)
            ball_vel[1] += math.sin(angle) * bullet[3] * power_increment * (powerbullet_multiplier if bullet[4] == "power" else 1)
            bullets.remove(bullet)

def restart_game():
    global player1_score, player2_score, counter, bullets_used1, bullets_used2, round_counter
    round_counter = 0
    bullets_used1, bullets_used2 = 0, 0
    counter = game_time
    player1_score, player2_score = 0, 0
    reset_ball()

def main():
    global cannon1_angle, cannon1_power, cannon2_angle, cannon2_power, charging_power, powerbulletscount, precisionbulletscount, powerbullets1, powerbullets2, precisionbullets1, precisionbullets2, powerbullet_angle_error, player1_score, player2_score, ball_vel, ball_pos, bullets, counter, bullets_used1, bullets_used2, player1_ready, player2_ready, last_shot_time1, last_shot_time2, player1_executing, player2_executing
    running = True
    game_over = False
    while running:
        if game_over:
            screen.fill(WHITE)
            winner_text = font.render(f"Player {1 if player1_score > player2_score else 2} wins!", True, BLACK)
            if player1_score == player2_score:
                if bullets_used1 == bullets_used2:
                    winner_text = font.render("It's a tie!", True, BLACK)
                else:
                    winner_text = font.render(f"Player {1 if bullets_used1 < bullets_used2 else 2} wins!", True, BLACK)
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
            player1_score_text = font.render(f"Player 1 Score: {player1_score}", True, BLACK)
            player2_score_text = font.render(f"Player 2 Score: {player2_score}", True, BLACK)
            screen.blit(player1_score_text, (WIDTH // 2 - player1_score_text.get_width() // 2, HEIGHT // 2 - 150))
            screen.blit(player2_score_text, (WIDTH // 2 - player2_score_text.get_width() // 2, HEIGHT // 2 - 100))
            bullets_used_text = font.render(f"Bullets Used - Player 1: {bullets_used1}  Player 2: {bullets_used2}", True, BLACK)
            screen.blit(bullets_used_text, (WIDTH // 2 - bullets_used_text.get_width() // 2, HEIGHT // 2 + 100))
            restart_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 50)
            pygame.draw.rect(screen, GRAY, restart_button)
            restart_text = font.render("Restart", True, BLACK)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 65))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        game_over = False
                        restart_game()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()
            clock.tick(FPS)
            continue
        # screen.fill(WHITE)
        draw_field()

        # Draw Cannons
        cannon1_angle = draw_cannon(50, HEIGHT // 2, cannon1_img)
        cannon2_angle = draw_cannon(WIDTH - 50, HEIGHT // 2, cannon2_img)

        draw_ball()
        draw_bullets()

        # Draw power bars
        draw_power_bar(50, HEIGHT // 2, cannon1_power, RED)
        draw_power_bar(WIDTH - 50, HEIGHT // 2, cannon2_power, BLUE)

        current_time = pygame.time.get_ticks()

        # Handle turns without blocking
        if current_time - last_shot_time1 >= turn_delay * 1000:
            player1_ready = True
        else:
            player1_ready = False
        
        if current_time - last_shot_time2 >= turn_delay * 1000:
            player2_ready = True
        else:
            player2_ready = False
                
        angle, power = 0, 0
        if player1_executing is not None:
            if(cannon1_power < player1_executing[1] and cannon1_power<MAX_POWER):
                cannon1_power += 1
            elif(cannon1_power >= player1_executing[1] or cannon1_power>=MAX_POWER):
                bullets.append([50, HEIGHT // 2, player1_executing[0], cannon1_power, player1_executing[2]])
                last_shot_time1 = pygame.time.get_ticks()
                cannon1_power = 0
                player1_executing = None

        elif player1_ready:
            player1_command = player_script_left(cannon1_pos, ball_pos, powerbullets1, precisionbullets1, ball_vel)
            if player1_command is not None:
                angle, power, bullet_type = player1_command
                if bullet_type == "power" and powerbullets1 > 0:
                    player1_executing = (angle, power, bullet_type)
                    # bullets.append([50, HEIGHT // 2, angle, power, bullet_type])
                    powerbullets1 -= 1
                    bullets_used1 += 1

                elif bullet_type == "precision" and precisionbullets1 > 0:
                    player1_executing = (angle, power, bullet_type)
                    # bullets.append([50, HEIGHT // 2, angle, power, bullet_type])
                    precisionbullets1 -= 1
                    bullets_used1 += 1
                
                player1_ready = False

        if player2_executing is not None:
            if(cannon2_power < player2_executing[1] and cannon2_power<MAX_POWER):
                cannon2_power += 1
            elif(cannon2_power >= player2_executing[1] or cannon2_power>=MAX_POWER):
                bullets.append([WIDTH - 50, HEIGHT // 2, player2_executing[0], cannon2_power, player2_executing[2]])
                last_shot_time2 = pygame.time.get_ticks()
                cannon2_power = 0
                player2_executing = None

        elif player2_ready:
            player2_command = player_script_right(cannon2_pos, ball_pos, powerbullets2, precisionbullets2, ball_vel)
            if player2_command is not None:
                angle, power, bullet_type = player2_command
                if bullet_type == "power" and powerbullets2 > 0:
                    player2_executing = (angle, power, bullet_type)
                    # bullets.append([WIDTH - 50, HEIGHT // 2, angle, power, bullet_type])
                    powerbullets2 -= 1
                    bullets_used2 += 1
                elif bullet_type == "precision" and precisionbullets2 > 0:
                    player2_executing = (angle, power, bullet_type)
                    # bullets.append([WIDTH - 50, HEIGHT // 2, angle, power, bullet_type])
                    precisionbullets2 -= 1
                    bullets_used2 += 1
                player2_ready = False

        # Display scores and turn
        score_text = font.render(f"Player 1: {player1_score}  Player 2: {player2_score}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        screen.blit(font.render(f"Time: {counter}", True, BLACK), (WIDTH // 2 - 50, 100))
        # Display bullet counts for Player 1
        power_bullet_count_text1 = font_bulletcount.render(f"Power Bullets: {powerbullets1}", True, BLACK)
        screen.blit(power_bullet_count_text1, (10, HEIGHT - power_bullet_count_text1.get_height() - 10))

        precision_bullet_count_text1 = font_bulletcount.render(f"Precision Bullets: {precisionbullets1}", True, BLACK)
        screen.blit(precision_bullet_count_text1, (10, HEIGHT - power_bullet_count_text1.get_height() - 10 - precision_bullet_count_text1.get_height() - 10))

        # Display bullet counts for Player 2
        bullet_count_text2 = font_bulletcount.render(f"Power Bullets: {powerbullets2}", True, BLACK)
        screen.blit(bullet_count_text2, (WIDTH - bullet_count_text2.get_width() - 10, HEIGHT - bullet_count_text2.get_height() - 10))

        precision_bullet_count_text2 = font_bulletcount.render(f"Precision Bullets: {precisionbullets2}", True, BLACK)
        screen.blit(precision_bullet_count_text2, (WIDTH - precision_bullet_count_text2.get_width() - 10, HEIGHT - bullet_count_text2.get_height() - 10 - precision_bullet_count_text2.get_height() - 10))

        # Render FPS counter
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

        if(player1_score>=winning_score or player2_score>=winning_score):
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                counter -= 1
                if counter > 0:
                    text = str(counter).rjust(3)
                else:
                    text = 'Time is up!'.rjust(3)
                    game_over = True

        # Check if ball is not moving and both players are out of bullets
        if ball_vel[0] == 0 and ball_vel[1] == 0 and powerbullets1 == 0 and powerbullets2 == 0 and precisionbullets1 == 0 and precisionbullets2 == 0:
            if abs(ball_pos[0] - cannon1_pos[0]) > abs(ball_pos[0] - cannon2_pos[0]):
                player1_score += 1
            else:
                player2_score += 1
            reset_ball()

        # Update
        update_ball()
        handle_bullets()

        # Update screen
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
