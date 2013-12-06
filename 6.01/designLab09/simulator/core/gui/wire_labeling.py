"""
Script to correctly lable the wires that interconnect a group of drawables.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from components import Wire_Connector_Drawable
from constants import DEBUG_DISPLAY_WIRE_LABELS

def _label_wires_from_connector(connector, relabeled_wires, label):
  """
  Recursively labels all wires connected to |connector| via any connectors, i.e.
      not necessairly wire connectors.
  """
  for wire in connector.wires():
    if wire not in relabeled_wires:
      wire.label = str(label)
      relabeled_wires.add(wire)
      _label_wires_from_connector(wire.other_connector(connector),
          relabeled_wires, label)

def _label_wires_from(drawable, relabeled_wires, label,
    same_label_per_connector):
  """
  Labels wires starting from the given |drawable|. Returns the maximum laebel
      that may have been used.
  """
  for connector in drawable.connectors:
    if same_label_per_connector:
      _label_wires_from_connector(connector, relabeled_wires, label)
      label += 1
    else:
      for wire in connector.wires():
        if wire not in relabeled_wires:
          wire.label = str(label)
          relabeled_wires.add(wire)
          next_drawable = wire.other_connector(connector).drawable
          if isinstance(next_drawable, Wire_Connector_Drawable):
            _label_wires_from(next_drawable, relabeled_wires, label,
                same_label_per_connector)
          if not isinstance(drawable, Wire_Connector_Drawable):
            label += 1
  return label

def label_wires(drawables, same_label_per_connector=True):
  """
  Labels the wires that interconnect the given |drawables| such that two wires
      have the same label if and only if they are connected via connectors. If
      |same_label_per_connector| is true, then a connection is valid only via
      wire connectors. Otherwise, a connection is valid via any connectors.
  """
  relabeled_wires = set()
  label = 0
  for drawable in drawables:
    if not isinstance(drawable, Wire_Connector_Drawable):
      label = _label_wires_from(drawable, relabeled_wires, label,
          same_label_per_connector) + 1
