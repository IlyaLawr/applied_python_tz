import unittest
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minigolf import HitsMatch, HolesMatch, Player

class HitsMatchTestCase(unittest.TestCase):
    def test_scenario(self):
        players = [Player('A'), Player('B'), Player('C')]
        m = HitsMatch(3, players)

        self._first_hole(m)
        self._second_hole(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [
            players[0], players[2]
        ])

    def _first_hole(self, m):
        m.hit()     # 1
        m.hit()     # 2
        m.hit(True) # 3
        m.hit(True) # 1
        for _ in range(8):
            m.hit() # 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        m.hit() # 2
        for _ in range(3):
            m.hit(True) # 3, 1, 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (None, None, None),
        ])

    def _third_hole(self, m):
        m.hit()     # 3
        m.hit(True) # 1
        m.hit()     # 2
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, None, None),
        ])
        m.hit(True) # 3
        m.hit()     # 2
        m.hit(True) # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ])

    def test_scenario2(self):
        players = [Player('Felix'), Player('Motador'), Player('Djoni'), Player('Maks')]
        m = HitsMatch(4, players)

        self._first_hole2(m)

        self._second_hole2(m)

        self._third_hole2(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._fourth_hole2(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [players[2]])

    def _first_hole2(self, m):
        for _ in range(4):
             m.hit() # 1, 2, 3, 4

        m.hit(True) # 1
        m.hit()     # 2
        m.hit()     # 3
        m.hit(True) # 4

        for _ in range(6):
            m.hit() # 2, 3

        m.hit(True) # 2

        for _ in range(3):
            m.hit() # 3

        m.hit(True) # 3

        self.assertEqual(m.get_table(), [
            ('Felix', 'Motador', 'Djoni', 'Maks'),
            (2, 6, 9, 2),
            (None, None, None, None),
            (None, None, None, None),
            (None, None, None, None),
        ])

    def _second_hole2(self, m):
        for _ in range(3):
             m.hit(True) # 2, 3, 4
        m.hit()     # 1
        m.hit(True) # 1

        self.assertEqual(m.get_table(), [
            ('Felix', 'Motador', 'Djoni', 'Maks'),
            (2, 6, 9, 2),
            (2, 1, 1, 1),
            (None, None, None, None),
            (None, None, None, None),
        ])

    def _third_hole2(self, m):
        for _ in range(3):
             m.hit() # 3, 4, 1

        m.hit(True) # 2

        for _ in range(9):
            m.hit() # 3, 4, 1

        m.hit(True) # 3

        for _ in range(4):
            m.hit() # 4, 1

        m.hit()     # 4
        m.hit(True) # 1

        m.hit()     # 4
        m.hit(True) # 4

        self.assertEqual(m.get_table(), [
            ('Felix', 'Motador', 'Djoni', 'Maks'),
            (2, 6, 9, 2),
            (2, 1, 1, 1),
            (7, 1, 5, 9),
            (None, None, None, None),
        ])


    def _fourth_hole2(self, m):
        for _ in range(4):
            m.hit() # 4, 1, 2, 3

        m.hit()     # 4
        m.hit()     # 1
        m.hit()     # 2
        m.hit(True) # 3

        for _ in range(12):
            m.hit() # 4, 1, 2

        m.hit(True) # 4
        m.hit()     # 1
        m.hit()     # 2
        m.hit()     # 1
        m.hit()     # 2
        m.hit()     # 1
        m.hit()     # 2


        self.assertEqual(m.get_table(), [
            ('Felix', 'Motador', 'Djoni', 'Maks'),
            (2, 6, 9, 2),
            (2, 1, 1, 1),
            (7, 1, 5, 9),
            (10, 10, 2, 7),
        ])


    def test_scenario3(self):
        players = [Player('1'), Player('2'), Player('3')]
        m = HitsMatch(3, players)

        try:
            while True:
                m.hit()
        except RuntimeError:
            self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (10, 10, 10),
            (10, 10, 10),
            (10, 10, 10),
        ])

            self.assertEqual(m.get_winners(), [])

    def test_scenario4(self):
        players = [Player('Иван'), Player('Дмитрий'), Player('Александр')]
        m = HitsMatch(3, players)

        try:
            while True:
                m.hit(True)
        except RuntimeError:
            self.assertEqual(m.get_table(), [
            ('Иван', 'Дмитрий', 'Александр'),
            (1, 1, 1),
            (1, 1, 1),
            (1, 1, 1),
        ])

            self.assertEqual(m.get_winners(), [players[0], players[1], players[2]])


class HolesMatchTestCase(unittest.TestCase):
    def test_scenario(self):
        players = [Player('A'), Player('B'), Player('C')]
        m = HolesMatch(3, players)

        self._first_hole(m)
        self._second_hole(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [players[0]])

    def _first_hole(self, m):
        m.hit(True) # 1
        m.hit()     # 2
        m.hit()     # 3

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        for _ in range(10):
            for _ in range(3):
                m.hit() # 2, 3, 1

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, None),
        ])

    def _third_hole(self, m):
        for _ in range(9):
            for _ in range(3):
                m.hit() # 3, 1, 2
        m.hit(True) # 3
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, 1),
        ])
        m.hit(True) # 1
        m.hit()     # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (1, 0, 1),
        ])


    def test_scenario2(self):
        players = [Player('1'), Player('2'), Player('3')]
        m = HolesMatch(3, players)

        self._first_hole2(m)
        self._second_hole2(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._third_hole2(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [players[1]])

    def _first_hole2(self, m):
        m.hit()     # 1
        m.hit()     # 2
        m.hit()     # 3
        m.hit()     # 1
        m.hit(True) # 2
        m.hit(True) # 3

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (0, 1, 1),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole2(self, m):
        for _ in range(3):
            for _ in range(3):
                m.hit() # 2, 3, 1

        m.hit(True) # 2
        m.hit()     # 3
        m.hit(True) # 1

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (0, 1, 1),
            (1, 1, 0),
            (None, None, None),
        ])

    def _third_hole2(self, m):
        for _ in range(9):
            for _ in range(3):
                m.hit() # 3, 1, 2
        m.hit() # 3
        self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (0, 1, 1),
            (1, 1, 0),
            (None, None, 0),
        ])
        m.hit()     # 1
        m.hit(True) # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (0, 1, 1),
            (1, 1, 0),
            (0, 1, 0),
        ])


    def test_scenario3(self):
        players = [Player('1'), Player('2'), Player('3')]
        m = HolesMatch(3, players)

        try:
            while True:
                m.hit()
        except RuntimeError:
            self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ])

            self.assertEqual(m.get_winners(), [])


    def test_scenario4(self):
        players = [Player('1'), Player('2'), Player('3')]
        m = HolesMatch(3, players)

        try:
            while True:
                m.hit(True)
        except RuntimeError:
            self.assertEqual(m.get_table(), [
            ('1', '2', '3'),
            (1, 1, 1),
            (1, 1, 1),
            (1, 1, 1),
        ])

            self.assertEqual(m.get_winners(), [players[0], players[1], players[2]])

if __name__ == '__main__':
    unittest.main()

sys.path.pop(0)
