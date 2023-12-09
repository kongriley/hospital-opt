from optimization_model import *

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

result = list(map(float, open("only_numbers.txt").read().split(",")))
distances = compute_distances()

for time in range(TIME_SLOTS):
	print(f"Hour {time}: {sum(result[time:time+len(distances)*TIME_SLOTS:TIME_SLOTS])} people moved to hospitals")

for i, (name, la, lo, bed_count) in enumerate(hospital_data):
	start_index = len(distances) * TIME_SLOTS + i * TIME_SLOTS
	total_patients = sum(result[start_index:start_index+TIME_SLOTS])
	print(f"{round(bed_count)} bed hospital had a total of {round(total_patients)} patients (average of {round(100.0 * total_patients / (bed_count * TIME_SLOTS)) / 100.0} per bed per hour)")