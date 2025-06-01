import shutil
import subprocess
import sys

import av
import argparse
import os

from gallery_dl import job
from gallery_dl import config


def tweet_to_gif(urls, base_dir):
    config.load()
    config.set((), 'base-directory', base_dir)
    config.set(("extractor", "twitter"), 'filename', "[{date:%y-%m-%d}] {tweet_id}_p{num:A-1/}.{extension}")
    config.set((), 'image-filter', "extension in ('mp4')")

    for url in urls:
        print("Processing: {url}")

        j = job.DownloadJob(url)
        j.run()

        if not j.pathfmt.realpath:
            print("Skipping: {url}")
            continue

        file_dir = os.path.realpath(j.pathfmt.realdirectory)
        file_base_name = os.path.basename(j.pathfmt.path).split('.')[0]
        out_file = file_base_name + '.gif'
        frame_dir = os.path.join(file_dir, f'{file_base_name}_frames')

        shutil.rmtree(frame_dir, ignore_errors=True)
        os.mkdir(frame_dir)

        with av.open(j.pathfmt.path) as container:
            framerate = round(float(container.streams.video[0].average_rate), 2)
            for index, frame in enumerate(container.decode(video=0)):
                frame.to_image().save(os.path.join(frame_dir, f'frame{index:04d}.png'))

        command = f'gifski --fps {str(framerate)} -o "{os.path.join('..', out_file)}" frame*.png'
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


def check_gifski():
    if not shutil.which('gifski'):
        sys.stderr.write('Please install gifski from: https://gif.ski/')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTION]... URL...')
    parser.add_argument('urls',
                        nargs='+',
                        help='Tweets to process')
    parser.add_argument('-d', '--directory',
                        dest='directory',
                        default=os.path.join('.', 'out'),
                        help='Base output directory')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    check_gifski()
    av.logging.set_level(av.logging.VERBOSE)
    tweet_to_gif(args.urls, args.directory)


def test():
    urls = [
        # 'https://x.com/kdha2402/status/1925270463636545577',
        'https://x.com/dingkuang1/status/1927166916801565154',
    ]
    check_gifski()
    av.logging.set_level(av.logging.VERBOSE)
    directory = os.path.join('.', 'out')
    tweet_to_gif(urls, directory)


if __name__ == '__main__':
    # test()
    main()
