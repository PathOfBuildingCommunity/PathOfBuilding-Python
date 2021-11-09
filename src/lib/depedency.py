__credits__ = ['svrNinety']

import functools
import inspect

import networkx as nx
import matplotlib.pyplot as plt


class Dependency(nx.DiGraph):
    def __init__(self):
        super().__init__()

    def parse_node(self, _func=None, *, name=None, dependencies=None):
        # wrap the execution context of function for caching, lazy evaluation, etc.

        def node_decorator(func):
            @functools.wraps(func)
            def wrapper_decorator(*args, **kwargs):
                value = func(*args, **kwargs)
                # print(f"{func.__name__=} executed {value=}")
                return value
            return wrapper_decorator

        _decorator = node_decorator if _func is None else node_decorator(_func)
        _signature = inspect.signature(obj=_decorator)

        # add function as executable node, or edit pre-existing value node to executable node
        if _decorator.__name__ in self.nodes:
            # the node pre-existed as an executable function -> naming conflict
            assert self.nodes[_decorator.__name__] is None
            self.nodes[_decorator.__name__]["__func__"] = _decorator
        else:
            self.add_node(
                _decorator.__name__,
                __func__=_decorator,
                __parameters__=_signature.parameters,
                __rtype__=_signature.return_annotation,
            )

        def add_node_and_edge(identifier):
            if identifier not in self.nodes:
                self.add_node(identifier, __func__=None,
                              __rtype__=parameter.annotation)
            self.add_edge(identifier, _decorator.__name__)

        # add each parameter in signature as entry placeholder node
        for identifier, parameter in _signature.parameters.items():
            if identifier in ['self']:
                continue
            elif identifier == 'kwargs':
                # TODO
                # need to unpack kwargs and add as depedency if we
                # plan to allow kwargs pointers
                # else this can be removed
                continue
            else:
                add_node_and_edge(identifier)

        return _decorator

    def clear_depedencies(self):
        self.clear()

    def visualize_dependencies(self):
        options = {
            'node_size': 300,
            'width': 2,
            'with_labels': True,
            'connectionstyle': 'arc3, rad = 0.1'
        }
        nx.draw(self, **options)
        plt.show()
