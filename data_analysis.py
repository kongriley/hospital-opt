from dbfread import DBF
from thefuzz import fuzz
import plotly.express as px
import pandas as pd

def count_calls_by_location():
	counter = {}
	c = 0
	with open("calls.csv") as f:
		f.readline()
		for line in f:
			c += 1
			coords = tuple(f.readline()[:-1].split(",")[-2:])
			counter[coords] = counter.get(coords, 0) + 1
	with open("counts.csv", "a") as f:
		f.write("lat,long,count\n")
		for loc, count in counter.items():
			f.write(f"{loc[0]},{loc[1]},{count}\n")

def high_call_areas():
	with open("counts.csv") as f:
		with open("high.csv", "w") as w:
			w.write(f.readline())
			for line in f:
				if int(line.split(",")[-1]) >= 100:
					w.write(line)


def plot_on_map(filename="counts.csv"):
	df = pd.read_csv(filename)

	# color_scale = [(1, 'green'), (1,'red')]

	fig = px.density_mapbox(df, 
	                        lat="lat", 
	                        lon="long", 
	                        hover_name="count",
	                        zoom=8, 
	                        z="count",
	                        height=800,
	                        width=800,
	                        radius=10)

	fig.update_layout(mapbox_style="open-street-map")
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	fig.show()

def plot_ems(filename="ems_with_nearest_hospital.csv"):
	df = pd.read_csv(filename)

	color_scale = [(0, "green"), (0.2, "rgb(192, 128, 0)"), (1, "red")]

	fig = px.scatter_mapbox(df, 
	                        lat="lat", 
	                        lon="long", 
	                        hover_name="count",
	                        zoom=8, 
	                        size="count",
	                        color="distance",
	                        color_continuous_scale=color_scale,
	                        height=800,
	                        width=800,
	                        range_color=[0,10])

	hospitals = pd.read_csv("relevant_hospitals.csv")
	fig2 = px.scatter_mapbox(hospitals,
							lat="lat",
							lon="long",
							hover_name="name",
							zoom=8,
							height=800,
							width=800,
							color_continuous_scale="purple")

	# fig2.update_traces(marker={"size": 10000000, "symbol": ["cross"]})
	trace0 = fig2 # the second map
	fig.add_trace(trace0.data[0])
	trace0.layout.update(showlegend=False)
	fig.update_layout(mapbox_style="open-street-map")
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	fig.show()

def overwrite_ems():
	text = open("ems_aggregate.csv").read().split("\n")
	with open("ems_aggregate.csv", "w") as f:
		for line in text:
			if line:
				f.write(line + "\n")

def hospital_locations():
	with open("relevant_hospitals.csv", "w") as f:
		f.write("lat,long,name\n")
		for record in DBF("NYS_hospitals.dbf"):
			if record["City"] in {"Bronx", "Brooklyn", "Elmhurst", "Far Rockaway", "Flushing", "Jamaica", "New York", "Staten Island"}:
				f.write(f"{record['Latitude']},{record['Longitude']},{record['Name']}\n")

def distance(csv_line1, csv_line2):
	la1, lo1 = csv_line1.split(",")[:2]
	la2, lo2 = csv_line2.split(",")[:2]
	return abs(float(la1)*69 - float(la2)*69) + abs(float(lo1)*54.6 - float(lo2)*54.6)

def nearest_hospital():
	hospitals = open("relevant_hospitals.csv").read().split("\n")[1:-1]
	call_locations = open("ems_aggregate.csv").read().split("\n")[1:-1]
	with open("ems_with_nearest_hospital.csv", "w") as f:
		f.write("lat,long,count,distance\n")
		for loc in call_locations:
			d = min([distance(loc, hosp) for hosp in hospitals if loc and hosp])
			f.write(f"{loc},{d}\n")

def nearest_hospital_with_beds():
	hospitals = open("relevant_hospitals.csv").read().split("\n")[1:-1]
	beds = open("bed_counts.csv").read().split("\n")[1:-1]
	hospital_names = [h.split(",")[2] for h in hospitals]

	bed_names = {}
	for bed in beds:
		name, count = bed.split(",")
		closest = max(hospital_names, key = lambda arg: fuzz.token_set_ratio(arg, name))
		# print(f"Matched {name} to: \n{closest}")
		conflict = closest in bed_names
		if conflict:
			print(f"Conflict between new:\n{name} and old:\n{bed_names[closest]} for\n {closest}")
			choice = input("Please enter 0 for old option and 1 for new\n")
			if choice == "1":
				bed_names[closest] = (name, count)
		else:
			bed_names[closest] = (name, count)
		# bed_names[closest] = max(((name, count), *bed_names.get(closest, set())), key = lambda arg: fuzz.token_set_ratio(arg[0], name))
		# if conflict:
		# 	print(f"Resolved to \n{bed_names[closest]}")

	c = 0
	with open("hospitals_with_beds.csv", "w") as f:
		f.write("lat,long,name,beds\n")
		for hospital in hospitals:
			found = False
			lat, lon, name = hospital.split(",")
			for hosp, count in bed_names.items():
				if name == hosp:
					f.write(f"{hospital},{count[1]}\n")
					c += 1
					break
	print(f"Found {str(c)} matches")


def longest_common_substring(name, candidate):
	dp = [[0 for j in range(len(candidate) + 1)] for i in range(len(name) + 1)]
	for i in range(1, len(name) + 1):
		for j in range(1, len(candidate) + 1):
			include = int(name[i] == candidate[j])
			dp[i + 1][j + 1] = max(dp[i][j] + include, dp[i - 1][j], dp[i][j - 1])
	return dp[-1][-1]


# hospital_locations()
# nearest_hospital()
# plot_ems()
# nearest_hospital()
# nearest_hospital_with_beds()