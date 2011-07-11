class Observer(object):
    """An observer, initiated with a callback will notify
    callback of new value on value change."""
    def __init__(self, callback, default=None):
        self._callback = callback
        # a default value should be passed so attempting to increment 
        #  an observed object (before being set) 
        #  doesn't result in attribute error.
        self._default = default

    def __get__(self, instance, owner):
        """Get the hidden observable."""
        if instance is None:
            raise AttributeError("Not a class attribute, access from instance")
        try:
            return instance._observable
        except AttributeError:
            instance._observable = self._default
            # notify the callback that the observable has changed.
            self._callback(self._default)

            return instance._observable

    def __set__(self, instance, value):
        """Set the hidden attribute and notify callback."""
        if instance is None:
            raise AttributeError("Cannot set class attribute, use instance.")
        # notify the callback.
        self._callback(value)
        # now change the value.
        instance._observable = value

    def __delete__(self, instance):
        """remove the attribute and notify callback."""
        if instance is None:
            raise AttributeError("Cannot remove class attribute.")
        # set callback value to None.
        self._callback(None)
        # now set observable to None.
        instance._observable = None

