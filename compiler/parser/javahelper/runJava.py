import os, sys

text_file = open("classpath.args", "r")
classpathArgs = text_file.read()
text_file.close()

args = [] if len(sys.argv) <= 1 else sys.argv[1:]
command = " ".join(['java', classpathArgs, "App"] + args)
os.system(command)