# Created by Anh Nguyen 
# MIT 6.006 - Fall 2008,
#             Fall 2011     
#
# This application created the GUI for pocket cube solver. Its main features are:
# - Get input from users in a visual and convenient way.
# - Call up solver.py through RubikAbstraction.py to solve the cube.
# - Display solution in an intuitive way.
# Notes: This is created for Linux to match the font, size, and button behavior in Tk

from Tkinter import *
from RubikAbstraction import *

class Application:
    ################# CONSTANTS ##################
    colors = {}
    colors["#FF0000"]="r"
    colors["#00BB00"]="g"
    colors["#0000FF"]="b"
    colors["#FFFFFF"]="w"
    colors["#FFFF00"]="y"
    colors["#FFA500"]="o"

    colors_hover = {}
    colors_hover["#FF0000"]="#DD0000"
    colors_hover["#00BB00"]="#00DD00"
    colors_hover["#0000FF"]="#0000DD"
    colors_hover["#FFFFFF"]="#EEEEEE"
    colors_hover["#FFFF00"]="#DDDD00"
    colors_hover["#FFA500"]="#DD8300"
    
    faces = {}
    faces["F"]=[0, 0, 0, 0]
    faces["B"]=[0, 0, 0, 0]
    faces["L"]=[0, 0, 0, 0]
    faces["R"]=[0, 0, 0, 0]
    faces["U"]=[0, 0, 0, 0]
    faces["D"]=[0, 0, 0, 0]
    
    faces_pos = {}
    faces_pos["F"]=[2, 2]
    faces_pos["B"]=[6, 2]
    faces_pos["L"]=[0, 2]
    faces_pos["R"]=[4, 2]
    faces_pos["U"]=[2, 0]
    faces_pos["D"]=[2, 4]

    faces_color = {}
    faces_color["F"]="r"
    faces_color["B"]="o"
    faces_color["L"]="g"
    faces_color["R"]="b"
    faces_color["U"]="w"
    faces_color["D"]="y"

    btnColor_w_defaut = 3
    btnColor_h_defaut = 2

#################### VARIABLES ###############
    current_color_selection = ""

    #list of color buttons for color picker
    btnColors = []

    #dictionary that map button for each cell on the face to a [face, index]
    faceButtons = {}

    #list of solving steps
    steps = []
    solution = []

    #list of solving steps buttons
    step_buttons = []
    step_buttons_faces = {}
    current_sol_button = 0
    sol_left = None
    sol_right = None

    #information label
    lblInfo = None
    lblSol = None

    #images
    imgRubik = None
    imgArrowUp = None
    imgArrowDown = None
    imgArrowLeft = None
    imgArrowRight = None
    imgArrowTurn0 = None
    imgArrowTurn90 = None
    imgArrowTurn180 = None
    imgArrowTurn270 = None
    imgArrowTurn0i = None
    imgArrowTurn90i = None
    imgArrowTurn180i = None
    imgArrowTurn270i = None
    imgBlank = None

    #direction buttons
    btnLogo = None
    btnUp = None
    btnDown = None
    btnLeft = None
    btnRight = None
    btnTurn0 = None
    btnTurn90 = None
    btnTurn180 = None
    btnTurn270 = None

###############################################

    def fill_cell_properties(self, button, x, y):
        button["borderwidth"] = 1
        #button["text"] = x % 2 + y % 2 * 2
        facePos = [x - x % 2, y - y % 2]
        face = self.value2key(self.faces_pos, facePos)
        i = x % 2 + y % 2 * 2
        button["bg"]  = self.getColor(self.faces[face][i])
        button["activebackground"] = self.colors_hover[self.getColor(self.faces[face][i])]
        return 0

    def value2key(self, d, value):
        for k in d.keys():
            if (d[k] == value):
                return k
            
        return None

    def getFaceColor(self, face):
        return self.getColor(self.faces_color[face])


    def getColor(self, colorCode):
        return self.value2key(self.colors, colorCode)

