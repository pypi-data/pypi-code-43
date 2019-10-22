"""
.inp file transcoding
"""
import transcoding as tc


def get_transcoding():
    section_marker = '*'
    comment_marker = '**'
    
    t_startDefault = tc.Trigger(lambda x: comment_marker not in x,
                                delay=0)
    t_blockStart = tc.Trigger(lambda x: x.startswith(section_marker) and not x.startswith(comment_marker),
                              delay=1)
    t_blockEnd = tc.Trigger(lambda x: x.startswith(section_marker),
                            delay=0)
    t_blockBarrier = tc.Trigger(lambda x: x.startswith(section_marker) and not x.startswith(comment_marker),
                                skip=1,
                                delay=0)
    
    """
    Head
    """
    b_heading = tc.Block(
        "*Heading",
        start=t_startDefault,
        barrier=t_blockBarrier)
    # b_preprint = tc.Block(
    #     "*Preprint, echo={echo:s},"
    #     " model={model:s}, history={history:s},"
    #     " contact={contact:s}",
    #     start=t_startDefault)
    b_preprint = tc.Block(
        "*Preprint, echo=NO, model=NO, history=NO, contact=NO",
        start=t_startDefault,
        barrier=t_blockBarrier)
    
    """
    Part Repetition
    """
    b_partHead = tc.Block(
        "*Part, name={part_name}",
        start=t_startDefault)
    b_nodeHead = tc.Block(
        "*Node",
        start=t_startDefault)
    # def f_nodeRead(line, **kwargs):
    #     spLine = line.split(",")
    #     d = {}
    #     d['node_index'] = int(spLine[0])
    #     d['x'] = float(spLine[1])
    #     d['y'] = float(spLine[2])
    #     d['z'] = float(spLine[3])
    #     return d
    b_node = tc.Table(
        tc.Pattern("{node_index:7d},{x:13f},{y:13f},{z:13f}"),
        stop=t_blockEnd,
        start=t_startDefault)
    b_elementHead = tc.Block(
        "*Element, type={element_type}",
        start=t_startDefault)
    # def f_element_read(line, **kwargs):
    #     spLine = line.split(",")
    #     d = {}
    #     d['element_index'] = int(spLine[0])
    #     d['node_index_0'] = int(spLine[1])
    #     d['node_index_1'] = int(spLine[2])
    #     d['node_index_2'] = int(spLine[3])
    #     TODO: node_index_3
    #     return d
    b_element = tc.Table(
        tc.Conditional(('parts', -1, 'element_type'),
                       ('S3', 'S4'),
                       ("{element_index:8d}, {node_index_0:8d}, {node_index_1:8d}, {node_index_2:8d}",
                        "{element_index:8d}, {node_index_0:8d}, {node_index_1:8d}, {node_index_2:8d}, {node_index_3:8d}")),
        stop=t_blockEnd,
        start=t_startDefault)
    b_partFoot = tc.Block(
        "*End Part",
        start=tc.Trigger(lambda x: '*End' in x))
    
    l_parts = tc.Loop(
        'parts',
        [b_nodeHead, b_node,
         b_elementHead, b_element],
        head=b_partHead,
        foot=b_partFoot)
    
    
    """
    Assembly Repetition
    """
    
    b_assemblyHead = tc.Block(
        "*Assembly, name={assembly_name}",
        start=t_startDefault)
    b_instanceHead = tc.Block(
        "*Instance, name={instance_name}, part={instance_part}",
        start=tc.Trigger(lambda x: '*Instance' in x))
    b_instanceFoot = tc.Block(
        "*End Instance",
        start=t_startDefault)
    b_assemblyFoot = tc.Block(
        "*End Assembly",
        start=tc.Trigger(lambda x: '*End Assembly' in x))
    l_assembly = tc.Loop(
        'assembly',
        [b_instanceHead,
         b_instanceFoot],
        head=b_assemblyHead,
        foot=b_assemblyFoot)
    
    obj = tc.Transcoding(
        b_heading,
        b_preprint,
        l_parts,
        l_assembly)
    
    # tc.Block.START_FUNCTION = lambda x: True
    return obj
