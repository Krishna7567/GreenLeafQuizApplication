namelist = []
langlist = []
ratinglist = []
n = int(input())

for i in range(n):
    name = input()
    city = input()
    lang = input()
    rating = int(input())
    namelist.append(name)
    langlist.append(lang.lower())
    ratinglist.append(rating)

inp = int(input())

ans = []

if len(namelist) != 0 or len(langlist) != 0 or len(ratinglist) != 0:
    for kk in range(len(namelist)):
        if ratinglist[kk] >= inp and langlist[kk] == "english":
            ans.append(namelist[kk])

if len(ans) != 0:
    for j in range(len(ans)):
        print(ans[j])
else:
    print("No Name Found")