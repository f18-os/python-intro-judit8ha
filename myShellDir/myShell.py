#! /usr/bin/env python3

import os, sys, re

program = ''


def is_direct_path(p):
    return p[0] == '/'


def changeDirec(cmds):
    if len(cmds) > 1:
        wd = cmds[1]
        if cmds[1] == '..':
            cd = os.getcwd().split('/')
            wd = '/'.join(cd[0:len(cd)-2])
        try:
            os.chdir(wd)
        except NotADirectoryError:
            sys.stderr("Not a Directory")
    return


# INSTRUCTION EXECUTION
def execute(cmds):
    global program
    if cmds[0] == 'cd':  # if command is cd call cd method & return
        changeDirec(cmds)
        return

    if len(cmds) > 1:
        if is_direct_path(cmds[1]):
            os.chdir(os.environ.get("HOME"))
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


def redirect_read(filename, fd):  #FD0 read from file not keyboard <
    os.close(fd)  # redirect child's stdin
    sys.stdin = open(filename, "r")
    f = sys.stdin.fileno()
    os.set_inheritable(f, True)


def findRedirects(args):
    for a in args:
        if a is '>' or a is '<':
            return True
    return False


def execRedirectrs(cmd, args):
    if findRedirects(args):
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


def execPipeProcess(process):
    curr = 0
    args = process[curr].split(' ')
    r, w = os.pipe()
    os.set_inheritable(r, True)
    os.set_inheritable(w, True)
    processpid = os.fork()

    if processpid < 0:
        sys.exit(1)

    if processpid == 0:
        os.close(1)
        os.dup(w)
        os.close(w)
        os.close(r)
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        execute(args)
    else:
        curr += 1  # change process
        args = process[curr].split(' ')
        os.waitpid(processpid,0)
        os.close(0)
        os.dup(r)
        os.close(r)
        os.close(w)
        fd = sys.stdin.fileno()
        os.set_inheritable(fd, True)
        execute(args)


# splitting input into a directory of processes by pipe --  args by space then
# moving commands into a separate list.
try:
   sys.ps1 = os.environ.get('PS1')
except AttributeError:
    sys.ps1 = '$ '

if sys.ps1 is None:
    sys.ps1 = '$'

user_in = ''
while user_in != "exit":
    user_in = input(sys.ps1)
    process = user_in.split(' | ')
    curr = 0
    #last = len(process) - 1
    args = process[curr].split(' ')
    cmd = [args[0]]  # creates a list of one argument leaves opportunity for addtl commands later
    pipe = (len(process) > 1)  # bool check for pipes
    pid = os.fork()
    if pid == 0:
        if pipe:
            execPipeProcess(process)
        else:                   #execute fork no pipes
            execRedirectrs(cmd, args)
    else:
        pid: os.wait()
        break
    user_in = ''
