from chibi.atlas import Chibi_atlas
from chibi.command import command


def nmcli( *args, stdout=True ):
    if stdout:
        stdout = 'pipe'
    return command( 'nmcli', '-t', *args, stdout=stdout )


class _Show:
    @property
    def current( self ):
        active_connections = self._ls( '--active' )
        return self( *active_connections )

    def __call__( self, *connections ):
        if not connections:
            names = self._ls()
            return self( *names )

        result = Chibi_atlas()
        connections_atlas = []
        for connection in connections:
            output, error, code = nmcli(
                'connection', 'show', '--show-secrets', connection )
            rows = output.split( '\n' )
            d = dict( ( tuple( r.rsplit( ':', 1 ) ) for r in rows if r ) )
            d = Chibi_atlas( d )
            connections_atlas.append( d )
            result[ connection ] = d
        return result

    def _ls( self, *args ):
        output, error, code = nmcli(
            'connection', 'show', '--show-secrets', *args )
        rows = output.split( '\n' )
        result = []
        for r in rows:
            if not r:
                continue
            r = r.split( ':' )
            d = r[3] if r[3] else None
            result.append(
                Chibi_atlas( name=r[0], uuid=r[1], kind=r[2], device=d ) )
        return [ r.name for r in result ]


class _Connection:
    def __init__( self ):
        self.show = _Show()


connection = _Connection()
