# Effective at avoiding Discord's afk timer for ending long calls prematurely (say if you like falling asleep with
# your partner on a call). 
# Interrupt at any time with CTRL-C.
from time import sleep, time
from random import randint
from pyautogui import press

start_time = time()
keys = ['space', 'e', 'q', 'w', 'a', 's', 'd', 'r', 'f']


def main():
    random_index = randint(0, len(keys) - 1)
    key = keys[random_index]
    press(key)
    print(f"Pressed {key}.")

    interval = randint(1, 5)
    sleep(interval - ((time() - start_time) % interval))


if __name__ == "__main__":
    input("Hit enter to start.")
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Good morning!")
            exit(0)
