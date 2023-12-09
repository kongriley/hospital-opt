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
ems_data = open_csv("ems_aggregate.csv")
ems_hourly_data = open_csv("ems_proportion_by_hour.csv")

CAR_SPEED = 20.0
DATA_TIME_SPAN = 365.0
HOSPITAL_COUNT = len(hospital_data)
EMS_LOCATION_COUNT = len(ems_data)
TIME_SLOTS = len(ems_hourly_data)
ER_FACTOR = 0.1

MAX_DISTANCE = 50
MIN_CANDIDATES = 2


def compute_distances(e_data=ems_data, h_data=hospital_data, min_candidates=MIN_CANDIDATES, max_distance=MAX_DISTANCE):
	# Only consider hospitals within reasonable distance
	distances = []
	for ems_index, ems_location in enumerate(e_data):
		hospital_distances = [(distance(hospital, ems_location), i, ems_index) for i, hospital in enumerate(h_data)]
		
		closer_hospitals = hospital_distances.copy()
		cur_distance = max_distance
		while len(closer_hospitals) >= min_candidates and cur_distance > 0:
			hospital_distances = closer_hospitals.copy()
			closer_hospitals = [(distance, i, e_idx) for distance, i, e_idx in hospital_distances if distance < cur_distance]
			cur_distance -= 1
		# print(len(hospital_distances))
		distances += hospital_distances

	distances = {(h_idx, e_idx) : distance for distance, h_idx, e_idx in distances}
	return distances

if __name__ == "__main__":
	distances = compute_distances()

	# Assume all patients are immediately transported
	travel_objective = []
	for (h_idx, e_idx), distance in distances.items():
		travel_objective += [distance / CAR_SPEED for time in range(TIME_SLOTS)]
	hospital_count_objective = [1.0 + 9.0 * int(time == TIME_SLOTS) for name, la, lo, count in hospital_data for time in range(TIME_SLOTS + 1)]

	objective = travel_objective + hospital_count_objective

	# print(distances)

	A_eq = []
	b_eq = []
	VAR_COUNT = len(distances) * TIME_SLOTS + HOSPITAL_COUNT * (TIME_SLOTS + 1)
	# bounds = [(0, None)] * (len(distances) * TIME_SLOTS) + [(0, None) if t > 0 else (0, 0) for t in range(TIME_SLOTS + 1)] * HOSPITAL_COUNT
	bounds = [(0, None)] * VAR_COUNT

	# Constraints on moving all patients to hospitals
	for e_idx, (la, lo, patient_count) in enumerate(ems_data):
		for time in range(TIME_SLOTS):
			b_eq.append(patient_count * ems_hourly_data[time][1] / DATA_TIME_SPAN)
			constraint = []
			for i, j in distances:
				constraint += [int(e_idx == j and t == time) for t in range(TIME_SLOTS)]
			# constraint = [int(e_idx == j) for i, j in distances] + [0] * HOSPITAL_COUNT
			A_eq.append(constraint + [0] * HOSPITAL_COUNT * (TIME_SLOTS + 1))

	print("Halfway through constraint creation")

	A_ub = []
	b_ub = []
	# Constraints on number of patients in hospitals
	for h_idx, (name, la, lo, bed_count) in enumerate(hospital_data):
		for time in range(TIME_SLOTS):
			b_eq.append(bed_count * ER_FACTOR)
			travel_constraint = []
			for i, j in distances:
				travel_constraint += [int(h_idx == i and t == time) for t in range(TIME_SLOTS)]
			bed_constraint = []
			for i in range(HOSPITAL_COUNT):
				bed_constraint += [int(i == h_idx) * (int(t == time) - int(t == time + 1)) for t in range(TIME_SLOTS + 1)]
			# constraint = [int(h_idx == i) for i, j in distances] + [-int(i == h_idx) for i in range(HOSPITAL_COUNT)]
			A_eq.append(travel_constraint + bed_constraint)

	print("Starting model")
	result = linprog(c=objective,A_eq=A_eq,b_eq=b_eq,bounds=bounds)
	# result = linprog(c=objective,A_eq=A_eq,b_eq=b_eq,A_ub=A_ub,b_ub=b_ub,bounds=bounds)

	file = "results_with_time.txt"
	with open(file, "w") as f:
		hospital_names = list(map(lambda arg:f"{arg[0]} ({arg[3]} beds)", hospital_data))
		hospital_names_with_times = []
		for string in hospital_names:
			hospital_names_with_times += [f"{string} (at time {t})" for t in list(range(TIME_SLOTS)) + ["overtime"]]
		transport_labels = list(map(lambda arg:(hospital_names[arg[0]], ems_data[arg[1]][:2]),distances.keys()))
		transport_labels_with_times = []
		for string in transport_labels:
			transport_labels_with_times += [f"{string} (at time {t})" for t in range(TIME_SLOTS)]
		for info, variable_val in zip(transport_labels_with_times + hospital_names_with_times, result.x):
			f.write(f"{str(info)}: {str(variable_val)}\n")
		# [f.write(f"{str(line)}\n") for line in result.x]
	open("only_numbers.txt", "w").write(",".join(list(map(str, result.x))))
	print(f"Wrote contents to {file}")
	print(f"Computed objective of {result.fun} people-hours")
	for time in range(TIME_SLOTS):
		print(f"Hour {time}: {sum(result.x[time:time+len(distances)*TIME_SLOTS:TIME_SLOTS])} people moved to hospitals")