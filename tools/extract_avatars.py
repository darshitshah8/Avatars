"""Cut avatars out of a sheet: fit each circle, remove the name banner, pad, export PNG."""
from PIL import Image
import numpy as np, sys, os

SRC, OUT = sys.argv[1], sys.argv[2]
# name: (search box x0,x1,y0,y1 around the circle, banner top y)
AVATARS = {
    'owner':    ((40, 520, 0, 470), 412),
    'manager':  ((530, 1010, 0, 470), 412),
    'employee': ((1020, 1500, 0, 470), 412),
    'guest':    ((270, 750, 480, 930), 872),
    'custom':   ((780, 1260, 480, 930), 874),
}
PAD, SIZE, SS = 0.11, 512, 4

img = np.array(Image.open(SRC).convert('RGB')).astype(float)
nonwhite = np.abs(img - 254).sum(2) > 45

def fit_circle(x0, x1, y0, cut):
    # left/right edge points of the colored disc, rows well below the crown and above the banner
    pts = []
    sub = nonwhite[:, x0:x1]
    rows = [y for y in range(y0, cut) if sub[y].any()]
    top = rows[0]
    for y in range(top + 60, cut - 40):
        xs = sub[y].nonzero()[0]
        pts += [(x0 + xs.min(), y), (x0 + xs.max(), y)]
    p = np.array(pts, float)
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    b = (p ** 2).sum(1)
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    return cx, cy, np.sqrt(c + cx * cx + cy * cy)

os.makedirs(OUT, exist_ok=True)
for name, ((x0, x1, y0, y1), cut) in AVATARS.items():
    cx, cy, R = fit_circle(x0, x1, y0, cut)
    R -= 1.0  # stay inside the anti-aliased rim
    print(f'{name}: center=({cx:.1f},{cy:.1f}) R={R:.1f}')
    work = img.copy()
    # banner removal: continue the clothing downward by repeating the last clean rows
    clean = work[cut - 4:cut].mean(0)
    work[cut:int(cy + R) + 3] = clean
    half = R * (1 + PAD)
    bx0, by0 = cx - half, cy - half
    side = 2 * half
    # supersampled crop + circle mask
    n = SIZE * SS
    ys, xs = np.mgrid[0:n, 0:n]
    sx = bx0 + (xs + 0.5) * side / n
    sy = by0 + (ys + 0.5) * side / n
    ix = np.clip(sx.astype(int), 0, img.shape[1] - 1)
    iy = np.clip(sy.astype(int), 0, img.shape[0] - 1)
    rgb = work[iy, ix]
    inside = ((sx - cx) ** 2 + (sy - cy) ** 2 <= R * R).astype(float)
    # parts that stick out of the circle above it (e.g. the crown): keep by non-whiteness
    dist_white = np.abs(rgb - 254).sum(2)
    above = (sy < cy - 0.55 * R) & (sy < cut)
    outside_a = np.where(above, np.clip((dist_white - 25) / 60, 0, 1), 0)
    alpha = np.maximum(inside, outside_a)
    # page-white slivers near the lower rim (where the body overhangs the disc): make transparent
    r = np.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)
    sliver = (sy > cy) & (r > R - 25) & (dist_white < 15)
    alpha = np.where(sliver, 0, alpha)
    # un-blend white from the soft edge pixels outside the circle
    a3 = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.where((inside < 1)[..., None], (rgb - (1 - a3) * 254) / a3, rgb)
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').resize((SIZE, SIZE), Image.LANCZOS).save(
        os.path.join(OUT, f'{name}.png'), optimize=True)
