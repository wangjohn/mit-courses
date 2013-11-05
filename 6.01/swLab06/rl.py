from Tkinter import *

class RootLocus:
    def increment3(self):
        self.update(self.K+10)
    def increment2(self):
        self.update(self.K+1)
    def increment1(self):
        self.update(self.K+0.1)
    def increment0(self):
        self.update(self.K+0.01)
    def decrement0(self):
        self.update(self.K-0.01)
    def decrement1(self):
        self.update(self.K-0.1)
    def decrement2(self):
        self.update(self.K-1)
    def decrement3(self):
        self.update(self.K-10)
    def __init__(self, makeSF):
        self.makeSF = makeSF
        self.zWidth = 300
        self.zHeight = 300
        self.pWidth = 600
        self.pHeight = 300
        self.zErase = []
        self.pErase = []
        self.root = Tk()
        self.zCanvas = Canvas(self.root, width=self.zWidth, height=self.zHeight)
        self.pCanvas = Canvas(self.root, width=self.pWidth, height=self.pHeight)
        self.zCanvas.pack(side='left')
        self.pCanvas.pack(side='left')
        self.zCanvas.create_rectangle(0,0,self.zWidth,self.zHeight,fill='white')
        self.zCanvas.create_line(self.zScaleX(0),self.zScaleY(-1.25),self.zScaleX(0),self.zScaleY(1.25),fill='black')
        self.zCanvas.create_line(self.zScaleX(-1.25),self.zScaleY(0),self.zScaleX(1.25),self.zScaleY(0),fill='black')
        self.zCanvas.create_oval(self.zScaleX(-1),self.zScaleY(-1),self.zScaleX(1),self.zScaleY(1),outline='black')
        self.zCanvas.create_text(self.zScaleX(1.4),self.zScaleY(0),text='Re',font=('Helvetica',9,'normal'),fill='black')
        self.zCanvas.create_text(self.zScaleX(0),self.zScaleY(1.35),text='Im',font=('Helvetica',9,'normal'),fill='black')
        self.pCanvas.create_rectangle(0,0,self.pWidth,self.pHeight,fill='white')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(-1.1),self.pScaleX(0),self.pScaleY(1.1),fill='black')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(0),self.pScaleX(1),self.pScaleY(0),fill='black')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(1/2.791),self.pScaleX(1),self.pScaleY(1/2.791),fill='red', dash=(2,2))
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(-1/2.791),self.pScaleX(1),self.pScaleY(-1/2.791),fill='red', dash=(2,2))
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(0.1),self.pScaleX(1),self.pScaleY(0.1),fill='green', dash=(2,2))
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(-0.1),self.pScaleX(1),self.pScaleY(-0.1),fill='green', dash=(2,2))
        self.pCanvas.create_text(self.pScaleX(1)+10,self.pScaleY(0),text='n',font=('Helvetica',9,'normal'),fill='black')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(1),self.pScaleX(0)-8,self.pScaleY(1),fill='black')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(0),self.pScaleX(0)-8,self.pScaleY(0),fill='black')
        self.pCanvas.create_line(self.pScaleX(0),self.pScaleY(-1),self.pScaleX(0)-8,self.pScaleY(-1),fill='black')

        Button(self.root, width=4, text="+10", command=self.increment3).pack()
        Button(self.root, width=4, text="+1", command=self.increment2).pack()
        Button(self.root, width=4, text="+0.1", command=self.increment1).pack()
        Button(self.root, width=4, text="+0.01", command=self.increment0).pack()
        Button(self.root, width=4, text="-0.01", command=self.decrement0).pack()
        Button(self.root, width=4, text="-0.1", command=self.decrement1).pack()
        Button(self.root, width=4, text="-1", command=self.decrement2).pack()
        Button(self.root, width=4, text="-10", command=self.decrement3).pack()

    def zScaleX(self, x):
        return (1.5+x)*self.zWidth/3.-5
    def zScaleY(self, y):
        return (1.5-y)*self.zHeight/3.
    def pScaleX(self, x):
        return x*(self.pWidth-100)+80
    def pScaleY(self, y):
        return (1.2-y)*self.pHeight/2.4
    def pole(self, x,y):
        self.zErase.append(self.zCanvas.create_line(self.zScaleX(x)-7,self.zScaleY(y)-7,self.zScaleX(x)+7,self.zScaleY(y)+7,fill='blue',width=3))
        self.zErase.append(self.zCanvas.create_line(self.zScaleX(x)-7,self.zScaleY(y)+7,self.zScaleX(x)+7,self.zScaleY(y)-7,fill='blue',width=3))
    def stem(self, x,y):
        self.pErase.append(self.pCanvas.create_line(self.pScaleX(x),self.pScaleY(y),self.pScaleX(x),self.pScaleY(0),fill='blue',width=2))
        self.pErase.append(self.pCanvas.create_oval(self.pScaleX(x)-4,self.pScaleY(y)-4,self.pScaleX(x)+4,self.pScaleY(y)+4,outline='blue',fill='white',width=2))
    def lineseg(self, x0,y0,x1,y1):
        self.pErase.append(self.pCanvas.create_line(self.pScaleX(x0),self.pScaleY(y0),self.pScaleX(x1),self.pScaleY(y1),fill='brown',dash=(2,4),width=2))
    
    def viewResponse(self,title,poles,response,envelope):
        for e in self.zErase:
            self.zCanvas.delete(e)
        for e in self.pErase:
            self.pCanvas.delete(e)
        self.zErase = []
        self.pErase = []
        self.root.wm_title(title)
        for p in poles:
            self.pole(p.real,p.imag)
        N = len(response)
        smax = max(response) + 1e-16
        self.pErase.append(self.pCanvas.create_text(self.pScaleX(0)-35,self.pScaleY(1),text="{0:5.2f}".format(smax),font=('Helvetica',9,'normal'),fill='black'))
        self.pErase.append(self.pCanvas.create_text(self.pScaleX(0)-35,self.pScaleY(0),text="{0:5.2f}".format(0.0),font=('Helvetica',9,'normal'),fill='black'))
        self.pErase.append(self.pCanvas.create_text(self.pScaleX(0)-35,self.pScaleY(-1),text="{0:5.2f}".format(-smax),font=('Helvetica',9,'normal'),fill='black'))
        s = [s/smax for s in response]
        for i in range(N):
            self.stem(i/(N-0.5),s[i])
        for i in range(N-1):
            self.lineseg((i)/(N-0.5),envelope[i]/smax,(i+1)/(N-0.5),envelope[i+1]/smax)
            self.lineseg((i)/(N-0.5),-envelope[i]/smax,(i+1)/(N-0.5),-envelope[i+1]/smax)

    def show(self):
        self.cont = '0'
        def reafter():
            if self.cont=='0':
                self.root.after(500,reafter)
            else:
                self.root.quit()
        self.root.after(500,reafter)
        def handleReturn(event):
            self.cont = event.char
        self.root.bind("<Key>",handleReturn)
        self.root.mainloop()
        return self.cont

    def update(self, K):
        self.K = K
        poles = self.makeSF(self.K).poles()
        response = self.makeSF(self.K).stateMachine().transduce([1]+29*[0])
        r = max([abs(pp) for pp in poles])
        a = max([abs(response[n])/(r**n+0.01) for n in range(30)])
        envelope = [a*(r**n) for n in range(30)]
        title = 'K = {0:f}     abs(dominant pole) = {1:f}'.format(self.K,r)
        self.viewResponse(title,poles,response,envelope)
        
    def view(self,K):
        self.update(K)
        self.show()
