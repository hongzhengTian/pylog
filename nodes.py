import ast

class Node:
    def __init__(self, ast_node=None):
        self.ast_node = ast_node
        self.name = "LpNode"
    def __repr__(self):
        return str(self.name)

class ConstNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.value = None
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if self.value != None:
            return str(self.value)
        else:
            return "ConstNode: Unknown value"

    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Num):
            self.value = self.ast_node.n
        elif isinstance(self.ast_node, ast.UnaryOp):
            if isinstance(self.ast_node.op, ast.USub):
                self.value = -self.ast_node.operand.n
            elif isinstance(self.ast_node.op, ast.UAdd):
                self.value = self.ast_node.operand.n
        else:
            raise NotImplementedError


class SliceNode(Node):
    def __init__(self, ast_node=None):
        Node.__init__(self, ast_node)
        self.slices = []
        self.dim = None
        self.lower = None
        self.upper = None
        self.step  = None
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if self.dim == 1:
            return str(self.lower)+":"+str(self.upper)+":"+str(self.step)
        else: 
            return "ExtSlice Content"

    def extract_slice(self, ast_node):
        lower = None
        upper = None
        step  = None
        if hasattr(ast_node.lower, "lp_data"):
            lower = ast_node.lower.lp_data.value
        if hasattr(ast_node.upper, "lp_data"):
            upper = ast_node.upper.lp_data.value
        if hasattr(ast_node.step, "lp_data"):
            step = ast_node.step.lp_data.value
        return (lower, upper, step)

    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Slice):
            self.dim = 1
            (self.lower, self.upper, self.step) = self.extract_slice(ast_node)
            self.slices = [(self.lower, self.upper, self.step)]

        elif isinstance(self.ast_node, ast.ExtSlice):
            self.dim = len(self.ast_node.dims)
            self.lower = None
            self.upper = None
            self.slices = [self.extract_slice(s) for s in self.ast_node.dims]

        else:
            raise NotImplementedError


class VariableNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        self.offset = offset
        self.index = index
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        return self.name

    def set_name(self, name):
        self.name = name
    def set_offset(self, offset):
        self.offset = offset
    def set_index(self, index):
        self.index = index
    def extract(self, ast_node):
        if ast_node == None:
            return
        self.ast_node = ast_node
        if isinstance(self.ast_node, ast.Subscript):
            self.name = self.ast_node.value.id
            assert(hasattr(self.ast_node.slice, "lp_data")) # has been traversed
            slice_node = self.ast_node.slice.lp_data
            self.dim = slice_node.dim
            self.upper = slice_node.upper
            self.lower = slice_node.lower
            self.slices = slice_node.slices
        elif isinstance(self.ast_node, ast.Name):
            self.name = self.ast_node.id
            self.offset = None
            self.index = None
        elif isinstance(self.ast_node, ast.arg):
            self.name = self.ast_node.arg
            self.offset = None
            self.index = None
        else:
            raise NotImplementedError

class BinOpNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        if ast_node != None:
            self.extract(ast_node)

    def __repr__(self):
        if isinstance(self.op, ast.Mult):
            return str(self.left) + "*" + str(self.right)


    def extract(self, ast_node):
        self.left = ast_node.left.lp_data
        self.right = ast_node.right.lp_data
        self.op = ast_node.op

class LambdaNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        if ast_node != None:
            self.extract(ast_node)
    def __repr__(self):
        return "LambdaNode"

    def extract(self, ast_node):
        self.args = ast_node.args.lp_data
        self.body = ast_node.body.lp_data

class HmapNode(Node):
    def __init__(self, ast_node=None, name=None, offset=None, index=None):
        Node.__init__(self, ast_node)
        self.name = name
        if ast_node != None:
            self.extract(ast_node)

    def extract(self, ast_node):
        self.func = ast_node.args[0].lp_data
        self.data = ast_node.args[1].lp_data
        self.target = ast_node.parent.targets[0].lp_data
        print(self.func)
        print(self.data)
        print(self.target)
