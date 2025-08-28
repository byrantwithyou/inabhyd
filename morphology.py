import enum
from random import shuffle, choice
from functools import reduce
from collections import namedtuple, defaultdict as dd
from util import *

Idx = namedtuple('Idx', ['concept', 'entity', 'prop'])


class Prop(object):
    def __init__(self, family, name, negated=False):
        self._family = family
        self._name = name
        self._negated = negated

    @property
    def name(self):
        return self._name

    @property
    def is_negated(self):
        return self._negated

    @property
    def family(self):
        return self._family

    def belong_to_same_family(self, other):
        return self._family == other._family

    def __str__(self):
        return f"{self.family}::" + (self.name if not self._negated else f"not {self.name}")

    def __eq__(self, other):
        return self.name == other.name and self._negated == other._negated and self._family == other._family

    def __hash__(self):
        return hash((self.name, self.family, self.is_negated))


class Morphology(object):
    _available_property_families = {"color": ["blue", "red", "brown", "orange"],
                                    "size": ["small", "large"],
                                    "material": ["metallic", "wooden",
                                                 "luminous", "liquid"],
                                    "light": ["transparent", "opaque", "translucent"],
                                    "mood": ["nervous", "happy", "feisty", "shy", "sad"],
                                    "meta_color": ["bright", "dull", "dark", "pale"],
                                    "taste": ["sweet", "sour", "spicy", "bitter", "salty"],
                                    "perfume": ["floral", "fruity", "earthy", "oriental"],
                                    "temperature": ["hot", "cold", "temperate"],
                                    "personality": ["kind", "mean", "angry",
                                                    "amenable", "aggressive"],
                                    "sound": ["melodic", "muffled",
                                              "discordant", "loud"],
                                    "speed": ["slow", "moderate", "fast"],
                                    "weather": ["windy", "sunny", "overcast", "rainy", "snowy"]}
    _available_concept_names = [
        ["wumpus", "yumpus", "zumpus", "dumpus", "rompus",
            "numpus", "tumpus", "vumpus", "impus", "jompus"],
        ["timple", "yimple", "starple", "shumple", "zhomple",
            "remple", "fomple", "fimple", "worple", "sorple"],
        ["tergit", "gergit", "stergit", "kergit", "shergit",
            "pergit", "bongit", "orgit", "welgit", "jelgit"],
        ["felper", "dolper", "sarper", "irper", "chorper",
            "parper", "arper", "lemper", "hilper", "gomper"],
        ["dalpist", "umpist", "rifpist", "storpist", "shalpist",
            "yerpist", "ilpist", "boompist", "scrompist", "phorpist"],
        ["prilpant", "gwompant", "urpant", "grimpant", "shilpant",
         "zhorpant", "rorpant", "dropant", "lerpant", "quimpant"],
        ["zilpor", "frompor", "stirpor", "porpor", "kurpor",
            "shampor", "werpor", "zhimpor", "yempor", "jempor"],
        ["folpee", "drompee", "delpee", "lompee", "wolpee",
            "gorpee", "shimpee", "rimpee", "twimpee", "serpee"],
        ["daumpin", "thorpin", "borpin", "rofpin", "bempin",
            "dulpin", "harpin", "lirpin", "yompin", "stopin"]
    ]
    _available_entity_names = ["James", "Mary",
                               "Michael", "Patricia",
                               "Robert", "Jennifer",
                               "John", "Linda",
                               "David", "Elizabeth",
                               "William", "Barbara",
                               "Richard", "Susan",
                               "Joseph", "Jessica",
                               "Thomas", "Karen",
                               "Christopher", "Sarah",
                               "Charles", "Lisa",
                               "Daniel", "Nancy",
                               "Matthew", "Sandra",
                               "Anthony", "Betty",
                               "Mark", "Ashley",
                               "Donald", "Emily",
                               "Steven", "Kimberly",
                               "Andrew", "Margaret",
                               "Paul", "Donna",
                               "Joshua", "Michelle",
                               "Kenneth", "Carol",
                               "Kevin", "Amanda",
                               "Brian", "Melissa",
                               "Timothy", "Deborah",
                               "Ronald", "Stephanie",
                               "George", "Rebecca",
                               "Jason", "Sharon",
                               "Edward", "Laura",
                               "Jeffrey", "Cynthia",
                               "Ryan", "Dorothy",
                               "Jacob", "Amy",
                               "Nicholas", "Kathleen",
                               "Gary", "Angela",
                               "Eric", "Shirley",
                               "Jonathan", "Emma",
                               "Stephen", "Brenda",
                               "Larry", "Pamela",
                               "Justin", "Nicole",
                               "Scott", "Anna",
                               "Brandon", "Samantha",
                               "Gregory", "Debra",
                               "Alexander", "Rachel",
                               "Patrick", "Carolyn",
                               "Frank", "Janet",
                               "Raymond", "Maria",
                               "Jack", "Olivia",
                               "Dennis", "Heather",
                               "Jerry", "Helen"]

    def __init__(self):
        self._concepts = list(
            reduce(lambda x, y: x + y, Morphology._available_concept_names, []))
        shuffle(self._concepts)
        self._property_familes = dd(list)
        for family in Morphology._available_property_families.keys():
            for prop in Morphology._available_property_families[family]:
                self._property_familes[family].append(Prop(family, prop))
                self._property_familes[family].append(
                    Prop(family, prop, negated=True))
            shuffle(self._property_familes[family])
        self._entites = list(Morphology._available_entity_names)
        shuffle(self._entites)
        self._idx = Idx(
            0, 0, {family: 0 for family in Morphology._available_property_families.keys()})

    @property
    def next_concept(self):
        if self._idx.concept >= len(self._concepts):
            raise MyError("Not enough concepts!")
        self._idx = Idx(concept=self._idx.concept + 1,
                        entity=self._idx.entity, prop=self._idx.prop)
        return self._concepts[self._idx.concept - 1]

    @property
    def next_entity(self):
        if self._idx.entity >= len(self._entites):
            raise MyError("Not enough entities!")
        self._idx = Idx(concept=self._idx.concept,
                        entity=self._idx.entity + 1, prop=self._idx.prop)
        return self._entites[self._idx.entity - 1]

    def next_property(self, prohibited_property_families=[]):
        candidates = [(family, self._property_familes[family][self._idx.prop[family]])
                      for family in self._property_familes.keys() if family not in prohibited_property_families]
        if not candidates:
            raise MyError("Not enough properties!")
        family, prop = choice(candidates)
        self._idx.prop[family] += 1
        return prop
