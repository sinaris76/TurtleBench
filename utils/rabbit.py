import turtle
import math

class Rabbit(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.setheading(90)
        self.pensize(5)
        self.hideturtle()

    def aa(self, length):
        self.forward(length)

    def bb(self, degree):
        self.right(degree)

    def cc(self, radius, degree):
        self.circle(radius, degree)

    def pp(self, vanish):
        if vanish:
            self.penup()
        else:
            self.pendown()