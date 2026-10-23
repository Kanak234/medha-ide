# Tower of Hanoi (recursion).
def hanoi(n, src="A", dst="C", via="B"):
    if n == 0:
        return 0
    moves = hanoi(n - 1, src, via, dst)
    print(f"move disk {n}: {src} -> {dst}")
    return moves + 1 + hanoi(n - 1, via, dst, src)

print("total moves:", hanoi(3))
