# Single inheritance 

class Apple:
    manufacturer = "Apple Inc."
    contactWebsite = "www.apple.com/contact"

    def contactDetails(self):
        print("To contact us, log on to ",self.contactWebsite)


class MacBook(Apple):
    def __init__(self):
        self.yearOfManufacture = 2018

    def manufactureDetails(self):
        print("This MacBook was manufactured in the year {} by {}".format(self.yearOfManufacture, self.manufacturer))


macBook = MacBook()
macBook.manufactureDetails()
macBook.contactDetails()