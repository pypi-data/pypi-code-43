from datetime import datetime
import re

from .pdfReader import PDFReader


class PDFParserSantander:
    def __init__(self, file):
        self.file = file
        self.cards = []
        self.results = []

        self._text = None
        self._type = None

    @staticmethod
    def __replace_separator(value_str_brl):
        return value_str_brl.replace(',', '.')

    def run(self):
        self.results.clear()

        reader = PDFReader()
        self._text = reader.run(self.file)

        pdf_type = self._get_type()

        if pdf_type == 'internet':
            self._run_internet_banking()
        if pdf_type == 'unique':
            self._run_unique()
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
            if self._text.find('SANTANDER UNIQUE') != -1:
                self._type = 'unique'
            else:
                self._type = 'unknown'
        return self._type

    def _run_internet_banking(self):
        cash_flows_delimiter = 'Resumo das despesas'
        if cash_flows_delimiter in self._text:
            tables_and_footers, _ = self._text.split(cash_flows_delimiter)
            cash_date = self.__find_cash_date()
        else:
            tables_and_footers = self._text
            cash_date = None

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
                    'date': datetime.strptime(tokens[i], '%d/%m/%Y'),
                    'description': tokens[i + 1],
                    'value_usd': self.__replace_separator(tokens[i + 2].strip('US$ ')),
                    'value_brl': self.__replace_separator(tokens[i + 3].strip('R$ ')),
                }

                # TODO: process expenses when currency is usd
                self.results.append([
                    cash_flow['date'],
                    cash_flow['description'],
                    cash_flow['value_brl'],
                    card['last_digits'],
                    cash_date,
                ])

                card['cash_flows'].append(cash_flow)

            self.cards.append(card)

    def _run_unique(self):
        cash_date = self.__find_cash_date()

        # Remove irrelevant information
        pages = self._text.split('SANTANDER UNIQUE')
        first_page_footer_removed = pages[1].split('IOF e CET')[0]
        expense_history = ''.join([first_page_footer_removed, pages[2]])

        pos = expense_history.find('Nº DO CARTÃO ')
        # format: Nº DO CARTÃO 1234 XXXX XXXX 4321
        origin = expense_history[pos+13:pos+32]

        expense_history = expense_history.split('Histórico das Despesas')[1]
        expense_history = expense_history.split('DataDescrição')[0]

        tokens = expense_history.split()
        for i in range(len(tokens)):
            cash_flow = {}
            token = tokens[i]

            if i == 0:
                date_str = f"{token}/{cash_date.year}"
                cash_flow['date'] = datetime.strptime(date_str, '%d/%m/%Y')
                next_token = tokens[i + 3]
                cash_flow['description'] = next_token
                next_token = tokens[i + 5]
                if next_token.startswith('PARC'):
                    cash_flow['description'] = f"{cash_flow.get('description')} {next_token}"
                    next_token = tokens[i + 6]
                cash_flow['value'] = self.__replace_separator(next_token)

            elif re.match(r"\d{2}/\d{2}", token[0:5]):
                date_str = f"{token[:5]}/{cash_date.year}"
                cash_flow['date'] = datetime.strptime(date_str, '%d/%m/%Y')
                cash_flow['description'] = token[5:]
                next_token = tokens[i + 1]
                if next_token.startswith('PARC'):
                    cash_flow['description'] = f"{cash_flow.get('description')} {next_token}"
                    next_token = tokens[i + 2]
                cash_flow['value'] = self.__replace_separator(next_token)

            else:
                continue

            self.results.append([
                cash_flow['date'],
                cash_flow['description'],
                cash_flow['value'],
                origin,
                cash_date,
            ])

    def __find_cash_date(self):
        if self._type == 'internet':
            delimiter = 'Data de vencimento:\n'
            pos = self._text.find(delimiter) + len(delimiter)
        elif self._type == 'unique':
            delimiter = '!Vencimento\n'
            pos = self._text.find(delimiter) + len(delimiter)

        # format dd/mm/YYYY (len=10)
        date_str = self._text[pos:pos + 10]
        return datetime.strptime(date_str, '%d/%m/%Y')
