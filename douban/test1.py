class Manager:
    # abc = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance


print(Manager())
print(Manager())
print(Manager())