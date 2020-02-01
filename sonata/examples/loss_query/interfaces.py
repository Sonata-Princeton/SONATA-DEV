#!/usr/bin/python
from tempfile import TemporaryFile
from subprocess import check_output, CalledProcessError

def get_out(args):
    with TemporaryFile() as t:
        try:
            out = check_output(args, stderr=t, shell=True)
            return True, out
        except CalledProcessError as e:
            t.seek(0)
            # print "ERROR: " + str(args) + str(e.returncode) + ',' + t.read()
            return False, t.read()

class Interfaces(object):
    inName = ""
    outName = ""
    TOE_OPTIONS=["rx", "tx", "sg", "tso", "ufo", "gso", "gro",
                 "lro", "rxvlan", "txvlan", "rxhash"]

    def __init__(self, inName, outName):
        self.inName = inName
        self.outName = outName

    def setup(self):

        # if self.check_link():
        self.set_peer()
        self.put_link_up(self.inName)
        self.put_link_up(self.outName)
        self.disable_ipv6(self.inName)
        self.disable_ipv6(self.outName)
        for toe_option in self.TOE_OPTIONS:
            self.put_toe_option_off(self.inName, toe_option)
            self.put_toe_option_off(self.outName, toe_option)

    def check_link(self):
        cmd = "ip link show  %s &> /dev/null"%(self.inName)
        (returncode, error) = get_out(cmd)
        return returncode

    def set_peer(self):
        base = "ip link add name %s type veth peer name %s"%(self.inName, self.outName)
        (returncode, error) = get_out(base)
        return returncode

    def put_link_up(self, interface):
        base = "ip link set dev %s up"%(interface)
        (returncode, error) = get_out(base)
        return returncode

    def put_toe_option_off(self, interface, toe_option):
        base = "/sbin/ethtool --offload %s \"%s\" off"%(interface, toe_option)
        (returncode, error) = get_out(base)
        return returncode

    def disable_ipv6(self, interface):
        base = "sysctl net.ipv6.conf.%s.disable_ipv6=1"%(interface)
        (returncode, error) = get_out(base)
        return returncode

if __name__ == '__main__':
    Interfaces("m-veth-1", "out-veth-1").setup()
    Interfaces("m-veth-2", "out-veth-2").setup()