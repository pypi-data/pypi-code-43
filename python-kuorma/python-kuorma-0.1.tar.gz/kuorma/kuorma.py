#!/usr/bin/python
# vi: et sw=2 fileencoding=utf-8

import bisect
import collections
import functools


@functools.total_ordering
class Toteutus:
  '''
  Täydellisesti järjestettävä kääre toteutusfunktiolle.

  Toteutus A < B silloin,
  kun A.ennen sisältää B:n tai B.jalkeen sisältää A:n.

  Toteutus A = B silloin,
  kun kumpikaan ei sisälly toisen ennen- tai jalkeen-luetteloon.
  '''
  def __init__(self, toteutus, ennen=None, jalkeen=None):
    self.nimi = f'{toteutus.__module__}:{toteutus.__qualname__}'
    self.toteutus = toteutus
    self.ennen = type(
      'Kaikki', (), {'__contains__': lambda *args: True}
    )() if ennen == '__all__' else ennen or ()
    self.jalkeen = type(
      'Kaikki', (), {'__contains__': lambda *args: True}
    )() if jalkeen == '__all__' else jalkeen or ()

  def __lt__(self, toteutus):
    return any((
      self.nimi in toteutus.jalkeen,
      toteutus.nimi in self.ennen,
    ))

  def __eq__(self, toteutus):
    return all((
      self.nimi not in toteutus.ennen,
      self.nimi not in toteutus.jalkeen,
      toteutus.nimi not in self.ennen,
      toteutus.nimi not in self.jalkeen,
    ))

  def __call__(self, *args, **kwargs):
    return self.toteutus(*args, **kwargs)

  # class Toteutus


class Kuormitus(collections.deque):

  def oletus(self, toteutus=None):
    '''
    Palauta sisempi Kuormitus, jota käytetään
    annetun toteutuksen oletustoteutuksena.
    '''
    # Etsi toteutusfunktiota toteutusten käärimistä funktioista.
    # Huomaa, että suora `self.index()`-kutsu hakee alkiota,
    # jolle `Toteutus.__eq__() = True`.
    indeksi = (
      [t.__wrapped__ for t in self].index(toteutus.__wrapped__) + 1
      if toteutus else 1
    )
    sisempi_kuormitus = self.copy()
    for x in range(indeksi):
      sisempi_kuormitus.popleft()
    return (
      functools.partial(sisempi_kuormitus)
      if sisempi_kuormitus else None
    )
    # def oletus

  def __call__(self, *args, **kwargs):
    ''' Kutsu ensimmäistä toteutusta. '''
    return self[0](*args, **kwargs)
    # def __call__

  # class Kuormitus


class Kuorma:

  _kuormitukset = {}

  # Luokkamääre, joka palauttaa kaikki olemassaolevat kuormitukset.
  kuormitukset = type('Kuormatut', (), {
    '__get__': lambda self, instance, cls=None: cls._kuormitukset
  })()

  @classmethod
  def toteutus(cls, nimi=None, ennen=None, jalkeen=None):
    '''
    Muuta koristeelle annettu funktiototeutus Kuormitus-luokan olioksi.

    Args:
      nimi (str): kuormituksen tunniste,
        oletuksena `f'{f.__module__}:{f.__qualname__}'` funktiolle `f`.
      ennen (iteroituva / None): luettelo niistä toteutuksista
        (moduuli:nimi-muodossa), jotka tämä toteutus korvaa.
      jalkeen (iteroituva / None): luettelo niistä toteutuksista
        (moduuli:nimi-muodossa), jotka korvaavat tämän toteutuksen.

    Oletuksena olio kutsuu sellaisenaan alkuperäistä toteutusta. Se saa
    määritteinään funktiot
    - `toteutukset`, joka palauttaa kaikki samalla nimellä määritetyt
      toteutukset suoritusjärjestyksessä; ja
    - `oletus`, joka suorittaa järjestyksessä seuraavan, samalla nimellä
      tallennetun funktiototeutuksen.

    Mikäli samalla nimellä annetaan uusi funktiototeutus, se korvaa
    kaikki aiemmat toteutukset (ks. kuitenkin suoritusjärjestys alla).

    Toteutusten keskinäinen järjestys määräytyy oletusarvoisesti tämän
    koristeen kutsumisjärjestyksessä (viimeksi kutsuttu ensin), mutta
    sitä voidaan muuttaa parametrien `ennen` ja `jalkeen` avulla.

    Olkoon esimerkiksi oletustoteutukselle `f` määritetty sitä
    kuormittavat funktiot `a`, `b`, `c` siten, että
    - `a.ennen = [f'{b.__module__}:{b.__qualname__}']` ja
    - `a.jalkeen = [f'{c.__module__}:{c.__qualname__}']`.
    Silloin kutsutaan ensisijaisesti funktiota `c`, ja lisäksi:
    - `c.oletus()` kutsuu funktiota `a`
    - `a.oletus()` kutsuu funktiota `b`
    - `b.oletus()` kutsuu oletustoteutusta `f`.
    '''
    # Salli kutsu ilman nimettyjä argumentteja.
    if callable(nimi):
      return cls.toteutus()(nimi)

    nimi2 = nimi
    def korvaa_funktio(f):
      nimi = nimi2 or f'{f.__module__}:{f.__qualname__}'
      toteutus = functools.wraps(f)(Toteutus(f, ennen=ennen, jalkeen=jalkeen))

      # Muodosta uusi Kuormitus tai lisää olemassaolevaan.
      if nimi not in cls._kuormitukset:
        cls._kuormitukset[nimi] = Kuormitus((toteutus, ))
      else:
        bisect.insort_left(cls._kuormitukset[nimi], toteutus)

      # Muodosta uusi funktio, joka kutsuu Kuormitus-oliota.
      korvattu = lambda *args, **kwargs: cls._kuormitukset[nimi](*args, **kwargs)

      # Lisää funktio kaikkien ajonaikaisten toteutusten hakemiseen.
      korvattu.toteutukset = lambda: [
        f'{t.__module__}:{t.__qualname__}' for t in cls._kuormitukset[nimi]
      ]

      # Lisää funktio oletustoteutuksen hakemiseen.
      def kutsu_oletusta(*args, **kwargs):
        oletus = cls._kuormitukset[nimi].oletus(toteutus)
        if oletus is None:
          raise AttributeError(
            'Oletusta ei ole; kyseessä on alkuperäinen toteutus.'
          )
        return oletus(*args, **kwargs)
        # def kutsu_oletusta
      korvattu.oletus = kutsu_oletusta

      return korvattu
      # def korvaa_funktio
    return korvaa_funktio
    # def toteutus

  # class Kuorma
