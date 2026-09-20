# -*- coding: utf-8 -*-
"""Serve the hotlinked product photography that this sandbox's egress blocks.

Every packshot in the catalogue is hotlinked from the brand that published it.
This container cannot reach those hosts, so the app does exactly what it was
built to do offline: it retires each dead photograph and takes the product off
the shelf. That is correct behaviour and wrong for a test — the shelf would be
measured against the firewall rather than against the app.

So the test network answers those requests with a stand-in packshot. The app
then behaves as it does on a customer's phone, and every assertion is about the
app.
"""
import pathlib

STUB = pathlib.Path(__file__).with_name('stub.png').read_bytes()


def serve_photos(ctx):
    def handler(route):
        u = route.request.url
        if u.startswith('file:') or u.startswith('data:') or u.startswith('blob:'):
            route.continue_(); return
        route.fulfill(status=200, content_type='image/png', body=STUB,
                      headers={'Access-Control-Allow-Origin': '*',
                               'Cache-Control': 'max-age=600'})
    ctx.route('**/*', handler)
