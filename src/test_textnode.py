import unittest

from textnode import TextNode, TextTypes


class TextNodeTests(unittest.TestCase):
    def test_Eq(self):
        node = TextNode(text="This is a text node", text_type=TextTypes.bold)
        node2 = TextNode(text="This is a text node", text_type=TextTypes.bold)
        self.assertEqual(node, node2)

    def test_Eq_NotEq(self):
        node = TextNode(text="A", text_type=TextTypes.bold)
        node2 = TextNode(text="B", text_type=TextTypes.bold)
        self.assertNotEqual(node, node2)

        node = TextNode(text="A", text_type=TextTypes.bold)
        node2 = TextNode(text="A", text_type=TextTypes.italic)
        self.assertNotEqual(node, node2)

    def test_Url(self):
        node = TextNode(text="A", text_type=TextTypes.bold)
        self.assertIsNone(node.url)

        node = TextNode(text="A", text_type=TextTypes.bold, url="haha")
        self.assertEqual(node.url, "haha")


if __name__ == "__main__":
    unittest.main()
