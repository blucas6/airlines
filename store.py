import random as rand
from entities import Plane
import math
from enums import *

class Store:
    def __init__(self):
        self.planes_available = []
        self.plane_prices = {   "A": 2000,
                                "B": 1000,
                                "C": 500 }
        self.airport_prices = [0, 0, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
        self.speed_benchmark = { "A": 2,
                                 "B": 1,
                                 "C": 0.5 }
        self.capacity_benchmark = { "A": 5,
                                    "B": 3,
                                    "C": 1 }
        self.fuel_benchmark = { "A": 1,
                                "B": 2,
                                "C": 3 }
    
    def refreshPlaneMarket(self, from_ctor, game):
        if not from_ctor:
            game.CASH -= REFRESH_PLANE_MARKET_PRICE
        b = [self.speed_benchmark, self.capacity_benchmark, self.fuel_benchmark]
        self.planes_available = []
        for p in range(3):
            rolls = [rand.random()*100, rand.random()*100, rand.random()*100]
            stats = [0,0,0]
            rank = 0
            for r in range(len(rolls)):
                if rolls[r] < 75:
                    stats[r] = round(b[r]["C"] + self.mod(b[r], "C"), 2)
                    rank += 1
                elif rolls[r] < 93:
                    stats[r] = round(b[r]["B"] + self.mod(b[r], "B"), 2)
                    rank += 2
                elif rolls[r] <= 100:
                    stats[r] = round(b[r]["A"] + self.mod(b[r], "A"), 2)
                    rank += 3
            rank = rank/3
            if round(rank) == 3:
                self.planes_available.append(Plane(stats[0], math.ceil(stats[1]), stats[2], self.plane_prices["A"], "None", "A", False))
            elif round(rank) == 2:
                self.planes_available.append(Plane(stats[0], math.ceil(stats[1]), stats[2], self.plane_prices["B"], "None", "B", False))
            else:
                self.planes_available.append(Plane(stats[0], math.ceil(stats[1]), stats[2], self.plane_prices["C"], "None", "C", False))

    def mod(self, bench, rank):
        mod = 1
        if rank == "A":
            mod = abs(bench["A"] - bench["B"]) / 2
        if rank == "B":
            mod = abs(bench["B"] - bench["C"]) / 2
        if rank == "C":
            mod = abs(bench["B"] - bench["C"]) / 2
        return rand.uniform(0.0001, mod) * (-1 if rand.random() < 0.4 else 1)
