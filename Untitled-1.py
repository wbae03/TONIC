import msvcrt, time

i = 0
x = 0
while True:

    x = x +0.000001
    print(x)

    if x>0:
        if i>=0:
            i = i + 1
            print(i)
            if msvcrt.kbhit():
                if msvcrt.getwche() == '\r':
                    break

    print('in test')
    
print('test')

