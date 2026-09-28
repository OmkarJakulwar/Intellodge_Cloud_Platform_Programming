import datetime
import random

# this function will generate the code which is random 
def generate_booking_code():
    date = datetime.datetime.now().strftime("%Y%m%d")
    rand = random.randint(1000, 9999)                  # this will create 4-digit random
    return f"BK-{date}-{rand}"                         