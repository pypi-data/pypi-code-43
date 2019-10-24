#  _____ _     _       _       ____  _             _       _
# |_   _| |__ (_)___  (_)___  |  _ \(_)_ __  _   _| | __ _| |_ ___
#   | | | '_ \| / __| | / __| | |_) | | '_ \| | | | |/ _` | __/ _ \
#   | | | | | | \__ \ | \__ \ |  __/| | |_) | |_| | | (_| | ||  __/
#   |_| |_| |_|_|___/ |_|___/ |_|   |_| .__/ \__,_|_|\__,_|\__\___|
# There are many frameworks like it,  |_| but this one is mine. --MikeL


import pickle
import gspread
import pandas as pd
from sys import stdout
from os import environ
import google.auth.transport.requests
from apiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def pipulate(tab, rows, cols, columns=None):
    """All that pipulate really is"""

    row1, row2 = rows
    col1, col2 = cols
    col1, col2 = a1(col1, reverse=True), a1(col2, reverse=True)
    cl = tab.range(row1, col1, row2, col2)
    list_of_lists = cl_to_list(cl)
    if not columns:
        columns = tab.range(row1, col1, row1, col2)
        columns = [a1(x.col) for x in columns]
    df = pd.DataFrame(list_of_lists, columns=columns)
    print('cl, df = gs.pipulate(tab, rows=%s, cols=%s) was successful.' % (rows, cols))
    print("You may now manipulate the DataFrame but maintain its (%s x %s) shape." % df.shape)
    print('To update the GSheet with changes, gs.populate(tab, cl, df)')
    return cl, df


def populate(tab, cl, df):
    """Push df back to spreadsheet."""

    if cl_df_fits(cl, df):
        lol = df.values.tolist()
        flat = [y for x in lol for y in x]
        flat[:] = ['N/A' if pd.isnull(x) else x for x in flat]
        for i, cell in enumerate(cl):
            cell.value = flat[i]
        tab.update_cells(cl)
    else:
        raise SystemExit()
    print('gs.populate(tab, cl, df) <<< GSHEET UPDATED! >>>')
    print()


def cl_to_list(cl):
    new_table = []
    for i, cell in enumerate(cl):
        if i == 0:
            row_num = 1
            memory = cell.row
            row = [cell.value]
        if cell.row == memory and i > 0:
            row.append(cell.value)
        else:
            row_num += 1
            memory = cell.row
            row = [cell.value]
            new_table.append(row)
    return new_table


def cl_df_fits(cl, df):
    """Check if GSpread cell list same shape as Pandas dataframe."""
    list_of_lists = cl_to_list(cl)
    height = len(list_of_lists)
    width = len(list_of_lists[0])
    size_tuple = (height, width)
    if size_tuple == df.shape:
        return True
    print('GOOGLE SHEET NOT UPDATED.')
    print('cl %s and df %s different sizes.' % (size_tuple, df.shape))
    return False


def a1(pos, reverse=False):
    """Return the column letter for numeric column index."""
    if reverse:
        return gspread.utils.a1_to_rowcol('%s1' % pos)[1]
    if str(pos).isdigit():
        return gspread.utils.rowcol_to_a1(1, pos)[:-1]
    else:
        return "Must be integer"


def spreadsheet(key):
    """Return instance of GSheet by key."""
    return gc.open_by_key(key)


def key(key):
    """Alias to Return instance of GSheet by key."""
    return gc.open_by_key(key)


def get_email():
    """Return email given provided Google OAuth account."""
    service = create_google_service("oauth2", "v2", filename)
    user_document = service.userinfo().get().execute()
    email = user_document['email']
    return email


def link(gsheet_key):
    """Return GSheet URL for data from Web UI."""
    return 'https://docs.google.com/spreadsheets/d/%s/edit' % gsheet_key


def create_google_service(api_name, version, filename):
    """Return instance of Google Service object."""

    path = os.path.dirname(os.path.realpath('__file__'))
    path_filename = os.path.join(path, filename)
    storage = file.Storage(path_filename)
    credentials = storage.get()
    http = credentials.authorize(http=httplib2.Http())
    service = build(api_name, version, http=http, cache_discovery=False)
    return service


def ga():
    """Return instance of Google Analytics object."""
    return create_google_service("analytics", "v3", filename)


def gsc():
    """Return instance of Google Search Console object."""
    return create_google_service("webmasters", "v3", filename)


class Unbuffered(object):
    """Provides more real-time streaming in Jupyter Notebook"""

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


try:
    with open("credentials.pickle", "rb") as input_file:
        credentials = pickle.load(input_file)
except:
    credentials = False
if not credentials:
    client_id = "769904540573-knscs3mhvd56odnf7i8h3al13kiqulft.apps.googleusercontent.com"
    client_secret = "D2F1D--b_yKNLrJSPmrn2jik"
    environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
    scopes = ["https://www.googleapis.com/auth/analytics.readonly", 
              "https://www.googleapis.com/auth/webmasters.readonly", 
              "https://www.googleapis.com/auth/yt-analytics.readonly",
              "https://www.googleapis.com/auth/youtube.readonly", 
              "https://spreadsheets.google.com/feeds/", 
              "https://www.googleapis.com/auth/gmail.modify", 
              "https://www.googleapis.com/auth/userinfo.email"] 
    client_config = {
        "installed": {
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "client_id": client_id,
            "client_secret": client_secret
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, scopes)
    credentials = flow.run_console()
    credentials.access_token = credentials.token
    with open("credentials.pickle", "wb") as output_file:
        pickle.dump(credentials, output_file)
if not credentials.valid:
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    credentials.access_token = credentials.token
    with open("credentials.pickle", "wb") as output_file:
        pickle.dump(credentials, output_file)
gc = gspread.authorize(credentials)

stdout = Unbuffered(stdout)
