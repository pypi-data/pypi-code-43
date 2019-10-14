def draw_wiremap(connections, shorts, family, size, color):
    width = 300
    result = '<svg width="{}" height="{}">'.format(width, 9 * 16 + 5)

    colors = [
        '#000',
        '#F94',
        '#F90',
        '#4D4',
        '#08F',
        '#48F',
        '#0D0',
        '#975',
        '#850'
    ]

    font = 'font-family="{}" font-size="{}" fill="{}"'.format(family, size, color)

    for connection_from, connection_to in enumerate(connections):
        top = connection_from * 16 + 10.5
        pin_name = "S" if connection_from == 0 else connection_from
        result += '<text x="10.5" y="{}" {}>{}</text>'.format(top + 4, font, pin_name)
        result += '<text x="{}" y="{}" {}>{}</text>'.format(width - 16, top + 4, font, pin_name)

        d = 'M 20 {} h 32'.format(top)

        if connection_to is not None:
            target = connection_to * 16 + 10.5
            d = make_path(top, target, width)

        result += '<path d="{}" fill="transparent" stroke="{}" stroke-width="3" />'.format(d, colors[connection_from])

    for short_from, short_to in enumerate(shorts):
        top = short_from * 16 + 10.5
        if short_to is not None:
            target = short_to * 16 + 10.5

            d = 'M 52 {top} A {arc} {arc} 0 1 1 52 {target}'.format(top=top, arc=((target - top) / 2), target=target)
            result += '<path d="{}" fill="transparent" stroke="red" stroke-width="3" />'.format(d)

    return result + '</svg>'


def make_path(source_top, target_top, width):
    # Short circuit for straight wires
    if source_top == target_top:
        return 'M 20 {} L {} {}'.format(source_top, width - 20, target_top)

    # Simple bezier curve non-straight wires
    d = 'M 20 {}'.format(source_top)
    d += ' h 32'
    d += ' C {x1} {y1}, {x2} {y2}, {x} {y}'.format(x=(width - 20 - 32), y=target_top, x1=100, y1=source_top,
                                                   x2=(width - 100), y2=target_top)
    d += ' h 32'
    return d


if __name__ == '__main__':
    connections = [None, 3, 6, 1, 4, 5, 2, 7, 8]
    shorts = [None, None, None, None, None, None, None, None, None]
    test = draw_wiremap(connections, shorts, "verdana", "11pt", "black")
    print(test)
