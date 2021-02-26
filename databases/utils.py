class SharedBetweenInstances:
    """
    Implementation of Shared Attribute Descriptor
    Safe way of keeping same Database client for all instances
    """
    def __init__(self, initial_value=None):
        self.value = initial_value
        self._name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.value is None:
            raise AttributeError(f'{self._name} was never set')
        return self.value

    def __set__(self, instance, new_value):
        self.value = new_value

    def __set_name__(self, owner, name):
        self._name = name
