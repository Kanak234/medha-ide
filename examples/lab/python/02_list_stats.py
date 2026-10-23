# Read numbers on one line, print sorted list, min, max, average.
nums = [float(x) for x in input("Numbers separated by spaces: ").split()]
if nums:
    print("sorted:", sorted(nums))
    print("min:", min(nums), "max:", max(nums), "average:", round(sum(nums) / len(nums), 2))
