from bs4 import BeautifulSoup
from sets import Set
import requests #allows us to download html from urls
import csv
import copy
import pandas as dapanda
import itertools as myitertool
import sys


def cleannames(array):
    result = []
    result = [x.encode('utf8') for x in array]
    result = [x.replace("Rookie","") for x in result]
    result = [x.replace(".","") for x in result]
    result = [x.replace("Jr","") for x in result]
    result = [x.replace("\xe2\x80\x99","") for x in result]
    result = [x.rstrip() for x in result]
    return result

starters_total_salary = int(sys.argv[2])

nba_2k19 = "https://www.2kratings.com/nba2k19-team/"
nba_teams = ["atlanta-hawks","boston-celtics","brooklyn-nets","charlotte-hornets","chicago-bulls","cleveland-cavaliers",
"dallas-mavericks","denver-nuggets","detroit-pistons","golden-state-warriors","houston-rockets","indiana-pacers",
"los-angeles-clippers","los-angeles-lakers","memphis-grizzlies","miami-heat","milwaukee-bucks","minnesota-timberwolves",
"new-orleans-pelicans","new-york-knicks","oklahoma-city-thunder","orlando-magic","philadelphia-76ers","phoenix-suns",
"portland-trail-blazers","sacramento-kings","san-antonio-spurs","utah-jazz","toronto-raptors","washington-wizards"]

players_array = []
bad_ratings = []
for x in nba_teams:
    #print(nba2k19 + x)
    current_team = requests.get(nba_2k19 + x)
    team_page = BeautifulSoup(current_team.content,'html.parser')
    team_result = team_page.find_all('td',class_ = "roster-entry")
    team_span = team_page.find_all('span')
    for y in team_result:
        players_array.append(y.get_text())
    for z in team_span:
        bad_ratings.append(z.get_text())


players = cleannames(players_array)
ratings = [int(x) for x in bad_ratings if len(x) == 2]
players_and_ratings = {player:rating for player,rating in zip(players,ratings)}
#print(playersandratings)

# ------- THIS WORKS ----------#

column_names = ['Position', 'Name+ID','Name','ID','RosterPosition','Salary','Gameinfo','Teamabbr','AvgPPG']
mycsv = dapanda.read_csv(sys.argv[1],header = None)
mycsv.columns = column_names
#print(mycsv.Name)
#csvcolumns = [x.replace(" ","") for x in mycsv.columns]

#print(mycsv)
dirty_name_list = [x for x in mycsv.Name]
dirty_name_list.pop(0)
name_list = cleannames(dirty_name_list)
# for x in namelist:
#     print(x)
tonights_player_2kratings = [players_and_ratings.get(x) for x in name_list]
salary_list = [x for x in mycsv.Salary]
salary_list.pop(0)
salary_list = [int(x) for x in salary_list]
position_list = [x for x in mycsv.Position]
position_list.pop(0)

salary_position_2krating = zip(salary_list,position_list,tonights_player_2kratings)
dirty_player_dict = {key:value for key,value in zip(name_list,salary_position_2krating)} #dirty b/c there's players with a "None"
                                                                                      #2k rating (b/c they're not important enough
                                                                                      #that their names are correct from both draftkings
                                                                                      #and 2k rating website)
player_dict = {key:value for key,value in dirty_player_dict.iteritems() if value[2] is not None}
pg = {}
sg = {}
sf = {}
pf = {}
c = {}
pg_list = []
sg_list = []
sf_list = []
pf_list = []
c_list = []
for x in player_dict:
    # print(x,playerdict.get(x)[0]
    player_value = player_dict.get(x)
    position = player_dict.get(x)[1]
    if position == 'PG':
        pg[x] = 1
    elif position == 'SG':
        sg[x] = 1
    elif position == 'SF':
        sf[x] = 1
    elif position == 'PF':
        pf[x] = 1
    elif position == 'C':
        c[x] = 1
    elif position == 'PG/SG':
        pg[x] = 1
        sg[x] = 1
    elif position == 'PG/SF':
        pg[x] = 1
        sf[x] = 1
        #pg_list.append(x)
        #sf_list.append(x)
    elif position == 'SG/SF':
        sg[x] = 1
        sf[x] = 1
    elif position == 'SF/PF':
        sf[x] = 1
        pf[x] = 1
    elif position == 'PF/C':
        pf[x] = 1
        c[x] = 1

