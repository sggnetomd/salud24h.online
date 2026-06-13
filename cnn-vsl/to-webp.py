#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor PNG/JPG -> WebP (preserva transparencia).

Uso:
  python to-webp.py <arquivo|pasta> [mais arquivos...] [opcoes]

Opcoes:
  -q N         qualidade 0-100 (padrao 82)  -> bom equilibrio peso/qualidade
  -o PASTA     pasta de saida (padrao: ./img)
  --lossless   sem perda (ideal p/ logo com bordas nitidas)
  --max N      redimensiona p/ no maximo N px de largura (mantem proporcao)

Exemplos:
  python to-webp.py "C:/.../logo.png" --lossless
  python to-webp.py "C:/.../logos-midia.jpg" -q 80 --max 1080
  python to-webp.py "C:/.../pasta-de-imagens" -q 82
"""
import sys, os
from PIL import Image

EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}


def coletar(alvos):
    arquivos = []
    for a in alvos:
        if os.path.isdir(a):
            for nome in sorted(os.listdir(a)):
                if os.path.splitext(nome)[1].lower() in EXTS:
                    arquivos.append(os.path.join(a, nome))
        elif os.path.isfile(a):
            arquivos.append(a)
        else:
            print(f"  [ignorado] nao encontrado: {a}")
    return arquivos


def converter(src, outdir, quality=82, lossless=False, maxw=0):
    base = os.path.splitext(os.path.basename(src))[0]
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, base + ".webp")

    im = Image.open(src)
    if im.mode in ("P", "LA"):
        im = im.convert("RGBA")
    elif im.mode == "CMYK":
        im = im.convert("RGB")

    if maxw and im.width > maxw:
        h = round(im.height * maxw / im.width)
        im = im.resize((maxw, h), Image.LANCZOS)

    if lossless:
        im.save(dst, "WEBP", lossless=True, quality=100, method=6)
    else:
        im.save(dst, "WEBP", quality=quality, method=6)

    o = os.path.getsize(src)
    n = os.path.getsize(dst)
    pct = 100 - int(n * 100 / o) if o else 0
    print(f"  OK  {os.path.basename(src)}  ->  {os.path.basename(dst)}"
          f"   ({o//1024} KB -> {n//1024} KB, -{pct}%)  [{im.width}x{im.height}]")
    return dst


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    quality, lossless, maxw = 82, False, 0
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
    alvos = []

    i = 0
    while i < len(args):
        a = args[i]
        if a == "-q":
            quality = int(args[i + 1]); i += 2
        elif a == "-o":
            outdir = args[i + 1]; i += 2
        elif a == "--lossless":
            lossless = True; i += 1
        elif a == "--max":
            maxw = int(args[i + 1]); i += 2
        else:
            alvos.append(a); i += 1

    arquivos = coletar(alvos)
    if not arquivos:
        print("Nenhuma imagem para converter.")
        return

    print(f"\nConvertendo {len(arquivos)} imagem(ns) -> WebP"
          f"  (qualidade={'lossless' if lossless else quality}, saida='{outdir}')\n")
    for f in arquivos:
        try:
            converter(f, outdir, quality, lossless, maxw)
        except Exception as e:
            print(f"  ERRO  {os.path.basename(f)}: {e}")
    print("\nConcluido.")


if __name__ == "__main__":
    main()
