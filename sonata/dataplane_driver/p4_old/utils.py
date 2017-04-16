from tempfile import TemporaryFile
from subprocess import check_output, CalledProcessError


def get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t, shell=True)
            print out
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) +',' +t.read()
            #raise RuntimeError
            return False, t.read()


def write_to_file(path, content):
    with open(path, 'w') as fp:
        fp.write(content)


def get_in(args, input):
    with TemporaryFile() as t:
        try:
            t.write(input)
            out = check_output(args, stdin=t, shell=False)
            #print "SUCCESS: " + str(args) + ",0 ," + str(out)
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            print "ERROR: " + str(args) + str(e.returncode) +',' +t.read()
            #raise RuntimeError

            return False, t.read()
