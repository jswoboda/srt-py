"""
This is a program to test the receiving on a new 5565 port.

The data is sent from the STR Daemon using zmq Push.
"""


import zmq
import json
import time

def main():
    # Add by jhl for receiving update of az_el
    context = zmq.Context()
    azel_port = 5565
    azel_socket = context.socket(zmq.SUB)
    azel_socket.connect("tcp://localhost:%s" % azel_port)
    azel_socket.subscribe("")

    # Initialize a pollre
    poller = zmq.Poller()
    poller.register(azel_socket, zmq.POLLIN)

    while True:
        try:
            socks = dict(poller.poll(10))
        except KeyboardInterrupt:
            break

        if azel_socket in socks:
            rec = azel_socket.recv()
            azel_status = json.loads(rec)
            print(azel_status)
            status_time = azel_status["time"]
            print(status_time)
            print(time.ctime(status_time))

    print("Client exiting.")
    azel_socket.close()
    context.term()

if __name__ == '__main__':
    main()
