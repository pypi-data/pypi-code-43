# this file is generated, do not modify
from enum import Enum
from typing import List, NewType, TypeVar, Union

from gqlpycgen.api import QueryBase, ObjectBase, MutationBase


ID = NewType('ID', str)
ID__Required = NewType('ID!', str)
Int = NewType('Int', int)
Int__Required = NewType('Int!', int)
String = NewType('String', str)
String__Required = NewType('String!', str)
Float = NewType('Float', float)
Float__Required = NewType('Float!', float)
Boolean = NewType('Boolean', bool)
Boolean__Required = NewType('Boolean!', bool)
Upload = NewType('Upload', str)
Upload__Required = NewType('Upload', str)
DateTime = NewType('DateTime', str)
DateTime__Required = NewType('DateTime', str)


class SortDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

    def __str__(self):
        return str(self.value)


SortDirection__Required = SortDirection


class SensorType(Enum):
    CAMERA = "CAMERA"
    RADIO = "RADIO"
    ACCELEROMETER = "ACCELEROMETER"
    GYROSCOPE = "GYROSCOPE"
    MAGNETOMETER = "MAGNETOMETER"
    INERTIAL = "INERTIAL"

    def __str__(self):
        return str(self.value)


SensorType__Required = SensorType


class PropertyType(Enum):
    BOOL = "BOOL"
    STR = "STR"
    INT = "INT"
    FLOAT = "FLOAT"
    NULL = "NULL"

    def __str__(self):
        return str(self.value)


PropertyType__Required = PropertyType


class AssignableTypeEnum(Enum):
    PERSON = "PERSON"
    DEVICE = "DEVICE"

    def __str__(self):
        return str(self.value)


AssignableTypeEnum__Required = AssignableTypeEnum


class DataSourceType(Enum):
    GROUND_TRUTH = "GROUND_TRUTH"
    GENERATED_TEST = "GENERATED_TEST"
    MEASURED = "MEASURED"
    INFERRED = "INFERRED"

    def __str__(self):
        return str(self.value)


DataSourceType__Required = DataSourceType


class Operator(Enum):
    OR = "OR"
    AND = "AND"
    NOT = "NOT"
    EQ = "EQ"
    NE = "NE"
    LIKE = "LIKE"
    RE = "RE"
    IN = "IN"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"

    def __str__(self):
        return str(self.value)


Operator__Required = Operator


class SourceType(Enum):
    TRUTH = "TRUTH"
    INFERRED = "INFERRED"

    def __str__(self):
        return str(self.value)


SourceType__Required = SourceType


class ConcentrationLevel(Enum):
    DEEP_CONCENTRATION = "DEEP_CONCENTRATION"
    CONCENTRATION = "CONCENTRATION"
    DISTRACTED_WORKING = "DISTRACTED_WORKING"
    QUIESENCE = "QUIESENCE"
    SLIGHT_DISORDER = "SLIGHT_DISORDER"
    DISORDER = "DISORDER"
    UNCONTROLLABLE = "UNCONTROLLABLE"

    def __str__(self):
        return str(self.value)


ConcentrationLevel__Required = ConcentrationLevel


class Level(Enum):
    COMPLETELY = "COMPLETELY"
    PARTIAL = "PARTIAL"
    NOT = "NOT"

    def __str__(self):
        return str(self.value)


Level__Required = Level


class EngagementType(Enum):
    W = "W"
    GL = "GL"
    GA = "GA"
    HA = "HA"
    Wait = "Wait"
    Wd = "Wd"
    S = "S"
    Obs = "Obs"
    Other = "Other"

    def __str__(self):
        return str(self.value)


EngagementType__Required = EngagementType


class Status(Enum):
    ok = "ok"
    error = "error"

    def __str__(self):
        return str(self.value)


Status__Required = Status


class DataFormat(Enum):
    BINARY = "BINARY"
    CSV = "CSV"
    IMAGE = "IMAGE"
    JSON = "JSON"
    TEXT = "TEXT"
    VIDEO = "VIDEO"

    def __str__(self):
        return str(self.value)


DataFormat__Required = DataFormat


class ObservationCodes(Enum):
    ic = "ic"
    sc = "sc"
    dc = "dc"
    ci = "ci"

    def __str__(self):
        return str(self.value)


ObservationCodes__Required = ObservationCodes


class Tuple(ObjectBase):
    FIELDS = ["x", "y", "z", ]
    TYPES = {"x": "Float__Required", "y": "Float__Required", "z": "Float__Required"}

    def __init__(self, x: 'Float__Required'=None, y: 'Float__Required'=None, z: 'Float__Required'=None):
        self.x = x
        self.y = y
        self.z = z


class Tuple__Required(Tuple):
    pass


