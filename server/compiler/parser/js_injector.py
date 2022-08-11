import subprocess

def js_injector(code):
    with open('app/helpers/parser/jshelper/in.txt', 'w') as f:
        f.write(code)

    subprocess.Popen("node helper.js injectjs", cwd="./app/helpers/parser/jshelper")

    with open('app/helpers/parser/jshelper/out.txt', 'r') as f:
        lines = f.readlines()
        print(f.read())

    return "".join(lines)