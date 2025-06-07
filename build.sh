#!/bin/bash
python3 -m virtualenv venv
source venv/bin/activate
python3 -m pip install pyinstaller
pyinstaller linux.spec
#pyinstaller windows.spec
./dist/tweet2gif https://x.com/kdha2402/status/1925270463636545577 'https://x.com/dingkuang1/status/1927166916801565154' -d 'out'
