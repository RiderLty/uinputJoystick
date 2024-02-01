import json

raw = json.load(open(r"code.json"))


# print(raw["data"][0]["map"])
# print(raw["data"][2]["map"])


list = []
existed = set()
for [scancode_1,friendly_name] in raw["data"][0]['map']:
    for [scancode_2,linuxcode] in raw["data"][2]['map']:
        if linuxcode != None and scancode_1 == scancode_2:
            if linuxcode not in existed:
                existed.add(linuxcode)
                list.append([linuxcode,friendly_name])

list.sort( key= lambda x : x[0])

for linuxcode,friendly_name in list:
    print(f"{linuxcode} :{friendly_name}")