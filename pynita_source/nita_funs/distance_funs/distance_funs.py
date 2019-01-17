import numpy as np
from .distance_funs_cython import distancePointEdge_cy

def distancePointEdge_py(points, edge):
    # Python implementation of MATLAB function distancePointEdge created by David Legland

    # edge shoud be in the format of [x0, y0, x1, y1]
    # pts should be in the format of [[x1, y1],
    #                                 [x2, y2],
    #                                   ...
    #                                 [xn,yn]]

    edge = np.array(edge).reshape((4,1))
    points = np.array(points)

    if edge.shape != (4,1):
        raise ValueError('in-valid edge shape!')

    if points.shape[1] != 2:
        raise ValueError('in-valid points shape!')

    # direction vector of each edge
    dx = edge[2] - edge[0]
    dy = edge[3] - edge[1]

    # compute position of points projected on the supporting line
    # (Size of tp is the max number of edges or points)
    delta = dx * dx + dy * dy
    tp = ((points[:, 0] - edge[0]) * dx + (points[:, 1] - edge[1]) *dy) / delta


    # change position to ensure projected point is located on the edge
    tp[tp < 0] = 0;
    tp[tp > 1] = 1;

    # coordinates of projected point
    p0 = np.column_stack((edge[0] + tp * dx, edge[1] + tp * dy))

    # compute distance between point and its projection on the edge
    dist = np.sqrt((points[:,0] - p0[:,0]) ** 2 + (points[:,1] - p0[:,1]) ** 2);

    return dist

def distancePointEdge_wrapper(points, edge):

    edge = np.array(edge).reshape((4,1))
    points = np.array(points)

    if edge.shape != (4,1):
        raise ValueError('in-valid edge shape!')

    if points.shape[1] != 2:
        raise ValueError('in-valid points shape!')

    return distancePointEdge_cy(points, edge)