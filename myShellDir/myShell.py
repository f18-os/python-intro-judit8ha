#! /usr/bin/env python3

import os, sys, time, re

hasR = True

# TODO create a check for creating additional file directories if pipe exists


# INSTRUCTION EXECUTION
def execute(cmds):
    for dir in re.split(":", os.environ['PATH']):  # try each directory in path
        program = "%s/%s" % (dir, cmds[0])
        try:
            os.execve(program, cmds, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly

    os.write(2, ("Error: Could not exec %s\n" % cmds[0]).encode())
    sys.exit(1)  # terminate with error


def redirect_write(fileName,fd):  # write to a file not to screen >
    os.close(fd)  # redirect child's stdout
    sys.stdout = open(fileName, "w")
    fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
    os.set_inheritable(fd, True)
    os.write(2, ("file directory  fd=%d redirected for  writing\n" % fd).encode())
    #sys.exit(0)


def redirect_read(filename, fd):  # read from file not keyboard <
    os.close(fd)  # redirect child's stdin
    sys.stdin = open(filename, "r")
    fd = sys.stdin.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file directory fd = %d redirected for reading\n" % fd).encode())
    #sys.exit(0)


def findRedirects(args):
    for a in args:
        if a is '>' or '<':
            return True


# searching for redirects
def managePipeRedirects(args, r, w):
    loc = 0
    global hasR
    for arg in args:
        if arg is '<':
            redirect_read(args[loc + 1],w )
            hasR = True
        else:
            os.close(w)
            os.fdopen(r)
            os.set_inheritable(w, True)
        if arg is '>':
            redirect_write(args[loc + 1],r)
            hasR = True
        else:
            os.close(r)
            os.fdopen(w)
            os.set_inheritable(r, True)
            hasR = False
        loc += 1


def manageRedirects(args):
    loc = 0
    global hasR
    for arg in args:
        if arg is '<':
            redirect_read(args[loc + 1],0)
            hasR = True
        if arg is '>':
            redirect_write(args[loc + 1],1)
            hasR = True
        else:
            hasR = False
        loc += 1


# splitting input into a directory of processes by pipe --  args by space then
# moving commands into a separate list.
process = input('myShell-' + os.getcwd() + ': ').split(' | ')
curr = 0
last = len(process)-1
args = process[curr].split(' ')
cmd = [args[0]]  # creates a list of one argument leaves opportunity for addtl commands later
pipe = (len(process) > 1)

if pipe:
    print('== PIPES EXIST == ')
    processpid = os.fork()
    r, w = os.pipe()
    if processpid:   #pipe parent
        print('== PARENT PIPE PROCESS ==')
        curr += 1  #change process
        args = process[curr].split(' ')
        processpid: os.wait()
        os.close(0)
        os.dup(r)
        #os.close(r)
        # os.close(w)
        execute(args)

        print('==NEW PROCESS  = %d' % curr)
    #IF PIPE'S PID == 0   -CHILD -
    else:
        print('== CHILD PIPE == ')
        manageRedirects(args)
        os.close(1)
        os.dup(w)
        execute(args)
        # sys.exit(0)
else:
    print('==NO PIPES == ')
    if findRedirects(args):
        pid = os.getpid()
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:  # child
            manageRedirects(args)
            execute(cmd)
            # sys.exit(0)
        else:
            os.write(1, ("forked = %d \n" % rc).encode())
            cPid: os.wait()
    else:
        execute(args)



# TODO - exit method to return to shell
# TODO - need to include pipes
# TODO - need to support multiple pipes
# TODO -
