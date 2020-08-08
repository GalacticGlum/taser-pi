import time
import threading
from flask import Flask, jsonify, request

app = Flask(__name__, instance_relative_config=True)
# Load configs
app.config.from_object('config')
app.config.from_pyfile('local_config.py')

def switch_relays(time_ms):
    print('Relay closed')
    # Convert milliseconds to seconds for sleep method
    time.sleep(time_ms / 1000)
    print('Relay open')


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
