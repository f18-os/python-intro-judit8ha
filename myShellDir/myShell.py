#! /usr/bin/env python3

import os, sys, time, re

# xjo
wT = '>'
rF = '<'

args = []  # making a list of args

# splitting input into a directory of arguments
args = input('myShell-' + os.getcwd() + ': ').split(' ')


# METHOD FOR INSTRUCTION EXECUTION
def execute(cmds):
    for dir in re.split(":", os.environ['PATH']):  # try each directory in path
        program = "%s/%s" % (dir, cmds[0])
        try:
            os.execve(program, cmds, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly

    os.write(2, ("Error: Could not exec %s\n" % cmds[0]).encode())
    sys.exit(1)  # terminate with error


def redirect_fd1(fileName):  #write to a file not to screen
    os.close(1)  # redirect child's stdout
    sys.stdout = open(fileName, "w")
    fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
    os.set_inheritable(fd, True)
    os.write(2, ("file directory  fd=%d redirected for  writing\n" % fd).encode())


def redirect_fd0(filename):  #read from file not keyboard
    os.close(0) #redirect child's stdin
    sys.stdin = open(filename, "r")
    fd = sys.stdout.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file directory fd = %d redirected for reading\n" % fd))


# REGULAR EXPRESSION SYNTAX VARIATIONS

    # 1 ARGUMENT
if len(args) is 1:
    execute(args)
# 2 ARGUMENTS
elif len(args[0]) is 2:
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child
        redirect_fd0(args[1])
        execute(args)

    else:
        os.write(1, ("forked = %d \n" % rc).encode())
# 3 ARGUMENTS
elif len(args) is 3:
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        # rc = os.fork()
        if args[1] is '>':
            redirect_fd1(args[2])
            execute(args)

        elif args[1] is '<':
            redirect_fd0(args[2])
            execute(args)

        else:
            os.write(1, ("command not recognized, exiting \n" % rc).encode())
            sys.exit(1)
    else:

        os.write(1, ("forked = %d \n" % rc).encode())
# 4 ARGUMENTS
elif len(args) is 4:
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        if args[2] is '>':
            redirect_fd1(args[3])
            redirect_fd0(args[1])
            execute(args)

        elif args[2] is '<':
            redirect_fd0(args[1])
            redirect_fd1(args[3])
            execute(args)

        else:
            os.write(1, ("command not recognized, exiting \n" % rc).encode())
            sys.exit(1)






#
# pid = os.getpid()  # get and remember pid
#
# os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
#
# rc = os.fork()
#
# if rc < 0:
#     os.write(2, ("fork failed, returning %d\n" % rc).encode())
#     sys.exit(1)
#
# elif rc == 0:  # child
#     os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" %
#                  (os.getpid(), pid)).encode())
#     # args = ["wc", "p3-exec.py"]
#
#     os.close(1)  # redirect child's stdout
#     sys.stdout = open("p4-output.txt", "w")
#     fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
#     os.set_inheritable(fd, True)
#     os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
#
#     #   for dir in re.split(":", os.environ['PATH']): # try each directory in path
#     #       program = "%s/%s" % (dir, args[0])
#     #       try:
#     #           os.execve(program, args, os.environ) # try to exec program
#     #       except FileNotFoundError:             # ...expected
#     #           pass                              # ...fail quietly
#
#     # os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
#     # sys.exit(1)  # terminate with error
#
# else:  # parent (forked ok)
#     os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" %
#                  (pid, rc)).encode())
#     childPidCode = os.wait()
#     os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
#                  childPidCode).encode())
