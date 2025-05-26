import pygame
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
W, H = 640, 480
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
title_font = pygame.font.SysFont(None, 90)
menu_font = pygame.font.SysFont(None, 60)

# Sound Synthesis
def tone(freq=440, length=0.5, volume=1.0):
    sample_rate = 44100
    t = np.arange(int(length * sample_rate)) / sample_rate
    samples = np.sin(2 * np.pi * freq * t)
    samples = np.vstack([samples]*2).T
    samples = np.ascontiguousarray(samples)
    sound = pygame.sndarray.make_sound((samples * 32767).astype(np.int16))
    sound.set_volume(volume)
    return sound

snd_bounce = tone(800, 0.07, 0.7)
snd_score = tone(300, 0.15, 1.0)

# Game Constants
# Game Constants
WINNING_SCORE = 5  # Changed from 11 to 5
INITIAL_BALL_SPEED_X = 4
INITIAL_BALL_SPEED_Y = 4
MAX_BALL_SPEED_X = 10

# Game Objects
ball = pygame.Rect(W//2 - 10, H//2 - 10, 20, 20)
player = pygame.Rect(30, H//2 - 50, 10, 100)
ai = pygame.Rect(W - 40, H//2 - 50, 10, 100)
ball_speed_ref = [INITIAL_BALL_SPEED_X, INITIAL_BALL_SPEED_Y] # Use a reference for reset
player_score = 0 # Initialize here, reset in reset_game
ai_score = 0    # Initialize here, reset in reset_game

def reset_game_scores_ball_position():
    global player_score, ai_score, ball_speed_ref
    player_score = 0
    ai_score = 0
    ball.center = (W // 2, H // 2)
    # Keep ball_speed_ref as the base, assign to a mutable list for the game
    current_ball_speed = [INITIAL_BALL_SPEED_X * np.random.choice([-1, 1]), 
                          INITIAL_BALL_SPEED_Y * np.random.choice([-1, 1])]
    return current_ball_speed

def reset_ball_position_and_speed(direction, current_ball_speed_list):
    ball.center = (W // 2, H // 2)
    current_ball_speed_list[0] = INITIAL_BALL_SPEED_X * direction
    current_ball_speed_list[1] = INITIAL_BALL_SPEED_Y * np.random.choice([-1, 1])

def run_game():
    global player_score, ai_score # Scores are global to persist across resets if needed by menu
    
    game_state = "playing"
    current_ball_speed = reset_game_scores_ball_position()

    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit_application" # Signal to quit everything
            if game_state == "game_over" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    current_ball_speed = reset_game_scores_ball_position()
                    game_state = "playing"
                elif event.key == pygame.K_n:
                    return "return_to_menu" # Signal to go back to menu

        if game_state == "playing":
            mouse_y = pygame.mouse.get_pos()[1]
            player.centery = mouse_y
            player.clamp_ip(pygame.Rect(0, 0, W, H))
            
            if ai.centery < ball.centery:
                ai.y += 3
            elif ai.centery > ball.centery:
                ai.y -= 3
            ai.clamp_ip(pygame.Rect(0, 0, W, H))

            ball.x += current_ball_speed[0]
            ball.y += current_ball_speed[1]

            if ball.top <= 0 or ball.bottom >= H:
                current_ball_speed[1] *= -1
                snd_bounce.play()

            if ball.colliderect(player) and current_ball_speed[0] < 0:
                offset = (ball.centery - player.centery) / (player.height / 2)
                current_ball_speed[1] = offset * 5
                if abs(current_ball_speed[1]) < 0.5:
                    current_ball_speed[1] = 0.5 if current_ball_speed[1] >= 0 else -0.5
                
                current_ball_speed[0] = abs(current_ball_speed[0]) + 0.3
                if current_ball_speed[0] > MAX_BALL_SPEED_X:
                    current_ball_speed[0] = MAX_BALL_SPEED_X
                current_ball_speed[0] *= -1
                ball.left = player.right
                snd_bounce.play()

            elif ball.colliderect(ai) and current_ball_speed[0] > 0:
                offset = (ball.centery - ai.centery) / (ai.height / 2)
                current_ball_speed[1] = offset * 5
                if abs(current_ball_speed[1]) < 0.5:
                    current_ball_speed[1] = 0.5 if current_ball_speed[1] >= 0 else -0.5
                
                current_ball_speed[0] = -(abs(current_ball_speed[0]) + 0.3)
                if abs(current_ball_speed[0]) > MAX_BALL_SPEED_X:
                    current_ball_speed[0] = -MAX_BALL_SPEED_X
                ball.right = ai.left
                snd_bounce.play()

            if ball.left <= 0:
                ai_score += 1
                snd_score.play()
                if ai_score >= WINNING_SCORE:
                    game_state = "game_over"
                else:
                    reset_ball_position_and_speed(1, current_ball_speed)
                    
            elif ball.right >= W:
                player_score += 1
                snd_score.play()
                if player_score >= WINNING_SCORE:
                    game_state = "game_over"
                else:
                    reset_ball_position_and_speed(-1, current_ball_speed)

        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), player)
        pygame.draw.rect(screen, (255, 255, 255), ai)
        pygame.draw.ellipse(screen, (255, 255, 255), ball)
        
        p_score_surf = font.render(str(player_score), True, (255, 255, 255))
        a_score_surf = font.render(str(ai_score), True, (255, 255, 255))
        screen.blit(p_score_surf, (W//4, 20))
        screen.blit(a_score_surf, (3*W//4 - a_score_surf.get_width(), 20))

        if game_state == "game_over":
            winner_text_str = "YAY" if player_score >= WINNING_SCORE else "GAME OVER YOU LOSE"
            game_over_font_big = pygame.font.SysFont(None, 74)
            prompt_font_small = pygame.font.SysFont(None, 36)
            winner_surf = game_over_font_big.render(winner_text_str, True, (255, 255, 255))
            restart_surf = prompt_font_small.render("Press Y to Restart, N to Main Menu", True, (255, 255, 255))
            
            winner_rect = winner_surf.get_rect(center=(W//2, H//2 - 40))
            restart_rect = restart_surf.get_rect(center=(W//2, H//2 + 40))
            
            screen.blit(winner_surf, winner_rect)
            screen.blit(restart_surf, restart_rect)
            
            pygame.display.flip()
            clock.tick(15) 
        else: # if game_state == "playing"
            pygame.display.flip()
            clock.tick(60)
    return "return_to_menu" # Default return if loop somehow exits without other signals

def main_menu():
    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    action = run_game()
                    if action == "quit_application":
                        menu_running = False
                elif event.key == pygame.K_q:
                    menu_running = False

        screen.fill((0,0,0))
        title_text = title_font.render("PONG", True, (255,255,255))
        start_text = menu_font.render("Press S to Start", True, (255,255,255))
        quit_text = menu_font.render("Press Q to Quit", True, (255,255,255))

        screen.blit(title_text, (W//2 - title_text.get_width()//2, H//2 - 100))
        screen.blit(start_text, (W//2 - start_text.get_width()//2, H//2))
        screen.blit(quit_text, (W//2 - quit_text.get_width()//2, H//2 + 60))

        pygame.display.flip()
        clock.tick(15)

    pygame.quit()

if __name__ == "__main__":
    # Sounds are already initialized globally
    # Screen, clock, fonts are also initialized globally
    main_menu()
