from .pdfReader import PDFReader


class PDFParserSantander:
    def __init__(self, file):
        self.file = file
        self.cards = []
        self.results = []

        self._text = None
        self._type = None

    def run(self):
        self.results.clear()

        reader = PDFReader()
        self._text = reader.run(self.file)

        pdf_type = self._get_type()

        if pdf_type == 'internet':
            self._run_internet_banking()
        elif pdf_type == 'unknown':
            raise ValueError(f'Parser does not know how to handle this file: {self.file}')
        else:
            raise ValueError(f'Unexpected value for type: {pdf_type}')

        return self.results

    def _get_type(self):
        if self._type is None:
            if self._text is None:
                raise ValueError(
                    'Run parser before calling this method or check if text is being improperly assigned'
                )
            if self._text.startswith('Internet Banking'):
                self._type = 'internet'
            else:
                self._type = 'unknown'
        return self._type

    def _run_internet_banking(self):
        cash_flows_delimiter = 'Resumo das despesas'
        if cash_flows_delimiter in self._text:
            tables_and_footers, _ = self._text.split(cash_flows_delimiter)
        else:
            tables_and_footers = self._text

        header_delimiter = 'Data\nDescrição\nValor (US$)\nValor (R$)'
        tables_and_footers_list = tables_and_footers.split(header_delimiter)

        footer_delimiter = ' Central de Atendimento Santander'
        table_list = [t.split(footer_delimiter)[0].strip() for t in tables_and_footers_list]
        tables = '\n'.join(table_list)

        cards_raw = tables.split('NªCartao')[1:]
        for raw in cards_raw:
            card = {}
            tokens = raw.strip().split('\n')
            card['last_digits'] = tokens[0].strip('Final:')
            card['owner'] = tokens[1].strip('Titular:')
            card['cash_flows'] = []
            for i in range(2, len(tokens), 4):
                cash_flow = {
                    'date': tokens[i],
                    'description': tokens[i + 1],
                    'value_usd': tokens[i + 2].strip('US$ '),
                    'value_brl': tokens[i + 3].strip('R$ '),
                }

                # TODO: add origin
                # TODO: process expenses when currency is usd
                self.results.append([
                    cash_flow['date'],
                    cash_flow['description'],
                    cash_flow['value_brl'],
                ])

                card['cash_flows'].append(cash_flow)

            self.cards.append(card)
