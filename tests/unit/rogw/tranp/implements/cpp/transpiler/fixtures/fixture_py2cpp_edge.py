from rogw.tranp.compatible.cpp.object import CP


def a(l: list[CP[int]]) -> None:
	for i, np in enumerate(l):
		n = np.raw
