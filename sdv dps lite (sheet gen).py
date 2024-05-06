# -*- coding: utf-8 -*-
"""
Created on Fri May  3 02:10:15 2024

@author: Artic144
"""

import numpy as np
import pandas as pd
from collections import Counter
import time

start_time = time.time()
last_time = time.time()

###############################|| WEAPON DATA LIST ||###################################

weapons = [["Infinity Blade",17,80,100,0.02,3,"Sword"],
           ["Dragontooth Cutlass",13,75,90,0.02,4,"Sword"],
           ["Dwarf Sword",13,65,75,0.02,3,"Sword"],
           ["Galaxy Sword",13,60,80,0.02,3,"Sword"],
           ["Lava Katana",10,55,64,0.015,3.5,"Sword"],
           ["Obsidian Edge",6,30,45,0.02,3.2,"Sword"],
           ["Steel Smallsword",1,4,8,0.02,3,"Sword"],
           ["Rusty Sword",1,2,5,0.02,3,"Sword"],
           ["Infinity Dagger",16,50,70,0.06,3,"Dagger"],
           ["Dragontooth Shiv",12,40,50,0.05,5,"Dagger"],
           ["Iridium Needle",12,20,35,0.1,7,"Dagger"],
           ["Dwarf Dagger",11,32,38,0.03,3,"Dagger"],
           ["Wicked Kris",8,24,40,0.06,3,"Dagger"],
           ["Galaxy Dagger",8,30,40,0.02,3,"Dagger"],
           ["Crystal Dagger",4,4,10,0.03,4,"Dagger"],
           ["Infinity Gavel",17,100,120,0.02,3,"Club"],
           ["Dragontooth Club",14,80,100,0.02,4,"Club"],
           ["Dwarf Hammer",13,75,85,0.02,3,"Club"],
           ["Galaxy Hammer",12,70,90,0.02,3,"Club"]]

###############################|| USER INPUTS ||###################################

# weapon input
#weapons = [["Iridium Needle",12,20,35,0.1,7,"Dagger"]]
'''
Weapon Format Guide ->  ["Weapon Name","Level",Min Dmg,Max Dmg,Crit Rate,Crit Multi,"Weapon Type"]
Ex: ["Iridium Needle",12,20,35,0.1,7,"Dagger"], ["Infinity Blade",17,80,100,0.02,3,"Sword"],
["Test",12,1,3,0.1,3,"Dagger"]
'''
# extra stat buffs
extra_luck = 0 # gives more crit chance 
extra_atk = 0  # gives +3 base damage per atk

# damage mult enchants
crusader = False
bug_killer = False

# slime slayer
slime_slayer = False


###############################|| ITERATING INPUTS ||###################################

def generate_inputs(weapon):
    
    weapon = weapon.copy()
    # rings
    # create all possible combined rings, then use those to gen list of all possible 4 ring combos
    valid_rings = ["Iridium","Aquamarine","Jade","Ruby","Lucky","Other"] #add warrior if u want
    combined_rings = [["Other","Other"]]
    for i in range(len(valid_rings)):
        for j in range(len(valid_rings)):
            if i < j:
                combined_rings.append([valid_rings[i],valid_rings[j]])
    
    input_rings = []
    for i in range(len(combined_rings)):
        for j in range(len(combined_rings)):
            input_rings.append(combined_rings[i]+combined_rings[j])
    
    # removing all redundant combinations of Iridium / Ruby Rings + dupe warrior rings
    for i in range(len(input_rings)-1,-1,-1):
        ir = input_rings[i]
        
        if ir.count("Warrior") > 1:
            del input_rings[i]
        else:
            match (ir.count("Ruby") + ir.count("Iridium")):
                case 1:
                    if ir.count("Ruby") ==  1:
                        del input_rings[i]
                case 2: 
                    if ir.count("Ruby") > 0:
                        del input_rings[i]
                case 3:
                    if ir.count("Ruby") ==  2:
                        del input_rings[i]
                               
    
    # removing all redundant duplicates like:
    # ['Iridium', 'Warrior', 'Iridium', 'Other']
    # ['Iridium', 'Other', 'Iridium', 'Warrior']
    counters = []
    for i in range(len(input_rings)-1,-1,-1):
        ir = input_rings[i]
        ir.sort()
        if Counter(ir) in counters:
            del input_rings[i]
        else:
            counters.append(Counter(ir))

    # forges
    valid_forges = ["Aquamarine","Jade","Ruby","Other"]
    input_forges = []
    for i in range(len(valid_forges)):
        for j in range(len(valid_forges)):
            for k in range(len(valid_forges)):
                if i <=  j <=  k:
                    input_forges.append([valid_forges[i],valid_forges[j],valid_forges[k]])
    
    # professions
    input_professions = [
        ["Fighter"],["Fighter","Brute"],
        ["Scout"],["Scout","Desperado"]     
        ]
    
    # innate enchantments
    input_innate_enchantments = []
    valid_innate_enchantments = [["Crit Power",3],["Crit Chance",3],["Attack",5],["Other",0]]
    if int(weapon[1]) >=  15 or "Galaxy" in weapon[0] or "Infinity" in weapon[0]:
        input_innate_enchantments = [["N/A",0]]
    elif slime_slayer:
        input_innate_enchantments = [["Slime Slayer",1]]
    else:
        input_innate_enchantments = valid_innate_enchantments
    
    out = []
    for f in input_forges:
        for i in input_innate_enchantments:
            for r in input_rings:
                for p in input_professions:
                    out.append([f,i,r,p])
    return out

