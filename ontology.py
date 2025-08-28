import enum
from morphology import *
from util import *
from random import randint
from fol import *
from numpy.random import choice
from collections import defaultdict as dd
import os


class Difficulty(enum.Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, missing_prob):
        self.missing_prob = missing_prob

    SINGLE = 0
    EASY = 0.1
    MEDIUM = 0.2
    HARD = 0.3


class OntologyNode(object):
    INDENT = 4

    def __init__(self, name, properties=[], members=[]):
        self.name = name
        self._members = {}
        for member in members:
            self.add_member(member)
        self._properties = {}
        for prop in properties:
            self.add_property(prop)
        self._parents = {}
        self._children = {}
        self.associated_members_for_recover_ontolog = []
        self.associated_members_for_recover_properties = dd(list)
        self.associated_properties_for_recover_memberships = []

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    # I: member related methods

    def add_member(self, member):
        assert member not in self._members
        self._members[member] = True

    def set_member_invisble(self, member):
        assert member in self._members and self._members[member]
        self._members[member] = False

    def members(self, visible=True):
        if visible is None:
            return list(self._members.keys())
        return [member for member, _visible in self._members.items() if visible == _visible]

    def num_members(self, visible=True):
        return len(self.members(visible))

    # II: property related method

    def add_property(self, prop):
        assert prop not in self._properties
        assert prop.family not in self.prohibited_property_familes
        self._properties[prop] = True

    def set_property_invisible(self, prop):
        assert prop in self._properties and self._properties[prop]
        self._properties[prop] = False

    def properties(self, visible=True):
        if visible is None:
            return list(self._properties.keys())
        return [prop for prop, _visible in self._properties.items() if visible == _visible]

    def num_properties(self, visible=True):
        return len(self.properties(visible))

    @property
    def property_familes(self):
        return [prop.family for prop in self.properties(None)]

    @property
    def prohibited_property_familes(self):
        prohibited_property_familes = list(self.property_familes)
        parents = self.parents(None)
        visited = set()
        while parents:
            parent = parents.pop(0)
            prohibited_property_familes.extend(parent.property_familes)
            visited.add(parent)
            for _parent in parent.parents(None):
                if _parent not in visited:
                    parents.append(_parent)
        children = self.children(None)
        visited = set()
        while children:
            child = children.pop(0)
            prohibited_property_familes.extend(child.property_familes)
            visited.add(child)
            for _child in child.children(None):
                if _child not in visited:
                    children.append(_child)
        return prohibited_property_familes

    # III: parent related method

    def add_parent(self, parent):
        assert parent not in self._parents
        self._parents[parent] = True

    def set_parent_invisible(self, parent):
        assert parent in self._parents and self._parents[parent]
        self._parents[parent] = False

    def parents(self, visible=True):
        if visible is None:
            return list(self._parents.keys())
        return [parent for parent, _visible in self._parents.items() if visible == _visible]

    def num_parents(self, visible=True):
        return len(self.parents(visible=visible))

    # IV: children related methods
    def add_child(self, child):
        assert child not in self._children
        self._children[child] = True

    def set_child_invisible(self, child):
        assert child in self._children and self._children[child]
        self._children[child] = False

    def children(self, visible=True):
        if visible is None:
            return list(self._children.keys())
        return [child for child, _visible in self._children.items() if visible == _visible]

    def num_children(self, visible=True):
        return len(self.children(visible=visible))

    # V: other methods
    @property
    def text(self):
        return f"""{self.name};{f""" prop:\
{', '.join([str(prop) for prop in self.properties(True)]
           + [f"({str(prop)})" for prop in self.properties(False)]) + ';'}"""
            if self.num_properties(None) else ''}{f""" members:\
{', '.join([member for member in self.members(True)]
                + [f"({member})" for member in self.members(False)])};"""
            if self.num_members(None) else ''}"""

    def print_ontology(self, indent=0, sep='='):
        print(sep * indent + self.text)
        for child in self.children(True):
            child.print_ontology(indent + OntologyNode.INDENT)
        for child in self.children(False):
            child.print_ontology(indent + OntologyNode.INDENT, sep='-')

    def ontology_str(self, indent=0, sep='='):
        ret = sep * indent + self.text + os.linesep
        for child in self.children(True):
            ret = ret + child.ontology_str(indent + OntologyNode.INDENT)
        for child in self.children(False):
            ret = ret + \
                child.ontology_str(indent + OntologyNode.INDENT, sep='-')
        return ret


