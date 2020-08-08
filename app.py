import time
import threading
from flask import Flask, jsonify, request

app = Flask(__name__, instance_relative_config=True)
# Load configs
app.config.from_object('config')
app.config.from_pyfile('local_config.py')

# A boolean indicating whether the relay thread is running currently
# This is so that we don't try to switch the state of the relay simultaneously.
is_switch_relay_running = False
lock = threading.Lock()

def switch_relays(time_ms):
    global is_switch_relay_running
    # Bail if another thread is running
    if is_switch_relay_running: return
    with lock:
        is_switch_relay_running = True

    print('Relay closed')
    # Convert milliseconds to seconds for sleep method
    time.sleep(time_ms / 1000)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0')