###############################|| DAMAGE CALC FUNCTION ||###################################

def calculate_damage(weapon, forges, innate_enchant, rings, professions, extra_luck, extra_atk):

    weapon = weapon.copy()
    # incorporating all forges into weapon base stats
    # forges
    
    weapon[2] += np.max([1, int(weapon[2]*0.1)]) * forges.count("Ruby") # mindmg
    weapon[3] += np.max([1, int(weapon[3]*0.1)]) * forges.count("Ruby") # maxdmg
    weapon[4] += 0.046 * forges.count("Aquamarine")                     # critchance
    weapon[5] += 0.1 * forges.count("Jade")                             # critpower
    
    # dagger crit buff
    
    if weapon[6] ==  "Dagger":
        weapon[4] = (weapon[4] + 0.005) * 1.12
        
    # ring / playereffect buffs + innate enchants 
    
    weapon[2] = int(weapon[2] * (1 + 0.1*(rings.count("Ruby")+rings.count("Iridium")))) # mindmg
    weapon[3] = int(weapon[3] * (1 + 0.1*(rings.count("Ruby")+rings.count("Iridium")))) # maxdmg
    if innate_enchant[0] ==  "Crit Chance":                                              # critchance
        weapon[4] = weapon[4] * (1 + 0.1*rings.count("Aquamarine") + 0.02*innate_enchant[1])
    else:
        weapon[4] = weapon[4] * (1 + 0.1*rings.count("Aquamarine")) 
    if innate_enchant[0] ==  "Crit Power":                                               # critpower       
        weapon[5] = weapon[5] * (1 + 0.1*rings.count("Jade") + 0.5*innate_enchant[1])
    else:
        weapon[5] = weapon[5] * (1 + 0.1*rings.count("Jade"))
    
    # scout crit increase
    
    if professions.count("Scout") > 0:
        weapon[4] *= 1.5
    
    # ingame, damage rolled between min and max now
    pre_nocrit_min = weapon[2]
    pre_nocrit_max = weapon[3]
    
    # luck crit increase
    
    weapon[4] = weapon[4] * (1 + 0.025*(rings.count("Lucky") + extra_luck))
    
    # crit damage calculated
    
    pre_crit_min = int(weapon[2] * weapon[5])
    pre_crit_max = int(weapon[3] * weapon[5])
    
    # ATK boosts calculated
    
    if innate_enchant[0] ==  "Attack":
        atk_boost = 3*(innate_enchant[1] + extra_atk + 10*(rings.count("Warrior") > 0))
        pre_nocrit_min += atk_boost
        pre_nocrit_max += atk_boost
        pre_crit_min += atk_boost
        pre_crit_max += atk_boost
    else:
        atk_boost = 3*(extra_atk + 10*(rings.count("Warrior") > 0))
        pre_nocrit_min += atk_boost
        pre_nocrit_max += atk_boost
        pre_crit_min += atk_boost
        pre_crit_max += atk_boost
        
    # professions' boosts calculated
    
    if professions.count("Fighter") > 0:
        pre_nocrit_min = int(np.ceil(1.1*pre_nocrit_min))
        pre_nocrit_max = int(np.ceil(1.1*pre_nocrit_max))
        pre_crit_min = int(np.ceil(1.1*pre_crit_min))
        pre_crit_max = int(np.ceil(1.1*pre_crit_max))
    
    if professions.count("Brute") > 0:
        pre_nocrit_min = int(np.ceil(1.15*pre_nocrit_min))
        pre_nocrit_max = int(np.ceil(1.15*pre_nocrit_max))
        pre_crit_min = int(np.ceil(1.15*pre_crit_min))
        pre_crit_max = int(np.ceil(1.15*pre_crit_max))
    
    if professions.count("Desperado") > 0:
        pre_crit_min *= 2
        pre_crit_max *= 2
        
    # weapon enchantments (bug killer, crusader, slime slayer?) apply here
    
    if crusader:
        pre_nocrit_min *= 1.5 
        pre_nocrit_max *= 1.5
        pre_crit_min *= 1.5
        pre_crit_max *= 1.5
        
    if bug_killer:
        pre_nocrit_min *= 2
        pre_nocrit_max *= 2
        pre_crit_min *= 2 
        pre_crit_max *= 2
        
    if slime_slayer:
        pre_nocrit_min = 1.33*pre_nocrit_min + 1
        pre_nocrit_max = 1.33*pre_nocrit_max + 1
        pre_crit_min = 1.33*pre_crit_min + 1
        pre_crit_max =1.33*pre_crit_max + 1
    
    ###############################|| OUTPUT CALCS ||###################################
    nocrit_min = pre_nocrit_min
    nocrit_max = pre_nocrit_max
    crit_min = pre_crit_min
    crit_max = pre_crit_max
    
    nocrit_avg = np.average([nocrit_min,nocrit_max])
    crit_avg = np.average([crit_min,crit_max])
    
    avg_damage = crit_avg*weapon[4] + nocrit_avg*(1-weapon[4])
    
    out = [avg_damage, nocrit_avg, nocrit_min, nocrit_max, crit_avg, crit_min, crit_max, weapon[4]]
    return(out)


