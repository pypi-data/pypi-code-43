import sys
import treeparser


def cli():
    if len(sys.argv) not in [2, 3]:
        print('Usage: {script} input-file [output-file]'.format(script=treeparser.__name__))
        return

    in_file = sys.argv[1]
    with open(in_file, 'r') as f:
        flat_string = f.read()

    token_stream = treeparser.tokenize(flat_string)
    treeparser.validate_token_stream(token_stream)
    trees = treeparser.build_trees(token_stream)
    output = treeparser.build_indexed_tree_table(trees)

    if len(sys.argv) == 3:
        out_file = sys.argv[2]
        with open(out_file, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    cli()
