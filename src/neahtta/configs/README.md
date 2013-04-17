# About configs

Because paths in the configs likely must change depending on the place the
service is running, the .in files are the only things checked in. Make a copy
and change the necessary paths to FSTs and such, and run the service with that.
If there are changes to paradigms and such, be sure to check those in.

Configs are written in .yaml, and should be fairly self explanatory. See 
sample.config.yaml.in for explanations of the various options.
