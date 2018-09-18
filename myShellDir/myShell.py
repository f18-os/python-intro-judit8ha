#! /usr/bin/env python3

import os, sys, time, re

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


# == REDIRECTS FOR PIPE AND/OR FILES  == #

def redirect_write(filename, fd):  #FD1 write to a file not to screen >
    os.close(fd)  # redirect child's stdout
    sys.stdout = open(filename, "w")
    fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
    os.set_inheritable(fd, True)
    os.write(2, ("file descriptor  fd=%d redirected for  writing\n" % fd).encode())


def redirect_read(filename, fd):  #FD0 read from file not keyboard <
    os.close(fd)  # redirect child's stdin
    sys.stdin = open(filename, "r")
    fd = sys.stdin.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file directory fd = %d redirected for reading\n" % fd).encode())


def redirectP_write():  # redirects to pipe's fd
    os.close(1)  # redirect child's stdout
    sys.stdout = os.fdopen(4, "w")
    #os.dup2(4, 1)
    #os.close(1)
    fd = sys.stdout.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file descriptor  fd=%d redirected for  writing to pipe\n" % fd).encode())


def redirectP_read():  # redirects to pipe's fd
    os.close(0)  # redirect child's stdin
    sys.stdin = os.fdopen(3, "r")
    #os.dup2(3, 0)
    #os.close(0)
    fd = sys.stdin.fileno()
    os.set_inheritable(fd, True)
    os.write(2, ("file descriptor fd = %d redirected for reading from pipe\n" % fd).encode())


def findRedirects(args):
    for a in args:
        if a is '>' or '<':
            return True


# searching for redirects
def managePipeRedirects(args, r, w):
    loc = 0
    global hasR
    for arg in args:
        if '<' in args:
            redirect_read(args[loc + 1],w )
        else:
            os.close(w)
            os.fdopen(r)
            os.set_inheritable(w, True)
        if arg is '>':
            redirect_write(args[loc + 1],r)
        else:
            os.close(r)
            os.fdopen(w)
            os.set_inheritable(r, True)
        loc += 1


def manageRedirects(args):
    loc = 0
    for arg in args:
        if arg is '<':
            redirect_read(args[loc + 1], 0)
        if arg is '>':
            redirect_write(args[loc + 1], 1)
        loc += 1


# splitting input into a directory of processes by pipe --  args by space then
# moving commands into a separate list.
os.export "PS1"

import fileinput
process = fileinput.input().split()
#process = input('myShell-' + os.getcwd() + ': ').split(' | ')
curr = 0
last = len(process)-1
args = process[curr].split(' ')
cmd = [args[0]]  # creates a list of one argument leaves opportunity for addtl commands later
pipe = (len(process) > 1) #bool check for pipes

if pipe:
    os.write(2, ('== PIPES EXIST == \n').encode())
    r, w = os.pipe()
    os.set_inheritable(r, True)
    os.set_inheritable(w, True)
    processpid = os.fork()

    if processpid < 0:
        os.write(2, ('INCORRECT PROCESS').encode())
        sys.exit(1)

    if processpid == 0:
        os.write(2, ('== CHILD PIPE == working on process %d\n' % curr).encode())
        os.dup2(4, 3)
        os.close(4)
        os.set_inheritable(3, True)
        execute(args)
        os.write(2, ("child done\n").encode())

    else:
        os.write(2, ('== PARENT PIPE PROCESS ==\n').encode())
        curr += 1  #change process
        args = process[curr].split(' ')
        os.write(2, (' == Parent waiting... \n\n').encode())
        os.dup2(1, sys.stdout.fileno)
        processpid: os.wait()
        os.dup2(0, 3)
        os.close(3)
        os.write(2, ('== PARENT PIPE PROCESS working on process %d ==\n' % curr).encode())
        execute(args)

else:                   #execute fork no pipes
    os.write(2, ('==NO PIPES == \n').encode())
    if findRedirects(args):
        pid = os.getpid()
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:  # child
            manageRedirects(args)
            execute(cmd)
        else:
            os.write(1, ("forked = %d \n" % rc).encode())
            cPid: os.wait()
    else:
        execute(args)

def main():




# TODO - exit method to return to shell
# TODO - need to include pipes
# TODO - need to support multiple pipes
# TODO -
