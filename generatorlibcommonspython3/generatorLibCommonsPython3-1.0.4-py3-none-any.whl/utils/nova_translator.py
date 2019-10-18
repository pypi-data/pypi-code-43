__all__ = [
    'NovaTranslator'
]

import decimal
from fractions import Fraction

class NovaTranslator:

  def deserialize(instance, novaMetadatasObject, outcomeMap):
    
    # Check if the metadata object is filled
    if novaMetadatasObject != None:
      
      # Iterate every element of the metadata object
      for novaMetadataObject in novaMetadatasObject:

        # Check, get the name value and set the field to be serialize
        novaOutputFieldName = novaMetadataObject.get("name", None)
        if "alias" in novaMetadataObject:
          
          novaOutputFieldName = novaMetadataObject.get("alias", None)

        # Get the field value
        novaOutputFieldValue = getattr(instance, novaMetadataObject.get("name", None))

        # Get the field type
        novaOutputFieldType = novaMetadataObject["type"]
        
        # Get the type of
        typeOf = novaMetadataObject["typeOf"]

        deserializedValue = None

        if novaOutputFieldValue != None:

          # Check if it is a simple type
          if novaOutputFieldType == "simple":
          
            deserializedValue = NovaTranslator.deserializeSimpleType(typeOf, novaOutputFieldValue)
        
          # Check if it is an array type
          elif novaOutputFieldType == "array":
 
            # Deserialize this array
            deserializedValue = NovaTranslator.deserializeArray(novaMetadataObject, novaOutputFieldValue, typeOf)

          else:

            # It is a complex type
            deserializedValue = novaOutputFieldValue.deserialize()

          # Set the deserialized value to the field in JSON
          outcomeMap[novaOutputFieldName] = deserializedValue

    return outcomeMap

  def deserializeArray(novaMetadataObject, novaOutputFieldValue, typeOf):
    
    # Get the depth
    depth = novaMetadataObject["depth"]

    # Recursive call
    return NovaTranslator.deserializeArrayRecursive(novaOutputFieldValue, depth, typeOf)

  def deserializeArrayRecursive(novaOutputFieldValue, depth, typeOf):
    
    novaOutputFieldNameArray = []

    if depth == 1:
    
      itemArrayValue = None

      # Iterate every item of the array
      for itemArray in novaOutputFieldValue:
      
        # Check if array item is simple type
        if NovaTranslator.isSimpleType(typeOf):

          itemArrayValue = NovaTranslator.deserializeSimpleType(typeOf, itemArray)

        else:
        
          # It is a complex type
          itemArrayValue = itemArray.deserialize()

        # Append the item to the JSON array
        novaOutputFieldNameArray.append(itemArrayValue)

    else:

      # Iterate every item of the array
      for itemArray in novaOutputFieldValue:
        
        # Decrement the depth
        newDepth = depth - 1

        # Recursive call to get the pending list
        outcomeListRecursiveCall = NovaTranslator.deserializeArrayRecursive(itemArray, newDepth, typeOf)

        # Add to list the recursive call
        novaOutputFieldNameArray.append(outcomeListRecursiveCall)

    return novaOutputFieldNameArray

  def deserializeSimpleType(typeOf, itemValue):

    if typeOf == bool:

      return NovaTranslator.deserializeSimpleTypeBoolean(itemValue)

    elif typeOf == decimal.Decimal:

      return NovaTranslator.deserializeSimpleTypeDecimal(itemValue)
  
    else:

      return itemValue

  def deserializeSimpleTypeBoolean(inputBoolean):

    isTrue = not (inputBoolean == None or inputBoolean == False or inputBoolean == 0 or inputBoolean == 0.0 or inputBoolean == 0j or inputBoolean == '' or inputBoolean == () or inputBoolean == [] or inputBoolean == {} or inputBoolean == decimal.Decimal(0) or inputBoolean == Fraction(0, 1) or inputBoolean == set() or inputBoolean == range(0))

    outcome = "false"

    if isTrue:

      outcome = "true"

    return outcome

  def deserializeSimpleTypeDecimal(obj):

    if isinstance(obj, decimal.Decimal):

      return str(obj)

    raise TypeError

  def serialize(instance, novaMetadatasObject, incomeMap):

    # Iterate every element of the metadata object
    for novaMetadataObject in novaMetadatasObject:

      # Check, get the name value and set the field to be serialize
      novaInputAliasName = novaMetadataObject.get("name", None)

      if "alias" in novaMetadataObject:
        novaInputAliasName = novaMetadataObject.get("alias", None)

      # Get the field value from the JSON
      novaInputFieldStringValue = incomeMap.get(novaInputAliasName, None)

      # Get the field type
      novaInputFieldType = novaMetadataObject["type"]

      # Get the type of
      typeOf = novaMetadataObject["typeOf"]

      serializedValue = None

      if novaInputFieldStringValue != None:

        # Check if it is a simple type
        if novaInputFieldType == "simple":

          serializedValue = novaInputFieldStringValue

        # Check if it is an array type
        elif novaInputFieldType == "array":

          # Get the depth
          depth = novaMetadataObject["depth"]

          # Recursive call
          serializedValue = NovaTranslator.serializeArrayRecursive(novaInputFieldStringValue, depth, typeOf)

        else:

          # It is a complex type
          serializedValue = getattr(typeOf, "serialize")(novaInputFieldStringValue)

        # Set the value to the specific field
        setattr(instance, novaMetadataObject.get("name", None), serializedValue)

  def serializeArrayRecursive(novaInputFieldStringValue, depth, typeOf):
    
    novaInputFieldNameArray = []

    if depth == 1:

      itemArrayValue = None

      # Iterate every item of the array
      for itemArray in novaInputFieldStringValue:
        if NovaTranslator.isSimpleType(typeOf):
          
          # Simple type
          itemArrayValue = itemArray

        else:

          # Complex type
          itemArrayValue = getattr(typeOf, "serialize")(itemArray)

        novaInputFieldNameArray.append(itemArrayValue)

    else:

      # Iterate every item of the array
      for itemArray in novaInputFieldStringValue:
        
        # Decrement the depth
        newDepth = depth - 1

        # Recursive call to get the pending list
        outcomeListRecursiveCall = NovaTranslator.serializeArrayRecursive(itemArray, newDepth, typeOf)

        # Add to list the recursive call
        novaInputFieldNameArray.append(outcomeListRecursiveCall)

    return novaInputFieldNameArray

  def isSimpleType(typeOf):

    return typeOf == str or typeOf == bool or typeOf == int or typeOf == float or typeOf == decimal.Decimal