# -*- coding: utf-8 -*-
"""Where the build is.

Every suite in here was written with the build's absolute path typed into it:

    B = '/root/work/smokers-paradise-demo/build/index.html'

which is the path it had in the container it was written in, and nowhere else.
That made all 65 suites unrunnable the moment the repo moved — including on the
machine of anybody who clones it, which is the only machine that matters now.

The path is resolved instead of typed. Walk up from this file until a directory
holds app/index.html, which is the one output the whole repo produces. Override
with SP_BUILD when testing a build that is somewhere else.
"""
import os

_here = os.path.dirname(os.path.abspath(__file__))


def _find():
    env = os.environ.get('SP_BUILD')
    if env:
        return env
    d = _here
    for _ in range(6):
        p = os.path.join(d, 'app', 'index.html')
        if os.path.exists(p):
            return p
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    raise SystemExit(
        'Cannot find app/index.html above %s. Set SP_BUILD to the build you '
        'want to test.' % _here)


APP = _find()
SHOTS = os.environ.get('SP_SHOTS', os.path.join(os.path.dirname(APP), '..', 'shots', 'qa'))
SHOTS = os.path.abspath(SHOTS)
