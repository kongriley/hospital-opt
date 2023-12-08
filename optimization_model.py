from scipy.optimize import milp, linprog, LinearConstraint, Bounds
import numpy as np
import math

def open_csv(filename, omit_first_column=False):
    return [list(map(float, row.split(",")[int(omit_first_column):]))
            for row in open(filename).read().strip().split("\n")[1:]]

def distance(p1, p2):
    x1, y1 = center
    x2, y2 = landfill
    return math.abs(x1-x2) + math.abs(y1-y2)

hospital_data = open_csv("hospitals_with_beds.csv",omit_first_column=True)
ems_data = open_csv("ems_aggregate.csv")

CAR_SPEED = 20
