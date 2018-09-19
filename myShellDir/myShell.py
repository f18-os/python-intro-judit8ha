#! /usr/bin/env python3

import os, sys, time, re

# TODO create a check for creating additional file directories if pipe exists
program = ''

def is_direct_path(p):
    return p[0] is '/'


# INSTRUCTION EXECUTION
def execute(cmds):
    global program
    if len(cmds) > 1:   #this is for cd "/some/path"
        if is_direct_path(cmds[1]):
            os.chdir(cmds[1])
    if is_direct_path(cmds[0]):
        program = cmds[0]
        try:
            os.execve(program, cmds, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            os.write(2, ("Error: Could not exec on 2nd if %s\n" % cmds[0]).encode())
            sys.exit(1)  # terminate with error
    else:
        for dir in re.split(":", os.environ['PATH']):  # try each directory in path
            program = "%s/%s" % (dir, cmds[0])
            try:
                os.execve(program, cmds, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

    os.write(2, ("Error: Could not exec %s\n" % cmds[0]).encode())
    sys.exit(1)  # terminate with error


# == REDIRECTS FOR PIPE AND/OR FILES  == #

def redirect_write(filename, fdd):  #FD1 write to a file not to screen >
    os.close(fdd)  # redirect child's stdout
    sys.stdout = open(filename, "w")
    f = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
    os.set_inheritable(f, True)
    os.write(2, ("file descriptor  fd=%d redirected for  writing\n" % fd).encode())


def redirect_read(filename, fd):  #FD0 read from file not keyboard <
    os.close(fd)  # redirect child's stdin
    sys.stdin = open(filename, "r")
    f = sys.stdin.fileno()
    os.set_inheritable(f, True)
    os.write(2, ("file directory fd = %d redirected for reading\n" % fd).encode())


def findRedirects(args):
    for a in args:
        if a is '>' or '<':
            return True


def execRedirectrs(cmd, args):
    #if findRedirects(args):
    for a in args:
        if a is '>' or '<':
            manageRedirects(args)
            execute(cmd)
    else:
        execute(args)


def manageRedirects(args):
    loc = 0
    for arg in args:
        if arg is '<':
            redirect_read(args[loc + 1], 0)
        if arg is '>':
            redirect_write(args[loc + 1], 1)
        loc += 1


def checkEOF():
    if os.read(sys.stdout) is 0:
        return


sys.path.append('myShell.py')


# splitting input into a directory of processes by pipe --  args by space then
# moving commands into a separate list.
try:
    os.environ.get('PS1')
except AttributeError:
    os.environ['PS1'] = '$ '

user_in = ''
while user_in is not 'exit':
    user_in = input('')
    prompt = os.environ.get('PS1')
    user_in = ' | ' os.read
    process = user_in.split('|')
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
            os.close(1)
            os.dup(w)
            os.close(w)
            os.close(r)
            fd = sys.stdout.fileno()
            os.set_inheritable(fd, True)
            execute(args)
            os.write(2, ("child done\n").encode())

        else:
            os.write(2, ('== PARENT PIPE PROCESS ==\n').encode())
            curr += 1  #change process
            args = process[curr].split(' ')
            os.write(2, (' == Parent waiting... \n\n').encode())
            processpid: os.wait()
            os.close(0)
            os.dup(r)
            os.close(r)
            os.close(w)
            fd = sys.stdin.fileno()
            os.set_inheritable(fd, True)
            os.write(2, ('== PARENT PIPE PROCESS working on process %d ==\n' % curr).encode())
            execute(args)
    else:                   #execute fork no pipes
        os.write(2, ('==NO PIPES == \n').encode())
        execRedirectrs(cmd, args)

    user_in = ''

os.write(2, 'Terminated with EXIT CODE 0'.encode())
