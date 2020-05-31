"""
Here we place the simple object factory class.

Goal is to simplify providers building and make if
more readable for clients.
"""

class ObjectFactory:
    """
    Helper Factory for push providers.
    """
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        """
        Save builders for push providers.
        """
        self._builders[key] = builder
    
    def unregister_builder(self, key):
        """
        Save builders for push providers.
        """
        del self._builders[key]

    def create(self, key, **kwargs):
        """
        Create a concrete push Provider.

        Use specialized builder to create a concrete
        push provider.
        """
        builder = self._builders.get(key)

        if not builder:
            raise ValueError(key)

        return builder(**kwargs)
