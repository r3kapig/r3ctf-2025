load("poly.sage")

class Ciphertext:
    def __init__(self, a, b):
        assert a.Q == b.Q
        self.a = a
        self.b = b

    def __add__(self, other):
        if isinstance(other, polynomial):
            return Ciphertext(self.a, self.b + other)
        elif isinstance(other, Ciphertext):
            return Ciphertext(self.a + other.a, self.b + other.b)
        else:
            raise TypeError("Type not support")

    def __sub__(self, other):
        if isinstance(other, polynomial):
            return Ciphertext(self.a, self.b - other)
        elif isinstance(other, Ciphertext):
            return Ciphertext(self.a - other.a, self.b - other.b)
        else:
            raise TypeError("Type not support")
        
    def __mul__(self, other):
        pass

    def __repr__(self):
        return f"ct: ({self.a}, {self.b})"