def calculate_average(array,dictionary):
    answer = 0
    for x in array:
        answer += dictionary.get(x)[2]
    return answer / len(array)

def calculate_salary(array,dictionary):
    answer1 = 0
    for x in array:
        answer1 += dictionary.get(x)[0]
        print(dictionary.get(x)[0])
    print(answer1, "this is answer 1")
    return answer1


answer = [None] * 3
finalanswer = []
# for x,y,z in zip(pg,sg,sf):
#     print(x,y,z)
average = 0
temp_average = 0
total_salary = 0
for a in pg:
    if a in sg:
        sg.pop(a)
        sg_list.append(a)
    if a in sf:
        sf.pop(a)
        sf_list.append(a)
    # print(a)
    answer[0] = a
    for b in sg:
        if b in sf:
            sf.pop(b)
            sf_list.append(b)
        #print(b)
        answer[1] = b
        for c in sf:
            # print(c)
            answer[2] = c
            temp_average = calculate_average(answer,player_dict)
            total_salary = calculate_salary(answer,player_dict)
            if temp_average > average and total_salary <= starters_total_salary:
                average = temp_average
                finalanswer = answer[:]
        if sf_list:
            sf[sf_list.pop()] = 1
    if sg_list:
        sg[sg_list.pop()] = 1
    if sf_list:
        sf[sf_list.pop()] = 1


print(finalanswer)
for x in finalanswer:
    print(player_dict.get(x)[0])
print(average,total_salary,starters_total_salary)
# print(type(sys.argv[2]))
#print(average)
#print(answer)


# for x in pg_list:
#     print(x)
# print('\n')
# for x in sg_list:
#     print(x)
# print('\n')
# for x in sf_list:
#     print(x)
# for x,y,z in zip(pg_list,sg_list,sf_list):
#     print(x,y,z)
# print(pg)
# print(sg)
# print(sf)
# print(pf)
# print(c)


'''
#print(columns)
namecolumn = mycsv.Name
salarycolumn = mycsv.Salary
positioncolumn = mycsv.Position

for x,y,z in zip(namecolumn,salarycolumn,positioncolumn):
    print(x,y,z)

twokratingg = []
for x in namecolumn:
   if thenbaroster.get(x) != None:
      twokratingg.append(thenbaroster.get(x))

#fix these lists
namecolumn = list(namecolumn)
namecolumn.pop(0)
namecolumn = [x for x in namecolumn if str(x) != 'nan']
#print(namecolumn)

salarycolumn = list(salarycolumn)
salarycolumn.pop(0)
salarycolumn = [x for x in salarycolumn if str(x) != 'nan']
salarycolumn = [int(x) for x in salarycolumn]

positioncolumn = list(positioncolumn)
positioncolumn.pop(0)

playerinfo = zip(namecolumn,salarycolumn,twokratingg,positioncolumn)
#for x in playerinfo:
#   print(x)

#pg = []
pgwithpgsg = []
#sg = []
sgwithsgsf = []
#sf = []
sfwithsfpf = []
#pf = []
pfwithpfc = []
c = []
pgandsg = []
for x in range(0,len(playerinfo)):
   if playerinfo[x][3] == 'PG':
      pg.append(playerinfo[x])
   elif playerinfo[x][3] == 'PG/SG':
      pg.append(playerinfo[x])
      sg.append(playerinfo[x])
   elif playerinfo[x][3] == 'SG':
      sg.append(playerinfo[x])
   elif playerinfo[x][3] == 'SG/SF':
      sg.append(playerinfo[x])
      sf.append(playerinfo[x])
   elif playerinfo[x][3] == 'SF':
      sf.append(playerinfo[x])
   elif playerinfo[x][3] == 'SF/PF':
      sf.append(playerinfo[x])
      pf.append(playerinfo[x])
   elif playerinfo[x][3] == 'PF':
      pf.append(playerinfo[x])
   elif playerinfo[x][3] == 'PF/C':
      pf.append(playerinfo[x])
      c.append(playerinfo[x])
   elif layerinfo[x][3] == 'C':
      c.append(playerinfo[x])

def calculate(pg, sg, sf, pf, c):
   result = []
   temp = []
   for a in pg:
      for b in sg:
         for c in sf:
            for d in pf:
               for e in c:
                   print('hi')
for x in pg:
   print(x)
   print('hey')
'''
