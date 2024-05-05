import re
from collections.abc import Callable
from enum import StrEnum
from os import makedirs
from os.path import dirname
from typing import cast

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextTypes


def extract_markdown_images(text: str) -> tuple[str, str]:
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    matches = cast(tuple[str, str], matches)
    return matches


def extract_markdown_links(text: str) -> tuple[str, str]:
    matches = re.findall(r"(?<![!])\[(.*?)\]\((.*?)\)", text)
    matches = cast(tuple[str, str], matches)
    return matches


def markdown_to_blocks(markdown: str) -> list[str]:
    split_markdown = markdown.split("\n\n")
    stripped_markdown = [string.strip() for string in split_markdown]
    output_string_blocks = [string for string in stripped_markdown if string != ""]
    return output_string_blocks


def text_node_to_html_node(node: TextNode) -> LeafNode:
    match node.text_type:
        case TextTypes.text:
            return LeafNode(value=node.text)
        case TextTypes.bold:
            return LeafNode(tag="b", value=node.text)
        case TextTypes.italic:
            return LeafNode(tag="i", value=node.text)
        case TextTypes.code:
            return LeafNode(tag="code", value=node.text)
        case TextTypes.link:
            return LeafNode(tag="a", value=node.text, props={"href": node.url})
        case TextTypes.image:
            return LeafNode(
                tag="img", value="", props={"src": node.url, "alt": node.text}
            )
        case _:
            raise Exception("TextNode text_type is invalid")


class BlockTypes(StrEnum):
    paragraph = "paragraph"
    heading = "heading"
    code = "code"
    quote = "quote"
    unordered_list = "unordered_list"
    ordered_list = "ordered_list"


def block_to_block_type(markdown_text: str) -> BlockTypes:
    is_heading = re.match(r"^(\#{1,6} )", markdown_text)
    if is_heading:
        return BlockTypes.heading

    is_code_block = re.match(r"(^```(.|\n)*```$)", markdown_text)
    if is_code_block:
        return BlockTypes.code

    if _is_quote(markdown_text):
        return BlockTypes.quote

    if _is_unordered_list(markdown_text):
        return BlockTypes.unordered_list

    if _is_ordered_list(markdown_text):
        return BlockTypes.ordered_list

    return BlockTypes.paragraph


def _is_quote(markdown: str) -> bool:
    return _starts_with_str_on_every_line(markdown, ">")


def _is_unordered_list(markdown: str) -> bool:
    return _starts_with_str_on_every_line(
        markdown, "* "
    ) or _starts_with_str_on_every_line(markdown, "- ")


def _starts_with_str_on_every_line(markdown: str, starting_str: str) -> bool:
    lines = markdown.split("\n")
    for line in lines:
        if not line.startswith(starting_str):
            return False
    return True


def _is_ordered_list(markdown) -> bool:
    lines = markdown.split("\n")
    for index, line in enumerate(lines):
        if not line.startswith(f"{index + 1}. "):
            return False
    return True


def markdown_block_to_html_node(
    markdown_block: str, block_type: BlockTypes
) -> HTMLNode:
    match block_type:
        case BlockTypes.paragraph:
            return _to_paragraph(markdown_block)
        case BlockTypes.heading:
            return _to_heading(markdown_block)
        case BlockTypes.code:
            return _to_code(markdown_block)
        case BlockTypes.quote:
            return _to_quote(markdown_block)
        case BlockTypes.unordered_list:
            return _to_list(markdown_block, "ul")
        case BlockTypes.ordered_list:
            return _to_list(markdown_block, "ol")
        case _:
            raise Exception("Invalid block type")


def _to_paragraph(markdown_block: str) -> HTMLNode:
    children = get_children_from_text(markdown_block)
    return ParentNode(tag="p", children=children)


def _to_heading(markdown_block: str) -> HTMLNode:
    heading_number = 0
    for char in markdown_block:
        if char != "#":
            break
        heading_number += 1
    markdown_block = markdown_block[heading_number + 1 :]

    children = get_children_from_text(markdown_block)
    return ParentNode(tag=f"h{heading_number}", children=children)


