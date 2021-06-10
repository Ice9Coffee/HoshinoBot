import random
import time
import re
import json


class Choicer:
    def _compile(self, d):
        t = type(d)
        if t is list:
            r = []
            for x in d:
                if type(x) is str and x.startswith('{') and x.endswith('}'):
                    for y in self.map[x[1:-1]]:
                        r.append(y[0])
                else:
                    r.append(x)
            p = 1.0 / len(r)
            return [(self._compile(x), p) for x in r]
        elif t is str:
            return d
        elif t is dict:
            if 'start' in d:
                return [(self._compile(d['d']), d['p'], d['start'])]
            elif 'p' in d:
                return [(self._compile(d['d']), d['p'])]
            else:
                return [(self._compile(x), d[x]) for x in d]
        else:
            return []

    reg = re.compile('{(.*?)}')

    def _runstr(self, s: str, vals: dict = {}) -> str:
        for k in vals:
            s = s.replace(f'{{{k}}}', vals[k])
        for k in self.vals:
            s = s.replace(f'{{{k}}}', self.vals[k])

        def repl(match):
            key = match.group(1)
            k = key.split(':')[0]
            if key not in self.m:
                self.m[key] = set()

            while True:
                r = self._run(self.map[k])
                if r not in self.m[key]:
                    self.m[key].add(r)
                    return r

        return Choicer.reg.sub(repl, s)

    def _run(self, d) -> str:
        t = type(d)
        if t is str:
            return self._runstr(d)
        elif t is list:
            if len(d) == 1 and len(d[0]) == 3:  # loop expr
                sb = []
                d = d[0]
                x = d[0]
                i = d[2]

                while True:
                    sb.append(self._runstr(x, {
                        "i": str(i)
                    }))
                    i += 1
                    if self.rand.random() >= d[1]:
                        break
                return ''.join(sb)
            else:
                r = self.rand.random()
                for d2, p in d:
                    if p > r:
                        return self._run(d2)
                    else:
                        r -= p
                return ''
        else:
            return ''

    def __init__(self, config):
        self.rand = random.Random()
        self.date = config['date']
        self.map = {}

        parts = config['parts']
        for name in parts:
            self.map[name] = self._compile(parts[name])

        self.result = [self._compile(x) for x in config['result']]

    def _setseed(self, qq):
        self.rand.seed(qq * (int(time.time() / 3600 / 24) if self.date else 1))

    def format_msg(self, qq, name):
        self.vals = {
            "name": name
        }
        self._setseed(qq)
        self.m = {}
        return ''.join([self._run(x) for x in self.result])
