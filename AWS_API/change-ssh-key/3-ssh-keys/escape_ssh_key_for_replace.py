import re
import os


KFR = re.escape(os.environ["KEY_FOR_REPLACE"])
KFR = KFR.replace('\\', '\\\\')

with open('vars.yaml', 'w') as f:
    f.write(f'\
ssh_key_for_replace: "{KFR}"\n\
new_ssh_key: "{os.environ["NEW_KEY"]}"\n\
')
