
class String:

    @staticmethod
    def number_format(num, pos=None, prefix='', suffix=''):
        # pos kwarg is there for compatibility with matplotlib but is otherwise unused
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}{}{}'.format(
            prefix,
            '{:f}'.format(num).rstrip('0').rstrip('.'),
            ['', 'K', 'M', 'B', 'T'][magnitude],
            suffix
        )

    @staticmethod
    def dollars_format(num, pos=None):
        # pos kwarg is there for compatibility with matplotlib but is otherwise unused
        return String.number_format(num, pos=None, prefix="$")


    @staticmethod
    def pounds_format(num, pos=None):
        # pos kwarg is there for compatibility with matplotlib but is otherwise unused
        return String.number_format(num, pos=None, prefix="£")

