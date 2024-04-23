import berserk
import os
from dotenv import load_dotenv

load_dotenv()

lichess_api = os.getenv('LICHESS_API')

session = berserk.TokenSession(lichess_api)
client = berserk.Client(session=session)

class GameDataCollector:
    def __init__(self, client, player):
        self.client = client
        self.games = client.games.export_by_player(player)
        self.gameData = {}

    def collectGameData(self, numberOfGames=10):
        for i, game in enumerate(self.games):
            if i >= numberOfGames:  # Ensure we don't exceed the requested number of games
                break
            self.gameId = game['id']
            opening = self.client.games.export(self.gameId)['opening']['name']
            gameSpeed = game['speed']
            gameResult = game['winner']
            self.gameData[self.gameId] = [opening, gameSpeed, gameResult]

    def get_game_data(self):
        return self.gameData

output = GameDataCollector(client, "defford1989")
output.collectGameData(10)

print(output.get_game_data())
