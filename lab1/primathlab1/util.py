class CallCounter:
    """Обёртка для подсчёта числа вызовов функции"""

    def __init__(self, fn):
        self._fn = fn
        self._count = 0

    def __call__(self, *args, **kwargs):
        self._count += 1
        return self._fn(*args, **kwargs)

    def get_count(self):
        return self._count

    def reset(self):
        self._count = 0
