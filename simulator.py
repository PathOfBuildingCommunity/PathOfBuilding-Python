# Simulator

import global_variables as GV
import time
from concurrent.futures import ProcessPoolExecutor
import secrets

class Simulator:
    def __init__(self, runAmount: int = 5, runTime: float = 100.0):
        self.runIndex = 0
        self.runAmount = runAmount
        self.runTime = runTime

    def runSingle(self, runID: int):
        self.runIndex = runID
        print("Starting run {} of {}".format(self.runIndex + 1, self.runAmount))
        sr = SimulationRun(self.runTime * secrets.randbelow(100))
        ret = sr.run()
        print("Completed run {} of {}".format(self.runIndex + 1, self.runAmount))
        return ret

    def runParallel(self, numWorkers: int = 5):
        with ProcessPoolExecutor(numWorkers) as executor:
            results = executor.map(self.runSingle, range(self.runAmount))
        return sum([x for x in results])

    def runAll(self):
        self.runParallel(5)


class SimulationRun:
    def __init__(self, runTime: float):
        self.runTime = runTime
        print(f'RUN TIME: {self.runTime}')

    def run(self):
        time = 0.0
        while time < self.runTime:
            time += GV.SERVER_TICK_INTERVAL
        return 1

if __name__ == "__main__":
    x = Simulator()
    x.runAll()
