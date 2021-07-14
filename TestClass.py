class Student:
    Name = ""
    Age = ""
    def __init__(self,name,age):
        self.Age=age
        self.Name=name
    def SayHello(self):
        print("hello i am "+self.Name+" i am "+self.Age+"years old !")