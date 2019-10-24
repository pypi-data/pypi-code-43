"""dynomock - commandline endpoint mocker"""

from dynomock import DynoMock, click


@click.command(name=__name__)
@click.option('--port', '-p', type=int, default=5001, help='Server port')
@click.option('--use_debugger', '-d', type=bool, default=False, help='Use debug')
@click.option('--use_reloader', '-r', type=bool, default=False, help='Use reload')
def main(port, use_debugger, use_reloader):
    app = DynoMock()
    from werkzeug.serving import run_simple
    run_simple('localhost', port, app, use_debugger, use_reloader)
main()