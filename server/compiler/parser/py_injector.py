import ast, astor

loop_counter = "AZEUS_LOOP_COUNTER"
call_counter = "AZEUS_CALL_COUNTER"

class PythonCounter(ast.NodeTransformer):
    def __init__(self):
        self.counters = ast.parse("{} = 0; {} = 0".format(loop_counter, call_counter))
        self.global_ = ast.parse("global {}, {}".format(loop_counter, call_counter))
        self.increment_loop = ast.parse("{} += 1".format(loop_counter))
        self.increment_call = ast.parse("{} += 1".format(call_counter))
        self.count = ast.parse("print('\\n{loop} =',{loop}, '\\n{call} =', {call})".format(loop=loop_counter,call=call_counter))

    def visit_Module(self, node):
        node.body.insert(0,self.counters.body[0])
        node.body.insert(0,self.counters.body[1])
        node.body.append(self.count.body[0])
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        node.body = [self.global_.body[0],self.increment_call.body[0]] + node.body
        self.generic_visit(node)
        return node

    def visit_For(self, node):
        node.body.insert(0,self.increment_loop.body[0])
        self.generic_visit(node)
        return node

    def visit_While(self, node):
        node.body.insert(0,self.increment_loop.body[0])
        self.generic_visit(node)
        return node

def py_injector(code):
    tree = ast.parse(code)
    renamer = PythonCounter()
    newtree = renamer.visit(tree)
    return(astor.to_source(newtree))