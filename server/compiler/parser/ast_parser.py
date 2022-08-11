import re
from pprint import pprint
from compiler.parser.c_injector import c_injector
from compiler.parser.py_injector import py_injector
from compiler.parser.js_injector import js_injector

loop_counter = "AZEUS_LOOP_COUNTER"
call_counter = "AZEUS_CALL_COUNTER"

def detail_finder(text):
    loop_pattern = re.compile(
        r'{}\s=\s([0-9]+)'.format(loop_counter),
    )

    call_pattern = re.compile(
        r'{}\s=\s([0-9]+)'.format(call_counter),
    )

    return re.findall(loop_pattern, text), re.findall(call_pattern, text)

def inject(code,language):
    if language == "c":
        return c_injector(code)

    elif language == "c++":
        return code

    elif language == "javascript":
        return js_injector(code)

    elif language == "python":
        return py_injector(code)

def exec_details(ret):
    loop_count, call_count = detail_finder(ret)
    if len(loop_count): loop_count = int(loop_count[-1])
    if len(call_count): call_count = int(call_count[-1])
    return loop_count, call_count

# injected = inject(open('resources/codes/py/1.py','r').read(),'python')
# print(injected)