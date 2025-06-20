import socket
import threading
import pickle
import random
from game import YahtzeeGame
from gamestate import GameState

HOST = '0.0.0.0'
PORT = 9009
rooms = {}
lock = threading.Lock()

# Create a unique 4-digit room code
def get_code():
    while True:
        code = str(random.randint(1000, 9999))
        with lock:
            if code not in rooms:
                return code

def client(conn, addr):
    print(f"New connection from {addr}")
    room = None
    name = None

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = pickle.loads(data)

            # Handle room creation
            if msg['action'] == 'create':
                room_code = get_code()
                name = msg['name']
                room = GameState(room_code)
                room.players.append(name)
                room.scores[name] = YahtzeeGame(name)
                with lock:
                    rooms[room_code] = {'clients': [conn], 'state': room}
                conn.sendall(pickle.dumps({'status': 'created', 'code': room_code}))
            
            # Handle joining an existing room
            elif msg['action'] == 'join':
                room_code = msg['code']
                name = msg['name']
                with lock:
                    if room_code not in rooms or rooms[room_code]['state'].is_full():
                        conn.sendall(pickle.dumps({'status': 'error', 'message': 'Room full or not found'}))
                        continue
                
                    room_data = rooms[room_code]
                    room = room_data['state']
                    room.players.append(name)
                    room.scores[name] = YahtzeeGame(name)
                    room_data['clients'].append(conn)
                    room.ready = True
                
                conn.sendall(pickle.dumps({'status': 'joined', 'code': room_code}))
                broadcast_state(room_code)
            
            # A client requests a state refresh
            elif msg['action'] == 'state_request':
                if room: broadcast_state(room.room_code)
            
            # Handle game commands from client (roll or score)
            elif msg['action'] == 'command':
                room_code = msg['room']
                player = msg['player']
                command = msg['command']

                with lock:
                    game = rooms[room_code]['state'].scores[player]
                    
                    if command == 'roll':
                        game.roll_dice(msg.get('keep', [False]*5))
                    elif command == 'score':
                        game.score_category(msg['category'])

                        # Reset dice lock state and move to next player's turn
                        rooms[room_code]['state'].keep = [False] * 5
                        rooms[room_code]['state'].next_turn()

                        # Check if all players are done
                        all_done = all(gm.game_complete for gm in rooms[room_code]['state'].scores.values())
                        if all_done:
                            scores = {p: g.get_current_score() for p, g in rooms[room_code]['state'].scores.items()}
                            winner = max(scores, key=scores.get)
                            rooms[room_code]['state'].winner = winner
                            rooms[room_code]['state'].final_scores = scores
                broadcast_state(room_code)
    except:
        print(f"Connection lost: {addr}")
    finally:
        # Clean up client and room if necessary
        with lock:
            for code, room_data in list(rooms.items()):
                if conn in room_data['clients']:
                    room_data['clients'].remove(conn)
                    print(f"Client removed from room {code}")
                    if not room_data['clients']:
                        del rooms[code]
                        print(f"Room {code} deleted (empty)")
        conn.close()

# Send the current GameState to all clients in a room
def broadcast_state(room_code):
    with lock:
        room_data = rooms[room_code]
        if not room_data:
            return
    game_state = room_data['state']
    data = pickle.dumps({'action': 'update', 'game': game_state})
    
    disconnected_clients = []
    for client in room_data['clients']:
        try:
            client.sendall(data)
        except:
            disconnected_clients.append(client)
    
    for dc in disconnected_clients:
            room_data['clients'].remove(dc)
            print("Disconnected client removed during broadcast")
    
    # If all clients are gone, delete the room
    if not room_data['clients']:
            del rooms[room_code]
            print(f"Room {room_code} deleted after all clients disconnected")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
