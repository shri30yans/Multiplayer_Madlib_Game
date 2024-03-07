import socket
import ssl

game_code = "1234"

HOST = "192.168.247.85"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cafile="ca.pem")
            try:
                ssl_socket = context.wrap_socket(s, server_hostname=HOST)
                ssl_socket.connect((HOST, PORT))
                print("Connected to server!")
            except ConnectionRefusedError:
                print("Connection refused. Please try again later.")
                return

            client_ip_address = s.getsockname()[0]

            # Input and send username to server.
            username = input("Enter your username: ")
            s.sendall(f"{username}".encode())

            # Receive joined acknowledgment
            print(s.recv(1024).decode())

            # Game Code
            s.sendall(game_code.encode())

            # Run rounds
            while True:
                # Receive question
                question = s.recv(1024).decode()
                if not question:
                    print("Connection closed by server.")
                    break
                
                if question.startswith("Game Over!"):
                    print(question)
                    exit()


                print("\n------------------------------------------------------------")
                print("Question:", question)
                print("------------------------------------------------------------")
                answer = input("Enter your answer: ")

                # Send answer to the server
                s.sendall(answer.encode())
                print("\nSent answer! Waiting for others to answer...")

                # Receive and display voting options
                voting_options = dict(eval(s.recv(1024).decode()))
                print("\n------------------------------------------------------------")
                print("Voting Options:")
                print("------------------------------------------------------------")

                # Uncomment if you want to remove the client's own answer from the voting options
                # voting_options.pop(client_ip_address)

                voting_options_list = list(voting_options.items())
                for index, (player, answer) in enumerate(voting_options_list):
                    print(f"    {index+1}: {answer}")

                # User inputs the index
                while True:
                    try:
                        choice = int(input("\nVote for an option: "))
                        if choice < 1 or choice > len(voting_options):
                            print("Invalid choice. Please enter a number between 1 and", len(voting_options))
                        else:
                            break  # a valid choice is entered
                    except ValueError:
                        print("Invalid input. Please enter an integer.")


                # Get the key-value pair at the given index
                player, answer = voting_options_list[choice-1]
                print(f"You selected the answer by {player}: {answer}")

                # Send the player username that the client voted for
                s.sendall(player.encode())

                # Display updated Scoreboard
                scoreboard = s.recv(1024).decode()
                print("\n------------------------------------------------------------")
                print("Updated Scoreboard:", scoreboard)
                print("------------------------------------------------------------\n")
    except Exception as e:
        print(f"An error occurred: {e}")

if _name_ == "_main_":
    main()
