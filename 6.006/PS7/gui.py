import os
import Tkinter, tkFileDialog
from resizeable_image import ResizeableImage

seam = None
image = None
temp='_gtemp_.ppm'

def open_file():
    global image, status
    filename = tkFileDialog.askopenfilename()
    if filename is None: return
    status['text'] = 'Loading %s...' % os.path.basename(filename)
    status.update()
    try:
        image = ResizeableImage(filename)
    except:
        status['text'] = 'Error loading %s!' % os.path.basename(filename)
        raise
    update_display()
    seam = None
    status['text'] = 'Loaded %s.  Now compute or remove seam.' % \
                     os.path.basename(filename)

def save_file():
    global image, status
    if image is None: return
    filename = tkFileDialog.asksaveasfilename()
    if filename is None: return
    status['text'] = 'Saving %s...' % os.path.basename(filename)
    status.update()
    try:
        image.save(filename)
    except:
        status['text'] = 'Error saving %s!' % os.path.basename(filename)
        raise
    status['text'] = 'Saved %s.' % os.path.basename(filename)

def update_display():
    global image, photo, display, root, buttons
    image.save_ppm(temp)
    photo = Tkinter.PhotoImage(master=root, file=temp)
    display['image'] = photo
    root.wm_geometry('%dx%d' % (
      buttons.winfo_width() + image.width,
      status.winfo_height() + max(image.height, buttons.winfo_height()) ))
    os.remove(temp)

def compute_seam(count=0):
    global seam
    if seam is None:
        if count:
            status['text'] = 'Computing seam %d...' % (count+1)
        else:
            status['text'] = 'Computing seam...'
        status.update()
        seam = image.best_seam()
        if count:
            status['text'] = 'Computed seam %d.' % (count+1)
        else:
            status['text'] = 'Computed seam.'

def show_seam():
    global image, seam
    if image is None: return
    compute_seam()
    image.color_seam(seam)
    update_display()
    status['text'] = 'Computed seam, as shown in red.'

def remove_seam():
    global image, seam
    if image is None: return
    count = 0
    while True:
        compute_seam(count)
        image.remove_seam(seam)
        update_display()
        seam = None
        count += 1

        try:
            repeat = int(multiple_spin.get())
        except ValueError:
            break
        if repeat <= 1: break
        repeat -= 1
        multiple_spin.delete(0,'end')
        multiple_spin.insert(0,repeat)
        multiple_spin.update()
    multiple_spin.delete(0,'end')
    multiple_spin.insert(0,1)
    if count > 1:
        status['text'] = 'Removed %d seams.' % count
    else:
        status['text'] = 'Removed seam.'

root = Tkinter.Tk()
root.title('6.006 Seam Carving')
status = Tkinter.Label(text='Please open an image.')
status.pack(side='top')
buttons = Tkinter.Frame()
open_button = Tkinter.Button(buttons, text='Open...', command=open_file)
open_button.pack(side='top', fill='x')
save_button = Tkinter.Button(buttons, text='Save...', command=save_file)
save_button.pack(side='top', fill='x')
show_button = Tkinter.Button(buttons, text='Show Seam', command=show_seam)
show_button.pack(side='top', fill='x')
remove_button = Tkinter.Button(buttons, text='Remove Seam', command=remove_seam)
remove_button.pack(side='top', fill='x')
multiple_frame = Tkinter.Frame(buttons)
multiple_label = Tkinter.Label(multiple_frame, text='Repeat:')
multiple_label.pack(side='left')
multiple_spin = Tkinter.Spinbox(multiple_frame,
    width=3, from_=1, to_=100, increment=1)
multiple_spin.pack(side='right')
multiple_frame.pack(side='top', fill='x')
buttons.pack(side='left')
display = Tkinter.Label(root)
display.pack(side='top')
root.mainloop()
