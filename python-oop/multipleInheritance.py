# Class 1 Base class
class OperatingSystem:
    multitasking = True
    name = "Mac OS"

# Class 2 Another Base Class
class Apple:
    website = "www.apple.com"
    name = "Apple"


# Class 3 Inherits both class 1 and 2
class MacBook(OperatingSystem, Apple):
    def __init__(self):
        if self.multitasking is True:
            print("This is a multi tasking system. Visit {} for more details".format(self.website))
            print("Name : ", self.name)


macBook = MacBook()

