from unittest import TestCase

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextTypes
from utils import (
    BlockTypes,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_block_to_html_node,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    text_to_text_nodes,
)


class ExtractMarkdownImagesTests(TestCase):
    def test_ExtractMarkdownImages_OneImage_ReturnList(self):
        markdown_images = extract_markdown_images("test ![image](https://someurl.com)")
        self.assertEqual(markdown_images, [("image", "https://someurl.com")])

    def test_ExtractMarkdownImages_OneImage_ReturnListOfTupleWithSizeOne(self):
        markdown_images = extract_markdown_images(
            "test ![image](https://someurl.com) next test ![lantern](www.dark.com) asd"
        )
        self.assertEqual(
            markdown_images,
            [("image", "https://someurl.com"), ("lantern", "www.dark.com")],
        )


class ExtractMarkdownLinksTests(TestCase):
    def test_ExtractMarkdownLinks_Links_ReturnList(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        markdown_links = extract_markdown_links(text)
        self.assertEqual(
            markdown_links,
            [
                ("link", "https://www.example.com"),
                ("another", "https://www.example.com/another"),
            ],
        )

    def test_ExtractMarkdownLinks_Images_DoNotReturnImages(self):
        markdown_links = extract_markdown_links("test ![image](https://someurl.com)")
        self.assertEqual(markdown_links, [])


class MarkdownToBlocksTests(TestCase):
    def test_MarkDownToBlocks_MarkdownProvided_ReturnStringBlocks(self):
        text = (
            "This is **bolded** paragraph\n"
            "\n"
            "This is another paragraph with *italic* text and `code` here\n"
            "This is the same paragraph on a new line\n"
            "\n"
            "* This is a list\n"
            "* with items\n"
        )

        string_blocks = markdown_to_blocks(text)

        expected_blocks = [
            "This is **bolded** paragraph",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            "* This is a list\n* with items",
        ]
        self.assertEqual(string_blocks, expected_blocks)


class TextNodeToHTMLNodeTests(TestCase):
    def test_TextNodeToHTMLNode_TextNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.text)

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(value="test text")
        self.assertEqual(html_node, expected_html_node)

    def test_TextNodeToHTMLNode_BoldNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.bold)

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(tag="b", value="test text")
        self.assertEqual(html_node, expected_html_node)

    def test_TextNodeToHTMLNode_ItalicNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.italic)

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(tag="i", value="test text")
        self.assertEqual(html_node, expected_html_node)

    def test_TextNodeToHTMLNode_CodeNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.code)

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(tag="code", value="test text")
        self.assertEqual(html_node, expected_html_node)

    def test_TextNodeToHTMLNode_LinkNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.link, url="www.test.com")

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(
            tag="a", value="test text", props={"href": "www.test.com"}
        )
        self.assertEqual(html_node, expected_html_node)

    def test_TextNodeToHTMLNode_ImageNode_ReturnHTMLNode(self):
        node = TextNode(text="test text", text_type=TextTypes.image, url="www.test.com")

        html_node = text_node_to_html_node(node)
        expected_html_node = HTMLNode(
            tag="img", value="", props={"src": "www.test.com", "alt": "test text"}
        )
        self.assertEqual(html_node, expected_html_node)


