# Multiplayer Mad Lib Game

## Project Details

### Abstract
This project implements a multiplayer Mad Libs game where players fill in blanks in a sentence, and voting occurs to determine the funniest or most creative response.

### Implementation Details

#### Server Initialization
- Establishes a socket connection on a specified port.
- Wraps the connection with an SSL context for secure communication.
- Loads server certificate (`cert.pem`) and private key (`key.pem`) for authentication.

#### Client Handling
- Listens for incoming client connections and accepts them using threads.
- Receives username from the client and creates a `ClientObj` instance containing client information.
- Adds `ClientObj` to the dictionary of players.

#### Game Loop
- Runs continuously in a different thread, handling rounds until terminated.
- Starts when a minimum number of players have joined.
- Selects a random question from a predefined list.
- Sends the question to all connected players.
- Collects and sends back answers to players.
- Players vote for their favorite answer.
- Tallies votes, and the player with the most votes receives a point.
- Sends updated scoreboard to all players.

## Certificate Generation for SSL

### Generate Private Key and CSR (Certificate Signing Request)
```
openssl genrsa -out key.pem 2048
openssl req -new -key key.pem -out csr.pem
```

### Generate Self-Signed Certificate
```
openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem
```

### Generate CA (Certificate Authority) Certificate
```
openssl genrsa -out ca-key.pem 2048
openssl req -new -x509 -days 365 -key ca-key.pem -out ca.pem
```

## Adding to Trusted Source

After generating `ca.pem`, import it into the trusted sources of your computer to ensure secure communication.
