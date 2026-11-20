
# NCV Level 4
# Day 3: Collections and Records
# Block 2B Activity: Learner Ranking

# 1. Create a dictionary of five learners and their marks

learners = {
    "Thandi": 75,
    "John": 62,
    "Maphorisa": 88,
    "Scott": 55,
    "Davide": 70
}

print("ORIGINAL LEARNER RECORDS")
print(learners)


# 2. Convert dictionary to a list of (mark, name) tuples

data = []

for name in learners:
    data.append((learners[name], name))

print("\nTUPLE LIST")
print(data)


# 3. Bubble sort in descending order

for i in range(len(data)):
    for j in range(len(data) - 1 - i):

        if data[j][0] < data[j + 1][0]:

            temp = data[j]
            data[j] = data[j + 1]
            data[j + 1] = temp


# 4. Print the ranking

print("\nLEARNER RANKING")
print("--------------------------------")
print(f"{'RANK':<6}{'NAME':<15}{'MARK':>8}")
print("--------------------------------")

rank = 1

for mark, name in data:
    print(f"{rank:<6}{name:<15}{str(mark) + '%':>8}")
    rank = rank + 1

print("--------------------------------")
print("Day 3: Sorted Summary")

