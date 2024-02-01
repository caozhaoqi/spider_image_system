import cProfile

def main():
    for i in range(100000):
        sum = 0
        for j in range(1000):
            sum += j
    print(sum)

if __name__ == '__main__':
    cProfile.run('main()')