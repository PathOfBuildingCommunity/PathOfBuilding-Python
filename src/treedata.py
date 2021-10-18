import itertools
import json
import math
import os
from typing import Optional, Union

import networkx as nx
from pydantic import BaseModel, Field


class MasteryEffectData(BaseModel):
    identifier: int = Field(alias="effect")
    stats: list[str]  # ToDo @svrNinety: update once a separate stat class exists


class NodeData(BaseModel):
    identifier: int = Field(alias="skill")
    name: Union[str, int]
    x_position: float = Field(default=-1.0)
    y_position: float = Field(default=-1.0)
    icon: str
    is_keystone: bool = Field(default=False, alias="isKeystone")
    is_notable: bool = Field(default=False, alias="isNotable")
    is_mastery: bool = Field(default=False, alias="isMastery")
    is_proxy: bool = Field(default=False, alias="isProxy")
    mastery_effects: list[MasteryEffectData] = Field(default=[], alias="masteryEffects")
    stats: list[str]  # ToDo @svrNinety: update once a separate stat class exists
    group_identifier: Optional[int] = Field(default=None, alias="group")
    orbit: int = 0
    orbit_index: int = Field(default=0, alias="orbitIndex")
    predecessors: list[int] = Field(default=[], alias="in")
    successors: list[int] = Field(default=[], alias="out")

    @property
    def position(self) -> tuple[float, float]:
        return self.x_position, self.y_position


class GroupData(BaseModel):
    identifier: int
    x_position: float = Field(alias="x")
    y_position: float = Field(alias="y")
    orbits: list[int]
    node_identifiers: list[int] = Field(alias="nodes")


