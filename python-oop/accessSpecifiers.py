# Public => memberName
# Protected => _memberName
# Private => __memberName

class Car:
    numberOfWheels = 4
    _color = "Black"
    __yearOfManufacture = 2018


class Bmw(Car):
    def __init__(self):
        print("Protected attribute color: ", self._color)

car = Car()
print("Public attribute numberOfWheels: ", car.numberOfWheels)
bmw = Bmw()
#print("Private attribute yearOfManufacture: ", car.__yearOfManufacture) # will get an error
print("Private attribute yearOfManufacture: ", car._Car__yearOfManufacture) # Name mangling