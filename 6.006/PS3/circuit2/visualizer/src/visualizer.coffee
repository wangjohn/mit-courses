# Model class for the layer of wires.
class WireLayer
  # Initializes the layer from data in the .jsonp file.
  constructor: (layerJson) ->
    @wireById = {}
    @wires = for jsonWire in layerJson.wires
      wire =
        id: jsonWire.id, x: jsonWire.x, y: jsonWire.y,
        coords: [jsonWire.x, jsonWire.y],
        selected: false, indexed: false
      @wireById[wire.id] = wire
      wire
      
  # @return the wire whose ID is @wireId
  wire: (wireId) -> @wireById[wireId]

  # @return [minX, minY, maxX, maxY] for the wires
  boundingBox: ->
    minX = maxX = @wires[0].x[0]
    minY = maxY = @wires[0].y[0]
    for wire in @wires
      for endpoint in [0, 1]
        x = wire.x[endpoint]
        y = wire.y[endpoint]
        minX = x if minX > x
        maxX = x if maxX < x
        minY = y if minY > y
        maxY = y if maxY < y
    [minX, minY, maxX, maxY]

# Model class for the simulator's event output.
class Trace
  # Initializes the trace from data in the .jsonp file.
  #
  # @param traceJson the trace information from the object in the .jsonp file
  # @param circuit the Circuit instance 
  constructor: (traceJson, resultJson, @layer) ->
    @crossings = []
    
    sweepX = null
    @events = for jsonEvent in traceJson
      event = { type: jsonEvent.type, sweepX: sweepX }
      switch event.type
        when 'add', 'delete'
          event.type = 'index'
          event.wire = @layer.wire jsonEvent.id
          event.indexed = jsonEvent.type is 'add'
        when 'count'
          event.query = [jsonEvent.from, jsonEvent.to]
          event.result = jsonEvent.result
        when 'list'
          event.query = [jsonEvent.from, jsonEvent.to]
          event.wires = (@layer.wire wireId for wireId in jsonEvent.ids)
        when 'crossing'
          event.crossing = {view: {}, added: false }
          @crossings.push event.crossing
          event.crossing.wire1 = @layer.wire jsonEvent.id1
          event.crossing.wire2 = @layer.wire jsonEvent.id2
          event.crossing.id = 'crossing@' + @crossings.length
          for wire in [event.crossing.wire1, event.crossing.wire2]
            event.crossing.x = wire.x[0] if wire.x[0] == wire.x[1]
            event.crossing.y = wire.y[0] if wire.y[0] == wire.y[1]
        when 'sweep'
          sweepX = event.sweepX = jsonEvent.x
      event
    @time = 0
    @sweepX = null
    @endTime = @events.length
    @selected = []
    
  # Resets the trace to time 0.
  rewind: ->
    for wire in @layer.wires
      wire.indexed = false
    @time = 0

  # Moves the trace timeline cursor forward by one step.
  #
  # @param changeBag initial value for the object recording changed wires;
  #                  passing something other than {} can be useful for merging
  #                  changes from multiple operations
  # @return object whose properties are the IDs of the wires whose state changed
  stepForward: (changeBag = {})->
    # Don't move past the end of the trace.
    return if @events[@time] is null

    for wire in @selected
      wire.selected = false
      changeBag[wire.id] = wire
    @selected = []

    event = @events[@time]
    @sweepX = event.sweepX
    switch event.type
      when 'index'
        wire = event.wire
        wire.indexed = event.indexed
        changeBag[wire.id] = wire
      when 'crossing'
        crossing = event.crossing
        crossing.added = true
        changeBag[crossing.id] = event.crossing
      when 'list'
        @selected = event.wires
        for wire in @selected
          wire.selected = true
          changeBag[wire.id] = wire
      when 'count'
        throw 'not implemented'
    
    @time += 1
    changeBag

  # Moves the trace timeline cursor back by one step.
  #
  # @param changeBag initial value for the object recording changed wires;
  #                  passing something other than {} can be useful for merging
  #                  changes from multiple operations
  # @return object whose properties are the IDs of the wires whose state changed
  stepBack: (changeBag = {})->
    # Don't move past the beginning of the trace.
    return changeBag if @time is 0

    @time -= 1
    event = @events[@time]
    switch event.type
      when 'index'
        wire = event.wire
        wire.indexed = !event.indexed
        changeBag[wire.id] = wire
      when 'crossing'
        crossing = event.crossing
        crossing.added = false
        changeBag[crossing.id] = crossing
      when 'list'
        for wire in @selected
          wire.selected = false
          changeBag[wire.id] = wire
        @selected = []
      when 'count'
        throw 'not implemented'

    lastEvent = @events[@time - 1] 
    @sweepX = lastEvent.sweepX
    if lastEvent
      @sweepX = event.sweepX
      switch lastEvent.type
        when 'list'
          @selected = lastEvent.wires
          for wire in @selected
            wire.selected = true
            changeBag[wire.id] = wire
        when 'count'
          throw 'not implemented'
    else
      @sweepX = null
      
    changeBag
    
  # True if the time offset points to the beginning of the trace.
  atBeginning: -> @time == 0

  # True if the time offset points to the end of the trace.
  atEnd: -> @time == @endTime
  
  # Time of the event that's closest to the given time.
  nearestEventTime: (time) ->
    time = Math.round time
    time = 0 if time < 0
    time = @endTime if time > @endTime
    time
    
  # Seeks into the trace timeline.
  #
  # @param changeBag initial value for the object recording changed wires;
  #                  passing something other than {} can be useful for merging
  #                  changes from multiple operations
  # @param time the time to move the trace timeline cursor to 
  # @return object whose properties are the IDs of the wires whose value changed
  seek: (time, changeBag = {}) ->
    @stepForward changeBag while @time < time
    @stepBack changeBag while @time > time
    changeBag
  
  # The [minY, maxY] range of the current selection, or null for no selection. 
  selectionRange: ->
    return null if @time is 0
    lastEvent = @events[@time - 1]
    switch lastEvent.type
      when 'list', 'count'
        lastEvent.query
      else
        null
    
