import os, sys, subprocess

text_file = open("classpath.args", "r")
classpathArgs = text_file.read()
text_file.close()

command = " ".join(['javac', classpathArgs, "App.java"])
os.system(command)