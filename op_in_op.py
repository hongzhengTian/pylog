import ast
import astor

class OpInOpTransformer(ast.NodeTransformer):
    def __init__(self):
        self.tmp_var_counter = 0

    def visit_FunctionDef(self, node):
        self.generic_visit(node) 
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                # if stmt is an assignment of a function call
                self.process_call(stmt.value, new_body)
                # add the original assignment
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        node.body = new_body
        return node

    def process_call(self, call_node, new_body):
        for i, arg in enumerate(call_node.args):
            if isinstance(arg, ast.Call):
                self.process_call(arg, new_body) # recursively process the call,
                # if the argument is a call, we need to create a new tmp variable
                # to store the result of the call
                tmp_var_name = f"_tmp_call_var_{self.tmp_var_counter}"
                # increment the counter to record the number of tmp variables
                self.tmp_var_counter += 1

                # create a new variable and assign the call result to it
                tmp_assign = ast.Assign(
                    targets=[ast.Name(id=tmp_var_name, ctx=ast.Store())],
                    value=arg
                )

                new_body.append(tmp_assign)

                call_node.args[i] = ast.Name(id=tmp_var_name, ctx=ast.Load())