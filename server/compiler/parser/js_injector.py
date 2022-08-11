import subprocess, shlex

def js_injector(code):
    with open('/app/compiler/parser/jshelper/in.txt', 'w') as f:
        f.write(code)

    args = shlex.split("node helper.js injectjs")
    subprocess.Popen(args, cwd="/app/compiler/parser/jshelper/")

    with open('/app/compiler/parser/jshelper/out.txt', 'r') as f:
        lines = f.readlines()
        print(f.read())

    return "".join(lines)