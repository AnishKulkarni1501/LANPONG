import socket
import ssl
import threading
import pickle
import pygame
import random
art ='''
                                                                                    
                                                                                    
PPPPPPPPPPPPPPPPP        OOOOOOOOO     NNNNNNNN        NNNNNNNN        GGGGGGGGGGGGG
P::::::::::::::::P     OO:::::::::OO   N:::::::N       N::::::N     GGG::::::::::::G
P::::::PPPPPP:::::P  OO:::::::::::::OO N::::::::N      N::::::N   GG:::::::::::::::G
PP:::::P     P:::::PO:::::::OOO:::::::ON:::::::::N     N::::::N  G:::::GGGGGGGG::::G
  P::::P     P:::::PO::::::O   O::::::ON::::::::::N    N::::::N G:::::G       GGGGGG
  P::::P     P:::::PO:::::O     O:::::ON:::::::::::N   N::::::NG:::::G              
  P::::PPPPPP:::::P O:::::O     O:::::ON:::::::N::::N  N::::::NG:::::G              
  P:::::::::::::PP  O:::::O     O:::::ON::::::N N::::N N::::::NG:::::G    GGGGGGGGGG
  P::::PPPPPPPPP    O:::::O     O:::::ON::::::N  N::::N:::::::NG:::::G    G::::::::G
  P::::P            O:::::O     O:::::ON::::::N   N:::::::::::NG:::::G    GGGGG::::G
  P::::P            O:::::O     O:::::ON::::::N    N::::::::::NG:::::G        G::::G
  P::::P            O::::::O   O::::::ON::::::N     N:::::::::N G:::::G       G::::G
PP::::::PP          O:::::::OOO:::::::ON::::::N      N::::::::N  G:::::GGGGGGGG::::G
P::::::::P           OO:::::::::::::OO N::::::N       N:::::::N   GG:::::::::::::::G
P::::::::P             OO:::::::::OO   N::::::N        N::::::N     GGG::::::GGG:::G
PPPPPPPPPP               OOOOOOOOO     NNNNNNNN         NNNNNNN        GGGGGG   GGGG
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                                        '''
print(art)
print("CN MINIPROJECT , ANISH K AND ANIRUDH M")
# Server Config
HOST = "0.0.0.0"
PORT = 5555
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)#Depracated!
context.load_cert_chain(certfile="ssl/server.crt", keyfile="ssl/server.key")

# Game Variables
width, height = 1000, 600
ball = pygame.Rect(width / 2 - 15, height / 2 - 15, 30, 30)
players = [
    pygame.Rect(10, height / 2 - 70, 10, 140),
    pygame.Rect(width - 20, height / 2 - 70, 10, 140)#this is where they're spawned
]
ball_speed = [6 * random.choice([-1, 1]), 6 * random.choice([-1, 1])]
scores = [0, 0]
clients = []

# Thread Lock for Safe Game State
lock = threading.Lock() #could maybe use more efficient multithreading?

def send_state():
    data = pickle.dumps({"players": players, "ball": ball, "scores": scores})
    for c in clients:
        try:
            c.sendall(data)
        except:
            pass

def handle_client(conn, index):
    global ball, ball_speed, scores
    try:
        while True:
            move = pickle.loads(conn.recv(1024))
            with lock:
                players[index].y += move
                players[index].y = max(0, min(height - players[index].height, players[index].y))
    except:
        print(f"[-] Player {index+1} disconnected")
    finally:
        conn.close()

def game_loop():
    global ball, ball_speed, scores
    clock = pygame.time.Clock()
    while True:
        pygame.time.wait(16) #frames delay if error
        with lock:
            # Ball-movement
            ball.x += ball_speed[0]
            ball.y += ball_speed[1]

            # Wall-col
            if ball.top <= 0 or ball.bottom >= height:
                ball_speed[1] *= -1

            # Paddle-col
            if ball.colliderect(players[0]) or ball.colliderect(players[1]):
                ball_speed[0] *= -1

            # Scoring
            if ball.left <= 0:
                scores[1] += 1
                if scores[1] > 10:
                    print("Game over. Player 2 wins.")
                    break
                ball = pygame.Rect(width / 2 - 15, height / 2 - 15, 30, 30)
                ball_speed = [6, 6]
            elif ball.right >= width:
                scores[0] += 1
                if scores[0] > 10:
                    print("Game over. Player 1 wins.")
                    break
                ball = pygame.Rect(width / 2 - 15, height / 2 - 15, 30, 30)
                ball_speed = [-6, 6]

            send_state()
        clock.tick(120)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind((HOST, PORT))
    sock.listen(2)
    print("[*] Waiting for 2 players...")
    with context.wrap_socket(sock, server_side=True) as ssock:
        for i in range(2):
            conn, addr = ssock.accept()
            print(f"[+] Player {i+1} connected from {addr}")
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, i))
            thread.start()
        game_loop()

for c in clients:
    c.close()
