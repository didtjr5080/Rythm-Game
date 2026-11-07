"""Regression checks for finger counts, rotation, mirror and tracker coordinates."""
import math
import sys
from pathlib import Path
from types import SimpleNamespace as Point
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from app.input.mediapipe_tracker import MediaPipeHandTracker as Tracker


def hand(open_fingers):
    points=[Point(x=.5,y=.95,z=0)]
    thumb=[(.43,.7),(.32,.6),(.21,.5),(.1,.4)] if 'thumb' in open_fingers else [(.43,.7),(.36,.62),(.4,.57),(.48,.59)]
    points += [Point(x=x,y=y,z=0) for x,y in thumb]
    for name,x in zip(('index','middle','ring','pinky'),(.36,.49,.62,.75)):
        coords=[(x,.5),(x,.35),(x,.21),(x,.08)] if name in open_fingers else [(x,.5),(x,.35),(x+.035,.46),(x+.02,.56)]
        points += [Point(x=x,y=y,z=0) for x,y in coords]
    return points

names=('thumb','index','middle','ring','pinky')
for mask in range(32):
    opened={name for i,name in enumerate(names) if mask & (1<<i)}
    original=hand(opened)
    for angle in (0,35,90,180,270):
        theta=math.radians(angle)
        for mirrored in (False,True):
            points=[]
            for p in original:
                x,y=p.x-.5,p.y-.5
                x,y=x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta)
                if mirrored: x=-x
                points.append(Point(x=x*.7+.5,y=y*.7+.5,z=0))
            assert Tracker.count_lane_fingers(points,'Left')==len(opened),(opened,angle,mirrored)
            assert Tracker.count_lane_fingers(points,'Right')==len(opened)
assert Tracker.finger_count_to_lane(1)==0
assert Tracker.finger_count_to_lane(2)==1
assert Tracker.finger_count_to_lane(3)==2
assert Tracker.finger_count_to_lane(5) is None

# The alternate mirrored detection candidate must map its landmarks back to display space.
tracker=Tracker.__new__(Tracker)
tracker.available=True; tracker.hands=object(); tracker.flip=True
tracker.last_error=None; tracker.status='test'
points=hand(set(names))
# x and z must be divided by aspect because the tracker corrects image proportions.
raw=[Point(x=p.x/2,y=p.y,z=p.z/2) for p in points]
result=Point(multi_hand_landmarks=[Point(landmark=raw)],multi_handedness=[Point(classification=[Point(label='Left')])])
frame=np.zeros((240,480,3),dtype=np.uint8)
with patch.object(tracker,'_process_candidates',return_value=(result,frame,True)):
    detected=tracker.track(frame)
assert detected['finger_count']==5 and detected['hand_label']=='Right'
assert detected['landmarks'][8][0]==1-raw[8].x
assert detected['lane']==Tracker.x_to_lane(detected['x'])
with patch.object(tracker,'_process_candidates',return_value=(None,frame,False)):
    assert not tracker.track(frame)['hand_visible']
print('PASS: all 32 finger combinations at 5 rotations and both mirrors; handedness invariance; aspect correction; mirrored overlay; lane mapping; no-hand detection')

# Natural fingertip curvature must not remove the ring finger from a 3-finger gesture.
curved=hand({'index','middle','ring'})
curved[15]=Point(x=.645,y=.22,z=0)
curved[16]=Point(x=.72,y=.20,z=0)
assert Tracker.count_lane_fingers(curved)==3
# An abducted thumb with a naturally flexed MCP still counts.
curved_thumb=hand(set(names))
curved_thumb[3]=Point(x=.19,y=.62,z=0)
curved_thumb[4]=Point(x=.06,y=.64,z=0)
assert Tracker.count_lane_fingers(curved_thumb)==5
# A straight thumb crossing the palm is folded, even when its IP angle is 180.
across=hand({'index','middle','ring'})
across[2]=Point(x=.32,y=.6,z=0)
across[3]=Point(x=.47,y=.56,z=0)
across[4]=Point(x=.62,y=.52,z=0)
assert not Tracker.finger_states(across)['thumb']
# World geometry takes precedence over foreshortened image geometry.
tracker._reset_finger_history()
world=hand({'index','middle','ring'})
projected=hand(set())
result=Point(multi_hand_landmarks=[Point(landmark=projected)],
             multi_hand_world_landmarks=[Point(landmark=world)],multi_handedness=[])
with patch.object(tracker,'_process_candidates',return_value=(result,frame,False)):
    detected=tracker.track(frame)
assert detected['finger_count']==3 and detected['lane']==2
# A one-frame count dropout is ignored, but two consistent samples update it.
all_open=dict.fromkeys(names,True)
ring_drop=dict(all_open,ring=False)
tracker._reset_finger_history()
assert sum(tracker._stabilize_fingers(all_open).values())==5
assert sum(tracker._stabilize_fingers(ring_drop).values())==5
assert sum(tracker._stabilize_fingers(all_open).values())==5
assert sum(tracker._stabilize_fingers(ring_drop).values())==5
assert sum(tracker._stabilize_fingers(ring_drop).values())==4
tracker._reset_finger_history()
assert sum(tracker._stabilize_fingers(ring_drop).values())==4
# Do not switch to a smaller second hand solely because its count maps to LEFT.
tracker._reset_finger_history()
main=hand({'index','middle','ring','pinky'})
small=[Point(x=p.x*.3+.65,y=p.y*.3,z=0) for p in hand({'index'})]
result=Point(multi_hand_landmarks=[Point(landmark=small),Point(landmark=main)],
             multi_hand_world_landmarks=[Point(landmark=hand({'index'})),Point(landmark=main)],multi_handedness=[])
with patch.object(tracker,'_process_candidates',return_value=(result,frame,False)):
    detected=tracker.track(frame)
assert detected['finger_count']==4
print('PASS: curved ring => 3 fingers / RIGHT; bent thumb; folded thumb; world geometry; single-frame dropout; deliberate changes; multi-hand selection')
