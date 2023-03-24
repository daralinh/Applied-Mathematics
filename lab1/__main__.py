import inspect
import sys
from argparse import ArgumentParser, BooleanOptionalAction
from math import log, sin

import matplotlib.pyplot as plt

from primathlab1.alg import minimizers
from primathlab1.util import CallCounter


def f(x):
    """Исходная функция"""
    return sin(x) - log(x ** 2) - 1


def f1(x):
    """Исходная функция"""
    return sin(x)


def f2(x):
    """Исходная функция"""
    return x + 1 / x


def f3(x):
    return sin(x - 1)


parser = ArgumentParser(
    description="Найти локальный минимум функции несколькими способами",
)
parser.add_argument("-l", type=float, default=0.1, help="Левая граница интервала")
parser.add_argument("-r", type=float, default=7.0, help="Правая граница интервала")
parser.add_argument("-e", "--eps", type=float, default=0.001, help="Точность")
parser.add_argument(
    "--plot",
    default=False,
    action=BooleanOptionalAction,
    help="Нарисовать графики длин интервалов",
)
parser.add_argument("--csv-dump", required=False, help="CSV файл для записи интервалов")

args = parser.parse_args()


def analysis(l, r, eps, f):

    if not l < r:
        print("Левая граница должна быть меньше правой", file=sys.stderr)
        sys.exit(1)

    print(
        "Исследуемая функция:",
        inspect.getsource(f).split("\n")[2].lstrip()[7:],
    )

    print(f"Исследуемый интервал: ({l}, {r})")
    print(f"Точность: {eps}")

    print()

    result_intervals = []

    for algo in minimizers:
        fn_counted = CallCounter(f)
        intervals = algo(fn_counted, l, r, eps)
        result_intervals.append(intervals)
        res = sum(intervals[-1]) / 2.0
        iter_count = len(intervals) - 1  # -1 - не учитывать исходный
        print(
            f"Метод: {algo.__name__}",
            f"Результат: {res:.3f}",
            f"Вызовов функции: {fn_counted.get_count()}",
            f"Итераций: {iter_count}",
            sep="\n",
            end="\n\n",
        )

    if args.csv_dump:
        with open(args.csv_dump, "w") as dump_f:
            for algo, intervals in zip(minimizers, result_intervals):
                print(algo.__name__, file=dump_f)
                print("left", "right", "width", "delta", sep=",", file=dump_f)
                prev_width = intervals[0][1] - intervals[0][0]
                for left, right in intervals:
                    width = right - left
                    delta = width / prev_width
                    print(left, right, width, delta, sep=",", file=dump_f)
                    prev_width = width

    if args.plot:
        for algo, intervals in zip(minimizers, result_intervals):
            lengths = [abs(b - a) for a, b in intervals]
            plt.plot(range(len(intervals)), lengths, ".-", label=algo.__name__)
            plt.plot()

        plt.legend()
        plt.gca().xaxis.get_major_locator().set_params(integer=True)
        plt.title("Изменение длин интервалов в процессе работы алгоритмов")
        plt.xlabel("Номер итерации")
        plt.ylabel("Длина интервала")
        plt.show()


analysis(args.l, args.r, args.eps, f)
# analysis(2.15, 7.15, 0.001, f1)
# analysis(0.5, 2.0, 0.001, f2)
# analysis(-1.0, 1.0, 0.001, f3)
# analysis(0.7, 6.7, 0.001, f)
