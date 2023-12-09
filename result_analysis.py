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
print(f"A total of {sum(result[:len(distances)*TIME_SLOTS])} people were moved")

with open("hospital_full_data.csv", "w") as f:
	f.write("name,lat,long,bed_count,er_bed_usage")
	for i, (name, la, lo, bed_count) in enumerate(hospital_data):
		start_index = len(distances) * TIME_SLOTS + i * TIME_SLOTS
		total_patients = sum(result[start_index:start_index+TIME_SLOTS])
		per_bed = round(100.0 * total_patients / (bed_count * TIME_SLOTS)) / 10.0
		print(f"{name} hospital had a total of {round(total_patients)} patients (average of {per_bed} per ER bed per hour)")
		f.write(f"{name},{la},{lo},{bed_count},{per_bed}\n")