###############################|| CRETAING TABLE OF DATA ||###################################

for base_weapon in weapons:
    final = []
    input_list = generate_inputs(base_weapon)
    for i in input_list:
        final.append(i + calculate_damage(base_weapon, *i, extra_luck, extra_atk))
        
    master_sheet = pd.DataFrame(data=final,
                          columns=["Forges",
                                   "Innate Enchant",
                                   "Rings",
                                   "Professions",
                                   "Avg. Hit Damage",
                                   "Avg. Noncrit",
                                   "Min Noncrit",
                                   "Max Noncrit",
                                   "Avg. Crit",
                                   "Min Crit",
                                   "Max Crit",
                                   "Crit. Chance"])
    
    # adding diagnostics to dataframe
    temp_empty_rings = []
    for rs in master_sheet["Rings"].values:
        temp_empty_rings.append(rs.count("Other"))
    master_sheet.insert(3,"Free Rings",temp_empty_rings)
    
    temp_empty_forges = []
    for fs in master_sheet["Forges"].values:
        temp_empty_forges.append(fs.count("Other"))
    master_sheet.insert(1,"Free Forges",temp_empty_forges)
    
    master_sheet = master_sheet[["Avg. Hit Damage",
                                 "Crit. Chance",
                                 "Innate Enchant",
                                 "Free Rings",
                                 "Free Forges",
                                 "Rings",
                                 "Forges",
                                 "Professions",
                                 "Avg. Noncrit",
                                 "Min Noncrit",
                                 "Max Noncrit",
                                 "Avg. Crit",
                                 "Min Crit",
                                 "Max Crit"
                                 ]]
    
    # create csv
    master_sheet.to_csv(f"{base_weapon[0]}.csv")
    
    print(f"finished {base_weapon[0]} in %s seconds "% (time.time() - last_time))
    last_time = time.time()

print("--- %s seconds ---" % (time.time() - start_time))