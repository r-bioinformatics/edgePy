
from edgePy.statistics.ks import kolmogorov_smirnov


def test_ks_poor_match():

    s1 = 1.0
    s2 = 1.0
    m1 = 2.0
    m2 = 6.0
    assert 0.9544997361036414 == kolmogorov_smirnov(m1, s1, m2, s2)


def test_ks_perfect_match():

    s1 = 1.0
    s2 = 1.0
    m1 = 2.0
    m2 = 2.0
    assert 0 == kolmogorov_smirnov(m1, s1, m2, s2)


def test_ks_ok_match():

    s1 = 0.5
    s2 = 4.0
    m1 = 2.0
    m2 = 2.0
    assert 0.35486490556273226 == kolmogorov_smirnov(m1, s1, m2, s2)


def test_ks_lousy_match():

    s1 = 0.5
    s2 = 4.0
    m1 = 6.0
    m2 = 2.0
    assert 0.7366114398572612 == kolmogorov_smirnov(m1, s1, m2, s2)