# Переписываем весь код на асинхронный стиль, согласно требованиям.
import asyncio
import random
import time
from collections import defaultdict, deque
from heapq import heappush, heappop
from typing import List, Dict, Tuple
import numpy as np
import json

# Глобальные параметры
EPOCHS = 10
TIME_ACCELERATION = 100  # Ускорение времени (1 реальная секунда = 100 симуляционных)
NUM_USERS = 100
NUM_MESSAGES = 500
MESSAGE_RATE = 0.25  # Лямбда для пуассоновского потока

# Ограничения Telegram API
GLOBAL_LIMIT = 30
USER_LIMIT = 20
USER_WINDOW = 60
GLOBAL_WINDOW = 1


# Структуры для хранения истории отправок
class RateLimiter:
    def __init__(self):
        self.global_history = deque()
        self.user_history = defaultdict(deque)

    def _prune(self, current_time):
        # Очистка устаревших записей
        while self.global_history and current_time - self.global_history[0] > GLOBAL_WINDOW:
            self.global_history.popleft()
        for user in self.user_history:
            while self.user_history[user] and current_time - self.user_history[user][0] > USER_WINDOW:
                self.user_history[user].popleft()

    def can_send(self, user_id, current_time):
        self._prune(current_time)
        return (len(self.global_history) < GLOBAL_LIMIT and
                len(self.user_history[user_id]) < USER_LIMIT)

    def record_send(self, user_id, current_time):
        self.global_history.append(current_time)
        self.user_history[user_id].append(current_time)

# Хранилище результатов
results = {
    "greedy": [],
    "fifo": []
}

# Генератор сообщений по пуассоновскому потоку
async def generate_messages(queue: asyncio.Queue, label: str):
    for j in range(NUM_MESSAGES):
        await asyncio.sleep(random.expovariate(MESSAGE_RATE) / TIME_ACCELERATION)
        a_j = time.time()
        U_j = random.sample(range(NUM_USERS), random.randint(1, NUM_USERS))
        await queue.put((j, a_j, U_j))
        print(f"[{label}] New message {j} to {len(U_j)} users at time {a_j:.2f}")

# Жадный алгоритм
async def greedy_dispatcher(input_queue: asyncio.Queue):
    Q_M = []
    limiter = RateLimiter()
    dispatched = []

    while len(dispatched) < NUM_MESSAGES:
        # Добавляем сообщения из очереди
        try:
            while True:
                j, a_j, U_j = input_queue.get_nowait()
                for u_k in U_j:
                    heappush(Q_M, (-1 * (time.time() - a_j), j, a_j, u_k, U_j))  # max-heap
        except asyncio.QueueEmpty:
            pass

        batch = []
        current_time = time.time()

        while Q_M and len(batch) < GLOBAL_LIMIT:
            _, j, a_j, u_k, U_j = heappop(Q_M)
            if limiter.can_send(u_k, current_time):
                limiter.record_send(u_k, current_time)
                batch.append((j, a_j, u_k, current_time))

        for j, a_j, u_k, t in batch:
            dispatched.append((j, a_j, u_k, t))

        await asyncio.sleep(1 / TIME_ACCELERATION)

    results["greedy"] = dispatched
    print("[Greedy] Finished dispatching.")

# FIFO алгоритм
async def fifo_dispatcher(input_queue: asyncio.Queue):
    Q_M = deque()
    limiter = RateLimiter()
    dispatched = []

    async def producer():
        while True:
            try:
                j, a_j, U_j = input_queue.get_nowait()
                for u_k in U_j:
                    Q_M.append((j, a_j, u_k))
            except asyncio.QueueEmpty:
                break
            await asyncio.sleep(0.01)

    async def consumer():
        while len(dispatched) < NUM_MESSAGES:
            current_time = time.time()
            if Q_M:
                j, a_j, u_k = Q_M.popleft()
                if limiter.can_send(u_k, current_time):
                    limiter.record_send(u_k, current_time)
                    dispatched.append((j, a_j, u_k, current_time))
            await asyncio.sleep(0.035 / TIME_ACCELERATION)

    await asyncio.gather(producer(), consumer())
    results["fifo"] = dispatched
    print("[FIFO] Finished dispatching.")

# Метрики
def analyze(name, dispatches):
    delays = [t - a for (_, a, _, t) in dispatches]
    missed = sum((t - a > 60) for (_, a, _, t) in dispatches)
    print(f"[{name}] Avg delay: {np.mean(delays):.3f}, Std: {np.std(delays):.3f}, >60s: {missed / len(dispatches) * 100:.2f}%")

# Главная функция
async def lemain():
    queue1 = asyncio.Queue()
    queue2 = asyncio.Queue()

    # Копируем одинаковые сообщения в обе очереди
    messages = []
    for _ in range(NUM_MESSAGES):
        a_j = time.time()
        U_j = random.sample(range(NUM_USERS), random.randint(1, NUM_USERS))
        messages.append((_, a_j, U_j))
        await asyncio.sleep(random.expovariate(MESSAGE_RATE) / TIME_ACCELERATION)

    for m in messages:
        await queue1.put(m)
        await queue2.put(m)

    await asyncio.gather(
        greedy_dispatcher(queue1),
        fifo_dispatcher(queue2)
    )

    analyze("Greedy", results["greedy"])
    analyze("FIFO", results["fifo"])

    with open("/mnt/data/results.json", "w") as f:
        json.dump(results, f)
