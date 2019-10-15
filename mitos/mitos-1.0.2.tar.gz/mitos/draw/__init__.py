'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from Bio.Graphics import GenomeDiagram
from Bio.SeqFeature import SeqFeature, FeatureLocation

def draw( featurelist, length, destination, circular = False ):
    gd_diagram = GenomeDiagram.Diagram( "name" )
    gd_track_for_features = gd_diagram.new_track( 1, name = "Annotated Features" )
    gd_feature_set = gd_track_for_features.new_set()
    for feature in featurelist:
        if feature.type == "gene":
            color = colors.green
        elif feature.type == "tRNA":
            color = colors.blue
        else:
            color = colors.red
        feat = SeqFeature( FeatureLocation( feature.start, feature.stop ), strand = feature.strand )
        gd_feature_set.add_feature( feat, name = feature.name, label = True, sigil = "ARROW", color = color )

    if circular:
        gd_diagram.move_track( 1, 3 )
        gd_diagram.draw( format = "circular", orientation = "landscape", pagesize = ( 20 * cm, 20 * cm ), fragments = 1, start = 0, end = length )
        gd_diagram.write( destination, "PDF" )
    else:
        gd_diagram.draw( format = "linear", orientation = "landscape", pagesize = ( 40 * cm, 5 * cm ), fragments = 1, start = 0, end = length )
        gd_diagram.write( destination, "PDF" )

def draw2( features, size ):
    """
    Function to draw a genom in png format
    It returns the pna so that it can write on a web page.
    @param features a feature list in feature format
    @param size the size of the whole genom
    """
    gdd = GenomeDiagram.Diagram( 'Test Diagram' )
    gdt_features = gdd.new_track( 1, scale_smalltick_interval = 1e3 )
    gd_feature_set = gdt_features.new_set()

    for feat in features:
        feature = SeqFeature( FeatureLocation( feat.start, feat.stop ), strand = feat.strand )
        # color the features
        if feat.type == "gene":
            color = "red"
        elif feat.type == "tRNA":
            color = "blue"
        elif feat.type == "rRNA":
            color = "green"
        else:
            color = "grey"
        # add it as a ARROW
        gd_feature_set.add_feature( feature, sigil = "ARROW", color = color, arrowshaft_height = 1, label = False, label_size = 10, label_angle = -90, name = feat.getname() )  # ,

    # draw it linear and in format 20/3
    gdd.draw( format = 'linear', pagesize = ( 10 * inch, 0.9 * inch ), fragments = 1, start = 0, end = size, tracklines = 0 )

#    gdd.move_track( 1, 3 )
#    gdd.draw( format = 'circular', circular = True, pagesize = ( 7 * inch, 7 * inch ), fragments = 1, start = 0, end = size, tracklines = 0 )

    return gdd.write_to_string( "PNG", dpi = 100 )

def draw3( features, size ):
    """
    Function to draw a genom in png format
    It returns the pna so that it can write on a web page.
    @param features a feature list in feature format
    @param size the size of the whole genom
    """
    gdd = GenomeDiagram.Diagram( 'Test Diagram' )
    gdt_features = gdd.new_track( 1, height = 0.5, scale_smalltick_interval = 1e3 )
    gd_feature_set = gdt_features.new_set()

    for feat in features:
        feature = SeqFeature( FeatureLocation( feat.start, feat.stop ), strand = feat.strand )
        # color the features
        if feat.type == "gene":
            color = "red"
        elif feat.type == "tRNA":
            color = "blue"
        elif feat.type == "rRNA":
            color = "green"
        else:
            color = "grey"
        # add it as a ARROW
        gd_feature_set.add_feature( feature, sigil = "ARROW", color = color, arrowshaft_height = 1, label = True, label_size = 6, label_angle = 90 , name = "  " + feat.getname(), label_position = "middle" )
    # draw it linear and in format 20/3
    gdd.draw( format = 'linear', pagesize = ( 8 * inch, 1.5 * inch ), fragments = 1, start = 0, end = size, tracklines = 0 )
    return gdd.write_to_string( "PNG", dpi = 150 )
