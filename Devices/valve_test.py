import H2_components

valve1 = valve('vavle1',18)

while True:
    A = input("1 for HIGH, 0 for LOW")
    print(A)
    if A == '1':
        print("LOW")
        valve1.enable()
    else:
        print("HIGH")
        valve1.disable()
