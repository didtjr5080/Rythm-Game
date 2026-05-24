# Graph Report - .  (2026-05-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 606 nodes · 772 edges · 59 communities (53 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6693d241`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]

## God Nodes (most connected - your core abstractions)
1. `Game Widget` - 32 edges
2. `Start Screen` - 32 edges
3. `Main Window` - 22 edges
4. `tr()` - 14 edges
5. `Rhythm Game Engine` - 14 edges
6. `Mock EMG Reader` - 13 edges
7. `load_settings()` - 12 edges
8. `Input Fusion` - 12 edges
9. `Note Generator Adapter` - 11 edges
10. `generateNotes()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Settings Manager` --semantically_similar_to--> `EMG Motion Rhythm`  [INFERRED] [semantically similar]
  app/settings.py → README.md
- `generateNotes()` --calls--> `generate_notes_from_analysis()`  [EXTRACTED]
  legacy_web/frontend/src/api.js → app/audio/note_generator_adapter.py
- `generateNotes()` --calls--> `save_notes_json()`  [EXTRACTED]
  legacy_web/frontend/src/api.js → app/audio/note_generator_adapter.py
- `Note Generator Adapter` --references--> `Legacy Backend`  [EXTRACTED]
  app/audio/note_generator_adapter.py → legacy_web/backend/main.py
- `Rhythm Game Engine` --uses--> `Note`  [INFERRED]
  app/game/rhythm_game_engine.py → app/game/note.py

## Communities (59 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (13): tr(), Main Entry Point, main(), Settings Manager, load_settings(), save_settings(), settings_path(), Main Window (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (26): save_chart_csv(), save_chart_json(), _analysis_path(), _chart_csv_path(), _chart_json_path(), export_csv(), export_json(), generate_notes_for_file() (+18 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (11): Serial EMG Reader, Input Fusion, MediaPipe Hand Tracker, Mock EMG Reader, _extract_value(), GameInputState, count_lane_fingers(), _empty_result() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.13
Nodes (15): Beat Analyzer, Note Generator Adapter, Start Screen, chart_to_motion_notes(), find_saved_notes_for_song(), generate_notes_from_analysis(), notes_dir(), notes_path_for_song() (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (26): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+18 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (3): calculate_game_metrics(), Game Widget, _handled_keys()

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (8): Judge, Rhythm Game Engine, judge_note(), Note, from_json_file(), generate_sample_notes(), normalize_note_dict(), ScoreState

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (15): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (15): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (15): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+7 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (15): dependencies, react, react-dom, wavesurfer.js, devDependencies, vite, @vitejs/plugin-react, name (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (15): accuracy, activation_count, avg_emg, avg_input_delay_ms, combo, emg_drop_rate, good_count, hit_count (+7 more)

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (8): upload_audio(), AnalyzeRequest, AnalyzeResponse, ChartResponse, GenerateNotesRequest, Note, UploadResponse, BaseModel

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (10): bpm, difficulty, duration, file_id, lanes, notes, offset, play_mode (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.40
Nodes (8): _find_sustain_segments(), generate_beat_notes(), generate_notes(), _group_onsets_by_bar(), _lane_candidates(), _median_diff(), _normalize_strengths(), _percentile()

### Community 25 - "Community 25"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 30 - "Community 30"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 31 - "Community 31"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 33 - "Community 33"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (9): bpm, difficulty, duration, file_id, lanes, notes, offset, title (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (6): browserHash, chunks, configHash, hash, lockfileHash, optimized

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (7): BEAT_JUDGE_WINDOWS, GamePlayer(), IGNORED_BEAT_KEYS, JUDGE_WINDOWS, KEY_INPUTS, KEYMAPS, SCORE_VALUES

## Knowledge Gaps
- **335 isolated node(s):** `score`, `combo`, `max_combo`, `hit_count`, `miss_count` (+330 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Game Widget` connect `Community 5` to `Community 0`, `Community 2`, `Community 13`, `Community 6`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `Start Screen` connect `Community 3` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Main Window` connect `Community 0` to `Community 3`, `Community 5`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Game Widget` (e.g. with `session_logger.py` and `audio_player.py`) actually correct?**
  _`Game Widget` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Main Window` (e.g. with `calibration_screen.py` and `results_browser_screen.py`) actually correct?**
  _`Main Window` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Rhythm Game Engine` (e.g. with `Note` and `ScoreState`) actually correct?**
  _`Rhythm Game Engine` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `score`, `combo`, `max_combo` to the rest of the system?**
  _336 weakly-connected nodes found - possible documentation gaps or missing edges._