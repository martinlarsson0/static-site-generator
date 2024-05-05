import shutil
from contextlib import suppress
from os import listdir, makedirs, mkdir
from os.path import dirname, isfile, join

from utils import generate_page


def main():
    with suppress(FileNotFoundError):
        shutil.rmtree("public")
    mkdir("public")
    copy_to_public("static")
    generate_pages_recursive("content/", "template.html", "public/")


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    items = listdir(dir_path_content)

    for item in items:
        content_path = join(dir_path_content, item)
        if isfile(content_path):
            if content_path[-3:] == ".md":
                output_path = join(
                    "public", content_path.replace("content/", "")
                ).replace(".md", ".html")
                output_dir = dirname(output_path)
                makedirs(output_dir, exist_ok=True)
                generate_page(content_path, template_path, output_path)
        else:
            generate_pages_recursive(content_path, template_path, dest_dir_path)


def copy_to_public(dir):
    items = listdir(dir)

    for item in items:
        new_path = join(dir, item)
        if isfile(new_path):
            print(f"Copying file {new_path}")
            output_path = join("public", new_path.replace("static/", ""))
            output_dir = dirname(output_path)
            makedirs(output_dir, exist_ok=True)
            shutil.copy(new_path, output_path)
        else:
            print(f"Looking deeper into directoy {new_path}")
            copy_to_public(new_path)


main()
