import sys
nam = sys.argv[1]
for line in open(nam).readlines():
  try:
    values = line.strip().split(" ")
    result = '  {}: ("{}", "{}"),'.format(values[0], values[1], " ".join(values[2:]))
    print(result)
  except:
    pass

