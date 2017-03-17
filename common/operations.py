from abc import ABC, abstractmethod
from types import *
from timeit import default_timer as timer


class Operation(ABC):
    '''Base class for a operation - a task to be done. Is should set EXIT_SUCCESS or EXIT_FAILURE as the status.
      If operation produces something that can be useful for following operation it can be added to _products.
    '''

    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    _status = None
    _products = {}

    @abstractmethod
    def __init__(self, args={}):
        self.args = args

    def allocate(self):
        """acquire resources"""
        pass

    def release(self):
        """release resources"""
        pass

    @abstractmethod
    def execute(self):
        """do something"""
        pass

    def cleanup(self):
        """cleanup if needed"""
        pass

    def add_product(self, key, value):
        """adds some information that can be useful for other operations """
        self._products[key] = value

    def get_products(self):
        return self._products

    @property
    def get_status(self):
        """return exit status """
        return self._status

    def log(self, msg, *params):
        """log message"""
        print(str(msg).format(*params))

    def err(self, msg, *params):
        """log error message"""
        print(" --- " + str(msg).format(*params))

    def tick(self):
        '''start counting time'''
        start = timer()

    def tock(self):
        '''display measured time'''
        end = timer()
        self.log("executed in  {} ", (end - self.start))


class Executor():
    '''Execute queued operations. Products of previous operation will be added to arguments of all next.'''

    _products = {}

    def __init__(self, operations):
        self.chain = operations
        self.index = 0

    def arg(self, opname, argname, value):
        changed = False
        for op in self.chain:
            print(str(op[0].__name__))
            if str(op[0].__name__) == opname:
                op[1][argname] = value
                changed = True
        if changed == False:
            raise Exception("There is no operation  " + opname)

    def all(self):
        '''Executes all the operaions'''
        lastExitCode = None
        while self.index < len(self.chain) and lastExitCode != Operation.EXIT_FAILURE:
            print("index : " + str(self.index))
            self.next()

    def next(self):
        '''Execute following operation'''
        if self.index < len(self.chain):
            operation = self.chain[self.index][0]
            args = self.chain[self.index][1]
            # add products of other operations to arguments
            args = {**args, **self._products}
            print('executable {} of type {}'.format(operation, type(operation)))
            if isinstance(operation, FunctionType):
                # executes simple function
                try:
                    operation(args);
                    self.index += 1
                    return True
                except Exception as ex:
                    raise self.e
            else:
                # executes Operation instance
                instance = operation(args)
                print('instance {} of type {}'.format(instance, type(instance)))
                assert isinstance(instance, Operation)
                try:
                    instance.execute()
                except Exception as ex:
                    instance.cleanup()
                    raise Exception(ex)
                finally:
                    instance.cleanup()

                status = instance.get_status
                if status == Operation.EXIT_SUCCESS:
                    self._products = {**self._products, **instance.get_products()}
                    self.index += 1
                    return True
                else:
                    raise Exception("Operation has failed")
        else:
            raise Exception("There are not operations to execute")
