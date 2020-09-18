topleft = '┌'
topright = '┐'
bottomleft = '└'
bottomright = '┘'
horizontal = '─'
vertical = '│'
joinleft = '├'
joinright = '┤'


def top(size):
    return topleft + horizontal * size + topright


def bottom(size):
    return bottomleft + horizontal * size + bottomright


def sep(size):
    return joinleft + horizontal * size + joinright


def label(size, text):
    return vertical + (' {:<%s}' % (size - 1)).format(text) + vertical


def field(size, label, value):
    size -= 1
    col_size = int(size * 0.6)
    l = (' {:<%s}' % (col_size)).format(label)
    v = ('{:<%s}' % (size - col_size)).format(value)
    return vertical + l + v + vertical


def render(title: str, fields: dict, size: int = 50):
    header = [top(size), label(size, title), sep(size)]
    body = [field(size, k, v) for k, v in fields.items()]
    footer = [bottom(size)]
    return '\n'.join(header + body + footer)