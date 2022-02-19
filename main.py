# Interface
import random

import matplotlib.pyplot as plt


class Scenario:
    queues = []
    stations = []

    def __init__(self) -> None:
        self.stations = [0 for i in range(5)]

    def add_job(self, job_time):
        pass

    def get_job(self, station_num) -> int:
        pass

    def tick(self):
        for i in range(len(self.stations)):
            if self.stations[i]:
                self.stations[i] -= 1  # tick the time for the service job down

            if self.stations[i] == 0 and not self.is_empty():  # if the station is empty now pull from the queue
                job = self.get_job(i)
                if job:
                    self.stations[i] = job

    def is_empty(self) -> bool:
        for q in range(len(self.queues)):
            if len(self.queues[q]):  # if any of the queues have something in them
                return False
        return True


class SingleQueue(Scenario):
    def __init__(self):
        super().__init__()
        self.queues = [[]]  # single queue

    def add_job(self, job_time):
        self.queues[0].insert(0, job_time)

    def get_job(self, station_num) -> int:
        return self.queues[0].pop()


class RoundRobinQueue(Scenario):
    robin_num = 0

    def __init__(self):
        super().__init__()
        self.queues = [[] for i in range(5)]

    def add_job(self, job_time):
        self.queues[self.robin_num].insert(0, job_time)
        self.robin_num = (self.robin_num + 1) % 5  # increment and set to next queue

    def get_job(self, station_num) -> int:
        if len(self.queues[station_num]):
            return self.queues[station_num].pop()

        return 0


class ShortestQueue(Scenario):

    def __init__(self):
        super().__init__()
        self.queues = [[] for i in range(5)]

    def add_job(self, job_time):
        s_idx = self.queues.index(min(self.queues))  # find the smallest queue
        self.queues[s_idx].insert(0, job_time)

    def get_job(self, station_num) -> int:
        if len(self.queues[station_num]):
            return self.queues[station_num].pop()
        return 0


class RandomQueue(Scenario):

    def __init__(self):
        super().__init__()
        self.queues = [[] for i in range(5)]

    def add_job(self, job_time):
        s_idx = random.randint(0, len(self.queues))
        self.queues[s_idx].insert(0, job_time)

    def get_job(self, station_num) -> int:
        if len(self.queues[station_num]):
            return self.queues[station_num].pop()
        return 0


def simulate(A: int, S: int, D: int, test: Scenario) -> (list, Scenario):
    stats = {
        'size': [[] for i in range(len(test.queues))],
        'tick_count': 0,
        'busy': [[] for i in range(len(test.stations))],
        'avg_wait': None
    }

    while D or not test.is_empty():
        if random.randint(1, A) == A and D:
            test.add_job(random.randint(1, S))

        test.tick()

        if D > 0:
            D -= 1

        stats['tick_count'] += 1

        for q in range(len(test.queues)):
            stats['size'][q].append(len(test.queues[q]))

        for s in range(len(test.stations)):
            if test.stations[s]:
                stats['busy'][s].append(1)

    items_in_system = 0
    for x in range(len(stats['size'])):
        items = 0
        for y in range(len(stats['size'][x])):
            items += stats['size'][x][y]
        items_in_system += items

    stats['avg_wait'] = items_in_system / stats['tick_count'] / A

    return stats, test


if __name__ == "__main__":
    A = 4
    S = 8 * A  # S >> 5*A
    D = 10000  # number of iterations, minutes

    sim_stats = {
        'single': {},
        'rr': {},
        'short': {}
    }

    # single queue simulation
    single = SingleQueue()
    stats, _ = simulate(A, S, D, single)
    sim_stats['single'] = stats
    for q in range(len(sim_stats['single']['size'])):
        ts = plt.plot(sim_stats['single']['size'][q], label='Queue %d' % q)
    print(stats['avg_wait'])

    # show plot
    plt.legend()
    plt.show()

    # round robing queue
    rr = RoundRobinQueue()
    stats, _ = simulate(A, S, D, rr)
    sim_stats['rr'] = stats
    for q in range(len(sim_stats['rr']['size'])):
        ts = plt.plot(sim_stats['rr']['size'][q], label='Queue %d' % q)
    print(stats['avg_wait'])

    # show plot
    plt.legend()
    plt.show()

    # shortest queue
    short = ShortestQueue()
    stats, _ = simulate(A, S, D, rr)
    sim_stats['short'] = stats
    for q in range(len(sim_stats['short']['size'])):
        ts = plt.plot(sim_stats['short']['size'][q], label='Queue %d' % q)
    print(stats['avg_wait'])

    # show plot
    plt.legend()
    plt.show()

    # random queue
    short = RandomQueue()
    stats, _ = simulate(A, S, D, rr)
    sim_stats['rand'] = stats
    for q in range(len(sim_stats['rand']['size'])):
        ts = plt.plot(sim_stats['rand']['size'][q], label='Queue %d' % q)
    print(stats['avg_wait'])

    # show plot
    plt.legend()
    plt.show()
