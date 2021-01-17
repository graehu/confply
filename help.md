# help #

usage : `confply.py --[options] | [config] [arguments];...`

### options ###

	--help : prints this file to the console.
	--gen_config [command] [out_file] : generates a runnable config file for [command] at [out_file] located.
	--config {overrides} : pass a dictionary of attributes to override e.g.: "{'confply':{'tool':'cl'}, 'warnings':None}"
	--config.{path} [value] : set or add a config value directly, e.g.: --config.confply.tool "cl"
	--launcher [out_file] : generates a runnable config launcher at [out_file] location. Set an alias to run a configs.
	--no_header : don't print confply header
	
### config ###

the config file to load/run as a part of command generation.

### arguments ###

arguments are passed to the config file during load/run.

### return codes ###

0 : successful run.
1 : fatal error in confply, aborted any further work.
2 : unsuccessful tool run, see output for return codes.
