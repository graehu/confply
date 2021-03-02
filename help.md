# help

confply lets your write config files in python.

usage : `./confply.py [config_file] --[options] [arguments] -- ...`


### options

	--help : prints this file to the console.
	--help.{tool_type} : prints the help file associated with the tool_type
	--new_tool_type [tool_type] : adds a new tool type, creating the relevant files automatically
	--gen_config [tool_type] [out_file] : generates a runnable config file for [tool_type] at [out_file] located.
	--config {overrides} : pass a dictionary of attributes to override e.g.: "{'confply':{'tool':'cl'}, 'warnings':None}"
	--config.{path} [value] : set or add a config value directly, e.g.: --config.confply.tool "cl"
	--launcher [out_file] : generates a runnable config launcher at [out_file] location. Set an alias to run a configs.
	--no_header : don't print confply header
	--no_run : don't run the generated commands
	--version : print version information
	-- : separates config runs


### config_file

the config file to load/run as a part of command generation.

### arguments

arguments are passed to the config file during load/run.

### return codes

0 : successful run.
1 : fatal error in confply, aborted any further work.
2 : unsuccessful tool run, see output for return codes.
