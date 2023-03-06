import webbrowser
from argparse import ArgumentParser
import pypdf
from os.path import exists, join
from os import mkdir
from shutil import move, rmtree
import logging
from itertools import pairwise
from uuid import uuid4
from pathlib import Path


tmp = Path("__temp__")


def process_page_range(reader, start, end):
    r_name = gen_pdf(reader, start, end)
    webbrowser.open(r_name)
    if name := input(f"Name pdf from pages {start} {end} (leave blank to ignore): "):
        name = name.replace("%b", "BARITONE")
        name = name.replace("%e", "EUPHONIUM")
        move(r_name, f"{name}.pdf")


def gen_pdf(pdf: pypdf.PdfReader, start: int, end: int, name=None):
    writer = pypdf.PdfWriter()
    assert end <= len(pdf.pages)
    for i in range(start, end + 1):
        writer.add_page(pdf.pages[i - 1])
    r_name = name or str(tmp / str(uuid4()))
    writer.write(r_name)
    return r_name


def get_pages_pairs():
    def cycle_input():
        while True:
            inp = input(": ")
            if inp == "stop":
                return
            try:
                i = int(inp)
                if i < 1:
                    raise ValueError
                yield i
            except ValueError:
                print(f"Invalid page number: {inp}")

    return pairwise(cycle_input())


def main(args):
    try:
        if not exists(args.file):
            return 1
        mkdir(tmp)
        webbrowser.open(args.file)
        pdf = pypdf.PdfReader(args.file)
        pages_c = len(pdf.pages)
        print("Insert the first page of each document. Enter 'stop' to end the process.")
        pairs = list(get_pages_pairs())
        for p0, p1 in pairs:
            process_page_range(pdf, p0, p1)
        process_page_range(pdf, pairs[-1][-1], pages_c)
    finally:
        if exists("__temp__"):
            rmtree("__temp__")


if __name__ == "__main__":
    argp = ArgumentParser(prog="pdf_splitter")
    argp.add_argument("file", metavar="FILE", help="Input file to split")
    arguments = argp.parse_args()
    exit(main(arguments))

