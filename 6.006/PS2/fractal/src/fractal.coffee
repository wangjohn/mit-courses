class Snowflake
  constructor: (@canvas) ->
    side = Math.min(@canvas.scrollWidth, @canvas.scrollHeight)
    @sx = side
    @sy = side
    @padding = 5
    
    @raphael = Raphael @canvas, side, side
  
  # Coordinates magic and recursion.
  
  redraw: (lod, useTriangles = false) ->
    @raphael.clear()
    @pathCommand = null
    @statsClear()
    
    sx = @sx - 2 * @padding
    sy = @sy - 2 * @padding
    s3 = Math.sqrt(3)
    @sideLength = sx * s3 / 2
    if useTriangles
      @triangleStart @padding + sx / 2, @padding
      @triangle sx * -s3 / 4, sy * 3 / 4, sx * s3 / 2, 0, lod 
    else
      @pathStart @padding + sx / 2, @padding
    @edge lod, sx * -s3 / 4, sy * 3 / 4
    @edge lod, sx * s3 / 2, 0
    @edge lod, sx * -s3 / 4, sy * -3 / 4
    @pathEnd() if @pathCommand
    
  edge: (lod, xDelta, yDelta) ->
    if lod is 0
      if @pathCommand
        @pathLine xDelta, yDelta
      else
        @triangleMove xDelta, yDelta
    else
      @edge lod - 1, xDelta / 3, yDelta / 3
      unless @pathCommand
        @triangle xDelta / 6 - yDelta * Math.sqrt(3) / 6,
                  yDelta / 6 + xDelta * Math.sqrt(3) / 6,
                  xDelta / 6 + yDelta * Math.sqrt(3) / 6,
                  yDelta / 6 - xDelta * Math.sqrt(3) / 6,
      @edge lod - 1, xDelta / 6 - yDelta * Math.sqrt(3) / 6,
                     yDelta / 6 + xDelta * Math.sqrt(3) / 6
      @edge lod - 1, xDelta / 6 + yDelta * Math.sqrt(3) / 6,
                     yDelta / 6 - xDelta * Math.sqrt(3) / 6, 
      @edge lod - 1, xDelta / 3, yDelta / 3

  # 2D rendering code

  pathStart: (xStart, yStart) ->
    @pathCommand = ['M', xStart, ',', yStart, 'l']

  pathLine: (xDelta, yDelta) ->
    @pathCommand.push xDelta, ',', yDelta, ' '

    @lineCount += 1
    xDelta /= @sideLength
    yDelta /= @sideLength
    @lineLength += Math.sqrt xDelta * xDelta + yDelta * yDelta
  
  pathEnd: ->
    @pathCommand.push 'c'
    @raphael.path @pathCommand.join('')
    
  # 3D rendering code
    
  triangleStart: (xStart, yStart) ->
    @triX = xStart
    @triY = yStart
    
  triangleMove: (xDelta, yDelta) ->
    @triX += xDelta
    @triY += yDelta
    
  triangle: (edge1X, edge1Y, edge2X, edge2Y, lod) ->
    pathCommand = ['M', @triX, ',', @triY, 'l', edge1X, ',', edge1Y, 'l',
                   edge2X, ',', edge2Y, 'Z']
    @raphael.path(pathCommand.join('')).attr('fill', '#e0e0e0').
             attr('stroke', '#202020')

    @triangleCount += 1
    edge1X /= @sideLength
    edge1Y /= @sideLength
    @triangleArea += Math.sqrt(3) * (edge1X * edge1X + edge1Y * edge1Y) / 4
        
  statsClear: ->
    @lineCount = 0
    @lineLength = 0
    @triangleCount = 0
    @triangleArea = 0

window.onload = ->
  snowFlake = new Snowflake document.getElementById('canvas')
  lodInput = document.getElementById 'lod'
  render2DInput = document.getElementById 'render-2d'
  render3DInput = document.getElementById 'render-3d'
  lineCountSpan = document.getElementById 'line-count'
  lineLengthSpan = document.getElementById 'line-length'
  triangleCountSpan = document.getElementById 'triangle-count'
  triangleAreaSpan = document.getElementById 'triangle-area'
  
  redraw = ->
    snowFlake.redraw parseInt(lodInput.value), render3DInput.checked
    lineCountSpan.innerHTML = snowFlake.lineCount
    lineLengthSpan.innerHTML = snowFlake.lineLength
    triangleCountSpan.innerHTML = snowFlake.triangleCount
    triangleAreaSpan.innerHTML = snowFlake.triangleArea
  for input in [lodInput, render2DInput, render3DInput]
    for event in ['change', 'click', 'keyup']
      input.addEventListener event, redraw, false
  redraw()
