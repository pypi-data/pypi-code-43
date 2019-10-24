__version__ = '0.1.0'
import fileinput
from mako.template import Template

def main():
  tmpl = ""
  for l in fileinput.input():
    tmpl += l
  print(Template(tmpl).render())


if __name__ == "__main__":
    main()
