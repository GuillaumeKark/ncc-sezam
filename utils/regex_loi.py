import pandas as pd
import re

# import data
df=pd.read_csv('textes.csv')

# obtenir liste (acccentuée) des types de loi
type_list=df.titre.apply(lambda s : m.group(1).lower() if (m:=re.match(r'(\w+).*\s\d{4}\s',s)) else None)
TYPES=set(type_list)
TYPES.discard(None)

# change "arrêté du ... 2021" en <LOI>
patterns=[rf'{type_loi}(.*?)\s\d{{4}}\s' for type_loi in TYPES]
for pattern in patterns:
    df.titre=df.titre.apply(lambda s : re.sub(pattern,'<LOI> ',s,flags=re.IGNORECASE))