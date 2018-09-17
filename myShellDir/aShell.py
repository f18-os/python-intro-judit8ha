#! /usr/bin/env python3

import os, sys, time, re


args = []  # making a list of args


# splitting input into a directory of arguments
args = input('myShell-' + os.getcwd() + ': ').split(' ')
cmd = [args[0]] # creates a list of one argument leaves opportunity for addtl commands later


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


def redirect_fd1(fileName):  # write to a file not to screen
    os.close()  # redirect child's stdout
    sys.stdout = open(fileName, "w")
    fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
    os.set_inheritable(fd, True)
    os.write(2, ("file directory  fd=%d redirected for  writing\n" % fd).encode())
     # sys.exit(0)


def redirect_fd0(filename):  # read from file not keyboard
    os.close(0)  # redirect child's stdin
    sys.stdin = open(filename, "r")
    fd = sys.stdin.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file directory fd = %d redirected for reading\n" % fd).encode())
    # sys.exit(0)


def rd_reader_to_file(filename, reader):
    os.close(reader)
    sys.stdin = open(filename, "r")




# REGULAR EXPRESSION SYNTAX VARIATIONS
# 1 ARGUMENT
if len(args) is 1:    #working
    execute(args)
# 2 ARGUMENTS
elif len(args) is 2: #working
    pid = os.getpid()
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child
        redirect_fd0(args[1])
        execute(cmd)
        sys.exit(0)

    else:
        os.write(1, ("forked = %d \n" % rc).encode())
        cPid: os.wait()
# 3 ARGUMENTS
elif len(args) is 3:
    pid = os.getpid()
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        # rc = os.fork()
        val: str
        for val in args: print("%s \n" % val)   ## DEBUGGING CODE
        if args[1] is '>':
            redirect_fd1(args[2])
            execute(cmd)
            sys.exit(0)

        elif args[1] is '<':
            redirect_fd0(args[2])
            execute(args[0])
            sys.exit(0)

        else:
            os.write(1, ("command not recognized, exiting \n" % rc).encode())
            sys.exit(1)
    else:
        os.write(1, ("forked = %d \n" % rc).encode())
        cPid: os.wait()
# 4 ARGUMENTS
elif len(args) is 4:
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        if args[2] is '>':
            redirect_fd1(args[3])
            redirect_fd0(args[1])
            execute(cmd)
            sys.exit(0)

        elif args[2] is '<':
            redirect_fd0(args[1])
            redirect_fd1(args[3])
            execute(cmd)
            sys.exit(0)

        else:
            os.write(1, ("command not recognized, exiting \n" % rc).encode())
            sys.exit(1)
    else:
        cPid: os.wait()
else:
    os.write(2, ("Error: number of arguments is not accepted \n").encode())