from Fortuna import CumulativeWeightedChoice, random_value


description = """
Example: `random_value()` inside a CumulativeWeightedChoice behind a lambda, flick and twist.
Typical treasure table from a massively popular roll playing game.


      d(100)  Treasure Table F
    --------------------------------
       1-30   Spell scroll (8th level) <spell name>
      31-55   Potion of storm giant strength
      56-70   Potion of supreme healing
      71-85   Spell scroll (9th level) <spell name>
      86-93   Universal solvent
      94-98   Arrow of slaying
      99-100  Sovereign glue
      
"""

Spells = {
    8: (
        "Antimagic Field", "Antipathy/Sympathy", "Clone", "Control Weather", "Demiplane", "Dominate Monster",
        "Earthquake", "Feeblemind", "Glibness", "Holy Aura", "Incendiary Cloud", "Maze", "Mind Blank",
        "Power Word Stun", "Sunburst", "Telepathy", "Trap the Soul",
    ),
    9: (
        "Astral Projection", "Foresight", "Gate", "Imprisonment", "Mass Heal", "Meteor Swarm", "Power Word Heal",
        "Power Word Kill", "Prismatic Wall", "Shapechange", "Time Stop", "True Polymorph", "True Resurrection",
        "Weird", "Wish",
    )
}

treasure_table_f = CumulativeWeightedChoice({
    (30, lambda: f"Spell scroll (8th level) {random_value(Spells[8])}"),
    (55, "Potion of storm giant strength"),
    (70, "Potion of supreme healing"),
    (85, lambda: f"Spell scroll (9th level) {random_value(Spells[9])}"),
    (93, "Universal solvent"),
    (98, "Arrow of slaying"),
    (100, "Sovereign glue"),
})


if __name__ == "__main__":

    print(description)
    N = 20
    print(f"{N} random selections from treasure_table_f():")
    for _ in range(N):
        print(treasure_table_f())
