import os
import struct
import sys

try:
    from PIL import Image
except:
    print 'You do not have PIL (the Python Imaging Library) installed.'
    sys.exit(1)

class SeamError(Exception):
    pass

class ImageMatrix(dict):
    def __init__(self, image):
        """Takes either a PIL image, or a filename of an image. Stores
        pixels in its dictionary, and also stores width and height."""
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        self.width, self.height = image.size
        pixels = iter(image.getdata())
        for j in range(self.height):
            for i in range(self.width):
                self[i,j] = pixels.next()

    def color_seam(self, seam, color=(255,0,0)):
        """Takes a seam (a list of coordinates) and colors it all one
        color."""
        for i,j in seam:
            self[i,j] = color

    def remove_seam(self, seam):
        """Takes a seam (a list of coordinates with exactly one pair of
        coordinates per row). Removes pixel at each of those coordinates,
        and slides left all the pixels to its right. Decreases the width
        by 1."""
        seen = [False for j in range(self.height)]
        for i,j in seam:
            if not (0 <= j < self.height):
                raise SeamError('seam has nonexistent row %d' % i)
            if seen[j]:
                raise SeamError('seam has repeated row %d' % i)
            seen[j] = True
            for ii in range(i, self.width-1):
                self[ii,j] = self[ii+1,j]
            del self[self.width-1,j]
        missed = [j for j in range(self.height) if not seen[j]]
        if missed:
            raise SeamError('seam missed rows %s' % ','.join(map(str,missed)))
        self.width -= 1

    def image(self):
        """Returns a PIL Image that is represented by self."""
        image = Image.new('RGB', (self.width, self.height))
        image.putdata(
            [self[i,j] for j in range(self.height) for i in range(self.width)])
        return image

    def save(self,*args,**keyw):
        self.image().save(*args,**keyw)

    def ppm(self):
        """Returns self in (binary) ppm form."""
        return 'P6 %d %d 255\n' % (self.width, self.height) + \
            ''.join ([struct.pack('BBB', *self[i,j])
                      for j in range(self.height) for i in range(self.width)])
    def save_ppm(self, filename):
        """Saves self as a .ppm"""
        f = open(filename, 'wb')
        f.write(self.ppm())
        f.close()

    def show(self,title='image',temp='_temp_.ppm'):
        """Displays self in a pop-up window using Tkinter,
        and waits till the user either clicks on or closes the window.
        Saves the image as a temporary ppm file (specified by temp)."""
        import Tkinter
        if Tkinter._default_root:
            root=Tkinter.Toplevel()
        else:
            root=Tkinter.Tk()
        self.save_ppm(temp)
        image = Tkinter.PhotoImage(master=root, file=temp)
        root.title('%dx%d image' % (self.width, self.height))
        label = Tkinter.Label(root, image=image)
        label.pack()
        label.bind('<Button>', lambda e: root.destroy())
        root.mainloop()
        os.remove(temp)

    def energy(self, i, j):
        """Given coordinates (i,j), returns an energy, or cost associated
        with removing that pixel."""
        if i==0 or j==0 or i==self.width-1 or j==self.height-1:
            # For simplicity, return an arbitrarily large value on the edge.
            return 10000
        else: # I think this is equivalent to the Sobel gradient magnitude.
            return self.distance(self[i-1,j], self[i+1,j]) +\
                   self.distance(self[i,j-1], self[i,j+1]) +\
                   self.distance(self[i-1,j-1], self[i+1,j+1]) +\
                   self.distance(self[i+1,j-1], self[i-1,j+1])

    def distance(self, pixelA, pixelB):
        """A distance metric between two pixels, based on their colors."""
        ans = 0
        for i in range(len(pixelA)):
            valueA = pixelA[i]
            valueB = pixelB[i]
            ans += abs(valueA-valueB)
        return ans
