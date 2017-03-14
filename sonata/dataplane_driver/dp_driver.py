#!/usr/bin/env python


from p4_old import P4Target


class DataplaneDriver(object):
    def __init__(self):
        pass

    def is_supportable(self, application, target):
        return True

    def get_cost(self, target):
        return 999

    def execute(self, application, target_type):
        if target_type == 'p4':
            target = P4Target()

            target.compile_app(application)



def main():
    dp_driver = DataplaneDriver()


if __name__ == '__main__':
    main()