class SplitNodesDelimiterTests(TestCase):
    def test_SplitNodesDelimiter_SplitCode_ReturnTextNodes(self):
        node1 = TextNode(
            text="Heyo, watch this code `console.log('Im cool')` or maybe this code `print('a bit cooler')`",
            text_type=TextTypes.text,
        )
        node2 = TextNode(text="No cool code to see here", text_type=TextTypes.text)
        node3 = TextNode(text="`:(`", text_type=TextTypes.text)

        nodes = split_nodes_delimiter([node1, node2, node3], "`", "code")

        expected_nodes = [
            TextNode(text="Heyo, watch this code ", text_type=TextTypes.text),
            TextNode(text="console.log('Im cool')", text_type=TextTypes.code),
            TextNode(text=" or maybe this code ", text_type=TextTypes.text),
            TextNode(text="print('a bit cooler')", text_type=TextTypes.code),
            TextNode(text="No cool code to see here", text_type=TextTypes.text),
            TextNode(text=":(", text_type=TextTypes.code),
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_SplitNodesDelimiter_SplitBold_ReturnTextNodes(self):
        node1 = TextNode(
            text="Heyo **bold**",
            text_type=TextTypes.text,
        )

        nodes = split_nodes_delimiter([node1], "**", "bold")

        expected_nodes = [
            TextNode(text="Heyo ", text_type=TextTypes.text),
            TextNode(text="bold", text_type=TextTypes.bold),
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_SplitNodesDelimiter_SplitItalic_ReturnTextNodes(self):
        node1 = TextNode(
            text="Heyo *italic*",
            text_type=TextTypes.text,
        )

        nodes = split_nodes_delimiter([node1], "*", "italic")

        expected_nodes = [
            TextNode(text="Heyo ", text_type=TextTypes.text),
            TextNode(text="italic", text_type=TextTypes.italic),
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_SplitNodesDelimiter_UnmatchedDelimiter_RaiseException(self):
        node1 = TextNode(
            text="Heyo *italic",
            text_type=TextTypes.text,
        )

        with self.assertRaises(Exception):
            split_nodes_delimiter([node1], "*", "italic")


class SplitNodesImageTests(TestCase):
    def test_SplitNodesImage_SplitImages_ReturnNodes(self):
        node1 = TextNode(
            text="![image](www.abc.com) heyo ![image2](www.dce.com) a",
            text_type=TextTypes.text,
        )
        node2 = TextNode(text="No image", text_type=TextTypes.text)

        nodes = split_nodes_image([node1, node2])

        expected_nodes = [
            TextNode(text="image", url="www.abc.com", text_type=TextTypes.image),
            TextNode(text=" heyo ", text_type=TextTypes.text),
            TextNode(text="image2", url="www.dce.com", text_type=TextTypes.image),
            TextNode(text=" a", text_type=TextTypes.text),
            TextNode(text="No image", text_type=TextTypes.text),
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_SplitNodesImage_NoImages_ReturnNode(self):
        node = TextNode(text="No image", text_type=TextTypes.text)

        nodes = split_nodes_image([node])

        expected_nodes = [
            TextNode(text="No image", text_type=TextTypes.text),
        ]
        self.assertEqual(nodes, expected_nodes)


class SplitNodesLinksTests(TestCase):
    def test_SplitNodesLinks_SplitLinks_ReturnNodes(self):
        node1 = TextNode(
            text="[link](www.abc.com) heyo [link2](www.dce.com) a",
            text_type=TextTypes.text,
        )
        node2 = TextNode(text="No link", text_type=TextTypes.text)

        nodes = split_nodes_link([node1, node2])

        expected_nodes = [
            TextNode(text="link", url="www.abc.com", text_type=TextTypes.link),
            TextNode(text=" heyo ", text_type=TextTypes.text),
            TextNode(text="link2", url="www.dce.com", text_type=TextTypes.link),
            TextNode(text=" a", text_type=TextTypes.text),
            TextNode(text="No link", text_type=TextTypes.text),
        ]
        self.assertEqual(nodes, expected_nodes)

    def test_SplitNodesImage_NoLink_ReturnNode(self):
        node = TextNode(text="No link", text_type=TextTypes.text)

        nodes = split_nodes_link([node])

        expected_nodes = [
            TextNode(text="No link", text_type=TextTypes.text),
        ]
        self.assertEqual(nodes, expected_nodes)


class TextToTextNodes(TestCase):
    def test_TextToTextNodes_StringBlob_ReturnListOfTextNodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)"
        nodes = text_to_text_nodes(text)

        expected_nodes = [
            TextNode(text="This is ", text_type=TextTypes.text),
            TextNode(text="text", text_type=TextTypes.bold),
            TextNode(text=" with an ", text_type=TextTypes.text),
            TextNode(text="italic", text_type=TextTypes.italic),
            TextNode(text=" word and a ", text_type=TextTypes.text),
            TextNode(text="code block", text_type=TextTypes.code),
            TextNode(text=" and an ", text_type=TextTypes.text),
            TextNode(
                text="image",
                text_type=TextTypes.image,
                url="https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(text=" and a ", text_type=TextTypes.text),
            TextNode(text="link", text_type=TextTypes.link, url="https://boot.dev"),
        ]
        self.assertEqual(nodes, expected_nodes)


class BlockToBlockTypeTests(TestCase):
    def test_BlockToBlockType_Headings_ParseItCorrectly(self):
        self._test_heading("# a")
        self._test_heading("## a")
        self._test_heading("### a")
        self._test_heading("#### a")
        self._test_heading("##### a")
        self._test_heading("###### a")

        block_type = block_to_block_type("######### abc")
        self.assertNotEqual(block_type, BlockTypes.heading)

    def _test_heading(self, string: str):
        block_type = block_to_block_type(string)
        self.assertEqual(block_type, BlockTypes.heading)

    def test_BlockToBlockType_Code_ParseItCorrectly(self):
        block_type = block_to_block_type("```abc\nassd\n   asdsa!!1212()\n```")
        self.assertEqual(block_type, BlockTypes.code)

        block_type = block_to_block_type("```abc\n")
        self.assertNotEqual(block_type, BlockTypes.code)

    def test_BlockToBlockType_Quote_ParseItCorrectly(self):
        block_type = block_to_block_type(">a\n>b\n>c")
        self.assertEqual(block_type, BlockTypes.quote)

        block_type = block_to_block_type(">a\n>b\nc")
        self.assertNotEqual(block_type, BlockTypes.quote)

    def test_BlockToBlockType_UnorderedList_ParseItCorrectly(self):
        block_type = block_to_block_type("* a\n* b\n* c")
        self.assertEqual(block_type, BlockTypes.unordered_list)

        block_type = block_to_block_type("- a\n- b\n- c")
        self.assertEqual(block_type, BlockTypes.unordered_list)

        block_type = block_to_block_type("- a\n- b\nc")
        self.assertNotEqual(block_type, BlockTypes.unordered_list)

    def test_BlockToBlockType_OrderedList_ParseItCorrectly(self):
        block_type = block_to_block_type("1. a\n2. b\n3. c")
        self.assertEqual(block_type, BlockTypes.ordered_list)

        block_type = block_to_block_type("1. a\n2. b\n2. c")
        self.assertNotEqual(block_type, BlockTypes.ordered_list)

        block_type = block_to_block_type("1. a\n2. b\nc")
        self.assertNotEqual(block_type, BlockTypes.ordered_list)

    def test_BlockToBlockType_Paragraph_ParseItCorrectly(self):
        block_type = block_to_block_type("ANYTHING\n\n\nABC")
        self.assertEqual(block_type, BlockTypes.paragraph)


class MarkdownBlockToHtmlNodeTests(TestCase):
    def test_MarkdownBlockToHtmlNode_Headings_ReturnHTMLNodes(self):
        self.assert_heading("# New heading abcd", "h1")
        self.assert_heading("## New heading abcd", "h2")
        self.assert_heading("### New heading abcd", "h3")
        self.assert_heading("#### New heading abcd", "h4")
        self.assert_heading("##### New heading abcd", "h5")
        self.assert_heading("###### New heading abcd", "h6")

    def assert_heading(self, text: str, expected_tag: str):
        html_block = markdown_block_to_html_node(text, BlockTypes.heading)
        children = [LeafNode(value="New heading abcd")]
        expected_node = ParentNode(tag=expected_tag, children=children)
        self.assertEqual(html_block, expected_node)

    def test_MarkdownBlockToHtmlNode_Paragraph_ReturnHTMLNodes(self):
        html_block = markdown_block_to_html_node(
            "Heyo *italic* soup", BlockTypes.paragraph
        )
        children = [
            LeafNode(value="Heyo "),
            LeafNode(tag="i", value="italic"),
            LeafNode(value=" soup"),
        ]
        expected_node = ParentNode(tag="p", children=children)
        self.assertEqual(html_block, expected_node)

    def test_MarkdownBlockToHtmlNode_Code_ReturnHTMLNodes(self):
        html_block = markdown_block_to_html_node(
            "```imaginary_code_language\nthe_best_code_ever();\n```",
            BlockTypes.code,
        )
        children = [
            LeafNode(value="imaginary_code_language\nthe_best_code_ever();"),
        ]
        code_node = ParentNode(tag="code", children=children)
        expected_node = ParentNode(tag="pre", children=[code_node])
        self.assertEqual(html_block, expected_node)

    def test_MarkdownBlockToHtmlNode_Quote_ReturnHTMLNodes(self):
        html_block = markdown_block_to_html_node(
            "> A **hero**\n>a\n>a",
            BlockTypes.quote,
        )
        children = [
            LeafNode(value=" A "),
            LeafNode(tag="b", value="hero"),
            LeafNode(value="\na\na"),
        ]
        expected_node = ParentNode(tag="blockquote", children=children)
        self.assertEqual(html_block, expected_node)

    def test_MarkdownBlockToHtmlNode_UnorderedList_ReturnHTMLNodes(self):
        html_block = markdown_block_to_html_node(
            "* A\n* B",
            BlockTypes.unordered_list,
        )
        children = [
            ParentNode(tag="li", children=[LeafNode(value="A")]),
            ParentNode(tag="li", children=[LeafNode(value="B")]),
        ]
        expected_node = ParentNode(tag="ul", children=children)
        self.assertEqual(html_block, expected_node)

        html_block = markdown_block_to_html_node(
            "- A\n- B",
            BlockTypes.unordered_list,
        )
        children = [
            ParentNode(tag="li", children=[LeafNode(value="A")]),
            ParentNode(tag="li", children=[LeafNode(value="B")]),
        ]
        expected_node = ParentNode(tag="ul", children=children)
        self.assertEqual(html_block, expected_node)

    def test_MarkdownBlockToHtmlNode_OrderedList_ReturnHTMLNodes(self):
        html_block = markdown_block_to_html_node(
            "1. A\n2. B",
            BlockTypes.ordered_list,
        )
        children = [
            ParentNode(tag="li", children=[LeafNode(value="A")]),
            ParentNode(tag="li", children=[LeafNode(value="B")]),
        ]
        expected_node = ParentNode(tag="ol", children=children)
        self.assertEqual(html_block, expected_node)


markdown = """
# Heading 1

A paragraph *italic* **bold** ![img](www.a.c) [link](www.a.c)

## Heading 2

```code```

### Heading 3

>Quote

#### Heading 4

* Unordered
* List

##### Heading 5

1. Ordered list
"""


class MarkdownToHtmlNode(TestCase):
    def test_MarkdownToHtmlNode_BigMarkDown_ReturnHtmlNode(self):
        html_node = markdown_to_html_node(markdown)
        children = [
            ParentNode(
                tag="h1",
                children=[
                    LeafNode(value="Heading 1"),
                ],
            ),
            ParentNode(
                tag="p",
                children=[
                    LeafNode(value="A paragraph "),
                    LeafNode(tag="i", value="italic"),
                    LeafNode(value=" "),
                    LeafNode(tag="b", value="bold"),
                    LeafNode(value=" "),
                    LeafNode(
                        tag="img",
                        value="",
                        props={"src": "www.a.c", "alt": "img"},
                    ),
                    LeafNode(value=" "),
                    LeafNode(tag="a", value="link", props={"href": "www.a.c"}),
                ],
            ),
            ParentNode(
                tag="h2",
                children=[
                    LeafNode(value="Heading 2"),
                ],
            ),
            ParentNode(
                tag="pre",
                children=[
                    ParentNode(tag="code", children=[LeafNode(value="code")]),
                ],
            ),
            ParentNode(
                tag="h3",
                children=[LeafNode(value="Heading 3")],
            ),
            ParentNode(tag="blockquote", children=[LeafNode(value="Quote")]),
            ParentNode(
                tag="h4",
                children=[LeafNode(value="Heading 4")],
            ),
            ParentNode(
                tag="ul",
                children=[
                    ParentNode(
                        tag="li",
                        children=[
                            LeafNode(value="Unordered"),
                        ],
                    ),
                    ParentNode(
                        tag="li",
                        children=[
                            LeafNode(value="List"),
                        ],
                    ),
                ],
            ),
            ParentNode(
                tag="h5",
                children=[LeafNode(value="Heading 5")],
            ),
            ParentNode(
                tag="ol",
                children=[
                    ParentNode(
                        tag="li",
                        children=[
                            LeafNode(value="Ordered list"),
                        ],
                    )
                ],
            ),
        ]
        expected_node = ParentNode(tag="div", children=children)
        self.assertEqual(html_node, expected_node)
