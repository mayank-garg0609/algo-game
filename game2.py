import pygame
import math
import random

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
pygame.display.set_caption("Turn-Based Cannon Ball Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Ball
BALL_RADIUS = 20
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [0, 0]
FRICTION = 0.995  # Friction factor

# Cannon settings
CANNON_RADIUS = 30
BULLET_RADIUS = 5
cannon1_angle, cannon1_power = 45, 0
cannon2_angle, cannon2_power = 45, 0
bullets = []

# Power settings
MAX_POWER = 20  # Maximum power for a shot
power_increment = 0.2
charging_power = False  # Whether a player is charging power

# Score
player1_score, player2_score = 0, 0

# Turn
current_turn = 1  # 1 for Player 1, 2 for Player 2

# Font
font = pygame.font.Font(None, 36)

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
    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Calculate angle to point the cannon at the mouse
    angle = math.degrees(math.atan2(y - mouse_y, mouse_x - x))
    
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

def reset_ball():
    ball_pos[:] = [WIDTH // 2 + random.randint(-5,5), HEIGHT // 2 + random.randint(-5,5)]
    ball_vel[:] = [0, 0]

def handle_bullets():
    global bullets, ball_vel
    for bullet in bullets[:]:
        bullet[0] += math.cos(math.radians(bullet[2])) * bullet[3]
        bullet[1] -= math.sin(math.radians(bullet[2])) * bullet[3]
        if (bullet[0] < 0 or bullet[0] > WIDTH or
                bullet[1] < 0 or bullet[1] > HEIGHT):
            bullets.remove(bullet)

        # Check collision with the ball
        dist = math.hypot(bullet[0] - ball_pos[0], bullet[1] - ball_pos[1])
        if dist <= BALL_RADIUS + BULLET_RADIUS:
            angle = math.atan2(ball_pos[1] - bullet[1], ball_pos[0] - bullet[0])
            ball_vel[0] += math.cos(angle) * bullet[3] * 0.2
            ball_vel[1] += math.sin(angle) * bullet[3] * 0.2
            bullets.remove(bullet)

def main():
    global cannon1_angle, cannon1_power, cannon2_angle, cannon2_power, current_turn, charging_power
    running = True
    while running:
        # screen.fill(WHITE)
        draw_field()

        # Draw elements
        # draw_cannon(50, HEIGHT // 2, cannon1_angle, RED)
        # draw_cannon(WIDTH - 50, HEIGHT // 2, cannon2_angle, BLUE)
        cannon1_angle = draw_cannon(50, HEIGHT // 2, cannon1_img)

        # Draw Player 2's cannon
        cannon2_angle = draw_cannon(WIDTH - 50, HEIGHT // 2, cannon2_img)

        draw_ball()
        draw_bullets()

        # Draw power bars
        if current_turn == 1:
            draw_power_bar(50, HEIGHT // 2, cannon1_power, RED)
        else:
            draw_power_bar(WIDTH - 50, HEIGHT // 2, cannon2_power, BLUE)

        # Display scores and turn
        score_text = font.render(f"Player 1: {player1_score}  Player 2: {player2_score}", True, BLACK)
        turn_text = font.render(f"Player {current_turn}'s Turn", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
        screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN :
                charging_power = True

            if event.type == pygame.MOUSEBUTTONUP and charging_power:
                x, y = pygame.mouse.get_pos()
                if current_turn == 1:
                    angle = math.degrees(math.atan2(HEIGHT // 2 - y, x - 50))
                    bullets.append([50, HEIGHT // 2, angle, cannon1_power])
                    cannon1_power = 0  # Reset power after shooting
                    current_turn = 2
                elif current_turn == 2:
                    angle = math.degrees(math.atan2(HEIGHT // 2 - y, x - (WIDTH - 50)))
                    bullets.append([WIDTH - 50, HEIGHT // 2, angle, cannon2_power])
                    cannon2_power = 0  # Reset power after shooting
                    current_turn = 1
                charging_power = False

        # Charge power
        if charging_power:
            if current_turn == 1 and cannon1_power < MAX_POWER:
                cannon1_power += power_increment
            elif current_turn == 2 and cannon2_power < MAX_POWER:
                cannon2_power += power_increment

        # Update
        update_ball()
        handle_bullets()

        # Update screen
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
