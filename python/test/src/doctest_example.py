from math import factorial
def binom(n: int, k: int) -> int:
    '''Computes the binomial coefficient.
    This shows how many combinations of
    *n* things taken in groups of size *k*.

    :param n: size of the universe
    :param k: size of each subset
    :returns: the number of combinations
    >>> binom(52, 5)
    2598960
    '''

    return factorial(n) // (factorial(k) * factorial(n-k))


__test__ = {
    'GIVEN_binom_WHEN_0_0_THEN_1':
        '''
        >>> binom(0, 0)
        1
        ''',

}

from statistics import median
from collections import Counter

class Summary:

    '''Computes summary statistics.
    >>> s = Summary()
    >>> s.add(8)
    >>> s.add(9)
    >>> s.add(9)
    >>> round(s.mean, 2)
    8.67
    >>> s.median
    9
    '''

    def __init__(self):
        self.counts = Counter()

    def __str__(self):
        return "mean = {:.2f}\nmedian = {:d}".format(
            self.mean, self.median)

    def add(self, value):
        '''Adds a value to be summarized.

        :param value: Adds a new value to the collection.
        '''
        self.counts[value] += 1

    @property
    def mean(self):
        '''Computes the mean of the collection.
        :return: mean value as a float
        '''
        s0 = sum(f for v,f in self.counts.items())
        s1 = sum(v*f for v,f in self.counts.items())
        return s1/s0

    @property
    def median(self):
        return median(self.counts.elements())


if __name__ == "__main__":
    import doctest
    doctest.testmod()



