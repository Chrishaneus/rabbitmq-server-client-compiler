#!/usr/bin/env python
import re
from pycparser import c_parser, c_ast, c_generator, parse_file

loop_counter = "AZEUS_LOOP_COUNTER"
call_counter = "AZEUS_CALL_COUNTER"

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'): return " "
        else: return s
        
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )

    return re.sub(pattern, replacer, text)

def include_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('#'): return ' '
        else: return s
        
    pattern = re.compile(
        r'\#include\s*<.*?>|\#include\s*".*?"',
    )

    return re.sub(pattern, replacer, text)

def include_finder(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('#'): return " "
        else: return s
        
    pattern = re.compile(
        r'\#include\s*<.*?>|\#include\s*".*?"',
    )

    return re.findall(pattern, text)

class MainVisit(c_ast.NodeVisitor):
    def __init__(self):
        self.count = c_parser.CParser().parse(
                """
                    int main() {{
                        int {loop} = 0, {call} = 0;
                        {loop}++;
                        {call}++;
                        printf("\\n{loop} = %d\\n{call} = %d", {loop}, {call});
                    }}
                """.format(loop=loop_counter, call=call_counter)
        )

        self.lcdecl = self.count.children()[0][1].body.block_items[0] # LOOP_COUNTER -> DECLARATION
        self.ccdecl = self.count.children()[0][1].body.block_items[1] # CALL_COUNTER -> DECLARATION
        self.lcincr = self.count.children()[0][1].body.block_items[2] # CALL_COUNTER -> UNARY_OPERATOR ON LOOP_COUNTER (INCREMENT)
        self.ccincr = self.count.children()[0][1].body.block_items[3] # CALL_COUNTER -> UNARY_OPERATOR ON CALL_COUNTER (INCREMENT)
        self.printf = self.count.children()[0][1].body.block_items[4] # CALL_COUNTER -> FUNCTION_CALL PRINT RESULTS

    def visit_Compound(self, node):
        if node.block_items:
            for index in range(len(node.block_items)):
                if isinstance(node.block_items[index], c_ast.Return):
                    node.block_items.insert(index,self.printf); break
                    
            self.visit(node.block_items)

    def visit_If(self, node):
        if node.iftrue: self.visit(node.iftrue)
        if node.iffalse: self.visit(node.iffalse)

        if isinstance(node.iftrue,c_ast.Return):
            node.iftrue = c_ast.Compound([self.printf, node.iftrue])

        if isinstance(node.iffalse,c_ast.Return):
            node.iffalse = c_ast.Compound([self.printf, node.iffalse])

    def visit_Case(self, node):
        if node.stmts:
            self.visit(node.stmts)
            for index in range(len(node.stmts)):
                if isinstance(node.stmts[index], c_ast.Return):
                    node.stmts.insert(index,self.printf); break

class CCounter(c_ast.NodeVisitor):
    def __init__(self):
        self.count = c_parser.CParser().parse(
                """
                    int main() {{
                        int {loop} = 0, {call} = 0;
                        {loop}++;
                        {call}++;
                        printf("\\n{loop} = %d\\n{call} = %d", {loop}, {call});
                    }}
                """.format(loop=loop_counter, call=call_counter)
        )

        self.lcdecl = self.count.children()[0][1].body.block_items[0] # LOOP_COUNTER -> DECLARATION
        self.ccdecl = self.count.children()[0][1].body.block_items[1] # CALL_COUNTER -> DECLARATION
        self.lcincr = self.count.children()[0][1].body.block_items[2] # CALL_COUNTER -> UNARY_OPERATOR ON LOOP_COUNTER (INCREMENT)
        self.ccincr = self.count.children()[0][1].body.block_items[3] # CALL_COUNTER -> UNARY_OPERATOR ON CALL_COUNTER (INCREMENT)
        self.printf = self.count.children()[0][1].body.block_items[4] # CALL_COUNTER -> FUNCTION_CALL PRINT RESULTS

    def visit_FileAST(self,node):
        if node.ext:
            self.visit(node.ext)

        node.ext.insert(0,self.lcdecl)
        node.ext.insert(0,self.ccdecl)

    def visit_FuncDef(self, node):
        if node.body.block_items:
            node.body.block_items.insert(0,self.ccincr)
        else: node.body.block_items = [self.ccincr]

        # Add the print statement to the end of the function
        if node.decl.name == "main":
            main_visit = MainVisit()
            node.body.block_items.append(self.printf)
            main_visit.visit(node.body)

        # Visit body in case it contains more func calls.
        if node.body.block_items:
            self.visit(node.body)

    def visit_For(self, node):
        if 'block_items' in dir(node.stmt):
            if node.stmt.block_items:
                node.stmt.block_items.insert(0,self.lcincr)
            else: node.stmt.block_items = [self.lcincr]

            # Visit statement in case it contains more func calls.
            if node.stmt.block_items:
                self.visit(node.stmt)
        else:
            compound = c_ast.Compound([self.lcincr, node.stmt])
            node.stmt = compound
            self.visit(node.stmt)

    def visit_While(self, node):
        if 'block_items' in dir(node.stmt):
            if node.stmt.block_items:
                node.stmt.block_items.insert(0,self.lcincr)
            else: node.stmt.block_items = [self.lcincr]

            # Visit statement in case it contains more func calls.
            if node.stmt.block_items:
                self.visit(node.stmt)
        else:
            compound = c_ast.Compound([self.lcincr, node.stmt])
            node.stmt = compound
            self.visit(node.stmt)

    def visit_DoWhile(self, node):
        if 'block_items' in dir(node.stmt):
            if node.stmt.block_items:
                node.stmt.block_items.insert(0,self.lcincr)
            else: node.stmt.block_items = [self.lcincr]

            # Visit statement in case it contains more func calls.
            if node.stmt.block_items:
                self.visit(node.stmt)
        else:
            compound = c_ast.Compound([self.lcincr, node.stmt])
            node.stmt = compound
            self.visit(node.stmt)

def c_injector(code):
    generator = c_generator.CGenerator()
    parser = c_parser.CParser()
    counter = CCounter()
    tree = parser.parse(include_remover(comment_remover(code)))
    counter.visit(tree)
    headers = include_finder(code)
    return "\n".join(headers) + "\n" + generator.visit(tree)