#!/usr/bin/env python


from sonata.dataplane_driver.openflow.openflow import OFTarget
from sonata.dataplane_driver.p4.p4_target_old import P4Target


class DataplaneDriver(object):
    def __init__(self, dpd_socket, runtime_socket):
        self.dpd_socket = dpd_socket
        self.runtime_socket = runtime_socket

        self.targets = dict()

    def is_supportable(self, application, target_type, target_id):
        target = self.get_target(target_type, target_id)

        if not isinstance(application, list):
            application = [application]

        supported_operators = target.get_supported_operators()

        for query_object in application:
            for operator in query_object.operators:
                if operator.name not in supported_operators:
                    return False
        return True

    def get_cost(self, application, target_type, target_id):
        target = self.get_target(target_type, target_id)

        if isinstance(application, list):
            pass
        else:
            pass
        return 999

    def configure(self, application, target_type, target_id):
        target = self.get_target(target_type, target_id)
        target.run(application)

    def update_configuration(self, target_type, target_id):
        target = self.get_target(target_type, target_id)
        target.update()

    def get_target(self, target_type, target_id, **kwargs):
        if target_id in self.targets:
            return self.targets[target_id]
        else:
            target = None
            if target_type == 'p4':
                if 'em_conf' in kwargs:
                    print 'Error: Missing Emitter Configuration'
                em_conf = kwargs['em_conf']
                target = P4Target(em_conf)
            elif target_type == 'openflow':
                target = OFTarget()

            self.targets[target_id] = target
        return target


def main():
    dp_driver = DataplaneDriver()


if __name__ == '__main__':
    main()
