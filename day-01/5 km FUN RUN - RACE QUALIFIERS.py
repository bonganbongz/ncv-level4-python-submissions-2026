
# 5 km FUN RUN - RACE QUALIFIERS

qualifying_time = 25 * 60

qualified = 0
winner_time = None
winners = []

print("===== 5 KM FUN RUN =====")
print("Enter athlete details.")
print("Enter X to finish.\n")

while True:
    name = input("Enter athlete name (X to stop): ")

    if name.lower() == "x":
        break

    time = input("Enter race time (mm:ss): ")

    try:
        parts = time.split(":")

        if len(parts) != 2:
            print("Invalid time! Please use mm:ss.\n")
            continue

        minutes = int(parts[0])
        seconds = int(parts[1])

        if minutes < 0 or seconds < 0 or seconds > 59:
            print("Invalid time! Please enter a valid time.\n")
            continue

    except ValueError:
        print("Invalid time! Please enter numbers in mm:ss format.\n")
        continue

    total_seconds = minutes * 60 + seconds

    if total_seconds <= qualifying_time:
        qualified = qualified + 1
        
    if winner_time is None or total_seconds < winner_time:
        winner_time = total_seconds
        winners = [name]

    elif total_seconds == winner_time:
        winners.append(name)

    print("Athlete recorded successfully!\n")

print("\n===== RACE RESULTS =====")

if winner_time is None:
    print("Nobody entered the race.")

else:
    if len(winners) == 1:
        print("Winner:", winners[0])
    else:
        print("Joint winners:", ", ".join(winners))

    winner_minutes = winner_time // 60
    winner_seconds = winner_time % 60

    print("Winning time: {:02d}:{:02d}".format(
        winner_minutes, winner_seconds
    ))

print("Number of qualified athletes:", qualified)
print("========================")