############ GUI COMPONENTS ############


        #creates Button objects for each face of a cubie
    def create_rubik(self, f):
        self.btnUp = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnUp.grid(row=0, column=3)
        
        for y in range(6):
            for x in range(8):
                if y in range(2,4) or x in range(2,4):
                    button = Button(f, width=4, height=3)
                    #if (x == 3 and y == 5):
                    #    button["image"] = self.imgRubik
                    #    button["width"] = lastButton["width"]
                    #    button["height"] = 20

                    button.grid(row = y + 1,column = x + 1)
                    
                    self.fill_cell_properties(button, x, y)
                    
                    facePos = [x - x % 2, y - y % 2]
                    face = self.value2key(self.faces_pos, facePos)
                    index = x % 2 + y % 2 * 2
                    self.faceButtons[button] = [face, index]
                    
                    button.bind("<Button-1>", self.btnCell_clicked)
					

        labelTop = Label(f, text="Top", width=5, height=3, bg="#E2E2E2")
        labelTop.grid(row=1,column=2)
                    
        labelBottom = Label(f, text="Down", width=5, height=3, bg="#E2E2E2")
        labelBottom.grid(row=6,column=2)
                    
        labelLeft = Label(f, text="Left", width=5, height=3, anchor=S, bg="#E2E2E2")
        labelLeft.grid(row=2,column=1)
                    
        labelRight = Label(f, text="Right", width=5, height=3, anchor=S, bg="#E2E2E2")
        labelRight.grid(row=2,column=6)
                    
        labelBack = Label(f, text="Back", width=5, height=3, anchor=S, bg="#E2E2E2")
        labelBack.grid(row=2,column=8)
                    
        self.btnLogo = Button(f, image=self.imgRubik, borderwidth=0, anchor=W, command=self.btnLogo_clicked, bg="#E2E2E2")
        self.btnLogo.grid(row=6, column=5)

                    
        self.btnDown = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnDown.grid(row=7, column=3)
        
        self.btnLeft = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnLeft.grid(row=3, column=0)
        
        self.btnRight = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnRight.grid(row=3, column=9)
        
        self.btnTurn270 = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnTurn270.grid(row=2, column=2)
        
        self.btnTurn0 = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnTurn0.grid(row=2, column=5)
        
        self.btnTurn90 = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnTurn90.grid(row=5, column=5)
        
        self.btnTurn180 = Button(f, image=self.imgBlank, borderwidth=0, command=self.btnArrow_clicked, bg="#E2E2E2")
        self.btnTurn180.grid(row=5, column=2)

        return None


    #update current configuration
    def update_rubik(self):
        for btn in self.faceButtons:
            self.update_cell(btn)
        self.lblInfo["text"] = ""

    #update the button representing a cell
    def update_cell(self, btn):
        face = self.faceButtons[btn][0]
        index = self.faceButtons[btn][1]
        self.fill_cell_properties(btn, self.faces_pos[face][0] + index % 2, self.faces_pos[face][1] + index / 2)

    
    #reset rubik to the initial state
    def reset_rubik(self):
        for f in self.faces.keys():
            for i in range(4):
                self.faces[f][i] = self.faces_color[f]
        return None

    #create color selection panel
    def create_color_picker(self, f):
        self.label = Label(f,text="Pick colors to edit the cube:", bg="#FFFFFF")
        self.label.pack(side=LEFT)

        for c in self.colors.keys():
            button = Button(f, width=self.btnColor_w_defaut, height=self.btnColor_h_defaut)
            button.bind("<Button-1>", self.btnColor_clicked)

                #button["command"] = self.btnColor_clicked
            button["bg"] = c
            button["activebackground"] = self.colors_hover[c]
            button.pack(side=LEFT)
            self.btnColors.append(button)

            if (self.current_color_selection == ""):
                self.current_color_selection = c
                button["width"] = self.btnColor_w_defaut + 1
                button["height"] = self.btnColor_h_defaut + 1

        return None

    #create controller
    def create_controller(self, f):
        button = Button(f, text="Reset", command=self.btnReset_clicked)
        button["bg"] = "#FFFFFF"
        button.pack(side=LEFT)

        button = Button(f, text="Solve", command=self.solve_rubik)
        button["bg"] = "#FFFFFF"
        button.pack(side=LEFT)

        button = Button(f, text="Demo", command=self.show_demo)
        button["bg"] = "#FFFFFF"
        button.pack(side=LEFT)

        button = Button(f, text="About", command=self.show_about)
        button["bg"] = "#FFFFFF"
        button.pack(side=LEFT)

        self.lblInfo = Label(f, bg="#FFFFFF")
        self.lblInfo.pack(side=LEFT)

        return None

    #create controller
    def create_solution_panel(self, f):
        self.lblSol = Label(f, text="Solving steps:")
        self.lblSol.pack(side=LEFT)
        self.lblSol["text"] = ""

        button = Button(f, command=self.btnPrevMove_clicked)
        button.pack(side=LEFT)
        self.sol_left = button
        self.sol_left["borderwidth"] = 0;

        button = Button(f, command=self.btnNextMove_clicked)
        button.pack(side=LEFT)
        self.sol_right = button
        self.sol_right["borderwidth"] = 0;

        for i in range(15):
            button = Button(f, state=DISABLED, width=1)
            button.pack(side=LEFT)
            button["borderwidth"] = 0
            self.step_buttons.append(button)
            button.bind("<Button-1>", self.btnSol_clicked)


        return None
    
    def show_sol_controllers(self):
        self.sol_left["borderwidth"] = 1;
        self.sol_left["bg"] = "#FFFFFF"
        self.sol_left["text"] = "<"

        self.sol_right["borderwidth"] = 1;
        self.sol_right["bg"] = "#FFFFFF"
        self.sol_right["text"] = ">"
		
        self.lblSol["text"] = "Solving steps:"
        
    def hide_sol_controllers(self):
        self.sol_left["borderwidth"] = 0;
        self.sol_left["bg"] = self.step_buttons[0]["bg"]
        self.sol_left["text"] = ""

        self.sol_right["borderwidth"] = 0;
        self.sol_right["bg"] = self.step_buttons[0]["bg"]
        self.sol_right["text"] = ""
		
        self.lblSol["text"] = ""
        for btn in self.step_buttons:
            btn["state"] = DISABLED
            btn["borderwidth"] = 0   
            btn["text"] = ""			

        self.display_arrow("0")

    #update solution buttons based on the answers
    def update_solution_panel(self, initial_face):
        self.show_sol_controllers()
        for i in range(15):
            self.step_buttons[i]["text"] = ""
            if (i <= len(self.solution)):
                if (i > 0):
                    self.step_buttons[i]["text"] = self.solution[i-1]
                    self.step_buttons_faces[self.step_buttons[i]] = self.steps[i-1]
                else:
                    self.step_buttons[i]["text"] = "Start"
                    self.step_buttons_faces[self.step_buttons[i]] = initial_face
        self.current_sol_button = self.step_buttons[0]
        self.update_solution_panel_display()
                
    def update_solution_panel_display(self):
        for i in range(15):
            if (i > len(self.steps)):
                self.step_buttons[i]["state"] = DISABLED
                self.step_buttons[i]["borderwidth"] = 0
            else:
                self.step_buttons[i]["state"] = NORMAL
                self.step_buttons[i]["borderwidth"] = 1
        self.current_sol_button["borderwidth"] = 0
        i = self.step_buttons.index(self.current_sol_button)
        if (i < len(self.solution)):
            self.display_arrow(self.solution[i])
        else:
            self.display_arrow("0")

        self.btnLogo["image"] = self.imgBlank
            

    #display arrows corresponding to the solution step
    def display_arrow(self, turn_type):
        if (turn_type == "U"):
            self.set_all_arrows([self.imgBlank, self.imgBlank, self.imgArrowLeft, self.imgArrowLeft] + [self.imgBlank] * 4)
        elif (turn_type == "Ui"):
            self.set_all_arrows([self.imgBlank, self.imgBlank, self.imgArrowRight, self.imgArrowRight] + [self.imgBlank] * 4)
        elif (turn_type == "L"):
            self.set_all_arrows([self.imgArrowDown, self.imgArrowDown] + [self.imgBlank] * 6)
        elif (turn_type == "Li"):
            self.set_all_arrows([self.imgArrowUp, self.imgArrowUp] + [self.imgBlank] * 6)
        elif (turn_type == "F"):
            self.set_all_arrows([self.imgBlank] * 4 + [self.imgArrowTurn270, self.imgArrowTurn0, self.imgArrowTurn90, self.imgArrowTurn180])
        elif (turn_type == "Fi"):
            self.set_all_arrows([self.imgBlank] * 4 + [self.imgArrowTurn0i, self.imgArrowTurn90i, self.imgArrowTurn180i, self.imgArrowTurn270i])
        else:
            self.set_all_arrows([self.imgBlank] * 12)

    #set a set of images to all arrows
    def set_all_arrows(self, image_set):
        if (len(image_set) < 8):
            print "not enough arrow images"
        else:
            self.btnUp["image"] = image_set[0]
            self.btnDown["image"] = image_set[1]
            self.btnLeft["image"] = image_set[2]
            self.btnRight["image"] = image_set[3]
            self.btnTurn270["image"] = image_set[4]
            self.btnTurn0["image"] = image_set[5]
            self.btnTurn90["image"] = image_set[6]
            self.btnTurn180["image"] = image_set[7]

