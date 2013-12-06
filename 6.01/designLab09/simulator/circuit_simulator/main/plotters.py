"""
Analysis plot display.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.simulation.circuit import Head_Connector
from circuit_simulator.simulation.circuit import Motor
from circuit_simulator.simulation.circuit import Signalled_Pot
from circuit_simulator.simulation.constants import NUM_SAMPLES
from circuit_simulator.simulation.constants import T
from constants import T_SAMPLES
from lib601.plotWindow import PlotWindow

class Plotter:
  """
  Abstract type that supports a |plot| method that, given the |data| for a
      particular circuit, plots something meaningful about the circuit.
  """
  def plot(self, data):
    """
    |data|: the data corresponding to the solved circuit.
    All subclasses should implement this.
    """
    raise NotImplementedError('subclasses should implement this')

class Motor_Plotter(Plotter):
  """
  Plots motor angle and speed.
  """
  def __init__(self, motor):
    assert isinstance(motor, Motor), 'motor must be a Motor'
    self._motor = motor
  def plot(self, data):
    # motor angle
    angle_plot = PlotWindow('Motor %s angle' % self._motor.label)
    angle_plot.stem(T_SAMPLES, self._motor.angle_samples[:-1])
    # motor speed
    speed_plot = PlotWindow('Motor %s speed' % self._motor.label)
    speed_plot.stem(T_SAMPLES, self._motor.speed_samples[:-1])

class Head_Plotter(Plotter):
  """
  Plots motor angle and speed, as well as lamp angle and distance.
  """
  def __init__(self, head_connector):
    assert isinstance(head_connector, Head_Connector), ('head_connector must '
        'be a Head_Connector')
    self._head_connector = head_connector
  def plot(self, data):
    # motor
    if self._head_connector.motor_present:
      self._head_connector.motor.label = self._head_connector.motor_label
      Motor_Plotter(self._head_connector.motor).plot(data)
    # lamp distance signal
    if self._head_connector.lamp_distance_signal:
      distance_plot = PlotWindow('Lamp %s distance' %
          self._head_connector.photo_label)
      distance_plot.stem(T_SAMPLES,
          self._head_connector.lamp_distance_signal.samples(0, T, NUM_SAMPLES))
    # lamp angle signal
    if self._head_connector.lamp_angle_signal:
      angle_plot = PlotWindow('Lamp %s angle' %
          self._head_connector.photo_label)
      angle_plot.stem(T_SAMPLES, self._head_connector.lamp_angle_signal.samples(
          0, T, NUM_SAMPLES))

class Signalled_Pot_Plotter(Plotter):
  def __init__(self, pot):
    assert isinstance(pot, Signalled_Pot), 'pot must be a Signalled_Pot'
    self._pot = pot
  def plot(self, data):
    alpha_plot = PlotWindow('Pot %s alpha' % self._pot.label)
    alpha_plot.stem(T_SAMPLES, self._pot.signal.samples(0, T, NUM_SAMPLES))

class Probe_Plotter(Plotter):
  """
  Plotter that shows the voltage difference accross probes.
  """
  def __init__(self, probe_plus, probe_minus):
    """
    |probe_plus|, |probe_minus|: probed nodes.
    """
    self._probe_plus = probe_plus
    self._probe_minus = probe_minus
  def plot(self, data):
    t_samples, probe_samples = [], []
    for t, solution in data.items():
      # ensure that the probes are in the solved circuits
      assert self._probe_plus in solution, ('+probe is disconnected from '
          'circuit')
      assert self._probe_minus in solution, ('-probe is disconnected from '
          'circuit')
      t_samples.append(t)
      probe_samples.append(
          solution[self._probe_plus] - solution[self._probe_minus])
    probe_plot = PlotWindow('Probe voltage difference')
    probe_plot.stem(t_samples, probe_samples)
