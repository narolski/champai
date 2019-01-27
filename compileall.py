# compileall.py
import os

tests = ['program0', 'program1', 'program2', '0-div-mod', '1-numbers', '2-fib', '3-fib-factorial', '4-factorial', '5-tab', '6-mod-mult', '7-loopiii', '8-for', '9-sort']

for test in tests:
    print("Compiling {}".format(test))
    os.system('python3 champai.py tests/gebala/{}.imp --out tests/gebala/{}.o'.format(test, test))