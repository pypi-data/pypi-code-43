#!/usr/bin/python
# vi: et sw=2 fileencoding=utf-8

import unittest

from . import toteutus


# TUOTANTOKOODIN YTIMESSÄ:

class Toteutus:
  def sisempi_metodi(self, arvo):
    return arvo + 2

  @toteutus('toteutettu_metodi')
  def alkuperainen_metodi(self, arvo=42):
    return [self.sisempi_metodi(arvo)]

  @toteutus
  def kutsuva_metodi(self, *args, **kwargs):
    return self.alkuperainen_metodi(*args, **kwargs)

  # class Toteutus

@toteutus
def toteutettu_funktio(x, y):
  return x + y


# TUOTANTOKOODIIN TEHDYT YLIKUORMITUKSET:

@toteutus('toteutettu_metodi', ennen=['kuorma.testaa:muokattu_1'])
def muokattu_2(self, *args, **kwargs):
  return [
    self.sisempi_metodi(7),
    *muokattu_2.oletus(self, *args, **kwargs),
  ]
@toteutus('toteutettu_metodi')
def muokattu_1(self, *args, **kwargs):
  return [
    *muokattu_1.oletus(self, *args, **kwargs),
    self.sisempi_metodi(21),
  ]
@toteutus('kuorma.testaa:Toteutus.kutsuva_metodi')
def muutettu_tamakin(self, *args, **kwargs):
  return muutettu_tamakin.oletus(self, arvo=43)

@toteutus('kuorma.testaa:toteutettu_funktio')
def muutettu_funktio(x, y):
  return (x - y) * muutettu_funktio.oletus(x, y)

@toteutus
def virheellinen_funktio(x):
  return virheellinen_funktio.oletus(42)


# TESTIKOODI:

class Testaa(unittest.TestCase):

  maxDiff = None

  def testaa_kuormitukset(self):
    ''' Ovatko toteutukset oikeassa järjestyksessä? '''
    self.assertEqual(
      Toteutus.alkuperainen_metodi.toteutukset(),
      [
        'kuorma.testaa:muokattu_2',
        'kuorma.testaa:muokattu_1',
        'kuorma.testaa:Toteutus.alkuperainen_metodi'
      ],
    )
    self.assertEqual(
      Toteutus.kutsuva_metodi.toteutukset(),
      [
        'kuorma.testaa:muutettu_tamakin',
        'kuorma.testaa:Toteutus.kutsuva_metodi'
      ],
    )
    self.assertEqual(
      toteutettu_funktio.toteutukset(),
      [
        'kuorma.testaa:muutettu_funktio',
        'kuorma.testaa:toteutettu_funktio'
      ],
    )
    # def testaa_kuormitukset

  def testaa_tulokset(self):
    ''' Kutsutaanko toteutuksia oikeassa järjestyksessä? '''
    self.assertEqual(
      Toteutus().kutsuva_metodi(),
      [9, 45, 23], # == [7+2] + ([43+2] + [21+2])
    )
    self.assertEqual(
      toteutettu_funktio(7, 5),
      24, # == (7 - 5) * (7 + 5)
    )
    # def testaa_tulokset

  def testaa_poikkeus(self):
    ''' Nostaako `oletus()`-kutsu poikkeuksen, kun oletusta ei ole? '''
    self.assertRaises(
      AttributeError,
      virheellinen_funktio,
      43,
    )
    # def testaa_poikkeus

  # class Testaa
