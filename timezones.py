import os

def _rlistdir(base, sub):
	path = os.path.join(base, sub)
	result = []
	list = os.listdir(path)
	for entry in os.listdir(path):
		if entry == 'right': continue
		if entry[-4:] == '.tab': continue
		if entry[:5] == 'posix': continue
		fullpath = os.path.join(path, entry)
		subpath = os.path.join(sub, entry)
		if os.path.isdir(fullpath):
			result.extend(_rlistdir(base, subpath))
		else:
			result.append(subpath)
	return result

zones = _rlistdir('/usr/share/zoneinfo', '')
zones.sort()
