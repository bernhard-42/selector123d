# %%
from build123d import *
from ocp_vscode import *
from selector123d import *

# %%
ms = Mode.SUBTRACT

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(31)
        with PolarLocations(31, 6) as loc:
            Circle(6)
        right_most_circle: Edge = s.edges().sort_by(Axis.X)[-1]
        c_tan_parm = right_most_circle.find_tangent(55 / 2 + 90)[0]
        c_tan_pnt = right_most_circle.position_at(c_tan_parm)
        c_tan_tan = -right_most_circle.tangent_at(c_tan_parm)
        fillet(s.vertices(), 6)
    extrude(amount=8, both=True)
    with BuildSketch() as s2:
        Rectangle(1, 1)
        with BuildLine() as bl1:
            Line((0, 0), c_tan_pnt)
            r = RadiusArc((100, 0), (0, -100), 100, mode=Mode.PRIVATE)
            l2 = IntersectingLine(start=c_tan_pnt, direction=c_tan_tan, other=r)
            RadiusArc(l2 @ 1, (0, -100), 100)
            mirror(about=Plane.YZ)
        make_face()
        fillet(s2.vertices().group_by(Axis.Y)[0], 15)
        corner_edges: Edge = (
            s2.edges(Select.LAST).filter_by(GeomType.CIRCLE).group_by(SortBy.RADIUS)[0]
        )
        corners = [e.arc_center for e in corner_edges]
    extrude(amount=7 / 2, both=True)
    with Locations(corners[0], (0, -85), corners[1]):
        Cylinder(30 / 2, 32)
        Cylinder(20 / 2, 32, mode=ms)
    with BuildSketch() as s3:
        Circle(40 / 2)
        with PolarLocations(31, 6):
            Circle(6 / 2)
    extrude(amount=100, both=True, mode=ms)

# %%
show(p)


# %%
objects = p.edges()
SelectorTool(objects, (Axis.Z, Axis.X, Axis.Y), "objects")

# %%
# _g0 = objects.group_by(Axis.Z)
# _g1 = _g0[2].group_by(Axis.X)
# _g2 = _g0[10].group_by(Axis.X)
# objs = flatten(
#     [_g0[i] for i in [0, 12]]
#     + [_g1[i] for i in [0, 1, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17]]
#     + [_g2[i] for i in [0, 1, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17]]
# )
_g0 = objects.group_by(Axis.Z)
_g1 = _g0[0].sort_by(Axis.X)
_g2 = _g0[2].group_by(Axis.X)
_g3 = _g2[7].sort_by(Axis.Y)
_g4 = _g0[10].group_by(Axis.X)
_g5 = _g0[12].sort_by(Axis.X)
objs = flatten(
    [_g1[i] for i in [0, 1, 2, 4, 5]]
    + [_g2[i] for i in [0, 1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17]]
    + [_g3[1]]
    + [_g4[i] for i in [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17]]
    + [_g5[i] for i in [0, 1, 2, 4, 5]]
)
show(p, objs)
# %%
p2 = fillet(objs, 1)
show(p2)
# %%
