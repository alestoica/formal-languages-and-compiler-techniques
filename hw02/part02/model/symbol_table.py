from model.node import Node


class SymbolTable:
    def __init__(self):
        self.root = None
        self.current_index = 1
        self.symbols = {}

    def insert(self, value):
        if self.root is None:
            self.root = Node(value, self.current_index)
            self.symbols[value] = self.root
            self.current_index += 1
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value, self.current_index)
                self.symbols[value] = node.left
                self.current_index += 1
            else:
                self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = Node(value, self.current_index)
                self.symbols[value] = node.right
                self.current_index += 1
            else:
                self._insert_recursive(node.right, value)

    def find(self, value):
        return self._find_recursive(self.root, value)

    def _find_recursive(self, node, value):
        if node is None:
            return None
        if node.value == value:
            return node.index
        elif value < node.value:
            return self._find_recursive(node.left, value)
        else:
            return self._find_recursive(node.right, value)

    def to_list(self):
        result = []
        self._in_order_traversal(self.root, result)
        return sorted(result, key=lambda x: x[0])

    def _in_order_traversal(self, node, result):
        if node is not None:
            self._in_order_traversal(node.left, result)
            result.append((node.value, node.index,
                           node.left.index if node.left else "-1",
                           node.right.index if node.right else "-1"))
            self._in_order_traversal(node.right, result)
