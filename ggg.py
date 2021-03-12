class X:
    def __init__(self, x):
        self.x = x

    def __truediv__(self, other):
        self.x = self.x / other.x
        return self

    def __str__(self):
        return str(self.x)


a = X(6)
b = X(2)

a /= b
print(a)