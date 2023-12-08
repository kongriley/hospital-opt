from scipy.optimize import milp, linprog, LinearConstraint, Bounds
import numpy as np
import math

def try_num(arg):
	try:
		return float(arg)
	except:
		return arg

def open_csv(filename):
    return [list(map(try_num, row.split(",")))
            for row in open(filename).read().strip().split("\n")[1:]]

LATITUDE_COEFFICIENT = 69
LONGITUDE_COEFFICIENT = 54.6

def distance(hospital, location):
    la1, lo1 = hospital[1:3]
    la2, lo2 = location[:2]
    return abs(la1-la2)*LATITUDE_COEFFICIENT + abs(lo1-lo2)*LONGITUDE_COEFFICIENT

hospital_data = open_csv("hospitals_with_beds.csv")
# hospital_names = 
ems_data = open_csv("ems_aggregate.csv")

CAR_SPEED = 20
HOSPITAL_COUNT = len(hospital_data)
EMS_LOCATION_COUNT = len(ems_data)
TIME_SLOTS = 10

MAX_DISTANCE = 64
MIN_CANDIDATES = 3
# Only consider hospitals within reasonable distance
distances = []
for ems_location in ems_data:
	hospital_distances = [(distance(hospital, ems_location), i) for i, hospital in enumerate(hospital_data)]
	
	closer_hospitals = hospital_distances.copy()
	cur_distance = MAX_DISTANCE
	while len(closer_hospitals) >= MIN_CANDIDATES and cur_distance > 0:
		hospital_distances = closer_hospitals.copy()
		closer_hospitals = [(distance, i) for distance, i in hospital_distances if distance < cur_distance]
		cur_distance /= (2**0.5)
	distances.append(hospital_distances)

