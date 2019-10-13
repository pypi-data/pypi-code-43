# -*- coding: utf-8 -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import inspect
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, DateTime, Text, FetchedValue, Index, Float, \
    LargeBinary, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import InstrumentedAttribute

Base = declarative_base()

__all__ = [
    'Aggregation',
    'Campaign',
    'Configuration',
    'ConfigurationSensorMapping',
    'Drive',
    'Driver',
    'Enrichment',
    'Maneuver',
    'Measurement',
    'Record',
    'RecordTransferredMapping',
    'Sensor',
    'Signal',
    'Signalgroup',
    'SignalsignalgroupMapping',
    'Transferred',
    'Unit',
    'Valuetype',
    'Vehicle',
    'Module',
    'AvailableDrive',
    'ProcessedDrive',
    'FailedDrive',
    'Base'
]


class Serializer(object):

    def to_dict(self, deep=False, root=()):

        result = {}
        for name, value in inspect.getmembers(self.__class__, lambda a: not (inspect.isroutine(a))):

            if isinstance(value, InstrumentedAttribute):

                val = getattr(self, name)

                if not isinstance(val, list):
                    val = [val]

                values = []
                for e in val:
                    if e in root:
                        continue

                    if deep and isinstance(e, Serializer):
                        values.append(e.to_dict(deep=deep, root=root + (self,)))
                    elif not isinstance(e, Serializer):
                        values.append(e)

                if values and len(values) == 1:
                    result[name] = values[0]

        return result


