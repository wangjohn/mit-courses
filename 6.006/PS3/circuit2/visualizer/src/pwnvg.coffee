# Wraps a SVG element.
class Pwnvg
  # Creates a SVG element inside a container.
  #
  # @param svgContainer a DOM element that will receive the new SVG element
  # @param minX left of the SVG coordinate system
  # @param maxX right of the SVG coordinate system
  # @param minY top of the SVG coordinate system
  # @param maxY bottom of the SVG coordinate system
  constructor: (@svgContainer, @minX, @minY, @maxX, @maxY) ->
    @svg = document.createElementNS 'http://www.w3.org/2000/svg', 'svg'
    @svg.setAttribute 'version', '1.1'
    @svg.setAttribute 'viewBox',
                      "#{@minX} #{@minY} #{@maxX - @minX} #{@maxY - @minY}"
    svgContainer.appendChild @svg

  # Creates a path inside the SVG element.
  path: (pathData) ->
    dom = document.createElementNS 'http://www.w3.org/2000/svg', 'path'
    dom.setAttribute 'd', pathData.toString()
    @svg.appendChild dom
    new PwnvgElement dom

  # Creates a rectangle inside the SVG element.
  rect: (x1, y1, x2, y2) ->
    [x2, x1] = [x1, x2] if x1 > x2
    [y2, y1] = [y1, y2] if y1 > y2
    dom = document.createElementNS 'http://www.w3.org/2000/svg', 'rect'
    dom.setAttribute 'x', x1
    dom.setAttribute 'y', y1
    dom.setAttribute 'width', x2 - x1
    dom.setAttribute 'height', y2 - y1
    @svg.appendChild dom
    new PwnvgElement dom

  # Creates a circle inside the SVG element.
  circle: (x, y, r) ->
    dom = document.createElementNS 'http://www.w3.org/2000/svg', 'circle'
    dom.setAttribute 'cx', x
    dom.setAttribute 'cy', y
    dom.setAttribute 'r', r
    @svg.appendChild dom
    new PwnvgElement dom

  # Helper for building a path data string.
  #
  # @return a new PwnvgPathBuilder instance
  @path: ->
    new PwnvgPathBuilder

# Wraps a SVG element like a path.
class PwnvgElement
  # Creates a wrapper around a SVG DOM element.
  constructor: (@dom) ->

  # True if the element's class list includes the given argument.
  hasClass: (klass) ->
    (new RegExp('(^|\\s)' + klass + '(\\s|$)')).
        test(@dom.getAttribute('class') || '')

  # Adds a class to the element's class list.
  #
  # @return the element to facilitate method chaining
  addClass: (klass) ->
    unless @hasClass klass
      @dom.setAttribute 'class',
                        [@dom.getAttribute('class'), ' ', klass].join('').trim()
    @
    
  # Removes a class from the element's class list.
  #
  # @return the element to facilitate method chaining
  removeClass: (klass) ->
    list = @dom.getAttribute 'class'
    @dom.setAttribute 'class',
        list.replace(new RegExp('(^|\\s)' + klass + '(\\s|$)'), ' ').trim()
    @

  # Sets the element's id.
  #
  # @return the element to facilitate method chaining
  id: (newId) ->
    @dom.id = newId
    @
    
  # Removes the element from the SVG.
  #
  # @return the element to facilitate method chaining
  remove: ->
    @dom.parentNode.removeChild @dom
    @
    
  # Moves the element above all the other elements in its container.
  moveToTop: ->
    parent = @dom.parentNode
    parent.removeChild @dom
    parent.appendChild @dom
    @
    
  # Moves the element below all the other elements in its container.
  moveToBottom: ->
    parent = @dom.parentNode
    parent.removeChild @dom
    parent.insertBefore @dom, parent.firstChild
    @
    

# Builder for path data strings.
class PwnvgPathBuilder
  # Creates an empty path.
  constructor: ->
    @command = []
    
  # Adds an absolute-move command to the path.
  #
  # @param x the X coordinate to move the pen to
  # @param y the Y coordinate to move the pen to
  # @return the path builder to facilitate method chaining
  moveTo: (x, y) ->
    @command.push 'M'
    @command.push x
    @command.push ','
    @command.push y
    @

  # Adds a relative-move command to the path.
  #
  # @param x how much to move the pen along the X axis
  # @param x how much to move the pen along the Y axis
  # @return the path builder to facilitate method chaining
  moveBy: (dx, dy) ->
    @command.push 'm'
    @command.push dx
    @command.push ','
    @command.push dy
    @

  # Adds an absolute-move-and-draw-line command to the path.
  #
  # @param x the X coordinate to move the pen to
  # @param y the Y coordinate to move the pen to
  # @return the path builder to facilitate method chaining
  lineTo: (x, y) ->
    @command.push 'L'
    @command.push x
    @command.push ','
    @command.push y
    @

  # Adds a relative-move-and-draw-line command to the path.
  #
  # @param x how much to move the pen along the X axis
  # @param x how much to move the pen along the Y axis
  # @return the path builder to facilitate method chaining
  lineBy: (dx, dy) ->
    @command.push 'l'
    @command.push dx
    @command.push ','
    @command.push dy
    @
    
  # Closes the path.
  #
  # @return the path builder to facilitate method chaining
  close: ->
    @command.push 'Z'
    @

  # The path data string constructed by this builder.
  toString: ->
    @command.join ''

# Export the Pwnvg class.
window.Pwnvg = Pwnvg
