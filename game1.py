import threading
import queue
import time
import random
import pygame
import math

# Setup for Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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

player1_queue = queue.Queue()
player2_queue = queue.Queue()


# Player Script Functions
def player_script(player_queue, response_queue, cannon_x, cannon_y):
    while True:
        ready_signal = player_queue.get()  # Wait for the ready signal
        if ready_signal == "READY":
            # Calculate angle and power (example logic)
            target_x, target_y = WIDTH // 2, HEIGHT // 2
            angle = math.degrees(math.atan2(cannon_y - target_y, target_x - cannon_x))
            power = random.randint(30, 100)  # Random power between 30 and 100
            response_queue.put((angle, power))  # Send calculated values

def main():
    global current_turn, ball_pos, ball_vel, player1_score, player2_score

    # Start player threads
    threading.Thread(target=player_script, args=(player1_queue, player1_response_queue, 50, HEIGHT // 2), daemon=True).start()
    threading.Thread(target=player_script, args=(player2_queue, player2_response_queue, WIDTH - 50, HEIGHT // 2), daemon=True).start()

    turn_delay = 0.5  # Delay between turns in seconds
    last_turn_time = pygame.time.get_ticks()  # Track time of the last turn
    waiting_for_response = False

    running = True
    while running:
        screen.fill(WHITE)  # Clear screen
        pygame.draw.circle(screen, RED, ball_pos, 10)  # Draw ball

        current_time = pygame.time.get_ticks()

        # Handle turns without blocking
        if not waiting_for_response and current_time - last_turn_time >= turn_delay * 1000:
            if current_turn == 1:
                player1_queue.put("READY")
                waiting_for_response = True
            elif current_turn == 2:
                player2_queue.put("READY")
                waiting_for_response = True

        if waiting_for_response:
            try:
                if current_turn == 1 and not player1_response_queue.empty():
                    angle, power = player1_response_queue.get_nowait()
                    ball_vel[0] = math.cos(math.radians(angle)) * power
                    ball_vel[1] = -math.sin(math.radians(angle)) * power
                    current_turn = 2
                    waiting_for_response = False
                    last_turn_time = pygame.time.get_ticks()

                elif current_turn == 2 and not player2_response_queue.empty():
                    angle, power = player2_response_queue.get_nowait()
                    ball_vel[0] = math.cos(math.radians(angle)) * power
                    ball_vel[1] = -math.sin(math.radians(angle)) * power
                    current_turn = 1
                    waiting_for_response = False
                    last_turn_time = pygame.time.get_ticks()
            except queue.Empty:
                pass

        # Ball movement
        ball_pos[0] += ball_vel[0] * 0.1
        ball_pos[1] += ball_vel[1] * 0.1

        # Check for scoring or collision
        if ball_pos[0] <= 0:
            player2_score += 1
            ball_pos = [WIDTH // 2, HEIGHT // 2]
            ball_vel = [0, 0]
        elif ball_pos[0] >= WIDTH:
            player1_score += 1
            ball_pos = [WIDTH // 2, HEIGHT // 2]
            ball_vel = [0, 0]

        # Render scores
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Player 1: {player1_score}  Player 2: {player2_score}", True, (0, 0, 0))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

        # Update screen
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# # Main Game Logic
# def main():
#     global current_turn, ball_pos, ball_vel, player1_score, player2_score

#     # Start player threads
#     threading.Thread(target=player_script, args=(player1_queue, player1_response_queue, 50, HEIGHT // 2), daemon=True).start()
#     threading.Thread(target=player_script, args=(player2_queue, player2_response_queue, WIDTH - 50, HEIGHT // 2), daemon=True).start()

#     running = True
#     while running:
#         screen.fill(WHITE)  # Clear screen
#         pygame.draw.circle(screen, RED, ball_pos, 10)  # Draw ball

#         # Send ready signal and get response from the current player
#         if current_turn == 1:
#             player1_queue.put("READY")
#             angle, power = player1_response_queue.get()
#             ball_vel[0] = math.cos(math.radians(angle)) * power
#             ball_vel[1] = -math.sin(math.radians(angle)) * power
#             current_turn = 2
#         elif current_turn == 2:
#             player2_queue.put("READY")
#             angle, power = player2_response_queue.get()
#             ball_vel[0] = math.cos(math.radians(angle)) * power
#             ball_vel[1] = -math.sin(math.radians(angle)) * power
#             current_turn = 1

#         # Ball movement
#         ball_pos[0] += ball_vel[0] * 0.1
#         ball_pos[1] += ball_vel[1] * 0.1

#         # Check for scoring or collision
#         if ball_pos[0] <= 0:
#             player2_score += 1
#             ball_pos = [WIDTH // 2, HEIGHT // 2]
#             ball_vel = [0, 0]
#         elif ball_pos[0] >= WIDTH:
#             player1_score += 1
#             ball_pos = [WIDTH // 2, HEIGHT // 2]
#             ball_vel = [0, 0]

#         # Render scores
#         font = pygame.font.Font(None, 36)
#         score_text = font.render(f"Player 1: {player1_score}  Player 2: {player2_score}", True, (0, 0, 0))
#         screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

#         # Update screen
#         pygame.display.flip()
#         clock.tick(FPS)

#         # Pause between turns
#         time.sleep(0.5)

#     pygame.quit()


# Queues for player responses
player1_response_queue = queue.Queue()
player2_response_queue = queue.Queue()

if __name__ == "__main__":
    main()
