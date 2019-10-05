from django.contrib.gis.db import models


class Adgangsadresse(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    oprettet = models.DateTimeField(blank=True, null=True)
    ændret = models.DateTimeField(blank=True, null=True)
    ikrafttrædelsesdato = models.DateTimeField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)
    vejkode = models.TextField(blank=True, null=True)
    husnr = models.TextField(blank=True, null=True)
    supplerendebynavn = models.TextField(blank=True, null=True)
    postnr = models.TextField(blank=True, null=True)
    ejerlavkode = models.IntegerField(blank=True, null=True)
    matrikelnr = models.TextField(blank=True, null=True)
    esrejendomsnr = models.TextField(blank=True, null=True)
    etrs89koordinat_øst = models.FloatField(blank=True, null=True)
    etrs89koordinat_nord = models.FloatField(blank=True, null=True)
    nøjagtighed = models.TextField(blank=True, null=True)
    kilde = models.IntegerField(blank=True, null=True)
    husnummerkilde = models.IntegerField(blank=True, null=True)
    tekniskstandard = models.TextField(blank=True, null=True)
    tekstretning = models.FloatField(blank=True, null=True)
    adressepunktændringsdato = models.DateTimeField(blank=True, null=True)
    esdhreference = models.TextField(blank=True, null=True)
    journalnummer = models.TextField(blank=True, null=True)
    højde = models.FloatField(blank=True, null=True)
    adgangspunktid = models.UUIDField(blank=True, null=True)
    supplerendebynavn_dagi_id = models.TextField(blank=True, null=True)
    vejpunkt_id = models.UUIDField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adgangsadresse'


