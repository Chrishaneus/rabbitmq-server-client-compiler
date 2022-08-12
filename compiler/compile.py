import shlex, subprocess, os, time, json, javalang
from subprocess import PIPE, Popen, run
from compiler.parser.ast_parser import inject, exec_details
os.environ['PYTHONIOENCODING'] = 'utf-8'

lang_details = json.load(open('/app/compiler/lang.json'))

# Executes a shell command
def get_exitcode_stdout_stderr(cmd, test = None, timeout=5):
    args = shlex.split(cmd)

    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    init_time = time.time()

    try: out, err = proc.communicate(input=test,timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = "", "Timeout occured - {}".format(timeout)

    exec_time = time.time() - init_time
    exitcode = proc.returncode if proc.returncode != None else -1
    return exitcode, out, err, exec_time

def java_class_name(code):
    tree = javalang.parse.parse(code)
    name = next(klass.name for klass in tree.types
            if isinstance(klass, javalang.tree.ClassDeclaration)
            for m in klass.methods
            if m.name == 'main' and m.modifiers.issuperset({'public', 'static'}))
    return name

# Write to a file
def write_code_to_file(filename, ext, content):
    with open(filename+'.'+ext, 'w') as f:
        f.write(content)

def compile(code, lang, tests, filename='temp'):
    # Get details of the language for compilation
    language = list(filter(lambda language: language['lang'] == lang, lang_details))

    # Special handling for Java codes
    if lang == 'java':
        filename = java_class_name(code)
    
    # If the language is not found, return error
    if len(language) == 0:
        return (
            [-1 for i in range(len(tests))],
            ["Language is not supported" for i in range(len(tests))],
            [ 0 for i in range(len(tests))],
            [-2 for i in range(len(tests))],
            [-2 for i in range(len(tests))],
        )
    else: language = language[0]
    
    # Initialize the return variables and write code to file
    exitcodes = []; stdout = []; exec_time = []; loop_count = []; call_count = []
    write_code_to_file(filename=filename, ext=language['extension'], content=code)

    # Compile the code
    for stdin in tests:
        for template in language['commands']:
            command = template.format(filename=filename)
            exitcode, out, err, exec_t = get_exitcode_stdout_stderr(command, stdin)
            if exitcode: break
        
        stdout.append(err if exitcode else out)
        exec_time.append(exec_t)
        exitcodes.append(exitcode)

    try:
        injected = inject(code,lang)
        write_code_to_file(filename=filename+"_injected", ext=language['extension'], content=injected)
        
        for stdin in tests:
            for template in language['commands']:
                command = template.format(filename=filename+"_injected")
                exitcode, out, err, exec_t = get_exitcode_stdout_stderr(command, stdin)
                if exitcode: break
            if exitcode:
                loop_count.append(-1)
                call_count.append(-1)
            else:
                loop_cnt, call_cnt = exec_details(err if exitcode else out)
                loop_count.append(loop_cnt if loop_cnt != None else -3)
                call_count.append(call_cnt if call_cnt != None else -3)
    except:
        loop_count.append(-2)
        call_count.append(-2)

    try: # remove the temporary file
        os.remove(filename+'.'+language['extension']) # Initial files
        os.remove(filename+'_injected'+'.'+language['extension']) # Injection
        os.remove(filename+'.'+'class') # Java classes
        os.remove(filename) # C and C++ binary files
    except: pass

    return exitcodes, stdout, exec_time, loop_count, call_count