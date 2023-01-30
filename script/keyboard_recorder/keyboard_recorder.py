import keyboard
import json

def print_pressed_keys(e):
    line = ', '.join(str(code) for code in keyboard._pressed_events)
    print(line)

    with open('keylogger.txt', 'a+') as f:
        f.write(line + '\n')

# keyboard.hook(print_pressed_keys)
# keyboard.wait('Esc')

def record_pressed_keys():
    recorded = keyboard.record(until='esc')
    print(recorded)


record_pressed_keys()