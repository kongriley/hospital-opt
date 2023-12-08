from scipy.optimize import linprog
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
ems_hourly_data = open_csv("ems_proportion_by_hour.csv")

CAR_SPEED = 20.0
DAYS_IN_YEAR = 365.0
HOSPITAL_COUNT = len(hospital_data)
EMS_LOCATION_COUNT = len(ems_data)
TIME_SLOTS = len(ems_hourly_data)

MAX_DISTANCE = 50
MIN_CANDIDATES = 2

# Only consider hospitals within reasonable distance
distances = []
for ems_index, ems_location in enumerate(ems_data):
	hospital_distances = [(distance(hospital, ems_location), i, ems_index) for i, hospital in enumerate(hospital_data)]
	
	closer_hospitals = hospital_distances.copy()
	cur_distance = MAX_DISTANCE
	while len(closer_hospitals) >= MIN_CANDIDATES and cur_distance > 0:
		hospital_distances = closer_hospitals.copy()
		closer_hospitals = [(distance, i, e_idx) for distance, i, e_idx in hospital_distances if distance < cur_distance]
		cur_distance /= 1.4
	print(len(hospital_distances))
	distances += hospital_distances

distances = {(h_idx, e_idx) : distance for distance, h_idx, e_idx in distances}

# Assume all patients are immediately transported
travel_objective = []
for (h_idx, e_idx), distance in distances.items():
	travel_objective.append(distance * hospital_data[h_idx][3] / CAR_SPEED)
hospital_count_objective = [1.0/count for name, la, lo, count in hospital_data]

objective = travel_objective + hospital_count_objective

# print(distances)

A_eq = []
b_eq = []
bounds = [(0, None)] * (len(distances) + HOSPITAL_COUNT)

# Constraints on moving all patients to hospitals
for e_idx, (la, lo, patient_count) in enumerate(ems_data):
	b_eq.append(patient_count / DAYS_IN_YEAR)
	constraint = [int(e_idx == j) for i, j in distances] + [0] * HOSPITAL_COUNT
	A_eq.append(constraint)

# Constraints on number of patients in hospitals
for h_idx, (name, la, lo, bed_count) in enumerate(hospital_data):
	b_eq.append(0)
	constraint = [int(h_idx == i) for i, j in distances] + [-int(i == h_idx) for i in range(HOSPITAL_COUNT)]
	A_eq.append(constraint)


result = linprog(c=objective,A_eq=A_eq,b_eq=b_eq,bounds=bounds)

with open("initial_results.txt", "w") as f:
	hospital_names = list(map(lambda arg:f"{arg[0]} ({arg[3]} beds)", hospital_data))
	transport_labels = list(map(lambda arg:(hospital_names[arg[0]], ems_data[arg[1]][:2]),distances.keys()))
	for info, variable_val in zip(transport_labels + hospital_names, result.x):
		f.write(f"{str(info)}: {str(variable_val)}\n")
	# [f.write(f"{str(line)}\n") for line in result.x]
print(result.x)