import socket
import ssl
import pickle
import pygame
import sys

# Network Setup
SERVER_IP = input('What is your server ip?\n').strip()  # Connect to server IP

PORT = 5555
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(sock, server_hostname=SERVER_IP)
conn.connect((SERVER_IP, PORT))

# Pygame Setup
pygame.init()
width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Secure Pong Multiplayer')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
bg_color = pygame.Color("black")
fps_font = pygame.font.Font(None, 30) #fps locked at 60?
names_font = pygame.font.Font(None,15)
player_speed = 0

while True:
    screen.fill(bg_color)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            conn.close()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_speed = -7
            elif event.key == pygame.K_DOWN:
                player_speed = 7
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                player_speed = 0

    try:
        conn.sendall(pickle.dumps(player_speed))
        data = conn.recv(4096)
        if not data:
            break
        game_state = pickle.loads(data)
        players = game_state["players"]
        ball = game_state["ball"]
        scores = game_state["scores"]

        pygame.draw.rect(screen, (255, 0, 0), players[0])
        pygame.draw.rect(screen, (0, 255, 0), players[1])
        pygame.draw.ellipse(screen, (0, 0, 255), ball)
        pygame.draw.aaline(screen, (200, 200, 200), (width / 2, 0), (width / 2, height))
        #latency issues!
        fps = clock.get_fps()
        fps_text = fps_font.render(f"FPS: {int(fps)}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))
        #By anish and anirudh
        names_text = names_font.render("By Anish Kulkarni and Anirudh Muraleedharan",True,(0,255,255))
        screen.blit(names_text,(width-250,10))

        score_text = font.render(f"{scores[0]} - {scores[1]}", True, (255, 255, 255))
        screen.blit(score_text, (width // 2 - 60, 20))

        pygame.display.flip()
        clock.tick(120)

    except Exception as e:
        print(f"Error: {e}")
        break

pygame.quit()
conn.close()