class TreeData:
    """Parses and validates data.json from https://github.com/grindinggear/skilltree-export

    Data validation is handled by pydantic's BaseModel (see MasteryEffectData, NodeData, GroupData). A rudimentary tree
    consistency validation (such as enforcing a bidirectional graph structure, consistent group-node affiliation, etc.)
    is performed. Generally speaking we trust GGG to not feed us a nonsensical nor broken tree structure, hence we only
    perform surface level validations.

    If something does go wrong, there is a high likelihood of an AssertionError to be raised due to extensive assertion
    checking during the parsing process. Incorrect tree data should at all times indicate that we've reached an
    irrecoverable state and we must exit.

    This class is meant to hold static data of the tree. Consumers are free to introspect nodes, groups and the
    resulting graph but must not mutate members. The NetworkX graph contains all necessary information to create an
    interactive skill tree (node data, node position, edges, etc.). Consumers must retrieve a deepcopy of graph before
    mutating the graph structure (e.g. jewels).

    ToDo @svrNinety: add logger output for debug/info tracing once its clear what logging framework this project uses
    """

    def __init__(self, file_path: Union[str, bytes, os.PathLike]):
        self.nodes: dict[int, NodeData] = dict()
        self.groups: dict[int, GroupData] = dict()
        self.graph: nx.Graph = nx.Graph()

        self._file_path: Union[str, bytes, os.PathLike] = file_path
        self._x_position_offset: float = 0.0
        self._y_position_offset: float = 0.0
        self._orbit_radii: list[int] = list()
        self._orbit_num_skills: list[int] = list()
        self._orbit_angles: dict[int, list[float]] = dict()

        # load json data and parse config & constants
        self._load_data()
        self._parse_orbits()
        self._parse_offsets()
        self._compute_orbit_angles()

        # parse tree data
        self._parse_nodes()
        self._parse_groups()
        # ToDo: parse assets
        # ToDo: parse skill sprites

        # validate data against parsed containers
        self._validate()

        # do heavy lifting
        self._compute_node_positions()
        self._build_graph()

    def _load_data(self) -> None:
        with open(self._file_path, "r") as f:
            self._data = json.load(f)

    def _parse_orbits(self) -> None:
        """parse 'orbitRadii' and 'skillsPerOrbit' from data, which are required to determine node positions"""
        assert "constants" in self._data.keys(), "Tree Data JSON must contain 'constants' key"
        _constants = self._data["constants"]

        assert "orbitRadii" in _constants, "Tree Data JSON must contain 'orbitRadii' key"
        _orbit_radii = _constants["orbitRadii"]
        assert isinstance(_orbit_radii, list) and all(
            isinstance(x, int) for x in _orbit_radii
        ), "Failed validation for 'orbitRadii' in Tree Data JSON to be list of integers"
        self._orbit_radii.extend(_orbit_radii)

        assert "skillsPerOrbit" in _constants, "Tree Data JSON must contain 'orbitRadii'"
        _skills_per_orbit = _constants["skillsPerOrbit"]
        assert isinstance(_skills_per_orbit, list) and all(
            isinstance(x, int) for x in _skills_per_orbit
        ), "Failed validation for 'skillsPerOrbit' in Tree Data JSON to be list of integers"
        self._orbit_num_skills.extend(_skills_per_orbit)

    def _compute_orbit_angles(self) -> None:
        """compute the orbital rad_angle of each index on each orbit; orbit 4 is the only orbit where the distance between two neighbours is not equidistant"""
        for orbit_index, num_skills in enumerate(self._orbit_num_skills):
            self._orbit_angles[orbit_index] = [math.radians(360 / num_skills * x) for x in range(num_skills)]

        # orbit 4 is an exception, since its neighbours are not equidistant: all multiples of 10° and 45° up to 359°
        self._orbit_angles[4] = [math.radians(x) for x in range(0, 360, 5) if x % 45 == 0 or x % 10 == 0]
        # assert that the 'hardcoded' orbit 4 structure still fits parsed num_skills in orbit
        assert (
            len(self._orbit_angles[4]) == self._orbit_num_skills[4]
        ), f"num_skills in orbit 4 mismatch: '{self._orbit_num_skills[4]}' expected but found '{len(self._orbit_angles[4])}' instead"

    def _compute_node_positions(self) -> None:
        """compute positions on the tree; must be invoked after _nodes and _groups have been validated"""
        for node in self.nodes.values():
            if node.group_identifier is not None:
                # grab angle and distance from precomputed orbital values; see '_compute_orbit_angles'
                _angle = self._orbit_angles[node.orbit][node.orbit_index]
                _dist = self._orbit_radii[node.orbit]
                # calculate the position of each node by its group
                parent_group = self.groups[node.group_identifier]
                node.x_position = parent_group.x_position + self._x_position_offset + math.sin(_angle) * _dist
                node.y_position = parent_group.y_position + self._y_position_offset - math.cos(_angle) * _dist
            else:
                # these are all nodes that are by default not connected to the graph (e.g. cluster nodes)
                # their position has to be determined at runtime and can not be statically precomputed
                pass

    def _build_graph(self) -> None:
        """iterate all parsed nodes to populate the nx.Graph"""
        # add all nodes first
        for node_identifier, node in self.nodes.items():
            if node.group_identifier is not None:
                # noinspection PyTypeChecker
                self.graph.add_node(node_identifier, **node.dict())

        # add all edges
        for node_identifier, node in self.nodes.items():
            for neighbour_identifier in itertools.chain(node.successors, node.predecessors):
                assert node_identifier != neighbour_identifier  # nobody is allowed to be a neighbour to himself
                self.graph.add_edge(node_identifier, neighbour_identifier)

    def _parse_nodes(self) -> None:
        assert "nodes" in self._data.keys(), "Tree Data JSON must contain 'nodes' key"
        for node_identifier, node_data in self._data["nodes"].items():
            # ignore the root node
            if node_identifier == "root":
                continue
            node = NodeData(**node_data)
            self._add_node(node)

    def _parse_groups(self) -> None:
        assert "groups" in self._data.keys(), "Tree Data JSON must contain 'groups' key"
        for group_identifier, group_data in self._data["groups"].items():
            group_data["identifier"] = group_identifier
            group = GroupData(**group_data)
            self._add_group(group)

    def _parse_offsets(self) -> None:
        assert "min_x" in self._data.keys(), "Tree Data JSON must contain 'min_x' key"
        assert "min_y" in self._data.keys(), "Tree Data JSON must contain 'min_y' key"
        x_min = self._data.get("min_x")
        y_min = self._data.get("min_y")
        self._x_position_offset = -x_min + self._orbit_radii[-1]
        self._y_position_offset = -y_min + self._orbit_radii[-1]

    def _validate(self) -> None:
        assert (
            len(self.nodes) == len(self._data["nodes"]) - 1
        ), f"expected number of parsed nodes '{len(self._data['nodes']) - 1}' does not equal number of parsed nodes '{len(self.nodes)}'"
        assert len(self.groups) == len(
            self._data["groups"]
        ), f"expected number of parsed groups '{len(self._data['groups'])}' does not equal number of parsed groups '{len(self.groups)}'"

        # assert that each node is part of its group (if group has been set)
        for node in self.nodes.values():
            if node.group_identifier is None:
                continue
            assert (
                node.group_identifier in self.groups
            ), f"{node!r} must be part of its group, but group with {node.group_identifier=} does not exist"
            assert (
                node.identifier in self.groups[node.group_identifier].node_identifiers
            ), f"{node!r} is missing in its {self.groups[node.group_identifier]!r}"

        # assert that each group contains nodes that have the group.identifier set to group
        for group in self.groups.values():
            for node_identifier in group.node_identifiers:
                assert node_identifier in self.nodes, f""
                assert self.nodes[node_identifier].group_identifier == group.identifier

    def _add_node(self, node: NodeData) -> None:
        assert node.identifier not in self.nodes, f"{node!r} already exists; duplicates are must not occur"
        self.nodes[node.identifier] = node

    def _add_group(self, group: GroupData) -> None:
        assert group.identifier not in self.groups, f"{group!r} already exists; duplicates are must not occur"
        self.groups[group.identifier] = group

    def interactive_plot(self):
        """temp interactive inspector as long as there is no UI

        @ToDo svrNinety: remove function and plotly dependency once project has capable UI components
        """
        import plotly.graph_objects as pgo

        # parse edges for scatter-line plot
        edges_x, edges_y = list(), list()
        for edge in self.graph.edges():
            source_node_id, target_node_id = edge[0], edge[1]

            source_node_x, source_node_y = self.nodes[source_node_id].position
            target_node_x, target_node_y = self.nodes[target_node_id].position
            edges_x.append(source_node_x)
            edges_x.append(target_node_x)
            edges_x.append(None)
            edges_y.append(source_node_y)
            edges_y.append(target_node_y)
            edges_y.append(None)

        # parse nodes for scatter-marker plot
        nodes_x, nodes_y, nodes_text = list(), list(), list()
        for node_identifier in self.graph.nodes():
            node_x, node_y = self.nodes[node_identifier].position
            nodes_x.append(node_x)
            nodes_y.append(node_y)
            _text = (
                json.dumps(self.nodes[node_identifier].dict(), sort_keys=True, indent=4).__str__().replace("\n", "<br>")
            )
            nodes_text.append(_text)

        # plot for edges between vertices
        edge_trace = pgo.Scatter(
            x=edges_x,
            y=edges_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        # plot for vertices
        node_trace = pgo.Scatter(
            x=nodes_x,
            y=nodes_y,
            text=nodes_text,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                color="#ADD8E6",
                size=10,
                line_width=2,
            ),
        )

        # final figure
        fig = pgo.Figure(
            data=[edge_trace, node_trace],
            layout=pgo.Layout(
                title=f"Path of Exile Tree Data Inspector [{self._file_path}]",
                showlegend=False,
                hovermode="closest",
                hoverlabel=dict(font_size=10, font_family="Ubuntu"),
                margin=dict(b=5, l=5, r=5, t=5),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    autorange="reversed",
                ),
            ),
        )
        fig.show()


def main():
    parent_dir = os.path.dirname(__file__)
    tree_316_json = os.path.join(parent_dir, "data", "tree", "3_16", "data.json")
    t = TreeData(file_path=tree_316_json)
    t.interactive_plot()


if __name__ == "__main__":
    main()
