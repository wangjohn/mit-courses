# Created by Huan Liu
# liuhuan@mit.edu
# MIT 6.006 - Fall 2008  
#
# This file defines additional pocket cube abstraction based on rubik.py.
# It also provides interface to the solver.


from rubik import *
import solver

# hash map from face_name to face_color_configuration[]
# 6 faces of the pocket cube
#     U
#  L  F  R  B
#     D
# faces[face_name]=[top_left, top_right, bottom_left, bottom_right]
#        0 1
#        2 3
#    0 1 0 1 0 1 0 1
#    2 3 2 3 2 3 2 3
#        0 1
#        2 3
faces={}
faces["F"]=["r", "r", "r", "r"]
faces["B"]=["o", "o", "o", "o"]
faces["D"]=["y", "y", "y", "y"]
faces["U"]=["w", "w", "w", "w"]
faces["L"]=["g", "g", "g", "g"]
faces["R"]=["b", "b", "b", "b"]

# hash map from RGB_value to color
colors={}
colors["#FF0000"]="r"
colors["#00BB00"]="g"
colors["#0000FF"]="b"
colors["#FFFFFF"]="w"
colors["#FFFF00"]="y"
colors["#FFA500"]="o"

# hash map from cubie_configuration to cubie_configuration_number
color_combos={}
color_combos["rgw"]=rgw
color_combos["gwr"]=gwr
color_combos["wrg"]=wrg
color_combos["rwb"]=rwb
color_combos["wbr"]=wbr
color_combos["brw"]=brw
color_combos["ryg"]=ryg
color_combos["ygr"]=ygr
color_combos["gry"]=gry
color_combos["rby"]=rby
color_combos["byr"]=byr
color_combos["yrb"]=yrb
color_combos["owg"]=owg
color_combos["wgo"]=wgo
color_combos["gow"]=gow
color_combos["obw"]=obw
color_combos["bwo"]=bwo
color_combos["wob"]=wob
color_combos["ogy"]=ogy
color_combos["gyo"]=gyo
color_combos["yog"]=yog
color_combos["oyb"]=oyb
color_combos["ybo"]=ybo
color_combos["boy"]=boy

# hash map from cubie_configuration_number to cubie_configuration
inv_color_combos={}
inv_color_combos[rgw]="rgw"
inv_color_combos[gwr]="gwr"
inv_color_combos[wrg]="wrg"
inv_color_combos[rwb]="rwb"
inv_color_combos[wbr]="wbr"
inv_color_combos[brw]="brw"
inv_color_combos[ryg]="ryg"
inv_color_combos[ygr]="ygr"
inv_color_combos[gry]="gry"
inv_color_combos[rby]="rby"
inv_color_combos[byr]="byr"
inv_color_combos[yrb]="yrb"
inv_color_combos[owg]="owg"
inv_color_combos[wgo]="wgo"
inv_color_combos[gow]="gow"
inv_color_combos[obw]="obw"
inv_color_combos[bwo]="bwo"
inv_color_combos[wob]="wob"
inv_color_combos[ogy]="ogy"
inv_color_combos[gyo]="gyo"
inv_color_combos[yog]="yog"
inv_color_combos[oyb]="oyb"
inv_color_combos[ybo]="ybo"
inv_color_combos[boy]="boy"

def faces_to_list(faces):
    # utility function takes a hash map of face configurations
    # returns a list of cubie_configuration number
    face_positions={}
    face_positions[flu]=faces["F"][0]+faces["L"][1]+faces["U"][2]
    face_positions[luf]=faces["L"][1]+faces["U"][2]+faces["F"][0]
    face_positions[ufl]=faces["U"][2]+faces["F"][0]+faces["L"][1]

    face_positions[fur]=faces["F"][1]+faces["U"][3]+faces["R"][0]
    face_positions[urf]=faces["U"][3]+faces["R"][0]+faces["F"][1]
    face_positions[rfu]=faces["R"][0]+faces["F"][1]+faces["U"][3]

    face_positions[fdl]=faces["F"][2]+faces["D"][0]+faces["L"][3]
    face_positions[dlf]=faces["D"][0]+faces["L"][3]+faces["F"][2]
    face_positions[lfd]=faces["L"][3]+faces["F"][2]+faces["D"][0]

    face_positions[frd]=faces["F"][3]+faces["R"][2]+faces["D"][1]
    face_positions[rdf]=faces["R"][2]+faces["D"][1]+faces["F"][3]
    face_positions[dfr]=faces["D"][1]+faces["F"][3]+faces["R"][2]

    face_positions[bul]=faces["B"][1]+faces["U"][0]+faces["L"][0]
    face_positions[ulb]=faces["U"][0]+faces["L"][0]+faces["B"][1]
    face_positions[lbu]=faces["L"][0]+faces["B"][1]+faces["U"][0]

    face_positions[bru]=faces["B"][0]+faces["R"][1]+faces["U"][1]
    face_positions[rub]=faces["R"][1]+faces["U"][1]+faces["B"][0]
    face_positions[ubr]=faces["U"][1]+faces["B"][0]+faces["R"][1]

    face_positions[bld]=faces["B"][3]+faces["L"][2]+faces["D"][2]
    face_positions[ldb]=faces["L"][2]+faces["D"][2]+faces["B"][3]
    face_positions[dbl]=faces["D"][2]+faces["B"][3]+faces["L"][2]

    face_positions[bdr]=faces["B"][2]+faces["D"][3]+faces["R"][3]
    face_positions[drb]=faces["D"][3]+faces["R"][3]+faces["B"][2]
    face_positions[rbd]=faces["R"][3]+faces["B"][2]+faces["D"][3]
    #for i in range(24): print face_positions[i]
    l=tuple(color_combos[face_positions[x]] for x in range(24))
    return l

