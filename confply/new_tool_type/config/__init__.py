# write your base configuration here
# write tool specific configs in a separate file, e.g. confply.config.echo
# then add "import confply.config.echo as echo" here
import confply.config as confply
confply.__tool_type = "{tool_type}"
confply.__imported_configs.append("{tool_type}")
