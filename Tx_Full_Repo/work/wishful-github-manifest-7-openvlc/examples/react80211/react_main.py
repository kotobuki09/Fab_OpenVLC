from react_simulator import Centralized_react
import time
import numpy as np
import _thread
def main():


	T_topology = [	[0,     1,     1,     0,     0,     0], #A
	[1,     0,     1,     0,     0,     0], #B
	[1,     1,     0,     0,     0,     0], #C
	[0,     0,     0,     0,     0,     0], #D
	[0,     0,     0,     0,     0,     0], #E
	[0,     0,     0,     0,     0,     0]] #F


	w_source = [0,     0,     0,     0,     0,     0]

	W_source = [	[0,     0,     0,     0,     0,     0],
	[0,     0,     0,     0,     0,     0],
	[0,     0,     0,     0,     0,     0],
	[0,     0,     0,     0,     0,     0],
	[0,     0,     0,     0,     0,     0],
	[0,     0,     0,     0,     0,     0]]

	node_claim_order = [0, 1, 2, 3, 4, 5]

	#start REACT
	x = Centralized_react(T_topology, W_source, w_source, len(w_source))
	_thread.start_new_thread( x.run_loop, () )
	time.sleep(1)
	[staions_claims, stations_w, stations_offer] = x.get_node_react_list()


	#update react
	w_source = [1, 1, 1, 0, 0, 0]
	W_source = [ [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
	x.update_traffic(W_source, w_source)
	[staions_claims, stations_w, stations_offer] = x.get_node_react_list()
	print(w_source)
	print('A B C D E F')
	print(staions_claims)

if __name__ == "__main__":
	main()

