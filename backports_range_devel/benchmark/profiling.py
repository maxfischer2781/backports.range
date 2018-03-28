from __future__ import print_function
import argparse
import cProfile
import backports.range
import time
import resource
import sys
import json


RANGE_TYPES = {
    'builtin': range,
    'backport': backports.range.range,
}


def pyrange(start_stop, stop, step):
    """Construct a python range object regardless of cython support"""
    self = object.__new__(backports.range.range)
    self.__init__(start_stop, stop, step)
    return self


RANGE_TYPES['pyrange'] = pyrange

try:
    RANGE_TYPES['xrange'] = xrange
except NameError:
    pass


def flatten_range_args(start_stop, stop=None, step=None):
    if not stop:
        stop = start_stop
        start_stop = 0
    step = step or 1
    return start_stop, stop, step


def profile_iteration(range_type, start, stop, step, max_time=1.0):
    profiler = cProfile.Profile()
    end_time = time.time() + max_time
    while time.time() < end_time:
        profiler.enable()
        range_obj = range_type(start, stop, step)
        result = [a for a in range_obj]
        profiler.disable()
    assert len(result) == len(range_type(start, stop, step))
    profiler.create_stats()
    return profiler


def track_iteration(range_type, start, stop=None, step=None, max_time=1.0):
    loops = 0
    start_resources = resource.getrusage(resource.RUSAGE_SELF)
    end_time = time.time() + max_time
    while time.time() < end_time:
        loops += 1
        range_obj = range_type(start, stop, step)
        result = [a for a in range_obj]
    end_resources = resource.getrusage(resource.RUSAGE_SELF)
    assert len(result) == len(range_type(start, stop, step))
    usage = resource.struct_rusage((end_resources[idx] - start_resources[idx]) for idx in range(len(end_resources)))
    return loops, usage


CLI = argparse.ArgumentParser()
CLI.add_argument(
    'type',
    nargs='?',
    choices=list(RANGE_TYPES),
    default='backport',
)
CLI.add_argument(
    'range_args',
    nargs='*',
    help='positional arguments to pass to range',
    type=int,
    default=[1024]
)
CLI.add_argument(
    '--profile',
    help='profile sort key (empty string disables profile)',
    default='cumtime',
)
CLI.add_argument(
    '--time',
    help='maximum duration per test',
    default=1.0,
    type=float,
)


def run_benchmark(range_type, start, stop, step, max_time, sort):
    range_class = RANGE_TYPES[range_type]
    if sort:
        profiler = profile_iteration(range_class, start, stop, step, max_time)
        profiler.print_stats(sort)
    loops, usages = zip(*(track_iteration(range_class, start, stop, step, max_time) for _ in range(5)))
    return {
        range_type: {
            'conditions': {
                'extend': (start, stop, step),
                'size': stop-start,
            },
            'results': {
                'loops': sorted(loops),
                'rss': [usage.ru_maxrss for usage in usages],
                'ops': sorted(loop * (stop-start) for loop in loops)
            }
        }
    }


def main():
    options = CLI.parse_args()
    assert len(options.range_args) <= 3, 'range expects at most 3 arguments, got %d' % len(options.range_args)
    start, stop, step = flatten_range_args(*options.range_args)
    print('backports path:', backports.range.__file__, file=sys.stderr)
    print('range size:', stop-start, file=sys.stderr)
    print(json.dumps(
        run_benchmark(options.type, start, stop, step, options.time, options.profile),
        indent=2,
    ))


if __name__ == '__main__':
    main()
