from unittest import TestCase

from htmlnode import HTMLNode, LeafNode, ParentNode


class HtmlNodeTests(TestCase):
    def test_Repr(self):
        child_node = HTMLNode(tag="span", value="My friend")
        node = HTMLNode(
            tag="h1", value="MONAMI", children=[child_node], props={"class": "header"}
        )
        self.assertEqual(
            str(node),
            "HTMLNode(h1, MONAMI, [HTMLNode(span, My friend, None, None)], {'class': 'header'})",
        )

    def test_PropsToHtml_PropsProvided_ReturnString(self):
        props = {"href": "abc.com", "class": "xyd"}
        node = HTMLNode(props=props)
        self.assertEqual(node.props_to_html(), 'href="abc.com" class="xyd"')

    def test_PropsToHtml_PropsNotProvided_ReturnEmpty(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")


class LeafNodeTests(TestCase):
    def test_ToHtml_LeafNodesProvided_ReturnHTML(self):
        node = LeafNode(tag="p", value="This is a paragraph of text.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")

        node = LeafNode(
            tag="a", value="Click me!", props={"href": "https://www.google.com"}
        )
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_ToHtml_NoValue_RaiseValueError(self):
        node = LeafNode(value=None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_ToHtml_NoTag_ReturnValue(self):
        node = LeafNode(value="abc")
        self.assertEqual(node.to_html(), "abc")


class ParentNodeTests(TestCase):
    def test_ToHtml_ParentNodeProvided_ReturnHTML(self):
        node = ParentNode(
            tag="p",
            children=[
                LeafNode(tag="b", value="Bold text"),
                LeafNode(tag=None, value="Normal text"),
                LeafNode(tag="i", value="italic text"),
                LeafNode(tag=None, value="Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_ToHtml_NestedParentNodes_ReturnHTML(self):
        nested_node = ParentNode(
            tag="p",
            children=[
                LeafNode(tag="b", value="Bold text"),
                LeafNode(tag=None, value="Normal text"),
                LeafNode(tag="i", value="italic text"),
                LeafNode(tag=None, value="Normal text"),
            ],
            props={"class": "classy"},
        )
        node = ParentNode(tag="h1", children=[nested_node])
        self.assertEqual(
            node.to_html(),
            '<h1><p class="classy"><b>Bold text</b>Normal text<i>italic text</i>Normal text</p></h1>',
        )

    def test_ToHtml_EmptyChildren_ReturnHtml(self):
        node = ParentNode(tag="h1", children=[])
        self.assertEqual(node.to_html(), "<h1></h1>")

    def test_ToHtml_NoTag_RaiseValueError(self):
        node = ParentNode(children=[])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_ToHtml_ChildrenNone_RaiseValueError(self):
        node = ParentNode(children=None)
        with self.assertRaises(ValueError):
            node.to_html()
