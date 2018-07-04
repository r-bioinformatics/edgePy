"""
Stastics methods for edgePy

"""


class BinomialTest(object):
    """
    Creates object to store data and run binomial tests on data and returns the actual p value using binom_test from sci_py
    Original Doc: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom_test.html
    """

    def __init__(self, x, n: int, p: float = .5, alternative: str = "two-sided"):
        """
        :param x: the number of successes, if x has length 2, it is the number of successes and the number of failures.
        :param n: the number of trials, ignored if len(x) is 2
        :param p: hypothesized probability of success. 0 <= p <= 1, set to 0.5 by default - same as scipy
        :param alternative: alternative hypothesis, set to two-sided by default. same as scipy. Options: {‘two-sided’, ‘greater’, ‘less’}
        """
        self.x = x
        self.n = n
        self.p = p
        self.alternative = alternative

    def test(self):
        """
        :return: p value of the test
        """
        pass


class Ftest(object):
    """
    Creates object to store data and run binomial tests on data and returns the actual p value using f from sci_py
    Original Doc: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f.html
    TODO: Do we use the currently displayed version of scipy f test or the one_way f test found here: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
    """

    def __init__(self, x, df1, df2, loc=0, scale=1):
        """
        :param x: positive float/int or array like? quantities
        :param df1: shape parameter
        :param df2: shape parameter
        :param loc: shift parameter, set to the same default as scipy
        :param scale: scale parameter, set to the same default as scipy
        """
        self.x = x
        self.df1 = df1
        self.df2 = df2
        self.loc = loc
        self.scale = scale

    def test(self):
        """

        :return: TODO: figure out which methods we need to run to get the desired output
        """
        pass


class LinearFit(object):
    """
    Creates object to store data and calculate a linear least-squares regression on data, returns slope, intercept, rvalue, pvalue, and stderr value using lin reg from sci_py
    Original Doc: https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.stats.linregress.html
    """

    def __init__(self, x, y):
        """

        :param x: array like, set of measurements if y is None than it is a 2d array with one dimension having len of 2
        :param y: array like, set of measurements
        """
        self.x = x
        self.y = y

    def test(self):  # Wanna call it fit but for consistency calling it test
        """

        :return: slope, intercept, rvalue, pvalue, stderr
        """
        pass


class NegativeBinomial(object):
    """
    Creates object to store data and run negative binomial tests on data and returns the ? using nbinom from sci_py
    Original Doc: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html
    """

    def __init__(self, n: float, p: float, loc=0):
        """

        :param n: number of successes
        :param p: probability of a single success
        :param loc: set to 0 by default
        """
        self.n = n
        self.p = p
        self.loc = loc

    def test(self):
        """

        :return: TODO: figure out which methods we need to run to get the desired output
        """
        pass


class Zscore(object):
    """
    Creates object to store data and run negative binomial tests on data and returns the zscore  using zscore from sci_py
    Original Doc: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html
    """

    def __init__(self, a, axis: int = 0, ddof: int = 0):
        """

        :param a: Array like with sample data
        :param axis: Set to same default as scipy, axis along which to operate
        :param ddof: Degrees of freedom correction in the calculation of the standard deviation, set to same default as scipy
        """
        self.a = a
        self.axis = axis
        self.ddof = ddof

    def test(self):
        """

        :return: z score which is an array like
        """
        pass


class GLM(object):
    """
    docstring for GLM
    Note: A little unsure how to approach the template for this function so I'm leaving it blank
    """

    def __init__(self, arg):
        self.arg = arg

    def test(self):
        pass
