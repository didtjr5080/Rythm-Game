"""Synthetic 3D palm tests; these do not claim physical-camera accuracy."""
import math
import unittest
from app.input.hand_gestures import WristTilt, FoldGestures


def palm(angle):
    points=[(0.,0.,0.) for _ in range(21)]
    for index,x in zip((5,9,13,17),(-.03,-.01,.01,.03)):
        points[index]=(x,-.1,.1*math.tan(math.radians(angle)))
    return points


class WristChecks(unittest.TestCase):
    def ready(self,angle=0):
        wrist=WristTilt()
        for now in (0,.15,.3,.45):
            self.assertEqual(wrist.feed(palm(angle),2,now),0)
        self.assertIsNotNone(wrist.reference)
        return wrist

    def test_two_fingers_extension_up_flexion_down_and_neutral_stop(self):
        wrist=self.ready()
        self.assertEqual(wrist.feed(palm(25),2,.6),-1)
        self.assertEqual(wrist.feed(palm(12),2,.7),-1)
        self.assertEqual(wrist.feed(palm(5),2,.8),0)
        self.assertEqual(wrist.feed(palm(-25),2,.9),1)
        self.assertEqual(wrist.feed(palm(0),2,1.),0)

    def test_other_finger_counts_cannot_scroll(self):
        wrist=self.ready()
        for count in (0,1,3,4,5,None):
            self.assertEqual(wrist.feed(palm(35),count,1.),0)

    def test_neutral_reference_is_relative(self):
        wrist=self.ready(15)
        self.assertEqual(wrist.feed(palm(35),2,.7),-1)
        self.assertEqual(wrist.feed(palm(-5),2,.8),1)

    def test_translation_and_scale_do_not_change_palm_tilt(self):
        wrist=self.ready()
        moved=[(2*x+5,2*y-3,2*z+9) for x,y,z in palm(25)]
        self.assertEqual(wrist.feed(moved,2,.7),-1)

    def test_missing_or_invalid_depth_cannot_scroll(self):
        for points in (None, [(0,0)]*21, [(float('nan'),0,0)]*21, [(0,0,0)]*21):
            wrist=self.ready()
            self.assertEqual(wrist.feed(points,2,.7),0)
            self.assertIsNone(wrist.reference)

    def test_unstable_initial_pose_does_not_set_reference(self):
        wrist=WristTilt()
        for now,angle in ((0,0),(.15,25),(.3,0),(.45,25)):
            wrist.feed(palm(angle),2,now)
        self.assertIsNone(wrist.reference)

    def test_direction_change_stops_before_debounced_reverse(self):
        gesture=FoldGestures()
        gesture.feed(2,False,0,None,-1)
        gesture.feed(2,False,.12,None,-1)
        self.assertTrue(gesture.scrolling)
        gesture.feed(2,False,.2,None,1)
        self.assertFalse(gesture.scrolling)
        gesture.feed(2,False,.32,None,1)
        self.assertTrue(gesture.scrolling)
        self.assertEqual(gesture.scroll_direction,1)


if __name__=='__main__':unittest.main()
