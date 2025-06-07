# -*- mode: python ; coding: utf-8 -*-    runs-on: ubuntu-latest    runs-on: ubuntu-latest

    steps:
    - uses: actions/download-artifact@v4

    - name: Environment Variables
      run: echo "DATE=$(date '+${{ env.DATE_FORMAT }}')" >> "$GITHUB_ENV"

    - name: Body
      run: printf 'https://github.com/%s/commit/%s' '${{ github.repository }}' '${{ github.sha }}' > body.md

    - uses: ncipollo/release-action@v1
      with:
        owner: gdl-org
        repo: builds
        tag: ${{ env.DATE }}
        bodyFile: body.md
        artifacts: "executable-*/*"
        allowUpdates: true
        makeLatest: true
        token: ${{ secrets.REPO_TOKEN }}

    steps:
    - uses: actions/download-artifact@v4

    - name: Environment Variables
      run: echo "DATE=$(date '+${{ env.DATE_FORMAT }}')" >> "$GITHUB_ENV"

    - name: Body
      run: printf 'https://github.com/%s/commit/%s' '${{ github.repository }}' '${{ github.sha }}' > body.md

    - uses: ncipollo/release-action@v1
      with:
        owner: gdl-org
        repo: builds
        tag: ${{ env.DATE }}
        bodyFile: body.md
        artifacts: "executable-*/*"
        allowUpdates: true
        makeLatest: true
        token: ${{ secrets.REPO_TOKEN }}


a = Analysis(
    ['tweet2gif.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tweet2gif',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
