import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("config")

for sec in Config.sections():
	print '[',sec,']'
	for opt in Config.options(sec):
		print opt,'=',Config.get(sec,opt)
