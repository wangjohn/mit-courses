# Model class for the circuit topology.
class Circuit
  # Initializes the circuit from data in the .jsonp file.
  constructor: (circuitJson) ->
    @gatesById = {}
    @gates = for jsonGate in circuitJson.gates
      gate =
        id: jsonGate.id, tableId: jsonGate.table, typeId: jsonGate.type,
        probed: jsonGate.probed
      @gatesById[gate.id] = gate
      gate
    
    @wires = []
    for jsonGate in circuitJson.gates
      gate = @gate jsonGate.id
      gate.outWires = for outGateId in jsonGate.outputs
        outGate = @gate outGateId
        wire = { from: gate, to: outGate }
        @wires.push wire
        wire
      
  # @return the gate whose ID is @gateId
  gate: (gateId) -> @gatesById[gateId]

# Model class for the simulator's event output.
class Trace
  # Initializes the trace from data in the .jsonp file.
  #
  # @param traceJson the trace information from the object in the .jsonp file
  # @param circuit the Circuit instance 
  constructor: (traceJson, @circuit) ->
    timeBag = {0: true}
    @events = for event in traceJson
      timeBag[event[0]] = true
      {time: event[0], gate: @circuit.gate(event[1]), value: event[2]}
    @endTime = @events[@events.length - 1].time
    @times = (parseInt time for time, _ of timeBag)
    @rewind()
    
  # Resets the trace to time 0.
  rewind: ->
    for gate in @circuit.gates
      gate.value = false
    @offset = 0
    while @events[@offset] and @events[@offset].time is 0
      @events[@offset].gate = @events[@offset].value
      @offset += 1
    @time = 0

  # Moves the trace forward one step in time.
  #
  # @return object whose properties are the IDs of the gates whose value changed
  stepForward: (changeBag = {})->
    # Don't move past the end of the trace.
    return changeBag if @events[@offset] is null
    @time = @events[@offset].time
    while @events[@offset] and @events[@offset].time is @time
      gate = @events[@offset].gate
      changeBag[gate.id] = true
      gate.value = @events[@offset].value
      @offset += 1
    changeBag

  # Moves the trace backward one step in time.
  #
  # @param changeBag initial value for the object recording changed gates;
  #                  passing something other than {} can be useful for merging
  #                  changes from multiple operations
  # @return object whose properties are the IDs of the gates whose value changed
  stepBack: (changeBag = {})->
    # Don't move past the beginning of the trace.
    return changeBag if @time is 0
    while @offset > 0 and @events[@offset - 1].time == @time
      @offset -= 1
      gate = @events[@offset].gate
      changeBag[gate.id] = true
      # The trace can be used as an undo log by flipping the gate output.
      gate.value = !@events[@offset].value
    @time = if @offset > 0 then @events[@offset - 1].time else 0
    changeBag
    
  # True if the time offset points to the beginning of the trace.
  atBeginning: -> @time == 0

  # True if the time offset points to the end of the trace.
  atEnd: -> @time == @endTime
  
  # Time of the event that's closest to the given time.
  nearestEventTime: (time) ->
    minDistance = Math.abs time
    minTime = 0
    for eventTime in @times
      distance = Math.abs time - eventTime
      if distance < minDistance
        minDistance = distance
        minTime = eventTime
    minTime
    
  # Moves the trace to the given time.
  #
  # @param changeBag initial value for the object recording changed gates;
  #                  passing something other than {} can be useful for merging
  #                  changes from multiple operations
  # @param time the 
  # @return object whose properties are the IDs of the gates whose value changed
  seek: (time, changeBag = {}) ->
    @stepForward changeBag while @time < time
    @stepBack changeBag while @time > time
    changeBag
  
    
# View class for the circuit layout and trace replay controls.
class LayoutView
  # Initializes the view from the SVG circuit layout in the .jsonp file.
  constructor: (svgContainer, svgLayoutString, @trace) ->
    @circuit = @trace.circuit
    # Will use the view property in some model objects to cache view data.
    gate.view = {} for gate in @circuit.gates
    wire.view = {} for wire in @circuit.wires
    
    # Load up the SVG data.
    svgContainer.innerHTML = svgLayoutString
    @svg = svgContainer.querySelector 'svg'
    @postGraphviz()
    @updateGate gate for gate in @circuit.gates
    
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
    
  # Post-processes the Graphviz-produced SVG so it looks good in the browser.
  postGraphviz: ->
    # Process the SVG so that it will scale to the browser window.
    @svg.removeAttribute 'width'
    @svg.removeAttribute 'height'
    
    # Remove the white background rectangle created by graphviz.
    background = @svg.querySelector 'polygon[fill="white"][stroke="white"]'
    background.parentNode.removeChild background

    # Replace hard stroke specs with a CSS-styleable class.
    for element in @svg.querySelectorAll 'symbol [stroke="#000"],[stroke="black"]'
      element.removeAttribute 'stroke'
      oldClass = element.getAttribute('class') || ''
      element.setAttribute 'class', 'gate-stroke ' + oldClass
    # Replace hard fill specs with a CSS-styleable class.
    for element in @svg.querySelectorAll 'symbol [fill="#FFF"],[fill="white"]'
      element.removeAttribute 'fill'
      oldClass = element.getAttribute('class') || ''
      element.setAttribute 'class', 'gate-fill ' + oldClass
    # Remove font family so the CSS can figure that out, and shrink fonts.
    for element in @svg.querySelectorAll 'text'
      element.removeAttribute 'font-family'
      if fontSizeString = element.getAttribute 'font-size'
        fontSize = Math.max 12, parseInt(fontSizeString) - 2
        element.setAttribute 'font-size', fontSize
      
  # The DOM element that represents a gate. 
  gateElement: (gate) ->
    gate.view.svg ||= @svg.getElementById('gate__' + gate.id)
    
  # The DOM element that represents a wire.
  wireElement: (wire) ->
    wire.view.svg ||= 
        @svg.getElementById('wire__' + wire.from.id + '__' + wire.to.id)
  
  # Updates the view to reflect a change in the gate's value.
  updateGate: (gate) ->
    svg = @gateElement gate
    klass = if gate.value then 'output-true' else 'output-false'
    klass += ' output-probed' if gate.probed
    svg.setAttribute 'class', klass
    @updateWire wire for wire in gate.outWires
    
  updateWire: (wire) ->
    svg = @wireElement wire
    klass = if wire.from.value then 'wire-true' else 'wire-false'
    svg.setAttribute 'class', klass
  
  # Updates the view to reflect a change in the trace's time offset.
  updateTrace: ->
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
  constructor: (svgContainer, simData) ->
    @circuit = new Circuit simData.circuit
    @trace = new Trace simData.trace, @circuit
    @view = new LayoutView svgContainer, simData.layout, @trace
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
    @view.updateGate @circuit.gate(gateId) for gateId, _ of changeBag
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
    
# Module-global that holds the simulation data until onload is called.
simData = null
# Called by circuit.jsonp to supply the simulation data.
window.onJsonp = (data) ->
  simData = data
  
# Sets up the simulation once everything is loaded.
window.onload = ->
  svgContainer = document.getElementById 'svg-container'
  window.visualizer = new Visualizer svgContainer, simData
  simData = null
  
  lodInput = document.querySelector '#lod'
