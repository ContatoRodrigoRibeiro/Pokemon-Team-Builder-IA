from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

class Type(str, Enum):
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"

@dataclass
class Pokemon:
    id: int
    name: str
    types: List[Type]
    abilities: List[str] = field(default_factory=list)
    base_stats: Dict[str, int] = field(default_factory=dict)
    sprite: Optional[str] = None

    def __str__(self):
        return f"{self.name} ({'/'.join(t.value for t in self.types)})"

@dataclass
class Team:
    pokemon: List[Pokemon] = field(default_factory=list)
    name: str = "Meu Time Gen 9"
    format: str = "gen9vgc"

    def add_pokemon(self, pokemon: Pokemon) -> bool:
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)
            return True
        return False

    def remove_pokemon(self, index: int) -> bool:
        if 0 <= index < len(self.pokemon):
            del self.pokemon[index]
            return True
        return False