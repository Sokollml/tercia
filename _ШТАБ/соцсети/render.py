#!/usr/bin/env python3
"""Отрисовка пачки постов в PNG.

    python3 render.py pack-2weeks.json            # все посты
    python3 render.py pack-2weeks.json ig-05 tt-06 # только выбранные

Поднимает временный локальный сервер, открывает редактор в режиме ?render=1
и снимает каждый слайд браузером Brave (Chromium) без окна.
Картинки кладёт в посты/<сеть>/<id>/NN.png.
"""
import json, sys, threading, subprocess, functools, pathlib, http.server, socketserver, time

HERE = pathlib.Path(__file__).resolve().parent
BRAVE = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
SIZES = {'feed': (1080, 1350), 'story': (1080, 1920), 'tg': (1280, 720), 'vkcover': (1920, 768), 'avatar': (512, 512)}

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def main():
    pack_name = sys.argv[1] if len(sys.argv) > 1 else 'pack-2weeks.json'
    only = set(sys.argv[2:])
    pack = json.loads((HERE / pack_name).read_text(encoding='utf-8'))
    handler = functools.partial(Quiet, directory=str(HERE))
    class Threaded(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
    with Threaded(('127.0.0.1', 0), handler) as srv:
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        # имя файла редактора кириллицей — в адресе нужна кодировка
        editor = 'http://127.0.0.1:%d/%s' % (port, '%D1%80%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%BE%D1%80.html')
        t0, n = time.time(), 0
        for pi, post in enumerate(pack['posts']):
            if only and post['id'] not in only:
                continue
            w, h = SIZES[post['format']]
            folder = HERE / 'посты' / post['net'] / post['id']
            folder.mkdir(parents=True, exist_ok=True)
            for old in folder.glob('[0-9][0-9].png'):
                old.unlink()
            for si in range(len(post['slides'])):
                url = f'{editor}?render=1&pack={pack_name}&post={pi}&slide={si}'
                subprocess.run([BRAVE, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                                '--force-device-scale-factor=1', '--virtual-time-budget=6000',
                                f'--window-size={w},{h}', f'--screenshot={folder / f"{si + 1:02d}.png"}', url],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                n += 1
            print(f"  {post['net']}/{post['id']}: {len(post['slides'])} слайд(ов)")
        srv.shutdown()
    print(f'готово: {n} слайдов за {time.time() - t0:.0f} с')

if __name__ == '__main__':
    main()
