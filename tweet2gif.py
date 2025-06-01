import io
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import av
import argparse
import os

import requests
from gallery_dl import job
from gallery_dl import config


def tweet_to_gif(urls, base_dir, gifski_path):
    config.load()
    config.set((), 'base-directory', base_dir)
    config.set(("extractor", "twitter"), 'filename', "[{date:%y-%m-%d}] {tweet_id}_p{num:A-1/}.{extension}")
    config.set((), 'image-filter', "extension in ('mp4')")
    config.set((), 'skip', "true")

    for url in urls:
        print(f'Processing: {url}')

        j = job.DownloadJob(url)
        j.run()

        if not j.pathfmt.realpath:
            print(f'Does not contain video: {url}', file=sys.stderr)
            continue

        base_path = os.path.abspath(j.pathfmt.path).split('.')[0]
        out_file = f'{base_path}.gif'
        if os.path.exists(out_file):
            print(f'Gif already exists: {out_file}', file=sys.stderr)
            continue
        frame_dir = f'{base_path}_frames'

        shutil.rmtree(frame_dir, ignore_errors=True)
        os.mkdir(frame_dir)

        with av.open(j.pathfmt.path) as container:
            framerate = round(float(container.streams.video[0].average_rate), 2)
            for index, frame in enumerate(container.decode(video=0)):
                frame.to_image().save(os.path.join(frame_dir, f'frame{index:04d}.png'))

        command = f'{gifski_path} --fps {str(framerate)} -o "{out_file}" frame*.png'
        print(command, end='')
        for out in execute(command, shell=True, cwd=frame_dir):
            print(out, end='')

        shutil.rmtree(frame_dir, ignore_errors=True)


def execute(command, shell=False, cwd=None):
    try:
        popen = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 shell=shell,
                                 cwd=cwd,
                                 universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ''):
            yield stdout_line
        popen.stdout.close()
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)


def get_gifski(directory):
    system = platform.system()
    utils_dir = os.path.join(directory, 'utils')
    file_name = 'gifski.exe' if system == 'Windows' else 'gifski'
    file_path = os.path.join(utils_dir, file_name)
    if not os.path.exists(file_path):
        Path.mkdir(Path(utils_dir), exist_ok=True)
        r = requests.get('https://api.github.com/repos/ImageOptim/gifski/releases/latest').json()
        r = requests.get(r['assets'][0]['browser_download_url'], stream=True)
        to_extract = os.path.join({
                                      'Windows': 'win',
                                      'Linux': 'linux',
                                      'Darwin': 'macos',
                                  }[platform.system()], file_name)
        with tarfile.open(fileobj=io.BytesIO(r.content)) as tar_xz:
            member = tar_xz.getmember(to_extract)
            member.name = file_name
            tar_xz.extract(member, path=utils_dir, filter='data')
    return file_path


def clean(obj_):
    def unquote(string):
        if string.startswith('"') and string.endswith('"'):
            return string[1:-1]
        elif string.startswith("'") and string.endswith("'"):
            return string[1:-1]
        return string

    if isinstance(obj_, str):
        return unquote(obj_)
    elif isinstance(obj_, (list, tuple)):
        return [unquote(s) for s in obj_]
    else:
        raise Exception("Unexpected type {}".format(type(obj_)))


def main():
    script_path = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTION]... URL...')
    parser.add_argument('urls',
                        nargs='+',
                        help='Tweets to process')
    parser.add_argument('-d', '--directory',
                        dest='directory',
                        default=os.path.join(script_path, 'out'),
                        help='Base output directory')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    av.logging.set_level(av.logging.VERBOSE)
    tweet_to_gif(clean(args.urls), clean(args.directory), get_gifski(script_path))


def test():
    urls = [
        'https://x.com/kdha2402/status/1925270463636545577',
        "'https://x.com/dingkuang1/status/1927166916801565154'",
    ]
    script_path = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_path, '"out"')
    av.logging.set_level(av.logging.VERBOSE)
    tweet_to_gif(clean(urls), clean(directory), get_gifski(script_path))


if __name__ == '__main__':
    # test()
    main()
