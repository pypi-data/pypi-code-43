from django.contrib.auth.decorators import login_required, permission_required
from django.db import connection
from django.http import HttpResponse, Http404
from django.shortcuts import render
from juntagrico.views import get_menu_dict
from pgspecial.main import PGSpecial

from juntagrico_pg.util.output import pretty_print


@permission_required('juntagrico_pg.can_sql')
def home(request):

    renderdict = get_menu_dict(request)
    renderdict .update({
        'menu': {'jpg': 'active'},
    })
    return render(request, "jpg/home.html", renderdict)


@permission_required('juntagrico_pg.can_sql')
def execute_sql(request):
    if request.method != 'POST':
        raise Http404
    sql = request.POST.get('sql')
    try:
        with connection.cursor() as cur:
            if sql.startswith('\\'):
                pgspecial = PGSpecial()
                pgspecial.execute(cur, '\\d')
            else:
                cur.execute(sql)
            output = pretty_print(cur)
            output += '\n'
            output += 'ROWS: ' + str(cur.rowcount)
    except Exception as e:
        output = str(e)
    return HttpResponse(output)
