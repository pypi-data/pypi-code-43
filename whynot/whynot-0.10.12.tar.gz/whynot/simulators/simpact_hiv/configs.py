"""Configurations files for the HIV simulator."""

TOY_CONFIG = {
    "population.nummen": 200,
    "population.numwomen": 200,
    "population.simtime": 40,
    "hivtransmission.param.c": 0.10,
}

TOY_INTERVENTION_CONFIG = {
    "population.nummen": 200,
    "population.numwomen": 200,
    "population.simtime": 40,
    "hivtransmission.param.c": 0.1649,
}

# Take from:
# https://rstudio-pubs-static.s3.amazonaws.com/93073_0ce8e66a84184adfae0f7a8075909d1c.html
DEFAULT_CONFIG = {
    "population.nummen": 5000,
    "population.numwomen": 5000,
    "population.eyecap.fraction": 0.1,  # 1
    "syncpopstats.interval": 1,

    # 110 is 10 years of "burn in", followed by 100 years of HIV transmission
    "population.simtime": 110,
    "hivseed.time": 10,
    "hivseed.type": "amount",
    "hivseed.amount": 100,     # 100 out of 10000 is 1% of the population

    # HIV is introduced at an age that the individual is likely already sexually
    # active, in a relationship, and still has lots of time to infect others
    "hivseed.age.min": 20,
    "hivseed.age.max": 25,

    # Nobody will start ART during the simulations
    # This will result in timing of HIV diagnosis way beyond the simulation period.
    "diagnosis.baseline": -100,

    # We are inflating the transmission parameters "for effect"
    "hivtransmission.param.a": -0.3,
    "hivtransmission.param.b": -8,
    "hivtransmission.param.c": 0.1649,
}
