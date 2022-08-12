import subprocess

def java_injector(code):
    with open('app/helpers/parser/javahelper/in.txt', 'w') as f:
        f.write(code)

    process = subprocess.Popen("python runJava.py inject", cwd="./app/helpers/parser/javahelper")
    process.wait()

    with open('app/helpers/parser/javahelper/out.txt', 'r') as f:
        lines = f.readlines()

    return "".join(lines)