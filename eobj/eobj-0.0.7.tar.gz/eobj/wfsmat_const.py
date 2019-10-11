#id                   original-id-number
#pid                  parent-original-id-number         single-parent
#pids                 parents-original-id-number        multi-parent 
#tag                  tag
#tpl                  tag-pathlist-without-number       single-parent
#tpls                                                   multi-parent
#fpl                  full-pathlist-with-number         single-parent
#fpls                                                   multi-parent
#pbreadth             parent-breadth
#pbreadths            parents-breadth 
#children
#child_ids
#loc                  (depth,breadth)
#sibseq
#samefpl_sibseq
#samefpl_sibseqs                                     multi-parent
#sametpl_sibseq
#sametpl_sibseqs                                     multi-parent
#dotpath
#dotpaths
#mkdir_path
#mkdir_paths
#orig_si
#orig_ei
#post_fmt_si
#post_fmt_ei


ANL = [
    'id',
    'pid',
    'pids',
    'ftag',
    'tag',
    'depth',
    'breadth',
    'tpl',
    'tpls',
    'fpl',
    'fpls',
    'pbreadth',
    'pbreadths',
    'children',
    'child_ids',
    'sibseq',
    'samefpl_sibseq',
    'samefpl_sibseqs',
    'sametpl_sibseq',
    'sametpl_sibseqs',
    'samefpl_breadth',
    'samefpl_breadths',
    'sametpl_breadth',
    'sametpl_breadths',
    'dotpath',
    'dotpaths',
    'mkdir_path',
    'mkdir_paths'
]


ANL_SP = [
    'id',
    'pid',
    'ftag',
    'tag',
    'depth',
    'breadth',
    'tpl',
    'fpl',
    'pbreadth',
    'children',
    'child_ids',
    'sibseq',
    'samefpl_sibseq',
    'sametpl_sibseq',
    'samefpl_breadth',
    'sametpl_breadth',
    'dotpath',
    'mkdir_path',
]


ANL_SP_RONLY = [
    'ftag',
    'tag',
    'depth',
    'breadth',
    'tpl',
    'fpl',
    'pbreadth',
    'children',
    'sibseq',
    'samefpl_sibseq',
    'sametpl_sibseq',
    'samefpl_breadth',
    'sametpl_breadth',
    'dotpath',
    'mkdir_path',
]

ANL_JOBJ_RONLY = [
    'ftag',
    'fatag',
    'depth',
    'breadth',
    'fpl',
    'fapl',
    'pbreadth',
    'children',
    'sibseq',
    'samefpl_sibseq',
    'samefpl_breadth',
    'dotpath',
    'mkdir_path',
]



