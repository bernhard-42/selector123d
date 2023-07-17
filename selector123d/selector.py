from ocp_tessellate import OCP_Edges, OCP_Faces, OCP_Vertices, OCP_Part, OCP_PartGroup
from ocp_vscode.colors import ColorMap
from build123d import Axis, Edge, Face, Vertex
from ocp_vscode import show, status

__all__ = ["SelectorTool"]

def axis_key(axis):
    return (axis.position.to_tuple(), axis.direction.to_tuple())


axis_lut = {
    axis_key(Axis.X): "Axis.X",
    axis_key(Axis.Y): "Axis.Y",
    axis_key(Axis.Z): "Axis.Z",
}


class SelectorTool:
    def __init__(self, objects, axes=None, label="obj", colormap=None):
        def _selector(parent, objects, cls, axes, label, width, colormap):
            if axes is None:
                axes = (Axis.Z, Axis.X, Axis.Y)

            pg = OCP_PartGroup([], name=label)
            if parent is not None:
                pg.objects.append(
                    OCP_Part([parent.wrapped], name="part", color="#bbbbbb40")
                )

            axis_label = axis_lut.get(axis_key(axes[0]))
            groups = objects.group_by(axes[0])

            color = {"color": next(colormap)}
            width_arg = {} if width is None else {"width": width}

            if all([len(obj) == 1 for obj in groups]):
                sorted_objects = objects.sort_by(axes[0])
                for j, obj in enumerate(sorted_objects):
                    pg.objects.append(
                        cls(
                            [obj.wrapped],
                            name=f"sort_by({axis_label})[{j}]",
                            **width_arg,
                            **color,
                        )
                    )
                return pg

            for j, obj in enumerate(groups):
                if len(obj) == 1:
                    pg.objects.append(
                        cls(
                            [obj[0].wrapped],
                            name=f"group_by({axis_label})[{j}][0]",
                            **width_arg,
                            **color,
                        )
                    )
                else:
                    if len(axes) > 1:
                        pg.objects.append(
                            _selector(
                                None,
                                obj,
                                cls,
                                axes[1:],
                                label=f"group_by({axis_label})[{j}]",
                                width=width,
                                colormap=colormap,
                            ),
                        )
            return pg

        if colormap is None:
            colormap = ColorMap.segmented(10, "mpl:cool")

        width = None

        if isinstance(objects[0], Edge):
            width = 3
            cls = OCP_Edges
        elif isinstance(objects[0], Face):
            cls = OCP_Faces
        elif isinstance(objects[0], Vertex):
            cls = OCP_Vertices

        parent = objects[0].topo_parent

        self.pg = _selector(
            parent, objects, cls, axes, label, width=width, colormap=colormap
        )
        show(self.pg, collapse=Collapse.ROOT, default_edgecolor="#aaaaaa")

    @property
    def selector(self):
        pick = status()["lastPick"]
        states = status()["states"]
        prefix = pick["path"] + "/" + pick["name"]
        states = {k: v for k, v in states.items() if k.startswith(prefix) and v[1] == 0}
        suffixes = [k[len(prefix) :] for k, v in states.items()]

        return pick["path"].replace("/", "") + pick["name"]