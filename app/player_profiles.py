"""Named local players with isolated calibration and basic-mode completions."""
import copy
import json
import math
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL
from app.atomic_io import atomic_text
from app.settings import settings_path
from app.input.leap_calibration import validate_thresholds, load_profiles


class ProfileStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else settings_path().with_name('player_profiles.json')
        self._allow_legacy = path is None

    def load(self):
        if not self.path.exists():
            data = {'version': 1, 'active': None, 'profiles': {}}
            if self._allow_legacy:
                legacy = load_profiles()
                for name, thresholds in legacy['profiles'].items():
                    key = uuid5(NAMESPACE_URL, 'emg-motion-rhythm/player/' + name).hex
                    data['profiles'][key] = {'name': name, 'pinch': thresholds, 'emg': None,
                                              'completed': {'pinch': False, 'emg': False}}
                    if name == legacy['active']: data['active'] = key
            return data
        data = json.loads(self.path.read_text(encoding='utf-8'))
        if (not isinstance(data, dict) or data.get('version') != 1
                or not isinstance(data.get('profiles'), dict)):
            raise ValueError('Invalid player profile file.')
        for key, person in data['profiles'].items():
            if not isinstance(key, str) or not isinstance(person, dict):
                raise ValueError('Invalid player profile.')
            self._name(person.get('name'))
            if person.get('pinch') is not None:
                validate_thresholds(person['pinch'])
            if person.get('emg') is not None:
                emg = person['emg']
                if not isinstance(emg, dict) or emg.get('duration_seconds') != 3.:
                    raise ValueError('Invalid EMG calibration.')
                self._value(emg.get('minimum'))
                samples = emg.get('samples')
                if not isinstance(samples, list) or not samples:
                    raise ValueError('Missing EMG calibration samples.')
                for sample in samples: self._value(sample)
                if min(samples) != emg['minimum']:
                    raise ValueError('EMG calibration minimum does not match samples.')
            completed = person.get('completed')
            if (not isinstance(completed, dict) or set(completed) != {'pinch', 'emg'}
                    or any(type(v) is not bool for v in completed.values())):
                raise ValueError('Invalid completion history.')
            if any(completed[m] and person.get(m) is None for m in completed):
                raise ValueError('Completed mode has no calibration.')
        if data.get('active') is not None and (not isinstance(data['active'], str) or data['active'] not in data['profiles']):
            raise ValueError('Active player profile does not exist.')
        return data

    @staticmethod
    def _name(name):
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
            raise ValueError('이름을 1~80자로 입력하세요.')
        return name.strip()

    @staticmethod
    def _value(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 4095:
            raise ValueError('Invalid EMG minimum or sample.')
        return float(value)

    def _write(self, data):
        atomic_text(self.path, json.dumps(data, ensure_ascii=False, indent=2))

    def get(self, profile_id):
        return copy.deepcopy(self.load()['profiles'].get(profile_id))

    def active(self):
        data = self.load()
        key = data['active']
        return (key, copy.deepcopy(data['profiles'][key])) if key is not None else (None, None)

    def create(self, name):
        name = self._name(name)
        data = self.load()
        if any(p['name'].casefold() == name.casefold() for p in data['profiles'].values()):
            raise ValueError('같은 이름의 프로필이 있습니다. 기존 프로필을 선택하세요.')
        key = uuid4().hex
        data['profiles'][key] = {'name': name, 'pinch': None, 'emg': None,
                                  'completed': {'pinch': False, 'emg': False}}
        data['active'] = key
        self._write(data)
        return key

    def select(self, profile_id):
        data = self.load()
        if profile_id is not None and profile_id not in data['profiles']:
            raise ValueError('선택한 프로필이 없습니다.')
        data['active'] = profile_id
        self._write(data)

    def delete(self, profile_id):
        data = self.load()
        if profile_id not in data['profiles']:
            raise ValueError('삭제할 프로필이 없습니다.')
        del data['profiles'][profile_id]
        if data['active'] == profile_id: data['active'] = None
        self._write(data)

    def _person(self, data, profile_id):
        if profile_id not in data['profiles']:
            raise ValueError('프로필이 삭제되었거나 존재하지 않습니다.')
        return data['profiles'][profile_id]

    def save_pinch(self, profile_id, thresholds):
        values = validate_thresholds(thresholds)
        data = self.load(); person = self._person(data, profile_id)
        person['pinch'] = values
        person['completed']['pinch'] = False
        self._write(data)

    def save_emg(self, profile_id, minimum, samples):
        minimum = self._value(minimum)
        values = [self._value(v) for v in samples]
        if not values or min(values) != minimum:
            raise ValueError('측정 최저값과 기록값이 일치하지 않습니다.')
        data = self.load(); person = self._person(data, profile_id)
        person['emg'] = {'minimum': minimum, 'samples': values, 'duration_seconds': 3.}
        person['completed']['emg'] = False
        self._write(data)

    def clear_calibration(self, profile_id, mode):
        if mode not in ('pinch', 'emg'): raise ValueError('Unknown basic mode.')
        data = self.load(); person = self._person(data, profile_id)
        person[mode] = None
        person['completed'][mode] = False
        self._write(data)

    def record_completion(self, profile_id, mode):
        if mode not in ('pinch', 'emg'): return
        data = self.load(); person = self._person(data, profile_id)
        if person[mode] is None:
            raise ValueError('보정값이 없는 프로필은 완료를 기록할 수 없습니다.')
        person['completed'][mode] = True
        self._write(data)

    def unlocked(self, profile_id):
        person = self.get(profile_id)
        return bool(person and person['pinch'] is not None and person['emg'] is not None
                    and all(person['completed'].values()))