# View class for the circuit layout and trace replay controls.
class LayoutView
  # Initializes the view from the SVG circuit layout in the .jsonp file.
  constructor: (svgContainer, @trace) ->
    @layer = @trace.layer
    # Will use the view property in some model objects to cache view data.
    wire.view = {} for wire in @layer.wires
    
    @buildWireSvg svgContainer
    @updateWire wire for wire in @layer.wires
    @updateCrossing crossing for crossing in @trace.crossings
    @selectionBox = null
    @sweepLine = null
    
    # Set up the timeline.
    @timeLabel = document.getElementById 'time-label'
    @startTimeLabel = document.getElementById 'start-time-label'
    @endTimeLabel = document.getElementById 'end-time-label'
    @timeline = document.getElementById 'timeline'
    @backButton = document.getElementById 'back'
    @forwardButton = document.getElementById 'forward'
    @seekStartButton = document.getElementById 'seek-start'
    @seekEndButton = document.getElementById 'seek-end'
    @playButton = document.getElementById 'play'
    @updateTrace()
    
  # Constructs the static SVG representing the wire layer.
  buildWireSvg: (svgContainer) -> 
    @padding = 5
    wireBB = @layer.boundingBox()
    @svg = new Pwnvg svgContainer, wireBB[0] - @padding, wireBB[1] - @padding,
                     wireBB[2] + @padding, wireBB[3] + @padding
    for crossing in @trace.crossings
      crossing.view.svg = @svg.circle(crossing.x, crossing.y, 2).
                               addClass('crossing')
    for wire in @layer.wires
      pathSpec = Pwnvg.path().moveTo(wire.x[0], wire.y[0]).
                              lineTo(wire.x[1], wire.y[1])
      wire.view.svg = @svg.path(pathSpec).addClass('wire').id("wire-" + wire.id)
        
  # Updates the view to reflect a change in a wire's value.
  updateWire: (wire) ->
    svg = @wireElement wire
    if wire.selected
      svg.addClass('selected').removeClass('not-selected')
    else
      svg.removeClass('selected').addClass('not-selected')
    if wire.indexed
      svg.addClass('indexed').removeClass('not-indexed')
    else
      svg.addClass('not-indexed').removeClass('indexed')

  # Updates the view to reflect a change in a wire's value.
  updateCrossing: (crossing) ->
    svg = @crossingElement crossing
    if crossing.added
      svg.addClass('added').removeClass('not-added')
    else
      svg.removeClass('added').addClass('not-added')
  
  # The DOM element that represents a wire.
  wireElement: (wire) -> wire.view.svg

  # The DOM element that represents a crossing.
  crossingElement: (crossing) -> crossing.view.svg
  
  # Updates the view to reflect a change in the trace's timeline cursor.
  updateTrace: ->
    if @selectionBox
      @selectionBox.remove()
      @selectionBox = null
    if range = @trace.selectionRange()
      @selectionBox = @svg.rect(@svg.minX, range[0], @svg.maxX, range[1]).
                           addClass('selection').moveToBottom()
    if @sweepLine
      @sweepLine.remove()
      @sweepLine = null
    unless @trace.sweepX is null
      pathSpec = Pwnvg.path().moveTo(@trace.sweepX, @svg.minY).
                              lineTo(@trace.sweepX, @svg.maxY)
      @sweepLine = @svg.path(pathSpec).addClass('sweep-line').moveToBottom()
    
    @timeLabel.innerHTML = @trace.time
    @startTimeLabel.innerHTML = 0
    @timeline.setAttribute 'min', 0
    @endTimeLabel.innerHTML = @trace.endTime
    @timeline.setAttribute 'max', @trace.endTime
    @timeline.value = @trace.time
    @seekStartButton.disabled = @backButton.disabled = @trace.atBeginning()
    @seekEndButton.disabled = @forwardButton.disabled = @trace.atEnd()
  
  # Updates the view to reflect whether the simulatin is animated or not.
  updateAnimationState: (state) ->
    @playButton.innerHTML = if state then 'Pause' else 'Play'
  
