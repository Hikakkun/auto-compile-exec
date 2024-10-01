python ./ace.py example/ > out.json && ./convert_md.py out.json > out.md

jq 'to_entries | map(select(.value.compile_error != null or (.value.execution | any(.diff != null or 
.runtime_error != null)))) | map({(.key): .value}) | add'

jq 'to_entries | map(select(.value.compile_error != null or (.value.execution | any(.diff != null or 
.runtime_error != null)))) | map({(.key): .value}) | add'