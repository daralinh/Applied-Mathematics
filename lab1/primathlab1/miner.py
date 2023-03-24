from math import log, sin

import matplotlib.pyplot as plt
from numpy import arange

from alg import minimizers
from util import CallCounter

LEFT = 0.1
RIGHT = 7
EPS_START = 0.001
EPS_END = 0.5
EPS_STEP = 0.001


def f(x):
    """Исходная функция"""
    return sin(x) - log(x ** 2) - 1


if __name__ == "__main__":
    eps_values = arange(EPS_START, EPS_END, EPS_STEP)
    for algo in minimizers:
        print(algo.__name__)
        call_counts = []
        for eps in eps_values:
            fn_counted = CallCounter(f)
            res = algo(fn_counted, LEFT, RIGHT, eps)
            call_counts.append(fn_counted.get_count())
        plt.plot(eps_values, call_counts, label=algo.__name__)

    plt.title("Число вызовов функции в зависимости от точности")
    plt.xlabel(f"Точность, [{EPS_START}, {EPS_END}], с шагом в {EPS_STEP}")
    plt.ylabel("Вызовов функции")
    plt.gca().yaxis.get_major_locator().set_params(integer=True)
    plt.legend()
    plt.show()