################### MOUSE ACTION ###################
    def btnColor_clicked(self, event):
        if (len(self.steps) == 0):
            for b in self.btnColors:
                b["width"] = self.btnColor_w_defaut
                b["height"] = self.btnColor_h_defaut
                
            event.widget["width"] = self.btnColor_w_defaut + 1
            event.widget["height"] = self.btnColor_h_defaut + 1

            self.current_color_selection = event.widget["bg"]
        else:
            self.lblInfo["text"] = "Please Reset before editing colors."

    def btnCell_clicked(self, event):
        btn = event.widget
        self.change_cell_color(btn, self.current_color_selection)

    def change_cell_color(self, btn, new_color):
        if (len(self.steps) == 0):
            face = self.faceButtons[btn][0]
            index = self.faceButtons[btn][1]
            if (face == "D" and index == 3):
                self.lblInfo["text"] = "By convention, the logo yellow square \nshould be here before solving."
                return
            else:
                self.lblInfo["text"] = ""
                self.faces[face][index] = self.colors[new_color]
                self.update_cell(btn)
        else:
            self.lblInfo["text"] = "Please Reset before editing colors."

    def solve_rubik(self):
        if (len(self.steps) == 0):
            ans = solve_puzzle(self.faces)
            if (type(ans) == type("abc")):
                print "Warning:" + ans
                self.lblInfo["text"] = ans
                return
            
            self.lblInfo["text"] = ""
            self.steps = ans[0]
            self.solution = ans[1]

            self.update_solution_panel(self.faces)
        else:
            self.lblInfo["text"] = "This is already solved. Click \nReset if you want to solve another."

        
    def btnLogo_clicked(self):
        self.lblInfo["text"] = "By convention, the logo yellow square \nshould be here before solving."
        
    def btnReset_clicked(self):
        self.reset_rubik()
        self.update_rubik()
        self.steps = []
        self.solution = []
        self.hide_sol_controllers()
        self.lblInfo["text"] = ""
        self.btnLogo["image"] = self.imgRubik

		
    def btnSol_clicked(self, event):
        btn = event.widget
        self.run_step(btn)

    def btnNextMove_clicked(self):
        i = self.step_buttons.index(self.current_sol_button)
        if (i < len(self.steps)):
            self.current_sol_button = self.step_buttons[i + 1]
            self.faces = self.step_buttons_faces[self.current_sol_button]
            self.update_solution_panel_display()
            self.update_rubik()
        
    def btnPrevMove_clicked(self):
        i = self.step_buttons.index(self.current_sol_button)
        if (i > 0):
            self.current_sol_button = self.step_buttons[i - 1]
            self.faces = self.step_buttons_faces[self.current_sol_button]
            self.update_solution_panel_display()
            self.update_rubik()

    def btnArrow_clicked(self):
        if (len(self.steps) > 0):
            self.lblInfo["text"] = "These arrows indicate the twisting \ndirection of the next move."

    def run_step(self, btn):
        if (btn["state"] == DISABLED):
            return
        self.current_sol_button = btn
        self.faces = self.step_buttons_faces[self.current_sol_button]
        self.update_solution_panel_display()
        self.update_rubik()

    #show a solution from a shuffled cube to the final configuration
    def show_demo(self):
        if (len(self.steps) == 0):
            self.faces["F"]=["w", "b", "r", "r"]
            self.faces["B"]=["g", "y", "o", "o"]
            self.faces["D"]=["b", "b", "y", "y"]
            self.faces["U"]=["g", "w", "g", "w"]
            self.faces["L"]=["r", "r", "g", "y"]
            self.faces["R"]=["o", "o", "w", "b"]
            self.update_rubik()
            self.steps = []
            self.solution = []
            self.hide_sol_controllers()
            self.btnLogo["image"] = self.imgRubik
            self.lblInfo["text"] = "Here is a shuffled cube, please click \non Solve button to solve."
        else:
            self.lblInfo["text"] = "This will interrupt your solving process\nplease Reset first."

    def show_about(self):
        print "====================================\n Created by Anh Nguyen and Huan Liu\n MIT 6.006 - Fall 2008.\n===================================="
        self.lblInfo["text"] = "====================================\n Created by Anh Nguyen and Huan Liu\n MIT 6.006 - Fall 2008.\n===================================="

