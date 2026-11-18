"""Local named pinch profiles; no raw hand measurements are persisted."""
import json
import math
from statistics import median

from app.atomic_io import atomic_text
from app.input.pinch_classifier import NAMES
from app.settings import settings_path

LABELS = ('NONE',) + NAMES


def profile_path():
    return settings_path().with_name('leap_calibration.json')


def validate_thresholds(values):
    if not isinstance(values, dict) or set(values) != set(NAMES):
        raise ValueError('All four finger thresholds are required.')
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not .12 <= v <= .70 or not math.isfinite(v) for v in values.values()):
        raise ValueError('Invalid Leap calibration threshold.')
    return dict(values)


def load_profiles(path=None):
    path = path or profile_path()
    if not path.exists():
        return {'active': None, 'profiles': {}}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('profiles'), dict):
        raise ValueError('Invalid Leap profile file.')
    for name, values in data['profiles'].items():
        if not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError('Invalid profile name.')
        validate_thresholds(values)
    active = data.get('active')
    if active is not None and (not isinstance(active, str) or active not in data['profiles']):
        raise ValueError('Active Leap profile does not exist.')
    return data


def save_profile(name, thresholds, path=None):
    name = name.strip()
    if not name or len(name) > 80:
        raise ValueError('Enter a profile name (1-80 characters).')
    values = validate_thresholds(thresholds)
    data = load_profiles(path)
    data['profiles'][name] = values
    data['active'] = name
    atomic_text(path or profile_path(), json.dumps(data, ensure_ascii=False, indent=2))


def activate_profile(name, path=None):
    data = load_profiles(path)
    if name is not None and name not in data['profiles']:
        raise ValueError('Select a saved profile first.')
    data['active'] = name
    atomic_text(path or profile_path(), json.dumps(data, ensure_ascii=False, indent=2))


def calculate_thresholds(samples):
    for label in LABELS:
        rows = samples.get(label, [])
        if len(rows) < 25:
            raise ValueError(f'{label}: at least 25 fresh frames are required. Please measure again.')
        if any(len(row) != 4 or any(not math.isfinite(v) or v < 0 for v in row) for row in rows):
            raise ValueError(f'{label}: invalid hand measurements.')
    values = {}
    for i, name in enumerate(NAMES):
        rest = median(row[i] for row in samples['NONE'])
        pinch = median(row[i] for row in samples[name])
        if rest - pinch < .08:
            raise ValueError(f'{name}: open hand and pinch are too similar. Please measure again.')
        values[name] = round(min(.70, max(.12, pinch + .40 * (rest - pinch))), 4)
    return values
