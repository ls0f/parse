#coding:utf-8
import re


class Parse(object):

    def __init__(self):
        self.i = 0
        self.text = ""
        self.js = None

    def cur_char(self):
        return self.text[self.i]

    def consume(self, l=1):
        assert self.i+l <= len(self.text)
        t = self.text[self.i: self.i+l]
        self.i += l
        return t

    def accept(self, c):
        if self.cur_char() != c:
            self.err()
        return self.consume()

    def accept_multi(self, multi):
        buf = ""
        for c in multi:
            buf += self.accept(c)
        return buf

    def accept_regexp(self, l, r):
        multi = self.consume(l)
        if re.search(r, multi) is None:
            raise
        return multi

    def consume_blank(self):
        while re.search(r"\s", self.cur_char()):
            self.consume()

    def err(self):
        raise Exception("unexpected char '%s', nearly '%s' " % (self.cur_char(), self.text[self.i:self.i+20]))

    def parse(self, text):
        self.text = text
        self.i = 0
        self.consume_blank()
        if self.cur_char() == '[':
            self.js = self.parse_array()
        elif self.cur_char() == '{':
            self.js = self.parse_object()
        else:
            self.err()

    def parse_object(self):

        d = dict()
        self.consume_blank()
        self.accept('{')
        self.consume_blank()
        if self.cur_char() == '"':
            k, v = self.parse_pair()
            d[k] = v
            while self.cur_char() == ',':
                self.accept(',')
                k, v = self.parse_pair()
                d[k] = v
        self.accept('}')
        return d

    def parse_pair(self):
        self.consume_blank()
        k = self.parse_string()
        self.accept(":")
        v = self.parse_value()
        self.consume_blank()
        return k, v

    def parse_string(self):
        self.accept('"')
        buf = u""
        while self.cur_char() != '"':
            c = self.cur_char()
            if c == '\\':
                self.consume()
                if self.cur_char() == 'u':
                    buf += self.parse_unicode()
                elif self.cur_char() == '"':
                    buf += self.consume()
                elif self.cur_char() == '\\':
                    buf += self.consume()
                elif self.cur_char() == '/':
                    buf += self.consume()
                elif self.cur_char() == 'n':
                    self.consume()
                    buf += '\n'
                elif self.cur_char() == 'b':
                    self.consume()
                    buf += '\b'
                elif self.cur_char() == 'f':
                    self.consume()
                    buf += '\f'
                elif self.cur_char() == 'r':
                    self.consume()
                    buf += '\r'
                elif self.cur_char() == 't':
                    self.consume()
                    buf += '\t'
                else:
                    raise
            else:
                buf += self.consume()
        self.accept('"')
        self.consume_blank()
        return buf

    def parse_value(self):

        self.consume_blank()
        if self.cur_char() == '"':
            v = self.parse_string()
        elif re.search(r"[1-9-]", self.cur_char()):
            v = self.parse_number()
        elif self.cur_char() == '{':
            v = self.parse_object()
        elif self.cur_char() == '[':
            v = self.parse_array()
        elif self.cur_char() == 't':
            self.accept_multi("true")
            v = 'true'
        elif self.cur_char() == 'f':
            self.accept_multi("false")
            v = 'false'
        elif self.cur_char() == 'n':
            self.accept_multi("null")
            v = 'null'
        else:
            self.err()
        self.consume_blank()
        return v

    def parse_array(self):
        l = []
        self.accept('[')
        self.consume_blank()
        while self.cur_char() != ']':
            l = self.parse_element()
        self.accept(']')
        self.consume_blank()
        return l

    def parse_element(self):
        ele = [self.parse_value()]
        while self.cur_char() == ',':
            self.accept(',')
            ele.append(self.parse_value())
        self.consume_blank()
        return ele

    def parse_unicode(self):
        self.accept("u")
        return unichr(int("0x%s" % (self.accept_regexp(4, r"[0-9a-fA-F]{4}")), 0))

    def parse_number(self):
        s = self.i
        self.parse_int()
        if self.cur_char() == '.':
            self.parse_frac()
        if self.cur_char() in ('e', "E"):
            self.parse_exp()
        t = self.text[s: self.i]
        if 'e' in t or '.' in t:
            return float(t)
        else:
            return int(t)

    def parse_int(self):
        if self.cur_char() == '-':
            self.consume()
        self.parse_digits()

    def parse_frac(self):
        self.accept('.')
        self.parse_digits()

    def parse_exp(self):
        self.accept_regexp(1, r'e|E')
        if self.cur_char() in ('+', '-'):
            self.consume()
        self.parse_digits()

    def parse_digits(self):
        self.accept_regexp(1, '[0-9]')
        while self.cur_char().isdigit():
            self.consume()


if __name__ == "__main__":
    import sys
    import json
    f = sys.stdin.readlines()
    js = ''.join(f)
    p = Parse()
    p.parse(js)
    print "par:", p.js
    print "std:", json.loads(js)
