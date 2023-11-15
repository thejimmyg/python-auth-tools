import html


class Html:
    def __init__(self, escaped_html):
        self._escaped_html = escaped_html

    def render(self):
        return self._escaped_html

    def __add__(self, other):
        other_type = type(other)
        if other_type is Html:
            self._escaped_html += other._escaped_html
        elif other_type is str:
            self._escaped_html += html.escape(other, quote=True)
        else:
            raise Exception(f"Unsupported type: {repr(other)}")
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    __str__ = render


if __name__ == "__main__":
    p = Html("1")
    p += Html("2")
    print(Html("0") + p + Html("3"))
