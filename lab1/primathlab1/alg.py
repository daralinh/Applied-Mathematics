from bisect import bisect_left
from math import sqrt, isclose

minimizers = []


def minimizer(fn):
    """Декоратор для регистрации алгоритмов"""
    minimizers.append(fn)
    return fn


# K - золотое сечения = 1 - 1 / phi = 1 - 1 / 1.618.. = 0.382
K = (3 - sqrt(5)) / 2
# STEP - длина шага для кв. аппроксимации
STEP = 0.05

# CODE STYLE
# a0, b0 - начальный интервал
# a, b - текущий интервал
# intervals - массив отрезков по итерациям
# [ d - длина текущего интервала ]
# K - золотое сечения = 1 - 1 / phi = 1 - 1 / 1.618.. = 0.382


@minimizer
def dichotomy_method(f, a0, b0, eps):
    """Метод дихотомии"""
    a = a0
    b = b0
    delta = eps / 2

    d = abs(b - a)
    intervals = [(a, b)]

    while d > eps:
        x1 = (a + b - delta) / 2
        x2 = (a + b + delta) / 2
        y1 = f(x1)
        y2 = f(x2)
        if y1 > y2:
            a = x1
        elif y1 < y2:
            b = x2
        else:
            a = x1
            b = x2

        d = abs(b - a)
        intervals.append((a, b))

    return intervals


@minimizer
def golden_ratio_method(f, a0, b0, eps):
    """Метод золотого сечения"""
    a = a0
    b = b0
    d = abs(b - a)

    x1 = a + K * d
    x2 = b - K * d
    y1 = f(x1)
    y2 = f(x2)

    intervals = [(a, b)]

    while d > eps:
        if y1 >= y2:
            a = x1
            x1 = x2
            x2 = b - K * (b - a)
            y1 = y2
            y2 = f(x2)
        else:
            b = x2
            x2 = x1
            x1 = a + K * (b - a)
            y2 = y1
            y1 = f(x1)
        d = b - a
        intervals.append((a, b))
    return intervals


class Fibonacci:
    """Класс для работы с числами Фибоначчи"""

    def __init__(self):
        self._cache = [1, 1]

    def _append_next(self):
        next_fib = sum(self._cache[-2:])
        self._cache.append(next_fib)

    def fib(self, n):
        """Найти n-ое число Фибоначчи, n >= 0"""

        while n >= len(self._cache):
            self._append_next()
        return self._cache[n]

    def n(self, fib):
        """Найти номер числа Фибоначчи, ближайшего сверху к fib"""

        if fib <= self._cache[-1]:
            return bisect_left(self._cache, fib)

        while fib > self._cache[-1]:
            self._append_next()
        return len(self._cache) - 1


@minimizer
def fibonacci_method(f, a0, b0, eps):
    """Метод Фибоначчи"""

    a = a0
    b = b0

    fib = Fibonacci()

    fib_iters = (b - a) / eps
    n = fib.n(fib_iters) - 2

    x1 = a + fib.fib(n) / fib.fib(n + 2) * (b - a)
    x2 = a + fib.fib(n + 1) / fib.fib(n + 2) * (b - a)
    y1 = f(x1)
    y2 = f(x2)

    intervals = [(a, b)]

    for k in range(2, n + 3):
        if y1 > y2:
            a = x1
            x1, y1 = x2, y2
            x2 = a + fib.fib(n - k + 2) / fib.fib(n - k + 3) * (b - a)
            y2 = f(x2)
        else:
            b = x2
            x2, y2 = x1, y1
            x1 = a + fib.fib(n - k + 1) / fib.fib(n - k + 3) * (b - a)
            y1 = f(x1)
        intervals.append((a, b))

    return intervals


def get_xs(f, x1, f1, step):
    """Найти точки вблизи начальной. Точки возвращаются в естественном порядке"""

    x2 = x1 + step
    f2 = f(x2)

    if f1 > f2:
        x3 = x1 + 2 * step
    else:
        x3 = x1 - step

    f3 = f(x3)

    (x1, f1), (x2, f2), (x3, f3) = sorted([(x1, f1), (x2, f2), (x3, f3)])

    #                        0               0      0                   0
    #  0          x3            0          0            x1            0
    #    0     x2                 x1    x3                  x2      0
    #       x1                       x2                         x3
    #
    #   МЕЖДУ x1, x2, x3 = step

    return x1, x2, x3, f1, f2, f3


