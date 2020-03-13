cimport cython
import numpy as np

cimport numpy as np
from libc.math cimport sqrt
from libc.math cimport pow as power
DTYPE = np.float64

ctypedef np.float64_t DTYPE_t


@cython.boundscheck(False)
@cython.wraparound(False)

def distancePointEdge_cy(np.ndarray[DTYPE_t, ndim = 2] points, np.ndarray[DTYPE_t, ndim = 2] edge):

    cdef DTYPE_t edge_x0 = edge[0][0]
    cdef DTYPE_t edge_y0 = edge[1][0]
    cdef DTYPE_t edge_x1 = edge[2][0]
    cdef DTYPE_t edge_y1 = edge[3][0]

    cdef DTYPE_t dx = edge_x1 - edge_x0
    cdef DTYPE_t dy = edge_y1 - edge_y0
    cdef DTYPE_t delta = dx * dx + dy * dy
    cdef int numPoints = points.shape[0]
    cdef np.ndarray[DTYPE_t, ndim = 1] dist = np.zeros(numPoints, dtype=DTYPE)
    cdef DTYPE_t tp
    cdef DTYPE_t p0_x, p0_y
    cdef DTYPE_t points_x, points_y

    for idx in xrange(numPoints):
        points_x = points[idx, 0]
        points_y = points[idx, 1]
        tp = ((points_x - edge_x0) * dx + (points_y - edge_y0) * dy) / delta
        if tp < 0:
            tp = 0
        elif tp > 1:
            tp = 1
        p0_x = edge_x0 + tp * dx
        p0_y = edge_y0 + tp * dy
        dist[idx] = sqrt(power((points_x - p0_x), 2) + power((points_y - p0_y), 2))

    return dist
