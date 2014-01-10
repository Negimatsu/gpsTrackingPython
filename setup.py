from distutils.core import setup
import py2exe

file_name = raw_input("put your file name: ")
setup(console=[file_name])
