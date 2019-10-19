class Common:
    @staticmethod
    def get_size_file_str(value):
        if value == 0:
            return ""

        if value > 0 and value <= 1024:
            return f'{value} Байт'

        if value > 1024 and value <= 1024 * 1024:
            return f'{round(value / 1024, 2)} КБайт'

        if value > 1024 * 1024 and value <= 1024 * 1024 * 1024:
            return f'{round(value / 1024 / 1024, 2)} МБайт'

        if value > 1024 * 1024 * 1024:
            return f'{round(value / 1024 / 1024 / 1024, 2)}  ГБайт'
        return value

    @staticmethod
    def arraund_error(error):
        str = '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        return f'\n{str}\n{error}\n{str}'
