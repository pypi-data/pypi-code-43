# COMMAND --------------
from DataSenticsLib.Greetings.Greeter import Greeter
from DataSenticsLib.DataFrame.display import d
from DataSenticsLib.DependencyInjection.container_init import container

# COMMAND --------------
# Ahoj svete

# COMMAND --------------
spark = container.getSpark()

# COMMAND --------------
a=[1, 2, 3, 6]
b=[2, 3, 4, 8]
df = spark.createDataFrame([a, b], schema=['a', 'b'])

# COMMAND --------------
df.show()

# COMMAND --------------
greeter = Greeter()
greeter.sayHello('Jano')
greeter.sayHello("Petre")

# COMMAND --------------
d(df)

# COMMAND --------------
from matplotlib import pyplot as plt

dfp = df.toPandas()
dfp.plot()