def get_min_x_f(f1, f2, f3, x1, x2, x3):
    """Выбрать точку с минимальным значением функции"""

    f_min, x_min = min((f1, x1), (f2, x2), (f3, x3))
    return x_min, f_min


class ApproximationError(RuntimeError):
    pass


def square_approximation(f, f1, f2, f3, x1, x2, x3, step):
    """Найти вершину параболы по трём точкам. При линейном расположении точек перейти к новым"""

    if isclose((x2 - x1) * (f2 - f3) - (x2 - x3) * (f2 - f1), 0):
        raise ApproximationError("Аппроксимируемые точки лежат на одной прямой")

    else:
        u = (
            0.5
            * (
                (x2 ** 2 - x3 ** 2) * f1
                + (x3 ** 2 - x1 ** 2) * f2
                + (x1 ** 2 - x2 ** 2) * f3
            )
            / ((x2 - x3) * f1 + (x3 - x1) * f2 + (x1 - x2) * f3)
        )
        return u


@minimizer
def parabola_method(f, a0, b0, eps):
    """Метод квадратичной аппроксимации"""

    eps /= 2
    intervals = []
    intervals.append((a0, b0))

    x1 = (a0 + b0) / 2
    f1 = f(x1)
    x1, x2, x3, f1, f2, f3 = get_xs(f, x1, f1, STEP)
    f3 = f(x3)

    while True:

        x_min, f_min = get_min_x_f(f1, f2, f3, x1, x2, x3)

        try:
            u = square_approximation(f, f1, f2, f3, x1, x2, x3, STEP)
        except ApproximationError:
            x1, x2, x3, f1, f2, f3 = get_xs(f, x_min, f_min, STEP)
            continue

            
        fu = f(u)

        if abs((f_min - fu) / fu) < eps and abs((x_min - u) / u) < eps:
            intervals.append((u - eps, u + eps))
            break

        if x1 <= u <= x3:
            # если улучшили результат, принять
            if f_min + eps >= fu:
                x2, f2 = u, fu
            else:
                x2, f2 = x_min, f_min
            x1 = x2 - STEP
            x3 = x2 + STEP
            f1 = f(x1)
            f3 = f(x3)

        else:
            x1, x2, x3, f1, f2, f3 = get_xs(f, u, fu, STEP)

        intervals.append((x1, x3))

    return intervals


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


@minimizer
def brent_method(f, a0, b0, eps):
    """Комбинированный метод Брента"""

    intervals = []
    intervals.append((a0, b0))

    # a, b - текущий интервал поиска
    # x - текущий минимум
    # f(x) - текущее минимальное значение
    # w - второе снизу значение функции
    # v - предыдущее значение w
    # u - минимум аппроксимации

    a = a0
    b = b0

    eps /= 2

    x = w = v = (a + b) / 2
    f_x = f_w = f_v = f(x)
    d = e = b - a

    while d > eps:
        g = e
        e = d

        if intervals[-1] != (a, b):
            intervals.append((a, b))

        # нужно выбрать минимум u:
        if (
            (x != w)
            and (x != v)
            and (w != v)
            and (f_x != f_w)
            and (f_x != f_v)
            and (f_w != f_v)
        ):
            try:
                u = square_approximation(f, f_v, f_x, f_w, v, x, w, STEP)
            except ApproximationError:
                pass
            else:
                if a + eps <= u <= b - eps and abs(u - x) < 0.5 * g:
                    d = abs(u - x)
                    continue

        if x < 0.5 * (b + a):
            u = x + K * (b - x)
            d = b - x
        else:
            u = x - K * (x - a)
            d = x - a

        if abs(u - x) < eps:
            u = x + sign(u - x) * eps

        # обновить значения с новой u
        f_u = f(u)
        if f_u <= f_x:
            if u >= x:
                a = x
            else:
                b = x
            v = w
            w = x
            x = u
            f_v = f_w
            f_w = f_x
            f_x = f_u
        else:
            if u >= x:
                b = u
            else:
                a = u
            if f_u <= f_w or w == x:
                # откатиться на 1 шаг назад
                v = w
                w = u
                f_v = f_w
                f_w = f_u
            elif f_u <= f_v or v == x or v == w:
                # откатиться на 2 шага назад
                v = u
                f_v = f_u

    return intervals