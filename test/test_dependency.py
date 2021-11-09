from src.lib.depedency import Dependency
import functools
import math

SHOW_DEPENDENCY_VISUALIZATION = True


class TestDepedency:
    def setup_class(cls):
        # module under test
        cls.dep_set_1 = Dependency()
        # inter-depedency maybe?
        cls.dep_set_2 = Dependency()

    def setup_method(self, method):
        # clear dependencies for each method
        self.dep_set_1.clear_depedencies()
        self.dep_set_2.clear_depedencies()

    def teardown_method(self, method):
        self.dep_set_1.visualize_dependencies() if SHOW_DEPENDENCY_VISUALIZATION else None

    def test_depedency_as_args_singleton_intra_depedency(self):
        # Sample implementation method
        @self.dep_set_1.parse_node
        def base_health(level: int = None, strength: int = None) -> int:
            return 38 + level * 12 + math.floor(strength / 2)

        # Invoke depedency graph decorator via base_health method
        # as arguments to form depedencies
        base_health(1, 20)

        # Inspect dependency graph nodes
        # Validate with expected nodes
        # Their set difference should be a null set
        expected_nodes = set(['base_health', 'level', 'strength'])
        assert(set(self.dep_set_1.nodes()).difference(expected_nodes) == set())

        # Inspect dependency graph edges
        # Validate with expected edges
        # Their set difference should be a null set
        expected_edges = set(
            [('strength', 'base_health'), ('level', 'base_health')])
        assert(set(self.dep_set_1.edges()).difference(expected_edges) == set())

    def test_depedency_as_unpacked_dict_singleton_intra_depedency(self):
        @self.dep_set_1.parse_node
        def base_health(level: int = None, strength: int = None) -> int:
            return 38 + level * 12 + math.floor(strength / 2)

        # Invoke depedency graph decorator via base_health method
        # as unpacked dict to form depedencies
        attrs = {
            'level': 1,
            'strength': 20
        }
        base_health(**attrs)

        # Inspect dependency graph nodes
        # Validate with expected nodes
        # Their set difference should be a null set
        expected_nodes = set(['base_health', 'level', 'strength'])
        assert(set(self.dep_set_1.nodes()).difference(expected_nodes) == set())

        # Inspect dependency graph edges
        # Validate with expected edges
        # Their set difference should be a null set
        expected_edges = set(
            [('level', 'base_health'), ('strength', 'base_health')])
        assert(set(self.dep_set_1.edges()).difference(expected_edges) == set())

    def test_depedency_as_args_multiple_intra_depedency(self):
        @self.dep_set_1.parse_node
        def base_health(level: int = None, strength: int = None) -> int:
            return 38 + level * 12 + math.floor(strength / 2)

        @self.dep_set_1.parse_node
        def max_health(base_health: int = None, inc_life: int = None, more_life: int = None) -> int:
            return int(base_health * (1 + inc_life / 100) * (1 + more_life / 100))

        base_health = base_health(1, 20)
        inc_life = 20
        more_life = 20
        max_health = max_health(base_health, inc_life, more_life)

        expected_nodes = set(
            ['base_health', 'level', 'strength', 'max_health', 'inc_life', 'more_life'])
        assert(set(self.dep_set_1.nodes()).difference(expected_nodes) == set())

        expected_edges = set([('base_health', 'max_health'), ('inc_life', 'max_health'), (
            'level', 'base_health'), ('more_life', 'max_health'), ('strength', 'base_health')])
        assert(set(self.dep_set_1.edges()).difference(expected_edges) == set())

    def test_depedency_as_unpacked_dict_multiple_intra_depedency(self):
        @self.dep_set_1.parse_node
        def base_health(level: int = None, strength: int = None) -> int:
            return 38 + level * 12 + math.floor(strength / 2)

        @self.dep_set_1.parse_node
        def max_health(base_health: int = None, inc_life: int = None, more_life: int = None) -> int:
            return int(base_health * (1 + inc_life / 100) * (1 + more_life / 100))

        attrs = {
            'base_health': base_health(1, 20),
            'inc_life': 20,
            'more_life': 20,
        }
        max_health = max_health(**attrs)

        expected_nodes = set(
            ['base_health', 'level', 'strength', 'max_health', 'inc_life', 'more_life'])
        assert(set(self.dep_set_1.nodes()).difference(expected_nodes) == set())

        expected_edges = set([('base_health', 'max_health'), ('inc_life', 'max_health'), (
            'level', 'base_health'), ('more_life', 'max_health'), ('strength', 'base_health')])
        assert(set(self.dep_set_1.edges()).difference(expected_edges) == set())
