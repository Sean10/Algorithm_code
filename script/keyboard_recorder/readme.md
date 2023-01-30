[boppreh/keyboard: Hook and simulate global keyboard events on Windows and Linux\.](https://github.com/boppreh/keyboard)

# Save JSON events to a file until interrupted:
sudo python -m keyboard > events.txt

cat events.txt
# {"event_type": "down", "scan_code": 25, "name": "p", "time": 1622447562.2994788, "is_keypad": false}
# {"event_type": "up", "scan_code": 25, "name": "p", "time": 1622447562.431007, "is_keypad": false}
# ...

# Replay events
python -m keyboard < events.txt

通过上述方式就可以捕获键盘记录了.