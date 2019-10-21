""" Test CLI """


from libs.core.cli import CliOptions, create_parser


def test_command():
    """ Test CLI options"""
    source_file = './tests/test_integration/content_files/'
    source_file += 'add_evc_correct_request.yaml'
    parser = create_parser()
    args = parser.parse_args(['-A',
                              '-u', 'admin',
                              '-t', 'admin',
                              '-p', 'sparc123!',
                              '-f', source_file,
                              '-O', 'https://192.168.56.10/oess/',
                              '-v', 'info',
                              '-q'
                              ])
    return CliOptions(parser, args)
