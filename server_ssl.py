import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import random
import ssl


# Server configuration
HOST = "192.168.247.85"
PORT = 65432  # The port used by the server

no_of_rounds = 3
minimum_players = 2

class ClientInfo:
    def __init__(self, conn, ip_address, username):
        self.conn = conn
        self.ip_address = ip_address
        self.username = username
        self.score = 0

# Dictionary to hold client information
client_info_dict = {}

client_answers = {}

questions_list = [
    "If user could have any superpower, it would be the ability to __________.",
    "user secret talent is juggling flaming __________.",
    "If user were a superhero, his arch-nemesis would be the evil __________.",
    "user once won a gold medal in the prestigious sport of __________.",
    "user pet cat's special skill is speaking fluent __________.",
    "user dream job is to be a professional stand-up comedian specializing in __________ jokes.",
    "user spirit animal is a rare, mythical creature known as the __________.",
    "user catchphrase is so legendary that it's now used as a national slogan for __________.",
    "In a parallel universe, user is the president of a country where everyone communicates exclusively through __________.",
    "If user could time travel, he/she would go back just to witness the epic showdown between __________ and __________.",
    "user alter ego moonlights as a superhero named Captain __________.",
    "user theme song for life is a remix of the chicken dance combined with __________.",
    "user ideal vacation spot is a tropical island where the main currency is __________.",
    "user once saved the day using only a rubber chicken and __________.",
    "user once won a hotdog eating contest by consuming __________ hotdogs in under 5 minutes.",
    "If user were a wizard, his/her wand would be made of __________.",
    "If user could have any animal as a sidekick, it would be a __________.",
    "user has a unique collection of __________ that most people find amusing.",
    "user once participated in a dance-off with a robot and surprisingly won by doing the __________ dance.",
    "If user were a famous rock star, the stage name would be 'The __________.'",
    "user once hosted a themed party where guests had to dress up as their favorite __________ character.",
]


# Lock for thread safety
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        # Input Username
        username = conn.recv(1024).decode()

        conn.sendall(f"{username} {addr} joined the game.".encode())
        print(f"{username} {addr} has joined the queue!")

        # Create an instance of ClientInfo
        client_info = ClientInfo(conn, addr[0], username)

        # Add the instance to the dictionary using the IP address as the key
        with lock:
            client_info_dict[addr[0]] = client_info

        # Ignore rn
        game_code = conn.recv(1024).decode()
        # print("Game code:", game_code)
    except Exception as e:
        print(f"An error occurred while handling client {addr}: {e}")

def run_game():
    round_counter = 0
    while True:
        if len(client_info_dict) >= minimum_players:
            try:
                while round_counter < no_of_rounds:  # Limit the number of rounds to 5
                    active_players = client_info_dict.copy()
                    round_counter += 1
                    print(f"\nRound {round_counter} started! Remaing players will be kept in queue!")

                    # Send questions to clients
                    shuffled_questions = list(questions_list)
                    random.shuffle(shuffled_questions)
                    question = shuffled_questions.pop()

                    random_player_name = random.choice(list(active_players.values())).username
                    question = question.replace("user", random_player_name)

                    for ip_addr, client_info in active_players.items():
                        client_conn = client_info.conn
                        try:
                            client_conn.sendall(question.encode())
                        except Exception as e:
                            print(f"Error occurred while sending question to {client_info.username} at {ip_addr}: {e}")
                            with lock:
                                # disconnected_players_dict[ip_addr] = client_info
                                del active_players[ip_addr]
                            continue

                    # Receive answers from clients
                    for ip_addr, client_info in active_players.items():
                        client_conn = client_info.conn
                        try:
                            answers = client_conn.recv(1024).decode()
                            client_answers[ip_addr] = answers
                            print(f"Answer from {client_info.username}: {answers}")
                        except Exception as e:
                            print(f"Error occurred while receiving answer from {client_info.username} at {ip_addr}: {e}")
                            with lock:
                                # disconnected_players_dict[ip_addr] = client_info
                                del active_players[ip_addr]
                            continue

                    # Process answers and update scores
                    print(f"Waiting for all clients to answer... {len(active_players) - len(client_answers)} left")
                    while len(active_players) > 0 and len(client_answers) < len(active_players):
                        pass

                    print("All clients have answered.")

                    # Send answers to all clients
                    for ip_addr, client_info in active_players.items():
                        client_conn = client_info.conn
                        try:
                            client_conn.sendall(str(client_answers).encode())
                        except Exception as e:
                            print(f"Error occurred while sending answers to {client_info.username} at {ip_addr}: {e}")
                            with lock:
                                # disconnected_players_dict[ip_addr] = client_info
                                del active_players[ip_addr]
                            continue

                    # Clear answers for the next round
                    client_answers.clear()

                    # Receive and process votes from clients
                    for ip_addr, client_info in active_players.items():
                        client_conn = client_info.conn
                        try:
                            voted_player = client_conn.recv(1024).decode()
                            print(f"Vote from {client_info.username}: {voted_player}")

                            if voted_player in active_players:
                                active_players[voted_player].score += 1
                            else:
                                active_players[voted_player] = ClientInfo(None, voted_player, None)
                                active_players[voted_player].score = 1
                        except Exception as e:
                            print(f"Error occurred while receiving vote from {client_info.username} at {ip_addr}: {e}")
                            with lock:
                                # disconnected_players_dict[ip_addr] = client_info
                                del active_players[ip_addr]
                            continue

                    # Display the updated scoreboard
                    scoreboard = ", ".join([f"{client_info.username}: {client_info.score}" for client_info in client_info_dict.values()])
                    print("Updated Scoreboard:", scoreboard)

                    # Send updated scoreboard to all clients
                    for ip_addr, client_info in active_players.items():
                        client_conn = client_info.conn
                        try:
                            client_conn.sendall(scoreboard.encode())
                        except Exception as e:
                            print(f"Error occurred while sending scoreboard to {client_info.username} at {ip_addr}: {e}")
                            with lock:
                                # disconnected_players_dict[ip_addr] = client_info
                                del active_players[ip_addr]
                            continue

                    
                
                # Find and declare the winner
                print("\nGame Over!")

                # Find and declare the winner or indicate a tie
                max_score = max(active_players.values(), key=lambda x: x.score).score
                winners = [player for player in active_players.values() if player.score == max_score]
                
                winners_string = ", ".join([winner.username for winner in winners])

                if len(winners) == 1:
                    final = f"Game Over! \n{winners[0].username} is the winner with a score of {winners[0].score}!"
                else:
                    final = f"Game Over! \nIt's a tie between {winners_string}!"

                for ip_addr, client_info in active_players.items():
                    client_conn = client_info.conn
                    try:
                        client_conn.sendall(final.encode())
                    except Exception as e:
                        print(f"Error occurred while sending final message to {client_info.username} at {ip_addr}: {e}")
                        with lock:
                            # disconnected_players_dict[ip_addr] = client_info
                            del active_players[ip_addr]
                        continue
                exit()

            except Exception as e:
                print(f"An error occurred during game execution: {e}")

threading.Thread(target=run_game, daemon=True).start()

def main():
        # Set up the server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Load SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        # Wrap the socket with SSL
        with context.wrap_socket(s, server_side=True) as ssl_socket:
            ssl_socket.bind((HOST, PORT))
            ssl_socket.listen()

        print(f"Server is listening on {HOST}:{PORT}")

        with ThreadPoolExecutor() as executor:
            while True:
                conn, addr = ssl_socket.accept()
                executor.submit(handle_client, conn, addr)

if __name__ == "__main__":
    main()
