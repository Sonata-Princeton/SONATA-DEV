import random
import math
import crc16

# d = number of rows in the count-min sketch, number of hash functions
d = 5
# w = number of columns in the count-min sketch
w = 5
# number of unique items
n_items = 1000
max_freq = 100
max_error_frac = 0.02
max_error_probability = 0.0010

def primes(low, high): # simple Sieve of Eratosthenes
    odds = range(low, high+1, 2)
    sieve = set(sum([range(q*q, high+1, q+q) for q in odds],[]))
    return [2] + [p for p in odds if p not in sieve]


def get_index(item, pn, w):
    xored_out = item ^ pn
    crc_out = crc16.crc16xmodem(str(xored_out))
    index = crc_out%w
    return index


def update(item, sketch, item_2_indexes):
    indexes = item_2_indexes[item]
    for d in range(len(indexes)):
        w_d = indexes[d]
        if d not in sketch:
            sketch[d] = {}
        if w_d not in sketch[d]:
            sketch[d][w_d] = 0
        sketch[d][w_d] += 1

def estimate(item, sketch, item_2_indexes):
    indexes = item_2_indexes[item]
    all_estimates = [sketch[d][indexes[d]] for d in range(len(indexes))]
    return min(all_estimates)

def get_random_prime_numbers(d):
    prime_numbers = primes(1, 64000)
    print prime_numbers
    print "Total prime numbers", len(prime_numbers)
    random_prime_numbers = []
    for i in range(d):
        random_prime_numbers.append(random.choice(prime_numbers))
    print "Selected random numbers", random_prime_numbers

    return random_prime_numbers



# Generate items
def get_sketch_error():
    total_item_count = 0
    items = random.sample(range(100*n_items), n_items)
    item_2_exact_count = {}
    item_2_indexes = {}
    item_2_approximate_count = {}
    sketch = {}

    # configure sketch
    d = int(math.ceil(-1*math.log(max_error_probability, 2)))
    for item in items:
        item_2_exact_count[item] = random.randint(1,max_freq)
        total_item_count += item_2_exact_count[item]

    random_prime_numbers = get_random_prime_numbers(d)

    # update w for error rate
    #max_error_number = max_error_frac*total_item_count
    max_error_frac = 1.0*max_freq/total_item_count
    w = int(2/max_error_frac)
    print "max error", max_error_frac, 2.0*total_item_count/w
    print "Configured ", w, " columns", d, "rows"

    # update item_2_index
    for item in items:
        item_2_indexes[item] = []
        for pn in random_prime_numbers:
            index = get_index(item, pn, w)
            #print "Input", item, pn, "index", index
            item_2_indexes[item].append(index)

    # update sketch
    for item in items:
        for elem in range(item_2_exact_count[item]):
            update(item, sketch, item_2_indexes)

    # retreive counts
    errors = []
    for item in items:
        item_2_approximate_count[item] = estimate(item, sketch, item_2_indexes)
        error = (1.0*(item_2_approximate_count[item]-item_2_exact_count[item]))
        errors.append(error)

    print total_item_count
    return errors

errors = get_sketch_error()
errors.sort(reverse=True)
print errors



