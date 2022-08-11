import subprocess, shlex

def js_injector(code):
    with open('/usr/src/app/server/compiler/parser/jshelper/in.txt', 'w') as f:
        f.write(code)

    args = shlex.split("node helper.js injectjs")
    subprocess.Popen(args, cwd="/usr/src/app/server/compiler/parser/jshelper/")

    with open('/usr/src/app/server/compiler/parser/jshelper/out.txt', 'r') as f:
        lines = f.readlines()
        print(f.read())

    return "".join(lines)