class OntologyConfig(object):
    def __init__(self, hops, recover_membership=False, recover_ontology=False,
                 recover_property=False, difficulty=Difficulty.SINGLE, mix_hops=False):
        self.hops = hops
        self.recover_membership = recover_membership
        self.recover_ontology = recover_ontology
        self.recover_property = recover_property
        self.difficulty = difficulty
        self.mix_hops = mix_hops

    @property
    def easiest_recover_membership(self):
        return OntologyConfig(self.hops, recover_membership=True)

    @property
    def easiest_recover_ontology(self):
        return OntologyConfig(self.hops, recover_ontology=True)

    @property
    def easiest_recover_property(self):
        return OntologyConfig(self.hops, recover_property=True)

    def add_hop(self, delta_hop):
        return OntologyConfig(self.hops + delta_hop, self.recover_membership,
                              self.recover_ontology, self.recover_property, self.difficulty, self.mix_hops)

    def __str__(self):
        return f"{self.hops} hops;{"membership;" if self.recover_membership else ''}{"ontology;" if self.recover_ontology else ''}{"property;" if self.recover_property else ''}{self.difficulty.name.lower() + ";"}{"mix;" if self.mix_hops else ''}"


class Ontology(object):
    MIN_DISCRIMINANT = 2
    MAX_CHILD_COUNT = MIN_DISCRIMINANT + 1
    MIN_CHILD_COUNT = 1
    MAX_PROP_RECOVER_MEMBERSHIP = MIN_DISCRIMINANT + 1
    MAX_MEMBEER_COUNT = MIN_DISCRIMINANT + 1

    def __init__(self, config: OntologyConfig):
        self.config = config
        self.morphology = Morphology()
        self.nodes = [[OntologyNode(self.morphology.next_concept)]]
        self.pseudo_root = None
        self.root = self.nodes[0][0]

        self._build_ontology()
        self._take_missing_ontology()
        self._take_missing_property()
        self._allocate_members()
        self._take_missing_members()
        self._allocate_properties()

    def next_property(self, node):
        return self.morphology.next_property(node.prohibited_property_familes)

    def print_ontology(self):
        if self.pseudo_root:
            self.pseudo_root.print_ontology()
            return
        self.root.print_ontology()

    def ontology_str(self):
        if self.pseudo_root:
            return self.pseudo_root.ontology_str()
        return self.root.ontology_str()

    def _build_ontology(self):
        # first step: add the pesudo root node if needed to recover the ontology
        if self.config.recover_ontology:
            self.pseudo_root = OntologyNode(self.morphology.next_concept)
            self.root.add_parent(self.pseudo_root)
            self.pseudo_root.add_child(self.root)
        for layer in range(self.config.hops - 1):
            previous_nodes = self.nodes[-1]
            self.nodes.append([])
            for parent_node in previous_nodes:
                num_children = Ontology.MIN_CHILD_COUNT
                if not layer or BiasedCoin.flip(1 - (1 - self.config.difficulty.missing_prob) ** 5):
                    num_children = Ontology.MAX_CHILD_COUNT
                for _ in range(num_children):
                    child_node = OntologyNode(self.morphology.next_concept)
                    child_node.add_parent(parent_node)
                    parent_node.add_child(child_node)
                    self.nodes[-1].append(child_node)

    def _take_missing_ontology(self):
        if not self.config.recover_ontology:
            return
        if self.config.mix_hops:
            for level_nodes in self.nodes:
                for node in level_nodes:
                    if node.num_children() > Ontology.MIN_DISCRIMINANT and BiasedCoin.flip(self.config.difficulty.missing_prob):
                        child = choice(node.children())
                        node.set_child_invisible(child)
                        child.set_parent_invisible(node)
        self.pseudo_root.set_child_invisible(self.root)
        self.root.set_parent_invisible(self.pseudo_root)

    def _take_missing_property(self):
        if not self.config.recover_property:
            return
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node == self.root or self.config.mix_hops and BiasedCoin.flip(self.config.difficulty.missing_prob):
                    prop = self.next_property(node)
                    node.add_property(prop)
                    node.set_property_invisible(prop)

    def _allocate_members(self):
        from functools import reduce
        for level_nodes in self.nodes:
            for node in level_nodes:
                # for missing ontology
                assert node.num_parents(False) <= 1
                if node.num_parents(False):
                    # first allocate a member for the node
                    member = self.morphology.next_entity
                    node.add_member(member)
                    node.associated_members_for_recover_ontolog.append(
                        (node, member))
                    # then traverse along the path to find the node candidates
                    candidate_nodes = [[node]]
                    while True:
                        next_candidate_nodes = []
                        for candidate_node in candidate_nodes[-1]:
                            for child_node in candidate_node.children():
                                next_candidate_nodes.append(child_node)
                        if not next_candidate_nodes:
                            break
                        candidate_nodes.append(next_candidate_nodes)
                    for _ in range(Ontology.MIN_DISCRIMINANT):
                        if not self.config.mix_hops:
                            choosen_node = choice(candidate_nodes[-1])
                        else:
                            choosen_node = choice(
                                reduce(lambda x, y: x + y, candidate_nodes, []))
                        member = self.morphology.next_entity
                        choosen_node.add_member(member)
                        node.associated_members_for_recover_ontolog.append(
                            (choosen_node, member))

                # for missing property
                assert node.num_properties(False) <= 1
                if node.num_properties(False):
                    prop = node.properties(False)[0]
                    # first allocate a member for the node
                    member = self.morphology.next_entity
                    node.add_member(member)
                    node.associated_members_for_recover_properties[prop].append(
                        (node, member))
                    # then traverse along the path to find the node candidates
                    candidate_nodes = [[node]]
                    while True:
                        next_candidate_nodes = []
                        for candidate_node in candidate_nodes[-1]:
                            for child_node in candidate_node.children():
                                next_candidate_nodes.append(child_node)
                        if not next_candidate_nodes:
                            break
                        candidate_nodes.append(next_candidate_nodes)
                    for _ in range(Ontology.MIN_DISCRIMINANT):
                        if not self.config.mix_hops:
                            choosen_node = choice(candidate_nodes[-1])
                        else:
                            choosen_node = choice(
                                reduce(lambda x, y: x + y, candidate_nodes, []))
                        member = self.morphology.next_entity
                        choosen_node.add_member(member)
                        node.associated_members_for_recover_properties[prop].append(
                            (choosen_node, member))

    def _take_missing_members(self):
        if not self.config.recover_membership:
            return
        for level_nodes in self.nodes:
            for node in level_nodes:
                if not node.num_members():
                    node.add_member(self.morphology.next_entity)
        _current_nodes = [self.root]
        leaf_nodes = list(_current_nodes)
        for layer in range(self.config.hops - 1):
            leaf_nodes = []
            for _node in _current_nodes:
                for _child_node in _node.children():
                    leaf_nodes.append(_child_node)
            _current_nodes = list(leaf_nodes)
        if self.config.difficulty == Difficulty.SINGLE:
            choosen_node = choice(leaf_nodes)
            hidden_member = choice(choosen_node.members())
            choosen_node.set_member_invisble(hidden_member)
            return
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node in leaf_nodes or self.config.mix_hops:
                    if BiasedCoin.flip(self.config.difficulty.missing_prob):
                        hidden_member = choice(node.members())
                        node.set_member_invisble(hidden_member)
        for node in leaf_nodes:
            if node.num_members(False):
                return
        choosen_node = choice(leaf_nodes)
        hidden_member = choice(choosen_node.members())
        choosen_node.set_member_invisble(hidden_member)

    def _allocate_properties(self):
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.num_members(False):
                    # first allocate a property for itself
                    prop = self.next_property(node)
                    node.add_property(prop)
                    node.associated_properties_for_recover_memberships.append(
                        (node, prop))
                    candidate_nodes = [node]
                    _node = node
                    while True:
                        if not _node.parents():
                            break
                        _node = _node.parents()[0]
                        candidate_nodes.append(_node)
                    for _ in range(Ontology.MIN_DISCRIMINANT):
                        if not self.config.mix_hops:
                            choosen_node = candidate_nodes[-1]
                        else:
                            choosen_node = choice(candidate_nodes)
                        success = False
                        for prop in choosen_node.properties():
                            if prop not in map(lambda x: x[1], node.associated_properties_for_recover_memberships):
                                if len(node.associated_properties_for_recover_memberships) < Ontology.MIN_DISCRIMINANT + 1:
                                    node.associated_properties_for_recover_memberships.append(
                                        (choosen_node, prop))
                                    success = True
                                    break
                        if not success:
                            if len(node.associated_properties_for_recover_memberships) < Ontology.MIN_DISCRIMINANT + 1:
                                prop = self.next_property(choosen_node)
                                choosen_node.add_property(prop)
                                node.associated_properties_for_recover_memberships.append(
                                    (choosen_node, prop))
        # self.print_ontology()

    def __str__(self):
        return ""

    @property
    def observations(self):
        observations = []
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.parents(False):
                    for (choosen_node, member) in node.associated_members_for_recover_ontolog:
                        observations.append(FOL(FOL_Entity(member), FOL_Concept(
                            node.parents(False)[0].name)))
                for prop in node.properties(False):
                    for (choosen_node, member) in node.associated_members_for_recover_properties[prop]:
                        observations.append(
                            FOL(FOL_Entity(member), FOL_Property(prop)))
                for member in node.members(False):
                    for (choosen_node, prop) in node.associated_properties_for_recover_memberships:
                        observations.append(
                            FOL(FOL_Entity(member), FOL_Property(prop)))
        shuffle(observations)
        return ". ".join([str(observation).capitalize() for observation in observations]) + "."

    @property
    def hypotheses(self):
        ret = 0
        hypotheses = []
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.parents(False):
                    hypotheses.append(
                        FOL(FOL_Concept(node.name), FOL_Concept(node.parents(False)[0].name)))
                for prop in node.properties(False):
                    hypotheses.append(
                        FOL(FOL_Concept(node.name), FOL_Property(prop)))
                for member in node.members(False):
                    hypotheses.append(
                        FOL(FOL_Entity(member), FOL_Concept(node.name)))

        return ". ".join([str(hypothesis).capitalize() for hypothesis in hypotheses])

    @property
    def CoT(self):
        CoT = []
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.members(False):
                    for hidden_member in node.members(False):
                        for (choosen_node, prop) in node.associated_properties_for_recover_memberships:
                            if choosen_node != node:
                                chains = [node]
                                while chains[-1] != choosen_node:
                                    chains.append(chains[-1].parents()[0])
                                for i in range(1, len(chains)):
                                    CoT.append(
                                        str(FOL(FOL_Concept(chains[i - 1].name), FOL_Concept(chains[i].name))))
                                    CoT.append(
                                        str(FOL(FOL_Entity(hidden_member), FOL_Concept(chains[i].name))))
                            CoT.append(
                                str(FOL(FOL_Concept(choosen_node.name), FOL_Property(prop))))
                            CoT.append(
                                "Suppose " + str(FOL(FOL_Entity(hidden_member), FOL_Concept(node.name))))
                            CoT.append(
                                str(FOL(FOL_Entity(hidden_member), FOL_Property(prop))))
        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.properties(False):
                    for prop in node.properties(False):
                        for (choosen_node, member) in node.associated_members_for_recover_properties[prop]:
                            if choosen_node != node:
                                _node = choosen_node
                                while _node.parents() and _node != node:
                                    CoT.append(
                                        str(FOL(FOL_Entity(member), FOL_Concept(_node.name))))
                                    CoT.append(
                                        str(FOL(FOL_Concept(_node.name), FOL_Concept(_node.parents()[0].name))))
                                    _node = _node.parents()[0]
                            # CoT.append(str(FOL(FOL_Entity(member))))
                            CoT.append(
                                str(FOL(FOL_Entity(member), FOL_Concept(node.name))))
                            CoT.append(
                                "Suppose " + str(FOL(FOL_Concept(node.name), FOL_Property(prop))))
                            CoT.append(
                                str(FOL(FOL_Entity(member), FOL_Property(prop))))

        for level_nodes in self.nodes:
            for node in level_nodes:
                if node.parents(False):
                    _parent = node.parents(False)[0]
                    for (choosen_node, member) in node.associated_members_for_recover_ontolog:
                        if choosen_node != node:
                            _node = choosen_node
                            while _node.parents() and _node != node:
                                CoT.append(
                                    str(FOL(FOL_Entity(member), FOL_Concept(_node.name))))
                                CoT.append(
                                    str(FOL(FOL_Concept(_node.name), FOL_Concept(_node.parents()[0].name))))
                                _node = _node.parents()[0]
                        # CoT.append(str(FOL(FOL_Entity(member))))
                        CoT.append(
                            str(FOL(FOL_Entity(member), FOL_Concept(node.name))))
                        CoT.append(
                            "Suppose " + str(FOL(FOL_Concept(node.name), FOL_Concept(_parent.name))))
                        CoT.append(
                            str(FOL(FOL_Entity(member), FOL_Concept(_parent.name))))

        return ". ".join([step[:1].upper() + step[1:] for step in CoT]) + "."

    @property
    def theories(self):
        theories = []
        for level_nodes in self.nodes:
            for node in level_nodes:
                for member in node.members():
                    theories.append(
                        FOL(FOL_Entity(member), FOL_Concept(node.name)))
                for prop in node.properties():
                    theories.append(
                        FOL(FOL_Concept(node.name), FOL_Property(prop)))
                for parent_node in node.parents():
                    theories.append(FOL(FOL_Concept(node.name),
                                    FOL_Concept(parent_node.name)))
        shuffle(theories)
        # print([str(theory) for theory in theories])
        return '. '.join([str(theory).capitalize() for theory in theories]) + '.'

    @property
    def prompt(self):
        return "prompt"


if __name__ == '__main__':
    pass