class DeviceList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[Device__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[Device__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class DeviceList__Required(DeviceList):
    pass


class Device(ObjectBase):
    FIELDS = ["device_id", "part_number", "name", "tag_id", "serial_number", "mac_address", "description", "sensors", "configurations", "system", ]
    TYPES = {"device_id": "ID__Required", "part_number": "String", "name": "String__Required", "tag_id": "String", "serial_number": "String", "mac_address": "List[String__Required]", "description": "String", "sensors": "List[SensorInstallation__Required]", "configurations": "List[DeviceConfiguration__Required]", "system": "System__Required"}

    def __init__(self, device_id: 'ID__Required'=None, part_number: 'String'=None, name: 'String__Required'=None, tag_id: 'String'=None, serial_number: 'String'=None, mac_address: 'List[String__Required]'=None, description: 'String'=None, sensors: 'List[SensorInstallation__Required]'=None, configurations: 'List[DeviceConfiguration__Required]'=None, system: 'System__Required'=None):
        self.device_id = device_id
        self.part_number = part_number
        self.name = name
        self.tag_id = tag_id
        self.serial_number = serial_number
        self.mac_address = mac_address
        self.description = description
        self.sensors = sensors
        self.configurations = configurations
        self.system = system


class Device__Required(Device):
    pass


class SensorInstallation(ObjectBase):
    FIELDS = ["sensor_install_id", "device", "description", "start", "end", "sensor", "tag_id", "config", "system", ]
    TYPES = {"sensor_install_id": "ID__Required", "device": "Device__Required", "description": "String", "start": "DateTime__Required", "end": "DateTime", "sensor": "Sensor__Required", "tag_id": "String", "config": "List[Property__Required]", "system": "System__Required"}

    def __init__(self, sensor_install_id: 'ID__Required'=None, device: 'Device__Required'=None, description: 'String'=None, start: 'DateTime__Required'=None, end: 'DateTime'=None, sensor: 'Sensor__Required'=None, tag_id: 'String'=None, config: 'List[Property__Required]'=None, system: 'System__Required'=None):
        self.sensor_install_id = sensor_install_id
        self.device = device
        self.description = description
        self.start = start
        self.end = end
        self.sensor = sensor
        self.tag_id = tag_id
        self.config = config
        self.system = system


class SensorInstallation__Required(SensorInstallation):
    pass


class Sensor(ObjectBase):
    FIELDS = ["sensor_id", "part_number", "name", "description", "sensor_type", "version", "default_config", "system", ]
    TYPES = {"sensor_id": "ID__Required", "part_number": "String", "name": "String__Required", "description": "String", "sensor_type": "SensorType__Required", "version": "Int__Required", "default_config": "List[Property__Required]", "system": "System__Required"}

    def __init__(self, sensor_id: 'ID__Required'=None, part_number: 'String'=None, name: 'String__Required'=None, description: 'String'=None, sensor_type: 'SensorType__Required'=None, version: 'Int__Required'=None, default_config: 'List[Property__Required]'=None, system: 'System__Required'=None):
        self.sensor_id = sensor_id
        self.part_number = part_number
        self.name = name
        self.description = description
        self.sensor_type = sensor_type
        self.version = version
        self.default_config = default_config
        self.system = system


class Sensor__Required(Sensor):
    pass


class Property(ObjectBase):
    FIELDS = ["name", "value", "type", ]
    TYPES = {"name": "String__Required", "value": "String", "type": "PropertyType__Required"}

    def __init__(self, name: 'String__Required'=None, value: 'String'=None, type: 'PropertyType__Required'=None):
        self.name = name
        self.value = value
        self.type = type


class Property__Required(Property):
    pass


class DeviceConfiguration(ObjectBase):
    FIELDS = ["device_configuration_id", "device", "start", "end", "properties", "system", ]
    TYPES = {"device_configuration_id": "ID__Required", "device": "Device__Required", "start": "DateTime__Required", "end": "DateTime", "properties": "List[Property__Required]", "system": "System__Required"}

    def __init__(self, device_configuration_id: 'ID__Required'=None, device: 'Device__Required'=None, start: 'DateTime__Required'=None, end: 'DateTime'=None, properties: 'List[Property__Required]'=None, system: 'System__Required'=None):
        self.device_configuration_id = device_configuration_id
        self.device = device
        self.start = start
        self.end = end
        self.properties = properties
        self.system = system


class DeviceConfiguration__Required(DeviceConfiguration):
    pass


class PageInfo(ObjectBase):
    FIELDS = ["total", "count", "max", "cursor", "sort", ]
    TYPES = {"total": "Int", "count": "Int", "max": "Int", "cursor": "String", "sort": "List[Sort__Required]"}

    def __init__(self, total: 'Int'=None, count: 'Int'=None, max: 'Int'=None, cursor: 'String'=None, sort: 'List[Sort__Required]'=None):
        self.total = total
        self.count = count
        self.max = max
        self.cursor = cursor
        self.sort = sort


class PageInfo__Required(PageInfo):
    pass


class Sort(ObjectBase):
    FIELDS = ["field", "direction", ]
    TYPES = {"field": "String__Required", "direction": "SortDirection__Required"}

    def __init__(self, field: 'String__Required'=None, direction: 'SortDirection__Required'=None):
        self.field = field
        self.direction = direction


class Sort__Required(Sort):
    pass


class SensorList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[Sensor__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[Sensor__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class SensorList__Required(SensorList):
    pass


class SensorInstallationList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[SensorInstallation__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[SensorInstallation__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class SensorInstallationList__Required(SensorInstallationList):
    pass


class EnvironmentList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[Environment__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[Environment__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class EnvironmentList__Required(EnvironmentList):
    pass


class Environment(ObjectBase):
    FIELDS = ["environment_id", "name", "description", "location", "assignments", "layouts", "system", ]
    TYPES = {"environment_id": "ID__Required", "name": "String__Required", "description": "String", "location": "String", "assignments": "List[Assignment__Required]", "layouts": "List[Layout__Required]", "system": "System__Required"}

    def __init__(self, environment_id: 'ID__Required'=None, name: 'String__Required'=None, description: 'String'=None, location: 'String'=None, assignments: 'List[Assignment__Required]'=None, layouts: 'List[Layout__Required]'=None, system: 'System__Required'=None):
        self.environment_id = environment_id
        self.name = name
        self.description = description
        self.location = location
        self.assignments = assignments
        self.layouts = layouts
        self.system = system


class Environment__Required(Environment):
    pass


class Assignment(ObjectBase):
    FIELDS = ["assignment_id", "environment", "assigned", "assigned_type", "start", "end", "data", "system", ]
    TYPES = {"assignment_id": "ID__Required", "environment": "Environment__Required", "assigned": "Assignable__Required", "assigned_type": "AssignableTypeEnum__Required", "start": "DateTime__Required", "end": "DateTime", "data": "List[Datapoint__Required]", "system": "System__Required"}

    def __init__(self, assignment_id: 'ID__Required'=None, environment: 'Environment__Required'=None, assigned: 'Assignable__Required'=None, assigned_type: 'AssignableTypeEnum__Required'=None, start: 'DateTime__Required'=None, end: 'DateTime'=None, data: 'List[Datapoint__Required]'=None, system: 'System__Required'=None):
        self.assignment_id = assignment_id
        self.environment = environment
        self.assigned = assigned
        self.assigned_type = assigned_type
        self.start = start
        self.end = end
        self.data = data
        self.system = system


class Assignment__Required(Assignment):
    pass


class Person(ObjectBase):
    FIELDS = ["person_id", "name", ]
    TYPES = {"person_id": "ID__Required", "name": "String__Required"}

    def __init__(self, person_id: 'ID__Required'=None, name: 'String__Required'=None):
        self.person_id = person_id
        self.name = name


class Person__Required(Person):
    pass


class Datapoint(ObjectBase):
    FIELDS = ["data_id", "parents", "format", "file", "timestamp", "associations", "duration", "source", "system", ]
    TYPES = {"data_id": "ID__Required", "parents": "List[Datapoint]", "format": "String", "file": "S3File", "timestamp": "DateTime__Required", "associations": "List[Association__Required]", "duration": "Int", "source": "DataSource__Required", "system": "System__Required"}

    def __init__(self, data_id: 'ID__Required'=None, parents: 'List[Datapoint]'=None, format: 'String'=None, file: 'S3File'=None, timestamp: 'DateTime__Required'=None, associations: 'List[Association__Required]'=None, duration: 'Int'=None, source: 'DataSource__Required'=None, system: 'System__Required'=None):
        self.data_id = data_id
        self.parents = parents
        self.format = format
        self.file = file
        self.timestamp = timestamp
        self.associations = associations
        self.duration = duration
        self.source = source
        self.system = system


class Datapoint__Required(Datapoint):
    pass


class S3File(ObjectBase):
    FIELDS = ["name", "bucketName", "key", "data", "filename", "mime", "encoding", "contentType", "size", "created", ]
    TYPES = {"name": "String", "bucketName": "String__Required", "key": "String__Required", "data": "String__Required", "filename": "String", "mime": "String", "encoding": "String", "contentType": "String__Required", "size": "Int", "created": "String__Required"}

    def __init__(self, name: 'String'=None, bucketName: 'String__Required'=None, key: 'String__Required'=None, data: 'String__Required'=None, filename: 'String'=None, mime: 'String'=None, encoding: 'String'=None, contentType: 'String__Required'=None, size: 'Int'=None, created: 'String__Required'=None):
        self.name = name
        self.bucketName = bucketName
        self.key = key
        self.data = data
        self.filename = filename
        self.mime = mime
        self.encoding = encoding
        self.contentType = contentType
        self.size = size
        self.created = created


class S3File__Required(S3File):
    pass


class Material(ObjectBase):
    FIELDS = ["material_id", "name", "description", "system", ]
    TYPES = {"material_id": "ID__Required", "name": "String__Required", "description": "String", "system": "System__Required"}

    def __init__(self, material_id: 'ID__Required'=None, name: 'String__Required'=None, description: 'String'=None, system: 'System__Required'=None):
        self.material_id = material_id
        self.name = name
        self.description = description
        self.system = system


class Material__Required(Material):
    pass


class DataSource(ObjectBase):
    FIELDS = ["type", "source", ]
    TYPES = {"type": "DataSourceType__Required", "source": "SourceObject"}

    def __init__(self, type: 'DataSourceType__Required'=None, source: 'SourceObject'=None):
        self.type = type
        self.source = source


class DataSource__Required(DataSource):
    pass


class InferenceExecution(ObjectBase):
    FIELDS = ["inference_id", "name", "notes", "model", "version", "data_sources", "data_results", "execution_start", "system", ]
    TYPES = {"inference_id": "ID__Required", "name": "String", "notes": "String", "model": "String", "version": "String", "data_sources": "List[Datapoint__Required]", "data_results": "List[Datapoint__Required]", "execution_start": "DateTime__Required", "system": "System__Required"}

    def __init__(self, inference_id: 'ID__Required'=None, name: 'String'=None, notes: 'String'=None, model: 'String'=None, version: 'String'=None, data_sources: 'List[Datapoint__Required]'=None, data_results: 'List[Datapoint__Required]'=None, execution_start: 'DateTime__Required'=None, system: 'System__Required'=None):
        self.inference_id = inference_id
        self.name = name
        self.notes = notes
        self.model = model
        self.version = version
        self.data_sources = data_sources
        self.data_results = data_results
        self.execution_start = execution_start
        self.system = system


class InferenceExecution__Required(InferenceExecution):
    pass


class Layout(ObjectBase):
    FIELDS = ["layout_id", "environment", "spaces", "objects", "start", "end", "system", ]
    TYPES = {"layout_id": "ID__Required", "environment": "Environment__Required", "spaces": "List[Rect__Required]", "objects": "List[Rect__Required]", "start": "DateTime", "end": "DateTime", "system": "System__Required"}

    def __init__(self, layout_id: 'ID__Required'=None, environment: 'Environment__Required'=None, spaces: 'List[Rect__Required]'=None, objects: 'List[Rect__Required]'=None, start: 'DateTime'=None, end: 'DateTime'=None, system: 'System__Required'=None):
        self.layout_id = layout_id
        self.environment = environment
        self.spaces = spaces
        self.objects = objects
        self.start = start
        self.end = end
        self.system = system


class Layout__Required(Layout):
    pass


class Rect(ObjectBase):
    FIELDS = ["name", "x", "y", "width", "height", ]
    TYPES = {"name": "String", "x": "Int__Required", "y": "Int__Required", "width": "Int__Required", "height": "Int__Required"}

    def __init__(self, name: 'String'=None, x: 'Int__Required'=None, y: 'Int__Required'=None, width: 'Int__Required'=None, height: 'Int__Required'=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Rect__Required(Rect):
    pass


class DatapointList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[Datapoint__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[Datapoint__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class DatapointList__Required(DatapointList):
    pass


class InferenceExecutionList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[InferenceExecution__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[InferenceExecution__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class InferenceExecutionList__Required(InferenceExecutionList):
    pass


class MaterialList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[Material__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[Material__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class MaterialList__Required(MaterialList):
    pass


class MaterialInteraction(ObjectBase):
    FIELDS = ["material_interaction_id", "source", "subject", "objects", "start", "duration", "concentration", "engagementType", "validations", "system", ]
    TYPES = {"material_interaction_id": "ID__Required", "source": "SourceType__Required", "subject": "Person__Required", "objects": "Material", "start": "DateTime__Required", "duration": "Int", "concentration": "ConcentrationInformation__Required", "engagementType": "EngagementType", "validations": "List[InteractionValidation__Required]", "system": "System__Required"}

    def __init__(self, material_interaction_id: 'ID__Required'=None, source: 'SourceType__Required'=None, subject: 'Person__Required'=None, objects: 'Material'=None, start: 'DateTime__Required'=None, duration: 'Int'=None, concentration: 'ConcentrationInformation__Required'=None, engagementType: 'EngagementType'=None, validations: 'List[InteractionValidation__Required]'=None, system: 'System__Required'=None):
        self.material_interaction_id = material_interaction_id
        self.source = source
        self.subject = subject
        self.objects = objects
        self.start = start
        self.duration = duration
        self.concentration = concentration
        self.engagementType = engagementType
        self.validations = validations
        self.system = system


class MaterialInteraction__Required(MaterialInteraction):
    pass


class ConcentrationInformation(ObjectBase):
    FIELDS = ["concentration_id", "overall", "orientedTowards", "lookingAt", "touching", "distacted", "intentionalActions", "carefulActions", ]
    TYPES = {"concentration_id": "ID__Required", "overall": "ConcentrationLevel__Required", "orientedTowards": "Level", "lookingAt": "Level", "touching": "Level", "distacted": "Level", "intentionalActions": "Level", "carefulActions": "Level"}

    def __init__(self, concentration_id: 'ID__Required'=None, overall: 'ConcentrationLevel__Required'=None, orientedTowards: 'Level'=None, lookingAt: 'Level'=None, touching: 'Level'=None, distacted: 'Level'=None, intentionalActions: 'Level'=None, carefulActions: 'Level'=None):
        self.concentration_id = concentration_id
        self.overall = overall
        self.orientedTowards = orientedTowards
        self.lookingAt = lookingAt
        self.touching = touching
        self.distacted = distacted
        self.intentionalActions = intentionalActions
        self.carefulActions = carefulActions


class ConcentrationInformation__Required(ConcentrationInformation):
    pass


class InteractionValidation(ObjectBase):
    FIELDS = ["interaciton_validation_id", "interaciton", "validator", "validatedAt", "qualityOfInteraction", "system", ]
    TYPES = {"interaciton_validation_id": "ID__Required", "interaciton": "Interaction__Required", "validator": "Person__Required", "validatedAt": "DateTime__Required", "qualityOfInteraction": "Int__Required", "system": "System__Required"}

    def __init__(self, interaciton_validation_id: 'ID__Required'=None, interaciton: 'Interaction__Required'=None, validator: 'Person__Required'=None, validatedAt: 'DateTime__Required'=None, qualityOfInteraction: 'Int__Required'=None, system: 'System__Required'=None):
        self.interaciton_validation_id = interaciton_validation_id
        self.interaciton = interaciton
        self.validator = validator
        self.validatedAt = validatedAt
        self.qualityOfInteraction = qualityOfInteraction
        self.system = system


class InteractionValidation__Required(InteractionValidation):
    pass


class SocialInteraction(ObjectBase):
    FIELDS = ["social_interaction_id", "source", "subjects", "validations", "system", ]
    TYPES = {"social_interaction_id": "ID__Required", "source": "SourceType__Required", "subjects": "List[Person__Required]", "validations": "List[InteractionValidation__Required]", "system": "System__Required"}

    def __init__(self, social_interaction_id: 'ID__Required'=None, source: 'SourceType__Required'=None, subjects: 'List[Person__Required]'=None, validations: 'List[InteractionValidation__Required]'=None, system: 'System__Required'=None):
        self.social_interaction_id = social_interaction_id
        self.source = source
        self.subjects = subjects
        self.validations = validations
        self.system = system


class SocialInteraction__Required(SocialInteraction):
    pass


class MaterialInteractionList(ObjectBase):
    FIELDS = ["data", "page_info", ]
    TYPES = {"data": "List[MaterialInteraction__Required]", "page_info": "PageInfo__Required"}

    def __init__(self, data: 'List[MaterialInteraction__Required]'=None, page_info: 'PageInfo__Required'=None):
        self.data = data
        self.page_info = page_info


class MaterialInteractionList__Required(MaterialInteractionList):
    pass


class DeleteStatusResponse(ObjectBase):
    FIELDS = ["status", "error", ]
    TYPES = {"status": "Status__Required", "error": "String"}

    def __init__(self, status: 'Status__Required'=None, error: 'String'=None):
        self.status = status
        self.error = error


class DeleteStatusResponse__Required(DeleteStatusResponse):
    pass


class System(ObjectBase):
    FIELDS = ["type_name", "created", "last_modified", ]
    TYPES = {"type_name": "String__Required", "created": "DateTime__Required", "last_modified": "DateTime"}

    def __init__(self, type_name: 'String__Required'=None, created: 'DateTime__Required'=None, last_modified: 'DateTime'=None):
        self.type_name = type_name
        self.created = created
        self.last_modified = last_modified


class System__Required(System):
    pass


class CoordinateSpace(ObjectBase):
    FIELDS = ["space_id", "name", "environment", "start", "end", "system", ]
    TYPES = {"space_id": "ID__Required", "name": "String__Required", "environment": "Environment__Required", "start": "DateTime__Required", "end": "DateTime", "system": "System__Required"}

    def __init__(self, space_id: 'ID__Required'=None, name: 'String__Required'=None, environment: 'Environment__Required'=None, start: 'DateTime__Required'=None, end: 'DateTime'=None, system: 'System__Required'=None):
        self.space_id = space_id
        self.name = name
        self.environment = environment
        self.start = start
        self.end = end
        self.system = system


class CoordinateSpace__Required(CoordinateSpace):
    pass


class Vector(ObjectBase):
    FIELDS = ["x", "y", "z", ]
    TYPES = {"x": "Float__Required", "y": "Float__Required", "z": "Float__Required"}

    def __init__(self, x: 'Float__Required'=None, y: 'Float__Required'=None, z: 'Float__Required'=None):
        self.x = x
        self.y = y
        self.z = z


class Vector__Required(Vector):
    pass


class Point(ObjectBase):
    FIELDS = ["x", "y", "z", ]
    TYPES = {"x": "Float__Required", "y": "Float__Required", "z": "Float__Required"}

    def __init__(self, x: 'Float__Required'=None, y: 'Float__Required'=None, z: 'Float__Required'=None):
        self.x = x
        self.y = y
        self.z = z


class Point__Required(Point):
    pass


class Pair(ObjectBase):
    FIELDS = ["x", "y", ]
    TYPES = {"x": "Float__Required", "y": "Float__Required"}

    def __init__(self, x: 'Float__Required'=None, y: 'Float__Required'=None):
        self.x = x
        self.y = y


class Pair__Required(Pair):
    pass


class CameraParameters(ObjectBase):
    FIELDS = ["camera_matrix", "distortion_coeffs", ]
    TYPES = {"camera_matrix": "List[Float__Required]", "distortion_coeffs": "List[Float__Required]"}

    def __init__(self, camera_matrix: 'List[Float__Required]'=None, distortion_coeffs: 'List[Float__Required]'=None):
        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs


class CameraParameters__Required(CameraParameters):
    pass


class ExtrinsicCalibration(ObjectBase):
    FIELDS = ["start", "end", "translation", "rotation", "objects", ]
    TYPES = {"start": "DateTime__Required", "end": "DateTime", "translation": "Tuple__Required", "rotation": "Tuple__Required", "objects": "List[GeometricObject__Required]"}

    def __init__(self, start: 'DateTime__Required'=None, end: 'DateTime'=None, translation: 'Tuple__Required'=None, rotation: 'Tuple__Required'=None, objects: 'List[GeometricObject__Required]'=None):
        self.start = start
        self.end = end
        self.translation = translation
        self.rotation = rotation
        self.objects = objects


class ExtrinsicCalibration__Required(ExtrinsicCalibration):
    pass


class PaginationInput(ObjectBase):
    FIELDS = ["max", "cursor", "sort", ]
    TYPES = {"max": "Int", "cursor": "String", "sort": "List[SortInput__Required]"}

    def __init__(self, max: 'Int'=None, cursor: 'String'=None, sort: 'List[SortInput__Required]'=None):
        self.max = max
        self.cursor = cursor
        self.sort = sort


class PaginationInput__Required(PaginationInput):
    pass


class SortInput(ObjectBase):
    FIELDS = ["field", "direction", ]
    TYPES = {"field": "String__Required", "direction": "SortDirection"}

    def __init__(self, field: 'String__Required'=None, direction: 'SortDirection'=None):
        self.field = field
        self.direction = direction


class SortInput__Required(SortInput):
    pass


class QueryExpression(ObjectBase):
    FIELDS = ["field", "operator", "value", "children", ]
    TYPES = {"field": "String", "operator": "Operator__Required", "value": "String", "children": "List[QueryExpression__Required]"}

    def __init__(self, field: 'String'=None, operator: 'Operator__Required'=None, value: 'String'=None, children: 'List[QueryExpression__Required]'=None):
        self.field = field
        self.operator = operator
        self.value = value
        self.children = children


class QueryExpression__Required(QueryExpression):
    pass


class DeviceInput(ObjectBase):
    FIELDS = ["name", "description", "part_number", "tag_id", "serial_number", "mac_address", ]
    TYPES = {"name": "String", "description": "String", "part_number": "String", "tag_id": "String", "serial_number": "String", "mac_address": "List[String__Required]"}

    def __init__(self, name: 'String'=None, description: 'String'=None, part_number: 'String'=None, tag_id: 'String'=None, serial_number: 'String'=None, mac_address: 'List[String__Required]'=None):
        self.name = name
        self.description = description
        self.part_number = part_number
        self.tag_id = tag_id
        self.serial_number = serial_number
        self.mac_address = mac_address


class DeviceInput__Required(DeviceInput):
    pass


class DeviceConfigurationInput(ObjectBase):
    FIELDS = ["device", "start", "end", "properties", ]
    TYPES = {"device": "ID__Required", "start": "DateTime__Required", "end": "DateTime", "properties": "List[PropertyInput__Required]"}

    def __init__(self, device: 'ID__Required'=None, start: 'DateTime__Required'=None, end: 'DateTime'=None, properties: 'List[PropertyInput__Required]'=None):
        self.device = device
        self.start = start
        self.end = end
        self.properties = properties


class DeviceConfigurationInput__Required(DeviceConfigurationInput):
    pass


class PropertyInput(ObjectBase):
    FIELDS = ["name", "value", "type", ]
    TYPES = {"name": "String__Required", "value": "String", "type": "PropertyType__Required"}

    def __init__(self, name: 'String__Required'=None, value: 'String'=None, type: 'PropertyType__Required'=None):
        self.name = name
        self.value = value
        self.type = type


class PropertyInput__Required(PropertyInput):
    pass


class SensorInput(ObjectBase):
    FIELDS = ["part_number", "name", "description", "sensor_type", "version", "default_config", ]
    TYPES = {"part_number": "String", "name": "String__Required", "description": "String", "sensor_type": "SensorType__Required", "version": "Int__Required", "default_config": "List[PropertyInput__Required]"}

    def __init__(self, part_number: 'String'=None, name: 'String__Required'=None, description: 'String'=None, sensor_type: 'SensorType__Required'=None, version: 'Int__Required'=None, default_config: 'List[PropertyInput__Required]'=None):
        self.part_number = part_number
        self.name = name
        self.description = description
        self.sensor_type = sensor_type
        self.version = version
        self.default_config = default_config


class SensorInput__Required(SensorInput):
    pass


class SensorInstallationInput(ObjectBase):
    FIELDS = ["device", "sensor", "description", "start", "end", "tag_id", "config", ]
    TYPES = {"device": "ID__Required", "sensor": "ID__Required", "description": "String", "start": "DateTime", "end": "DateTime", "tag_id": "String", "config": "List[PropertyInput__Required]"}

    def __init__(self, device: 'ID__Required'=None, sensor: 'ID__Required'=None, description: 'String'=None, start: 'DateTime'=None, end: 'DateTime'=None, tag_id: 'String'=None, config: 'List[PropertyInput__Required]'=None):
        self.device = device
        self.sensor = sensor
        self.description = description
        self.start = start
        self.end = end
        self.tag_id = tag_id
        self.config = config


class SensorInstallationInput__Required(SensorInstallationInput):
    pass


class SensorInstallationUpdateInput(ObjectBase):
    FIELDS = ["description", "start", "end", "tag_id", "config", ]
    TYPES = {"description": "String", "start": "DateTime", "end": "DateTime", "tag_id": "String", "config": "List[PropertyInput__Required]"}

    def __init__(self, description: 'String'=None, start: 'DateTime'=None, end: 'DateTime'=None, tag_id: 'String'=None, config: 'List[PropertyInput__Required]'=None):
        self.description = description
        self.start = start
        self.end = end
        self.tag_id = tag_id
        self.config = config


class SensorInstallationUpdateInput__Required(SensorInstallationUpdateInput):
    pass


class EnvironmentInput(ObjectBase):
    FIELDS = ["name", "description", "location", ]
    TYPES = {"name": "String__Required", "description": "String", "location": "String"}

    def __init__(self, name: 'String__Required'=None, description: 'String'=None, location: 'String'=None):
        self.name = name
        self.description = description
        self.location = location


class EnvironmentInput__Required(EnvironmentInput):
    pass


class AssignmentInput(ObjectBase):
    FIELDS = ["environment", "assigned_type", "assigned", "start", "end", ]
    TYPES = {"environment": "ID__Required", "assigned_type": "AssignableTypeEnum__Required", "assigned": "ID__Required", "start": "DateTime", "end": "DateTime"}

    def __init__(self, environment: 'ID__Required'=None, assigned_type: 'AssignableTypeEnum__Required'=None, assigned: 'ID__Required'=None, start: 'DateTime'=None, end: 'DateTime'=None):
        self.environment = environment
        self.assigned_type = assigned_type
        self.assigned = assigned
        self.start = start
        self.end = end


class AssignmentInput__Required(AssignmentInput):
    pass


class AssignmentUpdateInput(ObjectBase):
    FIELDS = ["end", ]
    TYPES = {"end": "DateTime"}

    def __init__(self, end: 'DateTime'=None):
        self.end = end


class AssignmentUpdateInput__Required(AssignmentUpdateInput):
    pass


class LayoutInput(ObjectBase):
    FIELDS = ["environment", "spaces", "objects", "start", "end", ]
    TYPES = {"environment": "ID__Required", "spaces": "List[RectInput__Required]", "objects": "List[RectInput__Required]", "start": "DateTime", "end": "DateTime"}

    def __init__(self, environment: 'ID__Required'=None, spaces: 'List[RectInput__Required]'=None, objects: 'List[RectInput__Required]'=None, start: 'DateTime'=None, end: 'DateTime'=None):
        self.environment = environment
        self.spaces = spaces
        self.objects = objects
        self.start = start
        self.end = end


class LayoutInput__Required(LayoutInput):
    pass


class RectInput(ObjectBase):
    FIELDS = ["name", "x", "y", "width", "height", ]
    TYPES = {"name": "String", "x": "Int__Required", "y": "Int__Required", "width": "Int__Required", "height": "Int__Required"}

    def __init__(self, name: 'String'=None, x: 'Int__Required'=None, y: 'Int__Required'=None, width: 'Int__Required'=None, height: 'Int__Required'=None):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class RectInput__Required(RectInput):
    pass


class DatapointInput(ObjectBase):
    FIELDS = ["format", "file", "timestamp", "associations", "parents", "duration", "source", ]
    TYPES = {"format": "String", "file": "S3FileInput", "timestamp": "DateTime__Required", "associations": "List[ID__Required]", "parents": "List[ID__Required]", "duration": "Int", "source": "DataSourceInput"}

    def __init__(self, format: 'String'=None, file: 'S3FileInput'=None, timestamp: 'DateTime__Required'=None, associations: 'List[ID__Required]'=None, parents: 'List[ID__Required]'=None, duration: 'Int'=None, source: 'DataSourceInput'=None):
        self.format = format
        self.file = file
        self.timestamp = timestamp
        self.associations = associations
        self.parents = parents
        self.duration = duration
        self.source = source


class DatapointInput__Required(DatapointInput):
    pass


class S3FileInput(ObjectBase):
    FIELDS = ["name", "contentType", "data", ]
    TYPES = {"name": "String", "contentType": "String", "data": "Upload__Required"}

    def __init__(self, name: 'String'=None, contentType: 'String'=None, data: 'Upload__Required'=None):
        self.name = name
        self.contentType = contentType
        self.data = data


class S3FileInput__Required(S3FileInput):
    pass


class DataSourceInput(ObjectBase):
    FIELDS = ["type", "source", ]
    TYPES = {"type": "DataSourceType__Required", "source": "ID"}

    def __init__(self, type: 'DataSourceType__Required'=None, source: 'ID'=None):
        self.type = type
        self.source = source


class DataSourceInput__Required(DataSourceInput):
    pass


class InferenceExecutionInput(ObjectBase):
    FIELDS = ["name", "notes", "model", "version", "data_sources", "data_results", "execution_start", ]
    TYPES = {"name": "String", "notes": "String", "model": "String", "version": "String", "data_sources": "List[ID__Required]", "data_results": "List[ID__Required]", "execution_start": "DateTime__Required"}

    def __init__(self, name: 'String'=None, notes: 'String'=None, model: 'String'=None, version: 'String'=None, data_sources: 'List[ID__Required]'=None, data_results: 'List[ID__Required]'=None, execution_start: 'DateTime__Required'=None):
        self.name = name
        self.notes = notes
        self.model = model
        self.version = version
        self.data_sources = data_sources
        self.data_results = data_results
        self.execution_start = execution_start


class InferenceExecutionInput__Required(InferenceExecutionInput):
    pass


class MaterialInput(ObjectBase):
    FIELDS = ["name", "description", ]
    TYPES = {"name": "String", "description": "String"}

    def __init__(self, name: 'String'=None, description: 'String'=None):
        self.name = name
        self.description = description


class MaterialInput__Required(MaterialInput):
    pass


class MaterialInteractionInput(ObjectBase):
    FIELDS = ["source", "subject", "objects", "start", "duration", "concentration", "engagementType", ]
    TYPES = {"source": "SourceType__Required", "subject": "ID__Required", "objects": "ID__Required", "start": "DateTime__Required", "duration": "Int", "concentration": "ConcentrationInformationInput__Required", "engagementType": "EngagementType"}

    def __init__(self, source: 'SourceType__Required'=None, subject: 'ID__Required'=None, objects: 'ID__Required'=None, start: 'DateTime__Required'=None, duration: 'Int'=None, concentration: 'ConcentrationInformationInput__Required'=None, engagementType: 'EngagementType'=None):
        self.source = source
        self.subject = subject
        self.objects = objects
        self.start = start
        self.duration = duration
        self.concentration = concentration
        self.engagementType = engagementType


class MaterialInteractionInput__Required(MaterialInteractionInput):
    pass


class ConcentrationInformationInput(ObjectBase):
    FIELDS = ["overall", "orientedTowards", "lookingAt", "touching", "distacted", "intentionalActions", "carefulActions", ]
    TYPES = {"overall": "ConcentrationLevel__Required", "orientedTowards": "Level", "lookingAt": "Level", "touching": "Level", "distacted": "Level", "intentionalActions": "Level", "carefulActions": "Level"}

    def __init__(self, overall: 'ConcentrationLevel__Required'=None, orientedTowards: 'Level'=None, lookingAt: 'Level'=None, touching: 'Level'=None, distacted: 'Level'=None, intentionalActions: 'Level'=None, carefulActions: 'Level'=None):
        self.overall = overall
        self.orientedTowards = orientedTowards
        self.lookingAt = lookingAt
        self.touching = touching
        self.distacted = distacted
        self.intentionalActions = intentionalActions
        self.carefulActions = carefulActions


class ConcentrationInformationInput__Required(ConcentrationInformationInput):
    pass


class CascadeLink(ObjectBase):
    FIELDS = ["target_type_name", "target_field_name", "isS3File", ]
    TYPES = {"target_type_name": "String__Required", "target_field_name": "String__Required", "isS3File": "Boolean"}

    def __init__(self, target_type_name: 'String__Required'=None, target_field_name: 'String__Required'=None, isS3File: 'Boolean'=None):
        self.target_type_name = target_type_name
        self.target_field_name = target_field_name
        self.isS3File = isS3File


class CascadeLink__Required(CascadeLink):
    pass


class CoordinateSpaceInput(ObjectBase):
    FIELDS = ["name", "start", "end", ]
    TYPES = {"name": "String__Required", "start": "DateTime", "end": "DateTime"}

    def __init__(self, name: 'String__Required'=None, start: 'DateTime'=None, end: 'DateTime'=None):
        self.name = name
        self.start = start
        self.end = end


class CoordinateSpaceInput__Required(CoordinateSpaceInput):
    pass


class TupleInput(ObjectBase):
    FIELDS = ["x", "y", "z", ]
    TYPES = {"x": "Float__Required", "y": "Float__Required", "z": "Float__Required"}

    def __init__(self, x: 'Float__Required'=None, y: 'Float__Required'=None, z: 'Float__Required'=None):
        self.x = x
        self.y = y
        self.z = z


class TupleInput__Required(TupleInput):
    pass


class CalibrationInput(ObjectBase):
    FIELDS = ["translation", "rotation", ]
    TYPES = {"translation": "TupleInput__Required", "rotation": "TupleInput__Required"}

    def __init__(self, translation: 'TupleInput__Required'=None, rotation: 'TupleInput__Required'=None):
        self.translation = translation
        self.rotation = rotation


class CalibrationInput__Required(CalibrationInput):
    pass


class PersonInput(ObjectBase):
    FIELDS = ["name", ]
    TYPES = {"name": "String__Required"}

    def __init__(self, name: 'String__Required'=None):
        self.name = name


class PersonInput__Required(PersonInput):
    pass


Assignable = Union[Device, Person]
Assignable__Required = Union[Device, Person]
Association = Union[Device, Environment, Person, Material]
Association__Required = Union[Device, Environment, Person, Material]
SourceObject = Union[Assignment, InferenceExecution, Person]
SourceObject__Required = Union[Assignment, InferenceExecution, Person]
Interaction = Union[MaterialInteraction, SocialInteraction]
Interaction__Required = Union[MaterialInteraction, SocialInteraction]
GeometricObject = Union[SensorInstallation, CoordinateSpace]
GeometricObject__Required = Union[SensorInstallation, CoordinateSpace]


class Query(QueryBase):

    def devices(self, envId: 'String'=None, page: 'PaginationInput'=None) -> DeviceList__Required:
        args = ["envId: 'String'=None", "page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if envId is not None:
            var_types["envId"] = String
            if hasattr(envId, "to_json"):
                variables["envId"] = envId.to_json()
            else:
                variables["envId"] = envId

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(DeviceList__Required, "devices", variables, var_types)
        results = self.query(query, variables)
        return DeviceList__Required.from_json(results.get("devices"))

    def device(self, device_id: 'ID'=None) -> Device:
        args = ["device_id: 'ID'=None"]
        variables = dict()
        var_types = dict()

        if device_id is not None:
            var_types["device_id"] = ID
            if hasattr(device_id, "to_json"):
                variables["device_id"] = device_id.to_json()
            else:
                variables["device_id"] = device_id

        query = self.prepare(Device, "device", variables, var_types)
        results = self.query(query, variables)
        return Device.from_json(results.get("device"))

    def findDevice(self, name: 'String'=None, part_number: 'String'=None) -> DeviceList__Required:
        args = ["name: 'String'=None", "part_number: 'String'=None"]
        variables = dict()
        var_types = dict()

        if name is not None:
            var_types["name"] = String
            if hasattr(name, "to_json"):
                variables["name"] = name.to_json()
            else:
                variables["name"] = name

        if part_number is not None:
            var_types["part_number"] = String
            if hasattr(part_number, "to_json"):
                variables["part_number"] = part_number.to_json()
            else:
                variables["part_number"] = part_number

        query = self.prepare(DeviceList__Required, "findDevice", variables, var_types)
        results = self.query(query, variables)
        return DeviceList__Required.from_json(results.get("findDevice"))

    def sensors(self, page: 'PaginationInput'=None) -> SensorList__Required:
        args = ["page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(SensorList__Required, "sensors", variables, var_types)
        results = self.query(query, variables)
        return SensorList__Required.from_json(results.get("sensors"))

    def sensor(self, sensor_id: 'ID'=None) -> Sensor:
        args = ["sensor_id: 'ID'=None"]
        variables = dict()
        var_types = dict()

        if sensor_id is not None:
            var_types["sensor_id"] = ID
            if hasattr(sensor_id, "to_json"):
                variables["sensor_id"] = sensor_id.to_json()
            else:
                variables["sensor_id"] = sensor_id

        query = self.prepare(Sensor, "sensor", variables, var_types)
        results = self.query(query, variables)
        return Sensor.from_json(results.get("sensor"))

    def findSensor(self, name: 'String'=None, version: 'Int'=None) -> SensorList__Required:
        args = ["name: 'String'=None", "version: 'Int'=None"]
        variables = dict()
        var_types = dict()

        if name is not None:
            var_types["name"] = String
            if hasattr(name, "to_json"):
                variables["name"] = name.to_json()
            else:
                variables["name"] = name

        if version is not None:
            var_types["version"] = Int
            if hasattr(version, "to_json"):
                variables["version"] = version.to_json()
            else:
                variables["version"] = version

        query = self.prepare(SensorList__Required, "findSensor", variables, var_types)
        results = self.query(query, variables)
        return SensorList__Required.from_json(results.get("findSensor"))

    def sensorInstallations(self, page: 'PaginationInput'=None) -> SensorInstallationList__Required:
        args = ["page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(SensorInstallationList__Required, "sensorInstallations", variables, var_types)
        results = self.query(query, variables)
        return SensorInstallationList__Required.from_json(results.get("sensorInstallations"))

    def environments(self, page: 'PaginationInput'=None) -> EnvironmentList:
        args = ["page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(EnvironmentList, "environments", variables, var_types)
        results = self.query(query, variables)
        return EnvironmentList.from_json(results.get("environments"))

    def getEnvironment(self, environment_id: 'ID__Required'=None) -> Environment:
        args = ["environment_id: 'ID__Required'=None"]
        variables = dict()
        var_types = dict()

        if environment_id is not None:
            var_types["environment_id"] = ID__Required
            if hasattr(environment_id, "to_json"):
                variables["environment_id"] = environment_id.to_json()
            else:
                variables["environment_id"] = environment_id

        query = self.prepare(Environment, "getEnvironment", variables, var_types)
        results = self.query(query, variables)
        return Environment.from_json(results.get("getEnvironment"))

    def findEnvironment(self, name: 'String'=None, location: 'String'=None) -> EnvironmentList:
        args = ["name: 'String'=None", "location: 'String'=None"]
        variables = dict()
        var_types = dict()

        if name is not None:
            var_types["name"] = String
            if hasattr(name, "to_json"):
                variables["name"] = name.to_json()
            else:
                variables["name"] = name

        if location is not None:
            var_types["location"] = String
            if hasattr(location, "to_json"):
                variables["location"] = location.to_json()
            else:
                variables["location"] = location

        query = self.prepare(EnvironmentList, "findEnvironment", variables, var_types)
        results = self.query(query, variables)
        return EnvironmentList.from_json(results.get("findEnvironment"))

    def datapoints(self, page: 'PaginationInput'=None) -> DatapointList__Required:
        args = ["page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(DatapointList__Required, "datapoints", variables, var_types)
        results = self.query(query, variables)
        return DatapointList__Required.from_json(results.get("datapoints"))

    def getDatapoint(self, data_id: 'ID__Required'=None) -> Datapoint__Required:
        args = ["data_id: 'ID__Required'=None"]
        variables = dict()
        var_types = dict()

        if data_id is not None:
            var_types["data_id"] = ID__Required
            if hasattr(data_id, "to_json"):
                variables["data_id"] = data_id.to_json()
            else:
                variables["data_id"] = data_id

        query = self.prepare(Datapoint__Required, "getDatapoint", variables, var_types)
        results = self.query(query, variables)
        return Datapoint__Required.from_json(results.get("getDatapoint"))

    def findDatapoints(self, query: 'QueryExpression__Required'=None, page: 'PaginationInput'=None) -> DatapointList__Required:
        args = ["query: 'QueryExpression__Required'=None", "page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if query is not None:
            var_types["query"] = QueryExpression__Required
            if hasattr(query, "to_json"):
                variables["query"] = query.to_json()
            else:
                variables["query"] = query

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(DatapointList__Required, "findDatapoints", variables, var_types)
        results = self.query(query, variables)
        return DatapointList__Required.from_json(results.get("findDatapoints"))

    def inferences(self, page: 'PaginationInput'=None) -> InferenceExecutionList__Required:
        args = ["page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(InferenceExecutionList__Required, "inferences", variables, var_types)
        results = self.query(query, variables)
        return InferenceExecutionList__Required.from_json(results.get("inferences"))

    def getInferenceExecution(self, inference_id: 'ID__Required'=None) -> InferenceExecution__Required:
        args = ["inference_id: 'ID__Required'=None"]
        variables = dict()
        var_types = dict()

        if inference_id is not None:
            var_types["inference_id"] = ID__Required
            if hasattr(inference_id, "to_json"):
                variables["inference_id"] = inference_id.to_json()
            else:
                variables["inference_id"] = inference_id

        query = self.prepare(InferenceExecution__Required, "getInferenceExecution", variables, var_types)
        results = self.query(query, variables)
        return InferenceExecution__Required.from_json(results.get("getInferenceExecution"))

    def findInferences(self, query: 'QueryExpression__Required'=None, page: 'PaginationInput'=None) -> InferenceExecutionList__Required:
        args = ["query: 'QueryExpression__Required'=None", "page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if query is not None:
            var_types["query"] = QueryExpression__Required
            if hasattr(query, "to_json"):
                variables["query"] = query.to_json()
            else:
                variables["query"] = query

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(InferenceExecutionList__Required, "findInferences", variables, var_types)
        results = self.query(query, variables)
        return InferenceExecutionList__Required.from_json(results.get("findInferences"))

    def material(self, material_id: 'ID__Required'=None) -> Material__Required:
        args = ["material_id: 'ID__Required'=None"]
        variables = dict()
        var_types = dict()

        if material_id is not None:
            var_types["material_id"] = ID__Required
            if hasattr(material_id, "to_json"):
                variables["material_id"] = material_id.to_json()
            else:
                variables["material_id"] = material_id

        query = self.prepare(Material__Required, "material", variables, var_types)
        results = self.query(query, variables)
        return Material__Required.from_json(results.get("material"))

    def materials(self, query: 'QueryExpression__Required'=None, page: 'PaginationInput'=None) -> MaterialList__Required:
        args = ["query: 'QueryExpression__Required'=None", "page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if query is not None:
            var_types["query"] = QueryExpression__Required
            if hasattr(query, "to_json"):
                variables["query"] = query.to_json()
            else:
                variables["query"] = query

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(MaterialList__Required, "materials", variables, var_types)
        results = self.query(query, variables)
        return MaterialList__Required.from_json(results.get("materials"))

    def materialInteraction(self, material_interaction_id: 'ID__Required'=None) -> MaterialInteraction__Required:
        args = ["material_interaction_id: 'ID__Required'=None"]
        variables = dict()
        var_types = dict()

        if material_interaction_id is not None:
            var_types["material_interaction_id"] = ID__Required
            if hasattr(material_interaction_id, "to_json"):
                variables["material_interaction_id"] = material_interaction_id.to_json()
            else:
                variables["material_interaction_id"] = material_interaction_id

        query = self.prepare(MaterialInteraction__Required, "materialInteraction", variables, var_types)
        results = self.query(query, variables)
        return MaterialInteraction__Required.from_json(results.get("materialInteraction"))

    def materialInteractions(self, query: 'QueryExpression__Required'=None, page: 'PaginationInput'=None) -> MaterialInteractionList__Required:
        args = ["query: 'QueryExpression__Required'=None", "page: 'PaginationInput'=None"]
        variables = dict()
        var_types = dict()

        if query is not None:
            var_types["query"] = QueryExpression__Required
            if hasattr(query, "to_json"):
                variables["query"] = query.to_json()
            else:
                variables["query"] = query

        if page is not None:
            var_types["page"] = PaginationInput
            if hasattr(page, "to_json"):
                variables["page"] = page.to_json()
            else:
                variables["page"] = page

        query = self.prepare(MaterialInteractionList__Required, "materialInteractions", variables, var_types)
        results = self.query(query, variables)
        return MaterialInteractionList__Required.from_json(results.get("materialInteractions"))


class Mutation(MutationBase):

    def createDevice(self, device: 'DeviceInput'=None) -> Device:
        args = ["device: 'DeviceInput'=None"]
        variables = dict()
        var_types = dict()

        if device is not None:
            var_types["device"] = DeviceInput
            if hasattr(device, "to_json"):
                variables["device"] = device.to_json()
            else:
                variables["device"] = device

        query = self.prepare(Device, "createDevice", variables, var_types)
        results = self.query(query, variables)
        return Device.from_json(results.get("createDevice"))

    def updateDevice(self, device_id: 'ID__Required'=None, device: 'DeviceInput'=None) -> Device:
        args = ["device_id: 'ID__Required'=None", "device: 'DeviceInput'=None"]
        variables = dict()
        var_types = dict()

        if device_id is not None:
            var_types["device_id"] = ID__Required
            if hasattr(device_id, "to_json"):
                variables["device_id"] = device_id.to_json()
            else:
                variables["device_id"] = device_id

        if device is not None:
            var_types["device"] = DeviceInput
            if hasattr(device, "to_json"):
                variables["device"] = device.to_json()
            else:
                variables["device"] = device

        query = self.prepare(Device, "updateDevice", variables, var_types)
        results = self.query(query, variables)
        return Device.from_json(results.get("updateDevice"))

    def setDeviceConfiguration(self, deviceConfiguration: 'DeviceConfigurationInput'=None) -> DeviceConfiguration:
        args = ["deviceConfiguration: 'DeviceConfigurationInput'=None"]
        variables = dict()
        var_types = dict()

        if deviceConfiguration is not None:
            var_types["deviceConfiguration"] = DeviceConfigurationInput
            if hasattr(deviceConfiguration, "to_json"):
                variables["deviceConfiguration"] = deviceConfiguration.to_json()
            else:
                variables["deviceConfiguration"] = deviceConfiguration

        query = self.prepare(DeviceConfiguration, "setDeviceConfiguration", variables, var_types)
        results = self.query(query, variables)
        return DeviceConfiguration.from_json(results.get("setDeviceConfiguration"))

    def createSensor(self, sensor: 'SensorInput'=None) -> Sensor:
        args = ["sensor: 'SensorInput'=None"]
        variables = dict()
        var_types = dict()

        if sensor is not None:
            var_types["sensor"] = SensorInput
            if hasattr(sensor, "to_json"):
                variables["sensor"] = sensor.to_json()
            else:
                variables["sensor"] = sensor

        query = self.prepare(Sensor, "createSensor", variables, var_types)
        results = self.query(query, variables)
        return Sensor.from_json(results.get("createSensor"))

    def addSensorToDevice(self, sensorInstallation: 'SensorInstallationInput'=None) -> SensorInstallation:
        args = ["sensorInstallation: 'SensorInstallationInput'=None"]
        variables = dict()
        var_types = dict()

        if sensorInstallation is not None:
            var_types["sensorInstallation"] = SensorInstallationInput
            if hasattr(sensorInstallation, "to_json"):
                variables["sensorInstallation"] = sensorInstallation.to_json()
            else:
                variables["sensorInstallation"] = sensorInstallation

        query = self.prepare(SensorInstallation, "addSensorToDevice", variables, var_types)
        results = self.query(query, variables)
        return SensorInstallation.from_json(results.get("addSensorToDevice"))

    def updateSensorInstall(self, sensor_install_id: 'ID'=None, sensorInstallation: 'SensorInstallationUpdateInput'=None) -> SensorInstallation:
        args = ["sensor_install_id: 'ID'=None", "sensorInstallation: 'SensorInstallationUpdateInput'=None"]
        variables = dict()
        var_types = dict()

        if sensor_install_id is not None:
            var_types["sensor_install_id"] = ID
            if hasattr(sensor_install_id, "to_json"):
                variables["sensor_install_id"] = sensor_install_id.to_json()
            else:
                variables["sensor_install_id"] = sensor_install_id

        if sensorInstallation is not None:
            var_types["sensorInstallation"] = SensorInstallationUpdateInput
            if hasattr(sensorInstallation, "to_json"):
                variables["sensorInstallation"] = sensorInstallation.to_json()
            else:
                variables["sensorInstallation"] = sensorInstallation

        query = self.prepare(SensorInstallation, "updateSensorInstall", variables, var_types)
        results = self.query(query, variables)
        return SensorInstallation.from_json(results.get("updateSensorInstall"))

    def createEnvironment(self, environment: 'EnvironmentInput'=None) -> Environment:
        args = ["environment: 'EnvironmentInput'=None"]
        variables = dict()
        var_types = dict()

        if environment is not None:
            var_types["environment"] = EnvironmentInput
            if hasattr(environment, "to_json"):
                variables["environment"] = environment.to_json()
            else:
                variables["environment"] = environment

        query = self.prepare(Environment, "createEnvironment", variables, var_types)
        results = self.query(query, variables)
        return Environment.from_json(results.get("createEnvironment"))

    def updateEnvironment(self, environment_id: 'ID__Required'=None, environment: 'EnvironmentInput'=None) -> Environment:
        args = ["environment_id: 'ID__Required'=None", "environment: 'EnvironmentInput'=None"]
        variables = dict()
        var_types = dict()

        if environment_id is not None:
            var_types["environment_id"] = ID__Required
            if hasattr(environment_id, "to_json"):
                variables["environment_id"] = environment_id.to_json()
            else:
                variables["environment_id"] = environment_id

        if environment is not None:
            var_types["environment"] = EnvironmentInput
            if hasattr(environment, "to_json"):
                variables["environment"] = environment.to_json()
            else:
                variables["environment"] = environment

        query = self.prepare(Environment, "updateEnvironment", variables, var_types)
        results = self.query(query, variables)
        return Environment.from_json(results.get("updateEnvironment"))

    def assignToEnvironment(self, assignment: 'AssignmentInput'=None) -> Assignment:
        args = ["assignment: 'AssignmentInput'=None"]
        variables = dict()
        var_types = dict()

        if assignment is not None:
            var_types["assignment"] = AssignmentInput
            if hasattr(assignment, "to_json"):
                variables["assignment"] = assignment.to_json()
            else:
                variables["assignment"] = assignment

        query = self.prepare(Assignment, "assignToEnvironment", variables, var_types)
        results = self.query(query, variables)
        return Assignment.from_json(results.get("assignToEnvironment"))

    def updateAssignment(self, assignment_id: 'ID__Required'=None, assignment: 'AssignmentUpdateInput'=None) -> Assignment:
        args = ["assignment_id: 'ID__Required'=None", "assignment: 'AssignmentUpdateInput'=None"]
        variables = dict()
        var_types = dict()

        if assignment_id is not None:
            var_types["assignment_id"] = ID__Required
            if hasattr(assignment_id, "to_json"):
                variables["assignment_id"] = assignment_id.to_json()
            else:
                variables["assignment_id"] = assignment_id

        if assignment is not None:
            var_types["assignment"] = AssignmentUpdateInput
            if hasattr(assignment, "to_json"):
                variables["assignment"] = assignment.to_json()
            else:
                variables["assignment"] = assignment

        query = self.prepare(Assignment, "updateAssignment", variables, var_types)
        results = self.query(query, variables)
        return Assignment.from_json(results.get("updateAssignment"))

    def createLayout(self, layout: 'LayoutInput'=None) -> Layout:
        args = ["layout: 'LayoutInput'=None"]
        variables = dict()
        var_types = dict()

        if layout is not None:
            var_types["layout"] = LayoutInput
            if hasattr(layout, "to_json"):
                variables["layout"] = layout.to_json()
            else:
                variables["layout"] = layout

        query = self.prepare(Layout, "createLayout", variables, var_types)
        results = self.query(query, variables)
        return Layout.from_json(results.get("createLayout"))

    def updateLayout(self, layout_id: 'ID__Required'=None, layout: 'AssignmentUpdateInput'=None) -> Layout:
        args = ["layout_id: 'ID__Required'=None", "layout: 'AssignmentUpdateInput'=None"]
        variables = dict()
        var_types = dict()

        if layout_id is not None:
            var_types["layout_id"] = ID__Required
            if hasattr(layout_id, "to_json"):
                variables["layout_id"] = layout_id.to_json()
            else:
                variables["layout_id"] = layout_id

        if layout is not None:
            var_types["layout"] = AssignmentUpdateInput
            if hasattr(layout, "to_json"):
                variables["layout"] = layout.to_json()
            else:
                variables["layout"] = layout

        query = self.prepare(Layout, "updateLayout", variables, var_types)
        results = self.query(query, variables)
        return Layout.from_json(results.get("updateLayout"))

    def createDatapoint(self, datapoint: 'DatapointInput'=None) -> Datapoint:
        args = ["datapoint: 'DatapointInput'=None"]
        variables = dict()
        var_types = dict()

        if datapoint is not None:
            var_types["datapoint"] = DatapointInput
            if hasattr(datapoint, "to_json"):
                variables["datapoint"] = datapoint.to_json()
            else:
                variables["datapoint"] = datapoint

        query = self.prepare(Datapoint, "createDatapoint", variables, var_types)
        results = self.query(query, variables)
        return Datapoint.from_json(results.get("createDatapoint"))

    def deleteDatapoint(self, data_id: 'ID'=None) -> DeleteStatusResponse:
        args = ["data_id: 'ID'=None"]
        variables = dict()
        var_types = dict()

        if data_id is not None:
            var_types["data_id"] = ID
            if hasattr(data_id, "to_json"):
                variables["data_id"] = data_id.to_json()
            else:
                variables["data_id"] = data_id

        query = self.prepare(DeleteStatusResponse, "deleteDatapoint", variables, var_types)
        results = self.query(query, variables)
        return DeleteStatusResponse.from_json(results.get("deleteDatapoint"))

    def createInferenceExecution(self, inference: 'InferenceExecutionInput'=None) -> InferenceExecution:
        args = ["inference: 'InferenceExecutionInput'=None"]
        variables = dict()
        var_types = dict()

        if inference is not None:
            var_types["inference"] = InferenceExecutionInput
            if hasattr(inference, "to_json"):
                variables["inference"] = inference.to_json()
            else:
                variables["inference"] = inference

        query = self.prepare(InferenceExecution, "createInferenceExecution", variables, var_types)
        results = self.query(query, variables)
        return InferenceExecution.from_json(results.get("createInferenceExecution"))

    def createMaterial(self, material: 'MaterialInput'=None) -> Material:
        args = ["material: 'MaterialInput'=None"]
        variables = dict()
        var_types = dict()

        if material is not None:
            var_types["material"] = MaterialInput
            if hasattr(material, "to_json"):
                variables["material"] = material.to_json()
            else:
                variables["material"] = material

        query = self.prepare(Material, "createMaterial", variables, var_types)
        results = self.query(query, variables)
        return Material.from_json(results.get("createMaterial"))

    def createMaterialInteraction(self, material_interaction: 'MaterialInteractionInput'=None) -> MaterialInteraction:
        args = ["material_interaction: 'MaterialInteractionInput'=None"]
        variables = dict()
        var_types = dict()

        if material_interaction is not None:
            var_types["material_interaction"] = MaterialInteractionInput
            if hasattr(material_interaction, "to_json"):
                variables["material_interaction"] = material_interaction.to_json()
            else:
                variables["material_interaction"] = material_interaction

        query = self.prepare(MaterialInteraction, "createMaterialInteraction", variables, var_types)
        results = self.query(query, variables)
        return MaterialInteraction.from_json(results.get("createMaterialInteraction"))
