from src.lib.depedency import Dependency
import functools
import math

SHOW_DEPENDENCY_VISUALIZATION = True


class TestDependency:
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

    def test_depedency_as_unpacked_dict_multiple_layers_intra_depedency(self):
        class thisEntityClass(Dependency):
            def __init__(self, *args, **kwargs):
                for attr,val in kwargs.items():
                    setattr(self, attr, val)
                super().__init__()

            @property
            @self.dep_set_1.parse_node(tracked_as='mode')
            def Class(self):
                return self._Class
                
            @Class.setter
            def Class(self, value):
                self._Class = value

            @property
            @self.dep_set_1.parse_node(tracked_as='mode')
            def base_strength(self):
                base_str = {
                    'Duelist': 23,
                    'Marauder': 32,
                    'Ranger': 14,
                    'Scion': 20,
                    'Shadow': 14,
                    'Templar': 23,
                    'Witch': 14
                }
                return base_str[self.Class]

            @property
            @self.dep_set_1.parse_node(tracked_as='mod')
            def base_health(self) -> int:
                _base_strength = self.base_strength
                return 38 + self.level * 12 + math.floor(_base_strength / 2)  

            @property
            @self.dep_set_1.parse_node(tracked_as='mod')
            def inc_life(self):
                try:
                    return self._inc_life
                except:
                    return 0

            @inc_life.setter
            def inc_life(self, value):
                self._inc_life = value

            @property
            @self.dep_set_1.parse_node(tracked_as='mod')
            def more_life(self):
                try:
                    return self._more_life
                except:
                    return 0

            @more_life.setter
            def more_life(self, value):
                self._more_life = value

            @property
            @self.dep_set_1.parse_node(tracked_as='mod')
            def max_health(self) -> int:
                try:
                    return self._max_health
                except:
                    self._max_health = self.max_health_no_params_version()
                    return self._max_health

            @self.dep_set_1.parse_node(tracked_as='mod')
            def max_health_no_params_version(self) -> int:
                _inc_life = self.inc_life
                _more_life = self.more_life
                _base_health = self.base_health
                return int(_base_health * (1 + _inc_life / 100) * (1 + _more_life / 100))
          
            @self.dep_set_1.parse_node(tracked_as='mod')
            def max_health_with_params_version(self, inc_life, more_life, base_health) -> int:
                self._max_health = int(base_health * (1 + inc_life / 100) * (1 + more_life / 100))


        entityObj = thisEntityClass(level = 1, Class = 'Witch')
        # entityObj.max_health_with_params_version(10,10,57)
        # print(f'MAX HEALTH WITH PARAMS VERSION: {entityObj.max_health_with_params_version}')
        entityObj.more_life = 10
        entityObj.inc_life = 20
        print(f'MAX HEALTH USING PROPERTY SETTERS: {entityObj.max_health}')
        entityObj.max_health_with_params_version(100,200,entityObj.base_health)
        print(f'MAX HEALTH USING METHOD WITH PARAMS: {entityObj.max_health}')
        
        expected_nodes = set(
            ['base_health', 'level', 'strength', 'max_health', 'inc_life', 
            'more_life', 'Class', 'base_strength', 'max_health_no_params_version', 
            'max_health_with_params_version'])
        assert(set(self.dep_set_1.nodes()).difference(expected_nodes) == set())

        expected_edges = set([
            ('base_health', 'max_health'), 
            ('inc_life', 'max_health'), 
            ('level', 'base_health'), 
            ('more_life', 'max_health'), 
            ('strength', 'base_health'),
            ('max_health', 'base_health'),
            ('max_health', 'more_life'),
            ('max_health', 'inc_life'),
            ('base_strength', 'Class'),
            ('base_health', 'base_strength'),
            ('max_health_no_params_version', 'base_health'),
            ('max_health_no_params_version', 'more_life'),
            ('max_health_with_params_version', 'more_life'),
            ('max_health_with_params_version', 'inc_life'),
            ('max_health', 'max_health_no_params_version'),
            ('max_health_with_params_version', 'base_health'),
            ('max_health_no_params_version', 'inc_life')
        ])
        assert(set(self.dep_set_1.edges()).difference(expected_edges) == set())