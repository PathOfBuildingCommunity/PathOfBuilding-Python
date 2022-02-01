# Simulator

import global_variables as GV
import time
from concurrent.futures import ProcessPoolExecutor
import secrets


def log(msg: str) -> None:
    print(msg)


class Simulator:
    def __init__(self, runAmount: int = 5, runTime: float = 100.0) -> None:
        self.runIndex = 0
        self.runAmount = runAmount
        self.runTime = runTime

    def runSingle(self, runID: int) -> int:
        self.runIndex = runID
        sr = SimulationRun(self.runTime * secrets.randbelow(100))
        log(f"Starting run {self.runIndex + 1} of {self.runAmount}")
        ret = sr.run()
        log(f"Completed run {self.runIndex + 1} of {self.runAmount}")
        return ret

    def runParallel(self, numWorkers: int = 5) -> int:
        with ProcessPoolExecutor(numWorkers) as executor:
            results = executor.map(self.runSingle, range(self.runAmount))
        return sum([x for x in results])

    def runAll(self) -> None:
        self.runParallel(5)


class SimulationRun:
    def __init__(self, runTime: float) -> None:
        self.runTime = runTime
        log(f"RUN TIME: {self.runTime}")

    def run(self) -> int:
        time = 0.0
        while time < self.runTime:
            time += GV.SERVER_TICK_INTERVAL
        return 1


if __name__ == "__main__":
    x = Simulator()
    x.runAll()
