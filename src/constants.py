"""Enumeration Data for Path of Exile constants."""

import enum


@enum.unique
class PlayerClass(enum.IntEnum):
    SCION = 0
    MARAUDER = 1
    RANGER = 2
    WITCH = 3
    DUELIST = 4
    TEMPLAR = 5
    SHADOW = 6


@enum.unique
class PlayerAscendancy(enum.Enum):
    NONE = None
