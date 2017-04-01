#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)


class P4Primitive(object):
    def __init__(self, name, arguments):
        self.name = name
        self.args = arguments

    def get_code(self):
        out = '%s(%s)' % (self.name, ', '.join([str(x) for x in self.args]))
        return out


class AddHeader(P4Primitive):
    def __init__(self, header_instance):
        super(AddHeader, self).__init__('add_header', (header_instance, ))


class CopyHeader(P4Primitive):
    def __init__(self, destination, source):
        super(CopyHeader, self).__init__('copy_header', (destination, source))


class RemoveHeader(P4Primitive):
    def __init__(self, header_instance):
        super(RemoveHeader, self).__init__('remove_header', (header_instance, ))


class ModifyField(P4Primitive):
    def __init__(self, field_name, value):
        super(ModifyField, self).__init__('modify_field', (field_name, value))


class AddToField(P4Primitive):
    def __init__(self, field_name, value):
        super(AddToField, self).__init__('add_to_field', (field_name, value))


class Add(P4Primitive):
    def __init__(self, field_name, value1, value2):
        super(Add, self).__init__('add', (field_name, value1, value2))


class SubtractFromField(P4Primitive):
    def __init__(self, field_name, value):
        super(SubtractFromField, self).__init__('subtract_from_field', (field_name, value))


class Subtract(P4Primitive):
    def __init__(self, field_name, value1, value2):
        super(Subtract, self).__init__('subtract', (field_name, value1, value2))


class ModifyFieldWithHashBasedOffset(P4Primitive):
    def __init__(self, field_name, base, field_list_calc, size):
        super(ModifyFieldWithHashBasedOffset, self).__init__('modify_field_with_hash_based_offset',
                                                             (field_name, base, field_list_calc, size))


class ModifyFieldRNGUniform(P4Primitive):
    def __init__(self, dest, lower_bound, upper_bound):
        super(ModifyFieldRNGUniform, self).__init__('modify_field_rng_uniform', (dest, lower_bound, upper_bound))


class BitAnd(P4Primitive):
    def __init__(self, dest, value1, value2):
        super(BitAnd, self).__init__('bit_and', (dest, value1, value2))


class BitOr(P4Primitive):
    def __init__(self, dest, value1, value2):
        super(BitOr, self).__init__('bit_or', (dest, value1, value2))


class BitXor(P4Primitive):
    def __init__(self, dest, value1, value2):
        super(BitXor, self).__init__('bit_xor', (dest, value1, value2))


class ShiftLeft(P4Primitive):
    def __init__(self, dest, value1, value2):
        super(ShiftLeft, self).__init__('shift_left', (dest, value1, value2))


class ShiftRight(P4Primitive):
    def __init__(self, dest, value1, value2):
        super(ShiftRight, self).__init__('shift_right', (dest, value1, value2))


class Truncate(P4Primitive):
    def __init__(self, length):
        super(Truncate, self).__init__('truncate', (length, ))


class Drop(P4Primitive):
    def __init__(self):
        super(Drop, self).__init__('drop', ())


class NoOp(P4Primitive):
    def __init__(self):
        super(NoOp, self).__init__('no_op', ())


class Push(P4Primitive):
    def __init__(self, array, count):
        super(Push, self).__init__('push', (array, count))


class Pop(P4Primitive):
    def __init__(self, array, count):
        super(Pop, self).__init__('pop', (array, count))


class Count(P4Primitive):
    def __init__(self, counter_name, index):
        super(Count, self).__init__('count', (counter_name, index))


class ExecuteMeter(P4Primitive):
    def __init__(self, meter_name, index, field):
        super(ExecuteMeter, self).__init__('execute_meter', (meter_name, index, field))


class RegisterRead(P4Primitive):
    def __init__(self, dest, register_name, index):
        super(RegisterRead, self).__init__('register_read', (dest, register_name, index))


class RegisterWrite(P4Primitive):
    def __init__(self, register_name, index, value):
        super(RegisterWrite, self).__init__('register_write', (register_name, index, value))


class GenerateDigest(P4Primitive):
    def __init__(self, receiver, field_list):
        super(GenerateDigest, self).__init__('generate_digest', (receiver, field_list))


class Resubmit(P4Primitive):
    def __init__(self, field_list):
        super(Resubmit, self).__init__('resubmit', (field_list, ))


class Recirculate(P4Primitive):
    def __init__(self, field_list):
        super(Recirculate, self).__init__('recirculate', (field_list, ))


class CloneIngressPktToIngress(P4Primitive):
    def __init__(self, clone_spec, field_list):
        super(CloneIngressPktToIngress, self).__init__('clone_ingress_pkt_to_ingress', (clone_spec, field_list))


class CloneEgressPktToIngress(P4Primitive):
    def __init__(self, clone_spec, field_list):
        super(CloneEgressPktToIngress, self).__init__('clone_egress_pkt_to_ingress', (clone_spec, field_list))


class CloneIngressPktToEgress(P4Primitive):
    def __init__(self, clone_spec, field_list):
        super(CloneIngressPktToEgress, self).__init__('clone_ingress_pkt_to_egress', (clone_spec, field_list))


class CloneEgressPktToEgress(P4Primitive):
    def __init__(self, clone_spec, field_list):
        super(CloneEgressPktToEgress, self).__init__('clone_egress_pkt_to_egress', (clone_spec, field_list))
