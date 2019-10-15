from numpy.random import RandomState
from pyllist import dllist, dllistnode

from .text_merge import TextMerge
from .text_entity import TextEntity, GenericTextEntity


class RandomInsertTextMerge(TextMerge):
    def __init__(self):
        pass
    def do( self, obj1: TextEntity, obj2: TextEntity, random_state_obj: RandomState):
        # Pick a random location in the first object
        if( obj1.get_data().size == 0 ):
            output_entity = GenericTextEntity( obj2.get_text() )
        else:
            insert_loc = random_state_obj.randint( obj1.get_data().size, size=1 )[0]
            # Create a new entity to contain the output
            output_entity = GenericTextEntity( obj1.get_text() )
            # Insert the second object into the output
            for ind in range( obj2.get_data().size ):
                output_entity.data.insert( obj2.data.nodeat(ind).value, output_entity.data.nodeat( int(insert_loc + ind) ) )
                output_entity.delimiters.insert( obj2.delimiters.nodeat(ind).value, output_entity.delimiters.nodeat( int(insert_loc + ind) ) )
        return output_entity
