from numpy import matrix

bus = matrix([
    [0, 1.04, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1],
	[1, 1.02533, 0.00, 1.63, 0.00, 0.00, 0.00, 0.00, 0.00, 2],
	[2, 1.02536, 0.00, 0.85, 0.00, 0.00, 0.00, 0.00, 0.00, 2],
	[3, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 3],
	[4, 1.00, 0.00, 0.00, 0.00, 0.90, 0.30, 0.00, 0.00, 3],
	[5, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 3],
	[6, 1.00, 0.00, 0.00, 0.00, 1.00, 0.35, 0.00, 0.00, 3],
	[7, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 3],
	[8, 1.00, 0.00, 0.00, 0.00, 1.25, 0.50, 0.00, 0.00, 3]])

line = matrix([
    [0, 3, 0.0,    0.0576, 0.0,     1.0, 0],
	[3, 4, 0.017,  0.092,  0.158,  1.0, 0],
	[4, 5, 0.039,  0.17,   0.358, 1.0, 0],
	[2, 5, 0.0,    0.0586, 0.0,    1.0, 0],
	[5, 6, 0.0119, 0.1008, 0.209,  1.0, 0],
	[6, 7, 0.0085, 0.072,  0.149,  1.0, 0],
	[7, 1, 0.0,    0.0625, 0.0,     1.0, 0],
	[7, 8, 0.032,  0.161,  0.306,  1.0, 0],
	[8, 3, 0.01,   0.085,  0.176, 1.0, 0]])

