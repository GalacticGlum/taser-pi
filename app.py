import time
import atexit
import threading
import RPi.GPIO as GPIO
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, instance_relative_config=True)
# Load configs
app.config.from_object('config')
app.config.from_pyfile('local_config.py')

# A boolean indicating whether the relay thread is running currently
# This is so that we don't try to switch the state of the relay simultaneously.
is_switch_relay_running = False
lock = threading.Lock()

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
_RELAY_INPUT_PINS = app.config['RELAY_INPUT_PINS']
for pin in _RELAY_INPUT_PINS:
    GPIO.setup(pin, GPIO.OUT)

def switch_relays(time_ms):
    global is_switch_relay_running
    # Bail if another thread is running
    if is_switch_relay_running: return
    with lock:
        is_switch_relay_running = True

    for pin in _RELAY_INPUT_PINS:
        GPIO.output(pin, GPIO.HIGH)

    print('Relay closed')
    
    # Convert milliseconds to seconds for sleep method
    time.sleep(time_ms / 1000)
    
    for pin in _RELAY_INPUT_PINS:
        GPIO.output(pin, GPIO.LOW)
    print('Relay open')

    with lock:
        is_switch_relay_running = False

@app.route('/api/shock')
def shock_api():
    '''
    An API endpoint for triggering the relay state to closed.

    :param time:
        An integer representing the number of milliseconds
        to keep the switch closed. Defaults to 1000 ms (1 second).

    ''' 

    time = request.args.get('time', default=1000, type=int)
    threading.Thread(target=switch_relays, args=(time,)).start()
    return jsonify(message='Success!'), 200

@app.route('/')
def index():
    return render_template('index.html')

def exit_handler():
    for pin in _RELAY_INPUT_PINS:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

atexit.register(exit_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
