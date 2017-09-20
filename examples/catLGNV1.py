from csa import *

# Dow et al. 1985 (Macaque fovea)


@ProjectionOperator
def GvspaceToCx(p):
    w = 7.7 * cmath.log(complex(p[0] + 0.33, p[1]))
    return (w.real, w.imag)


@ProjectionOperator
def GcxToVspace(p):
    c = cmath.exp(complex(p[0], p[1]) / 7.7) - 0.33
    return (c.real, c.imag)

# g1 = grid2d(30)
# g2 = grid2d(30, x0=-7.0, xScale=8.0, yScale=8.0)
# c = disc(0.1) * euclidMetric2d(g1, GcxToVspace * g2)
# gplotsel2d(g2, c, 282)
