from pyhtml import html, body, img, table, li, a, td, tr


class pd2html:
    def __init__(self, data):
        self.data = data
        self.columns = data.columns.values
        self.data_dict = data.to_dict(orient='records')

        self.pass_words = ['url']

    def get_title(self):
        tds = []
        for col in self.columns:
            if col in self.pass_words:
                continue
            tds.append(td(col))
        return tr(tds)

    def get_td(self, col, data_dict: dict):
        data = data_dict[col]

        if col in self.pass_words:
            return None

        if col == 'id':
            url = data_dict['url']
            res = td(li(a(href=url, target="_blank")(data)))
        elif ("img" in col) or ("image" in col):
            res = td(img(src=data + "?w=250&h=250&cp=1"))
        else:
            res = td(data)
        return res

    def get_tr(self, data: dict):
        l1 = len(self.columns)
        tds = []
        for i in range(0, l1):
            temp_td = self.get_td(self.columns[i], data)
            if temp_td is not None:
                tds.append(temp_td)

        return tr(tds)

    def html(self):
        trs = [self.get_title()]
        for d in self.data_dict:
            trs.append(self.get_tr(d))

        return html(body(table(trs)))

    def html_str(self):
        return self.html().render(user='Cenk')
