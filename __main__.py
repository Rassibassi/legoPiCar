from carclasses import *
import threading

def main():

	lock = threading.Lock()

	cpw = CarPositionWrapper()

	car = Car()

	cc = CarControl(car,cpw,lock)
	cc.daemon = True
	cc.start()

	l = CarListener(cpw,lock)
	l.daemon = True
	l.start()

	try:
		while l.isAlive():
			l.join(5)
			cc.join(5)

	except (KeyboardInterrupt, SystemExit):
		car.cleanup()
		print '\n! Received keyboard interrupt, quitting threads.\n'

if __name__ == '__main__':
		main()
	