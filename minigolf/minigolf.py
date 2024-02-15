from dataclasses import dataclass

class Player:
    def __init__(self, name: str):
        self._name = name


    @property
    def name(self) -> str:
        return self._name


class HitsMatch:
    def __init__(self, holes: int, players: list):
        self._holes = holes
        self._players = players

        self._players_and_points = {player.name: 0 for player in self._players}
        self._result_table = [tuple(self._players_and_points), *[tuple(None for _ in range(len(self._players))) for _ in range(self._holes)]]
        self._hole_table = [None for _ in range(len(self._players))]

        self._finished = False
        self._hole = 1
        self._start_player = self._index_player = 0


    def hit(self, success: bool=False) -> None:
        if not self._finished:
            self._players_and_points[self._players[self._index_player].name] += 1
            if not success:
                if self._players_and_points[self._players[self._index_player].name] == 9:
                    self._players_and_points[self._players[self._index_player].name] = 10
                    self._set_hole_table()
            else:
                self._set_hole_table()
            self._player_choice()
        else:
            raise RuntimeError


    @property
    def finished(self) -> bool:
        return self._finished


    def get_winners(self, type_game: str='Hits') -> list[Player]:
        if not self._finished:
            raise RuntimeError

        @dataclass
        class PlayerPoints:
            name: str
            points: int

        self._winners = []
        for player in self._players:
            points = 0
            index_player = self._players.index(player)
            for hole_result in self._result_table[1:]:
                points += hole_result[index_player]
            self._winners.append(PlayerPoints(player, points))

        func = min if type_game == 'Hits' else max
        winner_points = func(self._winners, key=lambda player: player.points).points
        if len(self._winners) == len(self._players):
            if (type_game == 'Hits' and winner_points == 10 * (self._hole - 1)) or (type_game == 'Holes' and winner_points == 0):
                return []
        return [player.name for player in self._winners if player.points == winner_points]


    def _set_hole_table(self):
        self._hole_table[self._index_player] = self._players_and_points[self._players[self._index_player].name]
        self._players_and_points[self._players[self._index_player].name] = 0


    def _player_choice(self) -> None:
        self._index_player = (self._index_player + 1) if (self._index_player < (len(self._players) - 1)) else 0

        choice_limit = len(self._players)
        while self._hole_table[self._index_player] is not None and choice_limit:
            self._index_player = (self._index_player + 1) if (self._index_player < (len(self._players) - 1)) else 0
            choice_limit -= 1

        if not choice_limit:
            self._start_player += 1
            self._index_player = self._start_player
            self._set_table()


    def _hole_selection(self):
        self._hole += 1
        if self._hole == len(self._result_table):
            self._finished = True


    def _set_table(self):
        self._result_table[self._hole] = tuple(self._hole_table)
        self._hole_selection()
        if not self._finished:
            self._hole_table = [None for _ in range(len(self._players))]


    def get_table(self):
        if not self._finished:
            self._result_table[self._hole] = tuple(self._hole_table)
            return self._result_table
        return self._result_table


class HolesMatch(HitsMatch):
    def __init__(self, holes: int, players: list):
        super().__init__(holes, players)


    def hit(self, success: bool=False) -> None:
        if not self._finished:
            self._players_and_points[self._players[self._index_player].name] += 1
            if not success:
                if self._players_and_points[self._players[self._index_player].name] == 10:
                    self._set_hole_table(success)
            else:
                self._set_hole_table(success)
            self._player_choice()
        else:
            raise RuntimeError


    def _set_hole_table(self, success: bool) -> None:
        if success:
            self._hole_table[self._index_player] = 1
        else:
            self._hole_table[self._index_player] = 0


    def _set_table(self):
        self._hole_table = tuple(map(lambda item: item if item is not None else 0, self._hole_table))
        return super()._set_table()


    def _hole_selection(self):
        self._players_and_points = {player.name: 0 for player in self._players}
        return super()._hole_selection()


    def get_winners(self, type_game: str='Hits') -> list[Player]:
        return super().get_winners('Holes')


    def _player_choice(self) -> None:
        self._index_player = (self._index_player + 1) if self._index_player < (len(self._players) - 1) else 0

        if self._index_player == self._start_player:
            if any(self._hole_table) or sum(self._players_and_points.values()) == 30:
                self._start_player += 1
                self._index_player = self._start_player
                self._set_table()
