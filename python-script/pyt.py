# der = [1,2,3,4,56,6]
# for jelly in range(0,10):
#     print(jelly)

    # list(range(10))
# tweet = 'Go Sports! #Sports'

# tweet.split('#')

# count = 0
# while count <= 10:
#     print('count', count)
#     count += 1 # count = count + 1

# import datetime
# from datetime import date
# import camelcase

# today = date.today()

# print(today)

# camel = camelcase.CamelCase()
# text = 'hello there world'
# print(camel.hump(text))


# class

# class User:
#     # Constructor
#     def __init__(self, name, email, age):
#         self.name = name
#         self.email = email
#         self.age = age

#     def greeting(self):
#         return f'My name is {self.name} and I am {self.age}

# # Init user object
# feli = User('Felicia Ebikon', 'fe@gmail.com', 40)

# ebi = User('Ebi Ebikon', 'ebi@gmail.com', 20)

# # Edit property
# feli.age = 50

# print(feli.age)

# # Call method

# print(ebi.greeting())

# Open a file   Also creates an empty file
# myFile = open('myfile.txt', 'w')

# # Get some info

# print('Name: ', myFile.name)
# print('Is Closed: ', myFile.closed)
# print('Opening Mode: ', myFile.mode)

# # Write to file
# myFile.write('I love Python')
# myFile.write(' and JavaScript')
# myFile.close()

# # Append to file
# myFile = open('myfile.txt', 'a')
# myFile.write(' I also like PHP')
# myFile.close()

# # Read from file
# myFile = open('myfile.txt', 'r+')
# text = myFile.read(20)
# print(text)


# JSON

import json

# Sample JSON
userJSON = '{"fname": "Ebi", "lname": "Ebikon", "age": 40}'

# Parse to dictionary

user = json.loads(userJSON)

print(user)
print(user['fname'])

# from dict to json

car = {'make': 'Ford', 'model': 'Mustang', 'year': 1970}

carJSON = json.dumps(car)

print(carJSON)

