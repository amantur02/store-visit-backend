from enum import Enum


class UserRoleEnum(str, Enum):
    worker = "worker"
    customer = "customer"


class OrderStatusEnum(str, Enum):
    started = "started"
    ended = "ended"
    in_process = "in_process"
    awaiting = "awaiting"
    canceled = "canceled"
