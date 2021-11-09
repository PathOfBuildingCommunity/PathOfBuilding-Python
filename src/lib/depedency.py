__credits__ = ['svrNinety']

import functools
import inspect

import networkx as nx
import matplotlib.pyplot as plt


class Dependency(nx.DiGraph):
    def __init__(self):
        super().__init__()

    def _add_as_dependency_node(self, dependency_nodes):
        '''
            Adds the actual node to the Graph
        '''
        for dependency_node in dependency_nodes:
            if dependency_node['name'] not in self.nodes():
                self.add_node(dependency_node['name'])

    def _add_as_dependency_relationship_edge(self, func=None, dependency_nodes=None):
        '''
            Adds the actual edge to the Graph
        '''
        if func:
            dependency_nodes = self._get_dependency_node_infos(func)
        for dependency_node in dependency_nodes:
            if (dependency_node['type'] == 'parameter' or
                    dependency_node['type'] == 'called function'):
                self.add_edge(
                    dependency_node['parent'], dependency_node['name'])

    def _get_dependency_node_infos(self, func):
        '''
            Parses all relevant dependencies from function
            and signature
        '''
        dependency_nodes = []

        # called function parameters
        signature = inspect.signature(obj=func)
        for parameter_name in signature.parameters.keys():
            if parameter_name in ['self', 'args', 'kwargs']:
                continue
            else:
                dependency_nodes.append({
                    'name': parameter_name,
                    'type': 'parameter',
                    'parent': func.__name__
                })

        return dependency_nodes

    def parse_node(self, _func=None, *, tracked_as=None):
        def node_decorator(func, *args, **kwargs):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if tracked_as:
                    # inspection of called function
                    dependency_node_info = self._get_dependency_node_infos(
                        func)

                    # taking the caller function
                    wrapper_found = False
                    calling_func = None
                    prev_frame = inspect.currentframe().f_back
                    while not wrapper_found:
                        try:
                            caller_func = inspect.getframeinfo(prev_frame)[2]
                            if not calling_func:
                                calling_func = caller_func

                            # ! HARDCODE !
                            # Checking if this wrapper has been called via recursion
                            if caller_func == 'wrapper':
                                wrapper_found = True
                            else:
                                prev_frame = prev_frame.f_back
                        except Exception as e:
                            break

                    if wrapper_found:
                        dependency_node_info.append({
                            'name': func.__name__,
                            'type': 'called function',
                            'parent': calling_func
                        })

                    self._add_as_dependency_node(dependency_node_info)
                    self._add_as_dependency_relationship_edge(
                        dependency_nodes=dependency_node_info)

                retVal = func(*args, **kwargs)
                return retVal
            return wrapper

        node_decorator(_func)
        return node_decorator

    def clear_depedencies(self):
        self.clear()

    def visualize_dependencies(self):
        options = {
            'node_size': 200,
            'width': 2,
            'with_labels': True,
            'connectionstyle': 'arc3, rad = 0.0002'
        }
        nx.draw(self, **options)
        plt.show()
