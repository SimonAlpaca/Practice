# -*- coding: utf-8 -*-

def hanoi(n,ha,hb,hc):
    if n == 1:
        print(n,ha, "-->", hc)
    else:
        hanoi(n-1,ha,hc,hb)
        print(n, ha, "-->", hc)
        hanoi(n-1,hb,ha,hc)

# application
hanoi(3, "A", "B", "C")