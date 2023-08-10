import io
import slpp

line_count = 0
data = io.StringIO()
data.write("{")
with open("act_dex.lua") as fd:
    lines = fd.readlines()
for line in lines:
    line = line.strip()
    # Ignore comments or local Lua defines
    if line.startswith("--") or line.startswith("local"):
        continue
    data.write(line)
    line_count += 1
data.write("}")
data.seek(0)

converted_data = slpp.slpp.decode(data.read())
print(f"processed {line_count} lines")
# for key in converted_data:
#     print(key)
print(converted_data["AnimateWeapon"])
