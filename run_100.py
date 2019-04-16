#!/usr/bin/env python
import timeit
import sys

from run_once import run_once


def iterate():
    N = 100
    for i in range(N):
        img = run_once(write_outputs=False)
        img.save('/tmp/{0}.png'.format(i))
        sys.stdout.write('\r[{0}/{1}]'.format(i + 1, N))
        sys.stdout.flush()
    sys.stdout.write('\n')


print('elapsed time [s]: {0}'.format(timeit.timeit(iterate, number=1)))
