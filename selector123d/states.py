# %%
from ocp_vscode import show, status

__all__ = ["States"]


# %%
class States:
    def __init__(self, states=None):
        if states is None:
            states = status()["states"]
        self.root = self.get_roots(states)[0]  # only one exists
        self.states = {
            k.lstrip("/" + self.root): v[1] == 1
            for k, v in states.items()
            if not k.endswith("/part")
        }

    @staticmethod
    def get_roots(d):
        roots = set()
        for k in d.keys():
            roots.add(k.lstrip("/").partition("/")[0])
        return tuple(sorted(roots))

    @staticmethod
    def make_hierarchy(d):
        hierarchy = {}
        for path, state in d.items():
            path = path.split("/")
            d = hierarchy
            for p in path[:-1]:
                d = d.setdefault(p, {})
            d[path[-1]] = state
        return hierarchy

    def filtered(self, d=None):
        if d is None:
            d = self.states
        parents = set()

        for k, v in d.items():
            if v:
                k = k.replace("][", "]/[")
                parents.add(k.partition("/")[0])
        return {
            k: v
            for k, v in d.items()
            if any(k.startswith(parent) for parent in parents)
        }

    def optimize(self, d=None):
        if d is None:
            d = self.make_hierarchy(self.filtered(self.states))

        if isinstance(d, bool):
            return [d]
        elif all([isinstance(v, bool) for v in d.values()]):
            return d.values()
        else:
            result = {}
            for k, v in d.items():
                ret = self.optimize(v)
                if isinstance(ret, dict):
                    if all([isinstance(v, bool) for v in ret.values()]) and all(
                        ret.values()
                    ):
                        result[k] = True
                    else:
                        result[k] = ret
                elif all(ret):
                    result[k] = True
                elif any(ret):
                    result[k] = v
                else:
                    result[k] = False

            return result

    def variables(self):
        indexes = {}
        ind = 0

        def _variables(o, prefix):
            nonlocal ind, indexes
            mapping = {}
            result = []

            for key in list(set([k.split("[")[0] for k in o.keys()])):
                line = f"_g{ind} = {prefix}.{key}"
                result.append(line)
                mapping[key] = f"_g{ind}"

            for k, v in o.items():
                parts = k.split("[")
                index = int(parts[1].rstrip("]"))
                p = mapping[parts[0]]
                if isinstance(v, dict):
                    ind += 1
                    result += _variables(v, f"{p}[{index}]")
                elif v:
                    indexes.setdefault(p, []).append(index)

            return result

        return _variables(self.optimize(), self.root), indexes

    def code(self, var="objs"):
        if not any(self.states.values()):
            return ""

        code, indexes = self.variables()
        result = "\n".join(code)
        if len(indexes) > 1:
            result += f"\n{var} = flatten(\n"
            indent = "    "
        else:
            result += f"\n{var} = "
            indent = ""
        sep = ""
        for k, v in indexes.items():
            if len(v) == 1:
                result += f"{indent}{sep}[{k}{v}]\n"
            else:
                result += f"{indent}{sep}[{k}[i] for i in {v}]\n"
            sep = "+ "
        if len(indexes) > 1:
            result += ")\n"
        return result


# %%
