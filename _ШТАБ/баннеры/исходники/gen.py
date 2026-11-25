import json, pathlib, sys, re
T = pathlib.Path(__file__).parent
PRESETS = {'kwork': (1320, 880), 'fiverr': (1280, 769), 'square': (1080, 1080), 'wide': (1920, 1080)}

def build(preset, s):
    W, H = PRESETS[preset]
    k = W / 1320
    n = lambda v: round(v * k)
    v = {
      'WIDTH': W, 'HEIGHT': H, 'GRID': n(64), 'BLUR': n(100),
      'OV1': n(760), 'OV2': n(-360), 'OV3': n(-260),
      'OA1': n(600), 'OA2': n(-320), 'OA3': n(-200),
      'GLYPHR': n(78), 'GLYPHB': n(70), 'GLYPHW': n(360),
      'PAD': n(84), 'GAP2': n(18), 'MARK': n(66),
      'BRANDSIZE': n(46), 'KICKSIZE': n(14), 'PL1': n(18),
      'RULEW': n(64), 'RULEH': n(4), 'MB0': n(30),
      'H1SIZE': n(92), 'MAXW': n(940), 'SUBSIZE': n(27), 'MB2': n(24), 'SUBMAX': n(720),
      'TITLEKICK': s['kick'], 'HEADLINE': s['h1'], 'SUBLINE': s['sub'], 'FOOT': s['foot'],
    }
    html = re.sub(r'\{\{([A-Z0-9]+)\}\}', lambda m: str(v[m.group(1)]), (T/'_tpl.html').read_text(encoding='utf-8'))
    assert '{{' not in html
    out = T / f"{s['id']}--{preset}.html"
    out.write_text(html, encoding='utf-8')
    return out

if __name__ == '__main__':
    for s in json.loads((T/sys.argv[1]).read_text(encoding='utf-8')):
        for preset in sys.argv[2:]:
            print(build(preset, s).name)
