import sys
import terminalmushroom

def cli():
    if len(sys.argv) not in [2, 3]:
        print('Usage: {script} input-file [output-file]'.format(script=terminalmushroom.__name__))
        return

    in_file = sys.argv[1]
    with open(in_file, 'r') as f:
        flat_string = f.read()

    token_stream = terminalmushroom.tokenize(flat_string)
    terminalmushroom.validate_token_stream(token_stream)
    trees = terminalmushroom.build_trees(token_stream)
    output = terminalmushroom.build_indexed_tree_table(trees)

    if len(sys.argv) == 3:
        out_file = sys.argv[2]
        with open(out_file, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    cli()
