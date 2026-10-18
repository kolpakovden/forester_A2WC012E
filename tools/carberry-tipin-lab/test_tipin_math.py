"""Offline tests; they establish model consistency, not equivalence to HC16."""
import unittest
from carberry_tipin_math import (
 BASE_AXIS,BASE_VALUES,clamp_u8,current_from_working,delta_two_samples,
 delta_update,explicit_base_q8_8,compensated_pulse_raw,uniform_index_fraction
)
class TestTipInResearch(unittest.TestCase):
 def test_encoded_delta_neutral(self):
  self.assertEqual(delta_two_samples(100,100),128)
 def test_encoded_delta_positive_negative(self):
  self.assertEqual(delta_two_samples(120,100),148)
  self.assertEqual(delta_two_samples(100,120),108)
 def test_encoded_delta_saturation(self):
  self.assertEqual(delta_two_samples(255,0),255)
  self.assertEqual(delta_two_samples(0,255),0)
 def test_history_two_samples(self):
  self.assertEqual(delta_update(120,110,100),(148,120,110))
  self.assertEqual(delta_update(130,120,110),(148,130,120))
 def test_current_source(self):
  self.assertEqual(current_from_working(0x6400,0x1400,0),0x50)
  self.assertEqual(current_from_working(0x0100,0x0200,0),0)
  self.assertEqual(current_from_working(0xffff,0,1),0x0d)
 def test_base_nodes(self):
  for x,y in zip(BASE_AXIS,BASE_VALUES):
   self.assertEqual(explicit_base_q8_8(x),y<<8)
 def test_midpoint_and_pulse(self):
  self.assertEqual(explicit_base_q8_8(0x96),0x3080)
  self.assertEqual(compensated_pulse_raw(0x3080,32,32,32),388)
 def test_neutral_nodes(self):
  for y in BASE_VALUES:
   self.assertEqual(compensated_pulse_raw(y<<8,32,32,32),8*y)
 def test_uniform_boundaries(self):
  self.assertEqual(uniform_index_fraction(0x10,0x20,0x10,8,8),(0,0))
  self.assertEqual(uniform_index_fraction(0x18,0x20,0x10,8,8),(1,0))
  self.assertEqual(uniform_index_fraction(512,0x400,0,8,0),(8,0))
if __name__=="__main__":unittest.main()
