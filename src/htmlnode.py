from typing import Self


class HTMLNode:
    def __init__(
        self,
        *,
        tag: str | None = None,
        value: str | None = None,
        children: list[Self] | None = None,
        props: dict | None = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        output = ""
        if self.props is not None:
            for key, value in self.props.items():
                output += f'{key}="{value}" '
            output = output[:-1]
        return output

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

    def __eq__(self, other_node) -> bool:
        return (
            self.tag == other_node.tag
            and self.value == other_node.value
            and self.children == other_node.children
            and self.props == other_node.props
        )


class LeafNode(HTMLNode):
    def __init__(
        self, *, tag: str | None = None, value: str, props: dict | None = None
    ):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("A leaf node requires a value")

        if self.tag is None:
            return self.value

        props = self.props_to_html()
        if props != "":
            return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"
        else:
            return f"<{self.tag}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(
        self,
        *,
        tag: str | None = None,
        children: list[HTMLNode],
        props: dict | None = None,
    ):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if self.tag is None or self.tag == "":
            raise ValueError("Need to provide a tag")
        if self.children is None:
            raise ValueError("Need to provide children")

        output = f"<{self.tag}"
        props = self.props_to_html()
        if props != "":
            output += f" {self.props_to_html()}"
        output += ">"
        for child in self.children:
            output += child.to_html()
        output += f"</{self.tag}>"
        return output
