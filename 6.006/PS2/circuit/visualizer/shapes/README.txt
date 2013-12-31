This directory contains the shapes used to represent gates in the circuit
visualizer. All the files here were placed in the public domain.

If you are reading this document, you probably want to add a shape for a new
type of gate. Follow the steps below to obtain a small, normalized SVG file:

1) Find your SVG and download it, or create it with your editor of choice. The
visualizer only supports vector shapes. The shapes should have black (#000000)
outlines and white (#FFFFFF) fills.
2) Open the file in Inkscape.
3) Select everything (Ctrl+A)
4) In the top toolbar, set X to 0 and Y to 0.
5) Select File > "Vacuum Defs" from the menu.
6) Select File > "Document Properties" from the menu.
7) Open the "Resize page to content..." dropdown from the pop-up dialog box.
8) Press the "Resize page to drawing or selection" button.
9) Close the dialog box.
10) Select File > "Save as..." from the menu.
11) Select "Optimized SVG (*.svg)" from the drop-down at the bottom-right of the
dialog box.
12) Press the Save button.
13) Select the following options: "Simply colors", "Style to xml",
"Group collapsing", "Enable id stripping", "Embed rasters", "Enable viewboxing".
14) Make sure the following options are not selected: "Keep editor data",
"Strip xml prolog". 
15) Press the OK button.
16) Close the file in Inkscape.
17) Open the file in a text editor.
18) Remove comments.
19) Remove the <metadata> tag.