class Adresse(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    oprettet = models.DateTimeField(blank=True, null=True)
    ændret = models.DateTimeField(blank=True, null=True)
    ikrafttrædelsesdato = models.DateTimeField(blank=True, null=True)
    adgangsadresseid = models.UUIDField(blank=True, null=True)
    etage = models.TextField(blank=True, null=True)
    dør = models.TextField(blank=True, null=True)
    kilde = models.IntegerField(blank=True, null=True)
    esdhreference = models.TextField(blank=True, null=True)
    journalnummer = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adresse'


class Afstemningsomraade(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    nummer = models.TextField()
    navn = models.TextField(blank=True, null=True)
    afstemningsstednavn = models.TextField(blank=True, null=True)
    afstemningsstedadresse = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(primary_key=True)
    opstillingskreds_dagi_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'afstemningsområde'
        unique_together = (('kommunekode', 'nummer'),)


class Afstemningsomraadetilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    kommunekode = models.TextField()
    afstemningsområdenummer = models.TextField()

    class Meta:
        managed = False
        db_table = 'afstemningsområdetilknytning'
        unique_together = (('adgangsadresseid', 'kommunekode', 'afstemningsområdenummer'),)


class Brofasthed(models.Model):
    stedid = models.UUIDField(primary_key=True)
    brofast = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'brofasthed'


class Bygning(models.Model):
    id = models.TextField(primary_key=True)
    bygningstype = models.TextField(blank=True, null=True)
    metode3d = models.TextField(blank=True, null=True)
    målested = models.TextField(blank=True, null=True)
    bbrbygning_id = models.UUIDField(blank=True, null=True)
    synlig = models.BooleanField(blank=True, null=True)
    overlap = models.BooleanField(blank=True, null=True)
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'bygning'


class Bygningtilknytning(models.Model):
    bygningid = models.IntegerField(primary_key=True)
    adgangsadresseid = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'bygningtilknytning'
        unique_together = (('bygningid', 'adgangsadresseid'),)


class DagiPostnummer(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    nr = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dagi_postnummer'


class DarAdresseAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    dørbetegnelse = models.TextField(blank=True, null=True)
    dørpunkt_id = models.UUIDField(blank=True, null=True)
    etagebetegnelse = models.TextField(blank=True, null=True)
    fk_bbr_bygning_bygning = models.UUIDField(blank=True, null=True)
    husnummer_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_adresse_aktuel'


class DarAdresseHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    dørbetegnelse = models.TextField(blank=True, null=True)
    dørpunkt_id = models.UUIDField(blank=True, null=True)
    etagebetegnelse = models.TextField(blank=True, null=True)
    fk_bbr_bygning_bygning = models.UUIDField(blank=True, null=True)
    husnummer_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_adresse_historik'


class DarAdressepunktAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    oprindelse_kilde = models.TextField(blank=True, null=True)
    oprindelse_nøjagtighedsklasse = models.TextField(blank=True, null=True)
    oprindelse_registrering = models.DateTimeField(blank=True, null=True)
    oprindelse_tekniskstandard = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'dar_adressepunkt_aktuel'


class DarAdressepunktHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    oprindelse_kilde = models.TextField(blank=True, null=True)
    oprindelse_nøjagtighedsklasse = models.TextField(blank=True, null=True)
    oprindelse_registrering = models.DateTimeField(blank=True, null=True)
    oprindelse_tekniskstandard = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'dar_adressepunkt_historik'


class DarDarafstemningsomraadeAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    afstemningsområde = models.TextField(blank=True, null=True)
    afstemningsområdenummer = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darafstemningsområde_aktuel'


class DarDarafstemningsomraadeHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    afstemningsområde = models.TextField(blank=True, null=True)
    afstemningsområdenummer = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darafstemningsområde_historik'


class DarDarkommuneinddelingAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    kommuneinddeling = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darkommuneinddeling_aktuel'


class DarDarkommuneinddelingHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    kommuneinddeling = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darkommuneinddeling_historik'


class DarDarmenighedsraadsafstemningsomraadeAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    mrafstemningsområde = models.TextField(blank=True, null=True)
    mrafstemningsområdenummer = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darmenighedsrådsafstemningsområde_aktuel'


class DarDarmenighedsraadsafstemningsomraadeHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    mrafstemningsområde = models.TextField(blank=True, null=True)
    mrafstemningsområdenummer = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darmenighedsrådsafstemningsområde_historik'


class DarDarsogneinddelingAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    sogneinddeling = models.TextField(blank=True, null=True)
    sognekode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darsogneinddeling_aktuel'


class DarDarsogneinddelingHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    sogneinddeling = models.TextField(blank=True, null=True)
    sognekode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_darsogneinddeling_historik'


class DarHusnummerAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    adgangspunkt_id = models.UUIDField(blank=True, null=True)
    darafstemningsområde_id = models.UUIDField(blank=True, null=True)
    darkommune_id = models.UUIDField(blank=True, null=True)
    darmenighedsrådsafstemningsområde_id = models.UUIDField(blank=True, null=True)
    darsogneinddeling_id = models.UUIDField(blank=True, null=True)
    fk_bbr_bygning_adgangtilbygning = models.TextField(blank=True, null=True)
    fk_bbr_tekniskanlæg_adgangtiltekniskanlæg = models.TextField(blank=True, null=True)
    fk_geodk_bygning_geodanmarkbygning = models.TextField(blank=True, null=True)
    fk_geodk_vejmidte_vejmidte = models.TextField(blank=True, null=True)
    fk_mu_jordstykke_foreløbigtplaceretpåjordstykke = models.TextField(blank=True, null=True)
    fk_mu_jordstykke_jordstykke = models.TextField(blank=True, null=True)
    husnummerretning = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    husnummertekst = models.TextField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    postnummer_id = models.UUIDField(blank=True, null=True)
    supplerendebynavn_id = models.UUIDField(blank=True, null=True)
    vejpunkt_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_husnummer_aktuel'


class DarHusnummerHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    adgangspunkt_id = models.UUIDField(blank=True, null=True)
    darafstemningsområde_id = models.UUIDField(blank=True, null=True)
    darkommune_id = models.UUIDField(blank=True, null=True)
    darmenighedsrådsafstemningsområde_id = models.UUIDField(blank=True, null=True)
    darsogneinddeling_id = models.UUIDField(blank=True, null=True)
    fk_bbr_bygning_adgangtilbygning = models.TextField(blank=True, null=True)
    fk_bbr_tekniskanlæg_adgangtiltekniskanlæg = models.TextField(blank=True, null=True)
    fk_geodk_bygning_geodanmarkbygning = models.TextField(blank=True, null=True)
    fk_geodk_vejmidte_vejmidte = models.TextField(blank=True, null=True)
    fk_mu_jordstykke_foreløbigtplaceretpåjordstykke = models.TextField(blank=True, null=True)
    fk_mu_jordstykke_jordstykke = models.TextField(blank=True, null=True)
    husnummerretning = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    husnummertekst = models.TextField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    postnummer_id = models.UUIDField(blank=True, null=True)
    supplerendebynavn_id = models.UUIDField(blank=True, null=True)
    vejpunkt_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_husnummer_historik'


class DarNavngivenvejAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    administreresafkommune = models.TextField(blank=True, null=True)
    beskrivelse = models.TextField(blank=True, null=True)
    retskrivningskontrol = models.TextField(blank=True, null=True)
    udtaltvejnavn = models.TextField(blank=True, null=True)
    vejadresseringsnavn = models.TextField(blank=True, null=True)
    vejnavn = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_kilde = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_nøjagtighedsklasse = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_registrering = models.DateTimeField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_tekniskstandard = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_vejnavnelinje = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    vejnavnebeliggenhed_vejnavneområde = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    vejnavnebeliggenhed_vejtilslutningspunkter = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'dar_navngivenvej_aktuel'


class DarNavngivenvejHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    administreresafkommune = models.TextField(blank=True, null=True)
    beskrivelse = models.TextField(blank=True, null=True)
    retskrivningskontrol = models.TextField(blank=True, null=True)
    udtaltvejnavn = models.TextField(blank=True, null=True)
    vejadresseringsnavn = models.TextField(blank=True, null=True)
    vejnavn = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_kilde = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_nøjagtighedsklasse = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_registrering = models.DateTimeField(blank=True, null=True)
    vejnavnebeliggenhed_oprindelse_tekniskstandard = models.TextField(blank=True, null=True)
    vejnavnebeliggenhed_vejnavnelinje = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    vejnavnebeliggenhed_vejnavneområde = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    vejnavnebeliggenhed_vejtilslutningspunkter = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'dar_navngivenvej_historik'


class DarNavngivenvejkommunedelAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    kommune = models.TextField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    vejkode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejkommunedel_aktuel'


class DarNavngivenvejkommunedelHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    kommune = models.TextField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    vejkode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejkommunedel_historik'


class DarNavngivenvejpostnummerrelationAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    postnummer_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejpostnummerrelation_aktuel'


class DarNavngivenvejpostnummerrelationHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    postnummer_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejpostnummerrelation_historik'


class DarNavngivenvejsupplerendebynavnrelationAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    supplerendebynavn_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejsupplerendebynavnrelation_aktuel'


class DarNavngivenvejsupplerendebynavnrelationHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)
    supplerendebynavn_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_navngivenvejsupplerendebynavnrelation_historik'


class DarPostnummerAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    postnr = models.IntegerField(blank=True, null=True)
    postnummerinddeling = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_postnummer_aktuel'


class DarPostnummerHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    postnr = models.IntegerField(blank=True, null=True)
    postnummerinddeling = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_postnummer_historik'


class DarReserveretvejnavnAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navneområde = models.TextField(blank=True, null=True)
    reservationudløbsdato = models.DateTimeField(blank=True, null=True)
    reserveretafkommune = models.TextField(blank=True, null=True)
    reserveretnavn = models.TextField(blank=True, null=True)
    reserveretudtaltnavn = models.TextField(blank=True, null=True)
    reserveretvejadresseringsnavn = models.TextField(blank=True, null=True)
    retskrivningskontrol = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_reserveretvejnavn_aktuel'


class DarReserveretvejnavnHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navneområde = models.TextField(blank=True, null=True)
    reservationudløbsdato = models.DateTimeField(blank=True, null=True)
    reserveretafkommune = models.TextField(blank=True, null=True)
    reserveretnavn = models.TextField(blank=True, null=True)
    reserveretudtaltnavn = models.TextField(blank=True, null=True)
    reserveretvejadresseringsnavn = models.TextField(blank=True, null=True)
    retskrivningskontrol = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_reserveretvejnavn_historik'


class DarSupplerendebynavnAktuel(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    supplerendebynavn1 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_supplerendebynavn_aktuel'


class DarSupplerendebynavnHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    supplerendebynavn1 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dar_supplerendebynavn_historik'


class Ejerlav(models.Model):
    kode = models.IntegerField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    geo_ændret = models.DateTimeField(blank=True, null=True)
    ændret = models.DateTimeField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'ejerlav'


class Hoejde(models.Model):
    husnummerid = models.UUIDField(primary_key=True)
    højde = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'højde'


class IkkeBrofastHusnummer(models.Model):
    husnummerid = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'ikke_brofast_husnummer'


class Jordstykke(models.Model):
    ejerlavkode = models.IntegerField(primary_key=True)
    matrikelnr = models.TextField()
    kommunekode = models.TextField(blank=True, null=True)
    regionskode = models.TextField(blank=True, null=True)
    sognekode = models.TextField(blank=True, null=True)
    retskredskode = models.TextField(blank=True, null=True)
    esrejendomsnr = models.TextField(blank=True, null=True)
    udvidet_esrejendomsnr = models.TextField(blank=True, null=True)
    sfeejendomsnr = models.TextField(blank=True, null=True)
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    featureid = models.TextField(blank=True, null=True)
    fælleslod = models.BooleanField(blank=True, null=True)
    moderjordstykke = models.IntegerField(blank=True, null=True)
    registreretareal = models.IntegerField(blank=True, null=True)
    arealberegningsmetode = models.TextField(blank=True, null=True)
    vejareal = models.IntegerField(blank=True, null=True)
    vejarealberegningsmetode = models.TextField(blank=True, null=True)
    vandarealberegningsmetode = models.TextField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'jordstykke'
        unique_together = (('ejerlavkode', 'matrikelnr'),)


class Jordstykketilknytning(models.Model):
    ejerlavkode = models.IntegerField(primary_key=True)
    matrikelnr = models.TextField()
    adgangsadresseid = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'jordstykketilknytning'
        unique_together = (('ejerlavkode', 'matrikelnr', 'adgangsadresseid'),)


class Kommune(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    regionskode = models.TextField(blank=True, null=True)
    udenforkommuneinddeling = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kommune'


class Kommunetilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    kommunekode = models.TextField()

    class Meta:
        managed = False
        db_table = 'kommunetilknytning'
        unique_together = (('adgangsadresseid', 'kommunekode'),)


class Landpostnummer(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    nr = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'landpostnummer'


class Landsdel(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    nuts3 = models.TextField(primary_key=True)
    dagi_id = models.TextField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    regionskode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'landsdel'


class Landsdelstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    nuts3 = models.TextField()

    class Meta:
        managed = False
        db_table = 'landsdelstilknytning'
        unique_together = (('adgangsadresseid', 'nuts3'),)


class Menighedsraadsafstemningsomraade(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    nummer = models.TextField()
    navn = models.TextField(blank=True, null=True)
    afstemningsstednavn = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(primary_key=True)
    sognekode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menighedsrådsafstemningsområde'
        unique_together = (('kommunekode', 'nummer'),)


class Menighedsraadsafstemningsomraadetilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    kommunekode = models.TextField()
    menighedsrådsafstemningsområdenummer = models.TextField()

    class Meta:
        managed = False
        db_table = 'menighedsrådsafstemningsområdetilknytning'
        unique_together = (('adgangsadresseid', 'kommunekode', 'menighedsrådsafstemningsområdenummer'),)


class Navngivenvej(models.Model):
    id = models.UUIDField(primary_key=True)
    darstatus = models.TextField(blank=True, null=True)
    oprettet = models.DateTimeField(blank=True, null=True)
    ændret = models.DateTimeField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    adresseringsnavn = models.TextField(blank=True, null=True)
    administrerendekommune = models.TextField(blank=True, null=True)
    beskrivelse = models.TextField(blank=True, null=True)
    retskrivningskontrol = models.TextField(blank=True, null=True)
    udtaltvejnavn = models.TextField(blank=True, null=True)
    beliggenhed_oprindelse_kilde = models.TextField(blank=True, null=True)
    beliggenhed_oprindelse_nøjagtighedsklasse = models.TextField(blank=True, null=True)
    beliggenhed_oprindelse_registrering = models.DateTimeField(blank=True, null=True)
    beliggenhed_oprindelse_tekniskstandard = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'navngivenvej'


class Opstillingskreds(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    nummer = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    valgkredsnummer = models.TextField(blank=True, null=True)
    storkredsnummer = models.TextField(blank=True, null=True)
    kredskommunekode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opstillingskreds'


class Opstillingskredstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    opstillingskredskode = models.TextField()

    class Meta:
        managed = False
        db_table = 'opstillingskredstilknytning'
        unique_together = (('adgangsadresseid', 'opstillingskredskode'),)


class Politikreds(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'politikreds'


class Politikredstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    politikredskode = models.TextField()

    class Meta:
        managed = False
        db_table = 'politikredstilknytning'
        unique_together = (('adgangsadresseid', 'politikredskode'),)


class Postnummer(models.Model):
    nr = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    stormodtager = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'postnummer'


class Postnummertilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    postnummer = models.TextField()

    class Meta:
        managed = False
        db_table = 'postnummertilknytning'
        unique_together = (('adgangsadresseid', 'postnummer'),)


class Region(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    nuts2 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'region'


class Regionstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    regionskode = models.TextField()

    class Meta:
        managed = False
        db_table = 'regionstilknytning'
        unique_together = (('adgangsadresseid', 'regionskode'),)


class Retskreds(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'retskreds'


class Retskredstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    retskredskode = models.TextField()

    class Meta:
        managed = False
        db_table = 'retskredstilknytning'
        unique_together = (('adgangsadresseid', 'retskredskode'),)


class Sogn(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(blank=True, null=True)
    kode = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sogn'


class Sognetilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    sognekode = models.TextField()

    class Meta:
        managed = False
        db_table = 'sognetilknytning'
        unique_together = (('adgangsadresseid', 'sognekode'),)


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


class Sted(models.Model):
    id = models.UUIDField(primary_key=True)
    hovedtype = models.TextField(blank=True, null=True)
    undertype = models.TextField(blank=True, null=True)
    bebyggelseskode = models.IntegerField(blank=True, null=True)
    indbyggerantal = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'sted'


class Stednavn(models.Model):
    stedid = models.UUIDField(primary_key=True)
    navn = models.TextField()
    navnestatus = models.TextField(blank=True, null=True)
    brugsprioritet = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stednavn'
        unique_together = (('stedid', 'navn'),)


class Stednavntilknytning(models.Model):
    stednavn_id = models.UUIDField(primary_key=True)
    adgangsadresse_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'stednavntilknytning'
        unique_together = (('stednavn_id', 'adgangsadresse_id'),)


class Stedtilknytning(models.Model):
    stedid = models.UUIDField(primary_key=True)
    adgangsadresseid = models.UUIDField()

    class Meta:
        managed = False
        db_table = 'stedtilknytning'
        unique_together = (('stedid', 'adgangsadresseid'),)


class Storkreds(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    nummer = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    regionskode = models.TextField(blank=True, null=True)
    valglandsdelsbogstav = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'storkreds'


class Storkredstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    storkredsnummer = models.TextField()

    class Meta:
        managed = False
        db_table = 'storkredstilknytning'
        unique_together = (('adgangsadresseid', 'storkredsnummer'),)


class Supplerendebynavn(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    dagi_id = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplerendebynavn'


class Supplerendebynavntilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    dagi_id = models.TextField()

    class Meta:
        managed = False
        db_table = 'supplerendebynavntilknytning'
        unique_together = (('adgangsadresseid', 'dagi_id'),)


class Valglandsdel(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bogstav = models.TextField(primary_key=True)
    navn = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'valglandsdel'


class Valglandsdelstilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    valglandsdelsbogstav = models.TextField()

    class Meta:
        managed = False
        db_table = 'valglandsdelstilknytning'
        unique_together = (('adgangsadresseid', 'valglandsdelsbogstav'),)


class VaskAdresseHistorik(models.Model):
    husnummerid = models.UUIDField(blank=True, null=True)
    etage = models.TextField(blank=True, null=True)
    dør = models.TextField(blank=True, null=True)
    rowkey = models.IntegerField(primary_key=True)
    id = models.UUIDField(blank=True, null=True)
    adgangspunkt_status = models.IntegerField(blank=True, null=True)
    husnummer_status = models.IntegerField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)
    vejkode = models.TextField(blank=True, null=True)
    vejnavn = models.TextField(blank=True, null=True)
    adresseringsvejnavn = models.TextField(blank=True, null=True)
    husnr = models.TextField(blank=True, null=True)
    supplerendebynavn = models.TextField(blank=True, null=True)
    postnr = models.TextField(blank=True, null=True)
    postnrnavn = models.TextField(blank=True, null=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vask_adresse_historik'


class VaskHusnummerHistorik(models.Model):
    rowkey = models.IntegerField(primary_key=True)
    id = models.UUIDField(blank=True, null=True)
    adgangspunkt_status = models.IntegerField(blank=True, null=True)
    husnummer_status = models.IntegerField(blank=True, null=True)
    kommunekode = models.TextField(blank=True, null=True)
    vejkode = models.TextField(blank=True, null=True)
    vejnavn = models.TextField(blank=True, null=True)
    adresseringsvejnavn = models.TextField(blank=True, null=True)
    husnr = models.TextField(blank=True, null=True)
    supplerendebynavn = models.TextField(blank=True, null=True)
    postnr = models.TextField(blank=True, null=True)
    postnrnavn = models.TextField(blank=True, null=True)
    virkningstart = models.DateTimeField(blank=True, null=True)
    virkningslut = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vask_husnummer_historik'


class Vejmidte(models.Model):
    kommunekode = models.TextField(primary_key=True)
    vejkode = models.TextField()
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'vejmidte'
        unique_together = (('kommunekode', 'vejkode'),)


class Vejpunkt(models.Model):
    id = models.UUIDField(primary_key=True)
    kilde = models.TextField(blank=True, null=True)
    tekniskstandard = models.TextField(blank=True, null=True)
    nøjagtighedsklasse = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)  # This field is a geodjango field.

    class Meta:
        managed = False
        db_table = 'vejpunkt'


class Vejstykke(models.Model):
    id = models.TextField(blank=True, null=True)
    kommunekode = models.TextField(primary_key=True)
    kode = models.TextField()
    oprettet = models.DateTimeField(blank=True, null=True)
    ændret = models.DateTimeField(blank=True, null=True)
    navn = models.TextField(blank=True, null=True)
    adresseringsnavn = models.TextField(blank=True, null=True)
    navngivenvej_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vejstykke'
        unique_together = (('kommunekode', 'kode'),)


class Vejstykkepostnummerrelation(models.Model):
    kommunekode = models.TextField(primary_key=True)
    vejkode = models.TextField()
    postnr = models.TextField()

    class Meta:
        managed = False
        db_table = 'vejstykkepostnummerrelation'
        unique_together = (('kommunekode', 'vejkode', 'postnr'),)


class Zone(models.Model):
    ændret = models.TextField(blank=True, null=True)
    geo_ændret = models.TextField(blank=True, null=True)
    geo_version = models.IntegerField(blank=True, null=True)
    visueltcenter = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    bbox = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    geometri = models.TextField(blank=True, null=True)  # This field is a geodjango field.
    zone = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zone'


class Zonetilknytning(models.Model):
    adgangsadresseid = models.UUIDField(primary_key=True)
    zone = models.TextField()

    class Meta:
        managed = False
        db_table = 'zonetilknytning'
        unique_together = (('adgangsadresseid', 'zone'),)

