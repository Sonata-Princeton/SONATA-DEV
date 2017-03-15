#!/usr/bin/env python


from sonata.dataplane_driver.openflow.openflow import OFTarget
from sonata.dataplane_driver.p4.p4_old import P4Target


class DataplaneDriver(object):
    def __init__(self):
        pass

    def is_supportable(self, application, target_type):
        target = self.get_target(target_type)

        if not isinstance(application, list):
            application = [application]

        supported_operators = target.get_supported_operators()

        for query_object in application:
            for operator in query_object.operators:
                if operator.name not in supported_operators:
                    return False
        return True

    def get_cost(self, application, target_type):
        target = self.get_target(target_type)

        if isinstance(application, list):
            pass
        else:
            pass
        return 999

    def configure(self, application, target_type):
        target = self.get_target(target_type)
        target.run(application)

    def get_target(self, target_type):
        target = None

        if target_type == 'p4':
            target = P4Target()

        elif target_type == 'openflow':
            target = OFTarget()

        return target


def main():
    dp_driver = DataplaneDriver()


if __name__ == '__main__':
    main()