def list_to_faces(l):
    # utility function takes a list of cubie_configuration number
    # returns a hash map of face configurations
    f={}
    f["F"]=[0,0,0,0]
    f["B"]=[0,0,0,0]
    f["R"]=[0,0,0,0]
    f["L"]=[0,0,0,0]
    f["U"]=[0,0,0,0]
    f["D"]=[0,0,0,0]
    #cubie 0
    f["F"][0]=inv_color_combos[l[0]][0]
    f["L"][1]=inv_color_combos[l[0]][1]
    f["U"][2]=inv_color_combos[l[0]][2]    
    #cubie 1
    f["F"][1]=inv_color_combos[l[3]][0]
    f["U"][3]=inv_color_combos[l[3]][1]
    f["R"][0]=inv_color_combos[l[3]][2]    
    #cubie 2
    f["F"][2]=inv_color_combos[l[6]][0]
    f["D"][0]=inv_color_combos[l[6]][1]
    f["L"][3]=inv_color_combos[l[6]][2]    
    #cubie 3
    f["F"][3]=inv_color_combos[l[9]][0]
    f["R"][2]=inv_color_combos[l[9]][1]
    f["D"][1]=inv_color_combos[l[9]][2]    
    #cubie 4
    f["B"][1]=inv_color_combos[l[12]][0]
    f["U"][0]=inv_color_combos[l[12]][1]
    f["L"][0]=inv_color_combos[l[12]][2]    
    #cubie 5
    f["B"][0]=inv_color_combos[l[15]][0]
    f["R"][1]=inv_color_combos[l[15]][1]
    f["U"][1]=inv_color_combos[l[15]][2]    
    #cubie 6
    f["B"][3]=inv_color_combos[l[18]][0]
    f["L"][2]=inv_color_combos[l[18]][1]
    f["D"][2]=inv_color_combos[l[18]][2]    
    #cubie 7
    f["B"][2]=inv_color_combos[l[21]][0]
    f["D"][3]=inv_color_combos[l[21]][1]
    f["R"][3]=inv_color_combos[l[21]][2]    
    return f

def check_rep(faces):
    # sanity check for the input
    # checks if each color has 4 appearances
    r=0
    g=0
    b=0
    w=0
    y=0
    o=0
    for f in (faces["F"]+faces["B"]+faces["L"]+faces["R"]+faces["U"]+faces["D"]):
        if f=="r":
            r+=1
        elif f=="g":
            g+=1
        elif f=="b":
            b+=1
        elif f=="w":
            w+=1
        elif f=="y":
            y+=1
        elif f=="o":
            o+=1
        if r==4 and g==4 and b==4 and o==4 and w==4 and y==4:
            return True
    return False

def solve_puzzle(starting_faces):
    # takes the starting face configuration
    # returns a list of face configuration of the solution
    try:
        if check_rep(starting_faces)==False: return "Invalid color configuration, each\n color can only occurs 4 times."
        start=faces_to_list(starting_faces)
        ans=solver.shortest_path(start,I)
    except:
        return "Invalid color configuration, please\n check the colors on your cube."
    lf=[]
    ls=[]
    if ans == None:
        return "No solution"
    for p in ans:
        ls.extend([quarter_twists_names[p]])
        start=perm_apply(p,start)
        lf.extend([list_to_faces(start)])
    return [lf,ls]