################### INIT ###################
    def __init__(self, root):
        root.title("Pocket Cube Solver")
        root["bg"] = bg="#E2E2E2"
        self.initialize_images()

        self.reset_rubik()

        fColor = Frame(root, height=75, width=830, bg="#FFFFFF")
        fColor.pack_propagate(0)
        fColor.pack()
        self.create_color_picker(fColor)

        fRubik = Frame(root, height=400, width=830, bg="#E2E2E2")
        fRubik.pack_propagate(0) # don't shrink
        fRubik.pack()
        self.create_rubik(fRubik)

        fSol = Frame(root, height=60, width=830)
        fSol.pack_propagate(0)
        fSol.pack()
        self.create_solution_panel(fSol)

        fController = Frame(root, height=60, width=830, bg="#FFFFFF")
        fController.pack_propagate(0)
        fController.pack()
        self.create_controller(fController)

    def initialize_images(self):
        self.imgRubik = PhotoImage(file="img/rubiks_logo.gif")
        self.imgArrowUp = PhotoImage(file="img/up_arrow.gif")
        self.imgArrowRight = PhotoImage(file="img/right_arrow.gif")
        self.imgArrowDown = PhotoImage(file="img/down_arrow.gif")
        self.imgArrowLeft = PhotoImage(file="img/left_arrow.gif")
        self.imgArrowTurn0 = PhotoImage(file="img/turn0_arrow.gif")
        self.imgArrowTurn90 = PhotoImage(file="img/turn90_arrow.gif")
        self.imgArrowTurn180 = PhotoImage(file="img/turn180_arrow.gif")
        self.imgArrowTurn270 = PhotoImage(file="img/turn270_arrow.gif")
        self.imgArrowTurn0i = PhotoImage(file="img/turn0i_arrow.gif")
        self.imgArrowTurn90i = PhotoImage(file="img/turn90i_arrow.gif")
        self.imgArrowTurn180i = PhotoImage(file="img/turn180i_arrow.gif")
        self.imgArrowTurn270i = PhotoImage(file="img/turn270i_arrow.gif")
        self.imgBlank = PhotoImage(file="img/blank.gif")

################### RUN ############################

toplevel_window = Tk()

app = Application(toplevel_window)

toplevel_window.mainloop()