class Aggregation(Base, Serializer):
    __tablename__ = 'aggregation'

    idaggregation = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    timestamp = Column(DATETIME(fsp=6), nullable=False, unique=True)
    iddrive = Column(ForeignKey('drive.iddrive', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                     nullable=False, index=True)

    drive = relationship('Drive', primaryjoin='Aggregation.iddrive == Drive.iddrive', backref='aggregations')


class Campaign(Base, Serializer):
    __tablename__ = 'campaign'

    idcampaign = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    start = Column(DateTime, nullable=True)
    end = Column(DateTime, nullable=True)

    description = Column(Text)


class Configuration(Base, Serializer):
    __tablename__ = 'configuration'

    idconfiguration = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    idvehicle = Column(ForeignKey('vehicle.idvehicle', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                       index=True)
    description = Column(Text)

    vehicle = relationship('Vehicle', primaryjoin='Configuration.idvehicle == Vehicle.idvehicle',
                           backref='configurations')


class ConfigurationSensorMapping(Base, Serializer):
    __tablename__ = 'configuration_sensor_mapping'

    idconfiguration_sensor = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idsensor = Column(ForeignKey('sensor.idsensor', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    idconfiguration = Column(ForeignKey('configuration.idconfiguration', ondelete='CASCADE', onupdate='CASCADE'),
                             nullable=False, index=True)

    configuration = relationship('Configuration',
                                 primaryjoin='ConfigurationSensorMapping.idconfiguration == Configuration.idconfiguration',
                                 backref='configuration_sensor_mappings')
    sensor = relationship('Sensor', primaryjoin='ConfigurationSensorMapping.idsensor == Sensor.idsensor',
                          backref='configuration_sensor_mappings')


class Drive(Base, Serializer):
    __tablename__ = 'drive'

    iddrive = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    start = Column(DATETIME(fsp=6), nullable=False, index=True)
    end = Column(DATETIME(fsp=6), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    idvehicle = Column(ForeignKey('vehicle.idvehicle', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False, index=True, server_default=FetchedValue())

    iddriver = Column(ForeignKey('driver.iddriver', ondelete='CASCADE', onupdate='CASCADE'),
                      nullable=False, index=True, server_default=FetchedValue())

    idcampaign = Column(ForeignKey('campaign.idcampaign', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False, index=True, server_default=FetchedValue(), default=1)

    vehicle = relationship('Vehicle', primaryjoin='Drive.idvehicle == Vehicle.idvehicle', backref='drives')

    driver = relationship('Driver', primaryjoin='Drive.iddriver == Driver.iddriver', backref='drives')

    campaign = relationship('Campaign', primaryjoin='Drive.idcampaign == Campaign.idcampaign', backref='drives')


class Driver(Base, Serializer):
    __tablename__ = 'driver'

    iddriver = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    # make new columns optional to be backward compatible
    sex = Column(String(255), nullable=True)
    weight = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)


class Enrichment(Base, Serializer):
    __tablename__ = 'enrichment'
    __table_args__ = (
        Index('unique_key_combination', 'idaggregation', 'enricher'),
    )

    idenrichment = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    enriched_on = Column(DateTime, nullable=False, index=True)
    idaggregation = Column(ForeignKey('aggregation.idaggregation', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=False, index=True)
    enricher = Column(String(255), nullable=False)

    aggregation = relationship('Aggregation',
                               primaryjoin='Enrichment.idaggregation == Aggregation.idaggregation',
                               backref='enrichments')


class Measurement(Base, Serializer):
    __tablename__ = 'measurement'

    idmeasurement = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    idsignal = Column(ForeignKey('signal.idsignal', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                      index=True)
    idrecord = Column(ForeignKey('record.idrecord', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    idvehicle = Column(ForeignKey('vehicle.idvehicle', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                       index=True)
    flagvalue = Column(Integer)
    doublevalue = Column(Float(asdecimal=True))
    textvalue = Column(Text)
    binaryvalue = Column(LargeBinary)
    integervalue = Column(Integer)
    timestamp = Column(DATETIME(fsp=6), nullable=False, index=True)

    record = relationship('Record', primaryjoin='Measurement.idrecord == Record.idrecord',
                          backref='measurements')
    signal = relationship('Signal', primaryjoin='Measurement.idsignal == Signal.idsignal',
                          backref='measurements')
    vehicle = relationship('Vehicle', primaryjoin='Measurement.idvehicle == Vehicle.idvehicle',
                           backref='measurements')


class Record(Base, Serializer):
    __tablename__ = 'record'

    idrecord = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    start_mileage = Column(Float(asdecimal=True), nullable=False, index=True)
    end_mileage = Column(Float(asdecimal=True), nullable=False)
    drive_length = Column(Float(asdecimal=True), nullable=False)
    start_time = Column(DATETIME(fsp=6), nullable=False)
    end_time = Column(DATETIME(fsp=6), nullable=False, index=True)
    filepath = Column(String(256), nullable=False)

    iddrive = Column(ForeignKey('drive.iddrive', ondelete='CASCADE', onupdate='CASCADE'), index=True)

    drive = relationship('Drive', primaryjoin='Record.iddrive == Drive.iddrive', backref='records')


class RecordTransferredMapping(Base, Serializer):
    __tablename__ = 'record_transferred_mapping'

    idrecord_transferred = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idrecord = Column(ForeignKey('record.idrecord', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    idtransferred = Column(ForeignKey('transferred.idtransferred', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=False, index=True)

    record = relationship('Record', primaryjoin='RecordTransferredMapping.idrecord == Record.idrecord',
                          backref='record_transferred_mappings')
    transferred = relationship('Transferred',
                               primaryjoin='RecordTransferredMapping.idtransferred == Transferred.idtransferred',
                               backref='record_transferred_mappings')


class Sensor(Base, Serializer):
    __tablename__ = 'sensor'

    idsensor = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)
    parameter = Column(Text)
    additional_informations = Column(LargeBinary)
    description = Column(Text)


class Signal(Base, Serializer):
    __tablename__ = 'signal'

    idsignal = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    idvaluetype = Column(ForeignKey('valuetype.idvaluetype', ondelete='CASCADE',
                                    onupdate='CASCADE'), nullable=False, index=True)
    idsensor = Column(ForeignKey('sensor.idsensor', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                      index=True)
    idunit = Column(ForeignKey('unit.idunit'), index=True)

    sensor = relationship('Sensor', primaryjoin='Signal.idsensor == Sensor.idsensor', backref='signals')
    unit = relationship('Unit', primaryjoin='Signal.idunit == Unit.idunit', backref='signals')
    valuetype = relationship('Valuetype', primaryjoin='Signal.idvaluetype == Valuetype.idvaluetype',
                             backref='signals')


class Signalgroup(Base, Serializer):
    __tablename__ = 'signalgroup'

    idsignalgroup = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255))


class SignalsignalgroupMapping(Base, Serializer):
    __tablename__ = 'signalsignalgroup_mapping'

    idsignal_signalgroup_mapping = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idsignal = Column(ForeignKey('signal.idsignal', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    idsignalgroup = Column(ForeignKey('signalgroup.idsignalgroup', ondelete='CASCADE', onupdate='CASCADE'),
                           nullable=False, index=True)

    signal = relationship('Signal', primaryjoin='SignalsignalgroupMapping.idsignal == Signal.idsignal',
                          backref='signalsignalgroup_mappings')
    signalgroup = relationship('Signalgroup',
                               primaryjoin='SignalsignalgroupMapping.idsignalgroup == Signalgroup.idsignalgroup',
                               backref='signalsignalgroup_mappings')


class Transferred(Base, Serializer):
    __tablename__ = 'transferred'

    idtransferred = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date = Column(DateTime, nullable=False, server_default=FetchedValue())
    directory = Column(String(255), nullable=False)


class Unit(Base, Serializer):
    __tablename__ = 'unit'

    idunit = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(45), primary_key=True, nullable=False)


class Valuetype(Base, Serializer):
    __tablename__ = 'valuetype'

    idvaluetype = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)


class Vehicle(Base, Serializer):
    __tablename__ = 'vehicle'

    idvehicle = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    serial_number = Column(String(255), nullable=False)
    dimension_width = Column(Integer, nullable=False)
    dimension_height = Column(Integer, nullable=False)
    dimension_length = Column(Integer, nullable=False)
    description = Column(Text)


class Module(Base, Serializer):
    __tablename__ = 'module'

    # id of the module
    idmodule = Column(Integer, primary_key=True, autoincrement=True)

    # name of the module
    name = Column(String(255), nullable=False, unique=True)


class AvailableDrive(Base, Serializer):
    """
    Model to describe the table which contains all available drives.
    """
    __tablename__ = 'available_drive'

    # id of the entry
    idavailable_drive = Column(Integer, primary_key=True, autoincrement=True)

    # name of the available drive
    name = Column(String(255), nullable=False, unique=True)


class ProcessedDrive(Base, Serializer):
    """
    Model to describe the table which contains the already processed drives.
    """
    __tablename__ = 'processed_drive'

    # id of the entry
    idprocess_drive = Column(Integer, primary_key=True, autoincrement=True)

    # id of the available drive
    idavailable_drive = Column(ForeignKey('available_drive.idavailable_drive', ondelete='CASCADE',
                                          onupdate='CASCADE'), nullable=False, index=True)

    # id of the module
    idmodule = Column(ForeignKey('module.idmodule', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    # the timestamp when the drive was processed
    timestamp = Column(DateTime, nullable=False, default=datetime.now())

    # define relationships to the available drive
    drive = relationship('AvailableDrive',
                         primaryjoin='AvailableDrive.idavailable_drive == ProcessedDrive.idavailable_drive',
                         backref='processed_drives')

    # and the module
    module = relationship('Module', primaryjoin='ProcessedDrive.idmodule == Module.idmodule',
                          backref='processed_drives')

    # the combination of idavailable_drive, idmodule, timestamp should be unique, i.e. a drive should be processed by a
    # module at a certain point in time only once.
    __table_args__ = (UniqueConstraint('idavailable_drive', 'idmodule', 'timestamp', name='_drive_module_unique'),)


class Maneuver(Base, Serializer):
    """
    Model to describe the table containing the maneuver.
    """

    __tablename__ = 'maneuver'

    # id of the entry
    idmaneuver = Column(Integer, primary_key=True, autoincrement=True)

    # the id of the scene as the start of the maneuver
    start = Column(ForeignKey('aggregation.idaggregation', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                   index=True)
    # the id of the scene as the end of the maneuver
    end = Column(ForeignKey('aggregation.idaggregation', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                 index=True)

    # define relationships to the available drive
    start_scene = relationship('Aggregation',
                               primaryjoin='Aggregation.idaggregation == Maneuver.start',
                               backref='maneuver_starts')

    # and the module
    end_scene = relationship('Aggregation',
                             primaryjoin='Aggregation.idaggregation == Maneuver.end',
                             backref='maneuver_ends')

    # the name of the maneuver
    name = Column(String(255), nullable=False)


class DrivingPrimitive(Base, Serializer):
    """
    Model to represent a certain driving primitive
    """
    __tablename__ = 'driving_primitive'

    # id of the entry
    id_driving_primitive = Column(Integer, primary_key=True, autoincrement=True)

    # name of the driving primitive
    name = Column(String(255), nullable=False, unique=True, index=True)


class DrivingPrimitiveInDrive(Base, Serializer):
    """
    Model to represent driving primitives in drives
    """

    __tablename__ = 'driving_primitive_in_drive'

    # id of the entry
    id_driving_primitive_in_drive = Column(Integer, primary_key=True, autoincrement=True)

    # id of the driving primitive
    id_driving_primitive = Column(ForeignKey('{}.id_driving_primitive'.format(DrivingPrimitive.__tablename__),
                                             ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    driving_primitive = relationship('DrivingPrimitive',
                                     primaryjoin='DrivingPrimitive.id_driving_primitive == '
                                                 'DrivingPrimitiveInDrive.id_driving_primitive',
                                     backref='driving_primitives')

    # the probability of the driving primitive
    probability = Column(Float, nullable=True)

    # the id of the scene as the start of the maneuver
    start = Column(ForeignKey('{}.idaggregation'.format(Aggregation.__tablename__),
                              ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    # the id of the scene as the end of the maneuver
    end = Column(ForeignKey('{}.idaggregation'.format(Aggregation.__tablename__),
                            ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    # define relationships to the scene
    start_scene = relationship('Aggregation',
                               primaryjoin='Aggregation.idaggregation == DrivingPrimitiveInDrive.start',
                               backref='driving_primitive_starts')

    end_scene = relationship('Aggregation',
                             primaryjoin='Aggregation.idaggregation == DrivingPrimitiveInDrive.end',
                             backref='driving_primitive_ends')


class FailedDrive(Base, Serializer):
    """
    Model to describe the table which contains the drives where a module process failed.
    """
    __tablename__ = 'failed_drive'

    # id of the entry
    idfailed_drive = Column(Integer, primary_key=True, autoincrement=True)

    # id of the available drive
    idavailable_drive = Column(ForeignKey('available_drive.idavailable_drive', ondelete='CASCADE',
                                          onupdate='CASCADE'), nullable=False, index=True)

    # id of the module
    idmodule = Column(ForeignKey('module.idmodule', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    # the timestamp when the a modules failed to process a drive
    timestamp = Column(DateTime, nullable=False, default=datetime.now())

    # define relationships to the available drive
    drive = relationship('AvailableDrive',
                         primaryjoin='AvailableDrive.idavailable_drive == FailedDrive.idavailable_drive',
                         backref='failed_drives')

    # and the module
    module = relationship('Module', primaryjoin='FailedDrive.idmodule == Module.idmodule', backref='failed_drives')

    # the combination of idavailable_drive, idmodule, timestamp should be unique, i.e. a modules failed to process a
    # drive at a certain point in time only once.
    __table_args__ = (UniqueConstraint('idavailable_drive', 'idmodule', 'timestamp', name='_drive_module_unique'),)


def signal_tablename(name):
    """
    A wrapper for the table name
    Args:
        name:

    Returns:

    """
    return name


def signal_table_name(table_name, aggregated=False):
    """
    Get the signal table with the name `table_name` of the database `db`

    Args:
        table_name (str):  Name of the signal (without the signal\_ prefix)
        aggregated (bool): If the signal is an aggregated signal.

    Returns:
        str: The table name of a (aggregated) signal
    """
    if aggregated:
        return "signal_{}".format(signal_tablename(table_name))
    else:
        return "signal_{}".format(signal_tablename(table_name))


class SignalAggregatedBaseModel(object):
    """
    This is the base class of aggregated signals created dynamically.
    """

    # each model has to have a __tablename__ or __table__ attribute
    # due to the fact that the name of the table depends on the
    # signal name we define that attribute as declared_attr in order
    # to derive the name on class creation.
    @declared_attr
    def __tablename__(cls):
        return signal_table_name(cls.__name__, True)

    @declared_attr
    def id(self):
        """ The id of the signal. """

        return Column(
            "id{}".format(self.__tablename__),
            BigInteger,
            primary_key=True,
            autoincrement=True
        )

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    # each signal should have a timestamp
    timestamp = Column(DATETIME(fsp=6), nullable=False)

    @declared_attr
    def aggregation(cls):
        return relationship(Aggregation)

    @declared_attr
    def idaggregation(cls):
        return Column(BigInteger, ForeignKey(Aggregation.idaggregation, ondelete='CASCADE',
                                             onupdate='CASCADE'), nullable=False)


class SignalBaseModel(object):
    """
    This is the base class of signals created dynamically.
    """

    @declared_attr
    def __tablename__(cls):
        return signal_table_name(cls.__name__, False)

    @declared_attr
    def id(self):
        """ The id of the signal. """

        return Column(
            "id{}".format(self.__tablename__),
            BigInteger,
            primary_key=True,
            autoincrement=True
        )

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    # each signal should have a timestamp
    timestamp = Column(DATETIME(fsp=6), nullable=False)

    # Foreign keys
    @declared_attr
    def idsignal(cls):
        return Column(ForeignKey('signal.idsignal', ondelete='CASCADE', onupdate='CASCADE'), index=True)

    @declared_attr
    def idrecord(cls):
        return Column(ForeignKey('record.idrecord', ondelete='CASCADE', onupdate='CASCADE'), index=True)

    @declared_attr
    def idvehicle(cls):
        return Column(ForeignKey('vehicle.idvehicle', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                      index=True)
