import Pyro5.api
import threading


class Hall:
    def __init__(self, hall_id):
        self.players = {}
        self.player_id_counter = 1
        self.hall_id = hall_id

    def join_game(self):
        if len(self.players) < 2:
            player_id = self.player_id_counter
            self.player_id_counter += 1
            self.players[player_id] = {"data": {"x": 0, "y": 0}, "projectiles": 0, "life": 100}
            print(f"Se ha unido un jugador. Total de jugadores: {len(self.players)}")
            return player_id
        else:
            return -1

    def cant_players(self):
        return len(self.players)

    def receive_move(self, player_id, data):
        self.players[player_id]["data"] = data

    def receive_proyectil(self, player_id):
        self.players[player_id]["projectiles"] = 1

    def update_projectiles(self, player, projectiles):
        self.players[player]["projectiles"] = projectiles

    def get_move_and_projectiles(self, player_id):
        other_player_id = [p_id for p_id in self.players if p_id != player_id]
        if other_player_id:
            other_player_id = other_player_id[0]
            other_player_data = self.players[other_player_id]["data"]
            self.players[other_player_id]["data"] = {"x": 0, "y": 0}
            bool_proyectil = self.players[other_player_id]["projectiles"]
            self.players[other_player_id]["projectiles"] = 0
            return other_player_data, bool_proyectil
        else:
            return None, self.players[player_id]["projectiles"]

    def return_life(self, player_id):
        return self.players[player_id]["life"]

    def receive_colision(self, player_id):
        self.players[player_id]["life"] -= 15

    def return_life_player2(self, player_id):
        other_player_id = [p_id for p_id in self.players if p_id != player_id]
        if other_player_id:
            return self.players[other_player_id[0]]["life"]
        else:
            return -1

    def start_game(self):
        if len(self.players) == 2:
            return True
        else:
            return False

    def remove_players(self):
        self.players.clear()
        self.player_id_counter = 1


class GameServer:
    def __init__(self):
        self.halls = []

    @Pyro5.api.expose
    def join_game(self):
        for hall in self.halls:
            if hall.cant_players() < 2:
                player_id = hall.join_game()
                return hall.hall_id, player_id
        return -1, -1

    @Pyro5.api.expose
    def receive_move(self, hall_id, player_id, data):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                hall.receive_move(player_id, data)
                break

    @Pyro5.api.expose
    def receive_projectile(self, hall_id, player_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                hall.receive_proyectil(player_id)
                break

    @Pyro5.api.expose
    def get_move_and_projectiles(self, hall_id, player_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall.get_move_and_projectiles(player_id)

    @Pyro5.api.expose
    def return_life(self, hall_id, player_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall.return_life(player_id)

    @Pyro5.api.expose
    def receive_colision(self, hall_id, player_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                hall.receive_colision(player_id)

    @Pyro5.api.expose
    def return_life_player2(self, hall_id, player_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall.return_life_player2(player_id)

    @Pyro5.api.expose
    def start_game(self, hall_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                return hall.start_game()

    @Pyro5.api.expose
    def remove_players(self, hall_id):
        for hall in self.halls:
            if hall.hall_id == hall_id:
                hall.remove_players()
                print("jugadores removidos sala ", str(hall_id))
                break


def create_hall(sala_id, halls):
    hall = Hall(sala_id)
    halls.append(hall)
    return hall


def run_server():
    server = GameServer()
    daemon = Pyro5.api.Daemon(host='172.31.3.72', port=9090)
    uri = daemon.register(server, "server")
    halls = []
    threads = []
    for sala_id in range(4):
        thread = threading.Thread(target=create_hall, args=(sala_id, halls,))
        threads.append(thread)
        thread.start()

    server.halls = halls
    print("Servidor listo para aceptar conexiones.")
    print("URI del servidor: " + str(uri))
    daemon.requestLoop()


if __name__ == "__main__":
    run_server()
