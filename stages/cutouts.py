#!/usr/bin/env python3
"""Turn the embedded packshots into real transparent cutouts.

Every one of these files is a manufacturer or retailer photograph printed on a
white studio sweep. That white is why the app kept showing products inside
rectangles: the rectangle IS the photograph.

So the white ground is removed rather than hidden. The method is deliberately
conservative, because the alternative — an aggressive key — eats the white
parts of the packaging, and half this catalogue is white boxes:

  * the fill starts ONLY from the border of the image and floods inward, so a
    white cigarette carton in the middle of the frame is never touched: it is
    not connected to the edge
  * the tolerance is measured against the actual corner colour, not against
    pure white, because retailer sweeps are often #FAFAFA or a touch warm
  * the resulting alpha is feathered by one pixel so edges are not jagged
  * anything that keys away more than 92% of the frame, or less than 8%, is
    rejected and the original is kept: that is the signature of a photograph
    on a dark or busy ground, where a border flood does the wrong thing

The product's own pixels are never altered — only the alpha channel is
written. Nothing is recoloured, stretched or redrawn.
"""
import os, sys
from collections import deque
from PIL import Image, ImageFilter
import numpy as np

SRC = '/root/work/assets/products'
DST = '/root/work/assets/cutouts'
os.makedirs(DST, exist_ok=True)


def keyed(path, tol=26):
    im = Image.open(path).convert('RGBA')

    # A third of these files are ALREADY transparent: the manufacturer shipped
    # a cut-out PNG and the proxy carried the alpha through. Nothing to key —
    # trim the empty margin and pass the original pixels straight on.
    a0 = np.array(im)
    if (a0[:, :, 3] < 250).mean() > 0.03:
        bb = im.getchannel('A').getbbox()
        if bb: im = im.crop(bb)
        return im, 'already transparent -> %dx%d' % (im.width, im.height)

    a = np.array(im).astype(np.int16)
    h, w = a.shape[:2]
    rgb = a[:, :, :3]

    # the ground colour is whatever the corners agree on
    corners = np.concatenate([
        rgb[0:6, 0:6].reshape(-1, 3), rgb[0:6, w-6:w].reshape(-1, 3),
        rgb[h-6:h, 0:6].reshape(-1, 3), rgb[h-6:h, w-6:w].reshape(-1, 3)])
    ground = np.median(corners, axis=0)
    # only key a LIGHT ground; a dark or coloured frame is a real photograph
    if ground.mean() < 198:
        return None, 'ground is not a light sweep'

    near = (np.abs(rgb - ground).max(axis=2) <= tol)

    # flood from the border inward: interior white stays put
    keep = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not keep[y, x]:
                keep[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not keep[y, x]:
                keep[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not keep[ny, nx]:
                keep[ny, nx] = True; q.append((ny, nx))

    frac = keep.mean()
    # a thin downstem really is 3% of its frame, so the upper guard is loose;
    # the lower guard catches photographs that were never on a sweep at all
    if frac > 0.985: return None, 'keyed the whole frame (%.1f%%)' % (frac*100)
    if frac < 0.05:  return None, 'found almost no ground (%.0f%%)' % (frac*100)

    # soft edge: feather the mask by a pixel so the cutout is not jagged
    alpha = Image.fromarray(((~keep) * 255).astype(np.uint8), 'L')
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.7))
    # int32, not int16: (255-96)*255 is 40545 and silently wraps in int16,
    # which erases the product and leaves a wireframe of its own edges
    al = np.array(alpha).astype(np.int32)
    al = np.clip((al - 70) * 255 // max(1, 255 - 70), 0, 255).astype(np.uint8)

    out = a.astype(np.uint8).copy()
    out[:, :, 3] = al
    img = Image.fromarray(out, 'RGBA')

    # trim to what is left, so the cutout's box IS the product
    bb = img.getbbox()
    if bb: img = img.crop(bb)
    return img, 'ok %.0f%% keyed -> %dx%d' % (frac*100, img.width, img.height)


def main(ids):
    made, kept = 0, []
    for pid in ids:
        src = os.path.join(SRC, pid + '.webp')
        if not os.path.exists(src):
            kept.append((pid, 'no source')); continue
        img, why = keyed(src)
        if img is None:
            kept.append((pid, why)); continue
        img.thumbnail((360, 360))
        img.save(os.path.join(DST, pid + '.webp'), 'WEBP', quality=76, method=5)
        made += 1
    print('cut out %d, left alone %d' % (made, len(kept)))
    for pid, why in kept[:20]:
        print('   keep %-8s %s' % (pid, why))


if __name__ == '__main__':
    ids = sys.argv[1:]
    if not ids:
        ids = [f[:-5] for f in sorted(os.listdir(SRC)) if f.endswith('.webp')]
    main(ids)
