# View class for a raster image.
class ImageView
  # Initializes the layer from data in the .jsonp file.
  constructor: (@canvas, imageJson) ->
    @sy = imageJson.rows
    @sx = imageJson.cols
    @data = for hexString in imageJson.data
      i = 0
      row = []
      while i < hexString.length
        color = hexString.substring(i, i + 6)
        row.push [
          parseInt(color.substring(0, 2), 16),
          parseInt(color.substring(2, 4), 16),
          parseInt(color.substring(4, 6), 16),
        ]
        i += 6
      row
    @renderToCanvas()
    
  # Renders the static image to the canvas.
  renderToCanvas: () ->
    texture = document.createElement 'canvas'
    texture.width = @sx
    texture.height = @sy
    context = texture.getContext '2d'
    imageData = context.createImageData @sx, @sy
    for y in [0...@sy]
      for x in [0...@sx]
        imageData.data[y * @sx * 4 + x * 4] = @data[y][x][0]
        imageData.data[y * @sx * 4 + x * 4 + 1] = @data[y][x][1]
        imageData.data[y * @sx * 4 + x * 4 + 2] = @data[y][x][2]
        imageData.data[y * @sx * 4 + x * 4 + 3] = 255
    context.putImageData imageData, 0, 0
    
    context = @canvas.getContext '2d'
    context.drawImage texture, 0, 0, @sx, @sy, 0, 0, @canvas.width,
                      @canvas.height

# Controller for the visualization.
class Visualizer
  constructor: (encryptedCanvas, decryptedCanvas, traceData) ->
    @encryptedImage = new ImageView encryptedCanvas, traceData.encrypted
    @decryptedImage = new ImageView decryptedCanvas, traceData.image
    
# Module-global that holds the trace data until onload is called.
traceData = null
# Called by circuit.jsonp to supply the simulation data.
window.onJsonp = (data) ->
  traceData = data
  
# Sets up the simulation once everything is loaded.
window.onload = ->
  encryptedCanvas = document.getElementById 'encrypted-canvas'
  decryptedCanvas = document.getElementById 'decrypted-canvas'
  window.visualizer = new Visualizer encryptedCanvas, decryptedCanvas, traceData
  traceData = null