def _to_code(markdown_block: str) -> HTMLNode:
    markdown_block = markdown_block[3:-3]
    markdown_block = markdown_block.strip()
    children = get_children_from_text(markdown_block)
    code_block = ParentNode(tag="code", children=children)
    return ParentNode(tag="pre", children=[code_block])


def _to_quote(markdown_block: str) -> HTMLNode:
    text = "".join(markdown_block.split(">"))
    children = get_children_from_text(text)
    return ParentNode(tag="blockquote", children=children)


def _to_list(markdown_block: str, tag: str) -> HTMLNode:
    lines = markdown_block.split("\n")
    cleaned_lines = []
    for line in lines:
        cleaned_lines.append(line.split(" ", 1)[1])
    list_items = []
    for line in cleaned_lines:
        children = get_children_from_text(line)
        list_item = ParentNode(tag="li", children=children)
        list_items.append(list_item)
    return ParentNode(tag=tag, children=list_items)


def get_children_from_text(text: str) -> list[HTMLNode]:
    text_nodes = text_to_text_nodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: str
) -> list[TextNode]:
    nodes = []
    for node in old_nodes:
        if node.text_type != TextTypes.text:
            nodes.append(node)
            continue
        nodes.extend(_split_text_node(node, delimiter, text_type))
    return nodes


def _split_text_node(node: TextNode, delimiter, text_type) -> list[TextNode]:
    split_text = node.text.split(delimiter)
    if len(split_text) % 2 == 0:
        raise Exception("Mismatching amount of delimiters")

    nodes = []
    for index, text in enumerate(split_text):
        if text == "":
            continue

        if index % 2 == 0:
            nodes.append(TextNode(text=text, text_type=TextTypes.text))
        else:
            nodes.append(TextNode(text=text, text_type=text_type))
    return nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _image_and_link_splitter(
        old_nodes, extract_markdown_images, "![{0}]({1})", TextTypes.image
    )


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _image_and_link_splitter(
        old_nodes, extract_markdown_links, "[{0}]({1})", TextTypes.link
    )


def _image_and_link_splitter(
    old_nodes: list[TextNode], extract_func: Callable, pattern, text_type: TextTypes
) -> list[TextNode]:
    nodes = []
    for node in old_nodes:
        if node.text_type != TextTypes.text:
            nodes.append(node)
            continue

        images_tuple = extract_func(node.text)

        if len(images_tuple) == 0:
            nodes.append(node)
            continue

        text = node.text
        for image_text, image_url in images_tuple:
            split_node = text.split(pattern.format(image_text, image_url), 1)
            preceeding_text = split_node[0]
            if preceeding_text != "":
                nodes.append(TextNode(text=preceeding_text, text_type=TextTypes.text))
            nodes.append(TextNode(text=image_text, url=image_url, text_type=text_type))
            text = split_node[1]
        if text != "":
            nodes.append(TextNode(text=text, text_type=TextTypes.text))
    return nodes


def text_to_text_nodes(text) -> list[TextNode]:
    node = TextNode(text=text, text_type=TextTypes.text)
    nodes = split_nodes_delimiter([node], "`", TextTypes.code)
    nodes = split_nodes_delimiter(nodes, "**", TextTypes.bold)
    nodes = split_nodes_delimiter(nodes, "*", TextTypes.italic)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_html_node(markdown: str) -> ParentNode:
    text_blocks = markdown_to_blocks(markdown)
    blocks_and_types = []
    for block in text_blocks:
        block_type = block_to_block_type(block)
        blocks_and_types.append((block, block_type))
    children = [
        markdown_block_to_html_node(block, block_type)
        for block, block_type in blocks_and_types
    ]
    return ParentNode(tag="div", children=children)


def extract_title(markdown: str) -> str:
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:]
    raise Exception("No header found")


def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown_content = ""
    with open(from_path) as file:
        markdown_content = file.read()

    template_content = ""
    with open(template_path) as file:
        template_content = file.read()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)

    template_content = template_content.replace("{{ Title }}", title)
    template_content = template_content.replace("{{ Content }}", html)

    dir_path = dirname(dest_path)
    makedirs(dir_path, exist_ok=True)
    with open(dest_path, mode="w") as file:
        file.write(template_content)
