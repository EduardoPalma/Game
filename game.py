from cliente import Connection
from cliente.GameStart import GameStart

server = Connection.server()


def main():
    hall_id, id_player = server.join_game()
    game_start = GameStart(800, 600, hall_id, id_player, server, True)
    game_start.main_loop()


if __name__ == "__main__":
    main()