# Controller for the visualization.
class Visualizer
  constructor: (svgContainer, traceData) ->
    @layer = new WireLayer traceData.layer
    @trace = new Trace traceData.trace, traceData.result, @layer
    @view = new LayoutView svgContainer, @trace
    @frameTimeout = null
    
    document.getElementById('forward').
             addEventListener 'click', => @onForwardClick()
    document.getElementById('back').
             addEventListener 'click', => @onBackClick()
    document.getElementById('seek-start').
             addEventListener 'click', => @onSeekStartClick()
    document.getElementById('seek-end').
             addEventListener 'click', => @onSeekEndClick()
    document.getElementById('play').
             addEventListener 'click', => @onPlayClick()
    @timeline = document.getElementById 'timeline'
    @timeline.addEventListener 'change', => @onTimelineChange()

  # The user pressed the forward (>) button.
  onForwardClick: ->
    @updateView @trace.stepForward()
    
  # The user pressed the back (<) button.
  onBackClick: ->
    @updateView @trace.stepBack()
    
  # The user pressed the seek to the end (>>) button.
  onSeekEndClick: ->
    @updateView @trace.seek(@trace.endTime)
    
  # The user pressed the seek to the beginning (<<) button.
  onSeekStartClick: ->
    @updateView @trace.seek(0)
    
  # The user pressed the play / pause (<<) button.
  onPlayClick: ->
    if @frameTimeout
      @cancelAnimationFrame()
    else
      @scheduleAnimationFrame()
    @view.updateAnimationState !!@frameTimeout

  # The user or UI performed a seek on the timeline.
  onTimelineChange: ->
    # Prevent infinite recursion if the system initiated the seek.
    value = parseFloat @timeline.value
    return if @trace.time is value 
    newTime = @trace.nearestEventTime value
    @updateView @trace.seek newTime    
  
  # Updates the UI to reflect the changes performed by a trace operation.
  updateView: (changeBag) ->
    for _, model of changeBag
      if model.wire1
        @view.updateCrossing model
      else
        @view.updateWire model
    @view.updateTrace()

  # Schedules an doAnimationFrame() call.
  scheduleAnimationFrame: ->
    unless @frameTimeout
      @frameTimeout = window.setTimeout (=> @doAnimationFrame()), 1000
    
  # De-schedules a call scheduled with scheduleAnimationFrame().
  cancelAnimationFrame: ->
    window.clearTimeout @frameTimeout if @frameTimeout
    @frameTimeout = false
    
  # Advances the simulation trace by one frame.
  doAnimationFrame: ->
    @frameTimeout = null
    @onForwardClick()
    if @trace.atEnd()
      @view.updateAnimationState false
    else
      @scheduleAnimationFrame()
    
# Module-global that holds the trace data until onload is called.
traceData = null
# Called by circuit.jsonp to supply the simulation data.
window.onJsonp = (data) ->
  traceData = data
  
# Sets up the simulation once everything is loaded.
window.onload = ->
  svgContainer = document.getElementById 'svg-container'
  window.visualizer = new Visualizer svgContainer, traceData
  traceData = null
  
  lodInput = document.querySelector '#lod'
