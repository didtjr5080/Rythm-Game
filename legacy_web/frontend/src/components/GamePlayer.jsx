import { useEffect, useMemo, useRef, useState } from "react";

const JUDGE_WINDOWS = {
  perfect: 0.05,
  great: 0.1,
  good: 0.15,
  miss: 0.18
};

const SCORE_VALUES = {
  perfect: 1000,
  great: 700,
  good: 400,
  miss: 0
};

const KEYMAPS = {
  4: ["D", "F", "J", "K"],
  5: ["D", "F", "SPACE", "J", "K"],
  6: ["S", "D", "F", "J", "K", "L"],
  8: ["A", "S", "D", "F", "J", "K", "L", ";"]
};

const KEY_INPUTS = {
  4: ["d", "f", "j", "k"],
  5: ["d", "f", " ", "j", "k"],
  6: ["s", "d", "f", "j", "k", "l"],
  8: ["a", "s", "d", "f", "j", "k", "l", ";"]
};

const PIXELS_PER_SECOND = 420;
const NOTE_HEIGHT = 18;
const HIT_FLASH_DURATION = 0.12;
const HIT_RING_DURATION = 0.2;
const MAX_INPUT_WINDOW = 0.25;
const HOLD_END_BONUS = 200;
const SLIDE_TICK_INTERVAL = 0.25;
const SLIDE_TICK_SCORE = 60;
const SLIDE_END_BONUS = 80;
const BEAT_PREVIEW_SECONDS = 4.8;
const BEAT_JUDGE_WINDOWS = {
  perfect: 0.07,
  great: 0.13,
  good: 0.21,
  miss: 0.26
};
const IGNORED_BEAT_KEYS = new Set([
  "alt",
  "altgraph",
  "capslock",
  "control",
  "fn",
  "meta",
  "shift",
  "tab"
]);

function GamePlayer({ fileId, audioUrl, chart, onBack, onFinish }) {
  const canvasRef = useRef(null);
  const audioRef = useRef(null);
  const animationFrameRef = useRef(null);
  const notesRef = useRef(chart?.notes || []);
  const processedRef = useRef(new Set());
  const laneFlashRef = useRef([]);
  const hitRingRef = useRef([]);
  const holdingRef = useRef([]);
  const pressedRef = useRef([]);
  const scoreRef = useRef(0);
  const comboRef = useRef(0);
  const maxComboRef = useRef(0);
  const judgementRef = useRef({ perfect: 0, great: 0, good: 0, miss: 0 });
  const missTimerRef = useRef(null);
  const eventTimerRef = useRef(null);
  const comboTimerRef = useRef(null);
  const judgementTimerRef = useRef(null);

  const [isReady, setIsReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [maxCombo, setMaxCombo] = useState(0);
  const [accuracy, setAccuracy] = useState(0);
  const [lastJudgementText, setLastJudgementText] = useState("");
  const [lastJudgementType, setLastJudgementType] = useState("none");
  const [eventPulse, setEventPulse] = useState(null);
  const [exTapPulse, setExTapPulse] = useState(null);
  const [comboPulse, setComboPulse] = useState(null);
  const [missFlash, setMissFlash] = useState(false);
  const [volume, setVolume] = useState(0.85);
  const [judgementCounts, setJudgementCounts] = useState({
    perfect: 0,
    great: 0,
    good: 0,
    miss: 0
  });

  const lanes = chart?.lanes || 4;
  const duration = chart?.duration || 0;
  const playMode = chart?.play_mode || "lanes";
  const isBeatMode = playMode === "beat";
  const isHoldingIndex = (index) => {
    return holdingRef.current.some((holding) => holding && holding.index === index);
  };

  const keyLabels = useMemo(() => (isBeatMode ? ["SPACE", "ENTER"] : KEYMAPS[lanes] || KEYMAPS[4]), [isBeatMode, lanes]);
  const keyInputs = useMemo(() => KEY_INPUTS[lanes] || KEY_INPUTS[4], [lanes]);

  useEffect(() => {
    notesRef.current = chart?.notes || [];
    processedRef.current = new Set();
    laneFlashRef.current = new Array(lanes).fill(-1);
    hitRingRef.current = [];
    holdingRef.current = new Array(lanes).fill(null);
    pressedRef.current = new Array(lanes).fill(false);
    scoreRef.current = 0;
    comboRef.current = 0;
    maxComboRef.current = 0;
    judgementRef.current = { perfect: 0, great: 0, good: 0, miss: 0 };
    setScore(0);
    setCombo(0);
    setMaxCombo(0);
    setAccuracy(0);
    setJudgementCounts({ perfect: 0, great: 0, good: 0, miss: 0 });
    setLastJudgementText("");
    setLastJudgementType("none");
    setEventPulse(null);
    setExTapPulse(null);
    setComboPulse(null);
    setMissFlash(false);
    setIsPlaying(false);
    setIsFinished(false);
  }, [chart]);

  useEffect(() => {
    return () => {
      if (missTimerRef.current) {
        clearTimeout(missTimerRef.current);
      }
      if (eventTimerRef.current) {
        clearTimeout(eventTimerRef.current);
      }
      if (comboTimerRef.current) {
        clearTimeout(comboTimerRef.current);
      }
      if (judgementTimerRef.current) {
        clearTimeout(judgementTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }
      const parent = canvas.parentElement;
      if (!parent) {
        return;
      }
      canvas.width = parent.clientWidth;
      canvas.height = 520;
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!isPlaying || event.repeat) {
        return;
      }
      const key = event.key.toLowerCase();
      if (isBeatMode) {
        if (IGNORED_BEAT_KEYS.has(key)) {
          return;
        }
        event.preventDefault();
        const audio = audioRef.current;
        if (!audio) {
          return;
        }
        laneFlashRef.current[0] = audio.currentTime;
        judgeBeat(audio.currentTime);
        return;
      }
      const lane = keyInputs.indexOf(key);
      if (lane === -1) {
        return;
      }
      const audio = audioRef.current;
      if (!audio) {
        return;
      }
      pressedRef.current[lane] = true;
      if (holdingRef.current[lane]) {
        return;
      }
      laneFlashRef.current[lane] = audio.currentTime;
      judgeLane(lane, audio.currentTime);
    };
    const handleKeyUp = (event) => {
      if (!isPlaying) {
        return;
      }
      if (isBeatMode) {
        return;
      }
      const key = event.key.toLowerCase();
      const lane = keyInputs.indexOf(key);
      if (lane === -1) {
        return;
      }
      const audio = audioRef.current;
      if (!audio) {
        return;
      }
      pressedRef.current[lane] = false;
      const holding = holdingRef.current[lane];
      if (!holding) {
        return;
      }
      if (holding.type === "slide") {
        return;
      }
      if (audio.currentTime >= holding.endTime - 0.04) {
        processedRef.current.add(holding.index);
        applyJudgement(holding.judgement, lane, holding.type, HOLD_END_BONUS);
      } else {
        processedRef.current.add(holding.index);
        applyJudgement("miss", lane, holding.type);
      }
      holdingRef.current[lane] = null;
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, [isPlaying, isBeatMode, keyInputs]);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = volume;
    }
  }, [volume]);

  useEffect(() => {
    const renderLoop = () => {
      drawFrame();
      if (isPlaying) {
        processMisses();
        checkForFinish();
      }
      animationFrameRef.current = requestAnimationFrame(renderLoop);
    };

    animationFrameRef.current = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animationFrameRef.current);
  }, [isPlaying, isBeatMode, lanes, duration]);

  const syncState = () => {
    setScore(scoreRef.current);
    setCombo(comboRef.current);
    setMaxCombo(maxComboRef.current);
    setJudgementCounts({ ...judgementRef.current });

    const totalNotes = notesRef.current.length || 1;
    const totalScore = totalNotes * SCORE_VALUES.perfect;
    const nextAccuracy = (scoreRef.current / totalScore) * 100;
    const clamped = Number.isFinite(nextAccuracy) ? Math.min(nextAccuracy, 100) : 0;
    setAccuracy(clamped);
  };

  const addScore = (points) => {
    scoreRef.current += points;
  };

  const applyJudgement = (judgement, lane = null, noteType = null, bonus = 0) => {
    judgementRef.current[judgement] += 1;
    addScore(SCORE_VALUES[judgement] + bonus);
    if (judgement === "miss") {
      comboRef.current = 0;
    } else {
      comboRef.current += 1;
      maxComboRef.current = Math.max(maxComboRef.current, comboRef.current);
    }
    setLastJudgementText(judgement.toUpperCase());
    setLastJudgementType(judgement);
    setEventPulse(null);
    if (noteType === "ex_tap") {
      setExTapPulse({ id: Date.now() });
    }
    if (eventTimerRef.current) {
      clearTimeout(eventTimerRef.current);
    }
    if (judgementTimerRef.current) {
      clearTimeout(judgementTimerRef.current);
    }
    judgementTimerRef.current = setTimeout(() => {
      setLastJudgementText("");
      setLastJudgementType("none");
    }, 700);
    if (judgement === "miss") {
      setMissFlash(true);
      if (missTimerRef.current) {
        clearTimeout(missTimerRef.current);
      }
      missTimerRef.current = setTimeout(() => setMissFlash(false), 160);
    }
    if (judgement !== "miss" && comboRef.current > 0 && comboRef.current % 10 === 0) {
      setComboPulse({ id: Date.now(), value: comboRef.current });
      if (comboTimerRef.current) {
        clearTimeout(comboTimerRef.current);
      }
      comboTimerRef.current = setTimeout(() => setComboPulse(null), 520);
    }
    if (lane !== null) {
      hitRingRef.current.push({ lane, time: performance.now(), judgement });
    }
    syncState();
  };

  const startHold = (lane, noteIndex, note, judgement) => {
    const length = Math.max(note.length || 0, 0);
    const endTime = note.time + length;
    holdingRef.current[lane] = {
      index: noteIndex,
      endTime,
      judgement,
      type: note.type,
      nextTick: note.time + SLIDE_TICK_INTERVAL
    };
  };

  const getNoteWindows = (note) => {
    if (isBeatMode) {
      return {
        perfect: BEAT_JUDGE_WINDOWS.perfect,
        great: BEAT_JUDGE_WINDOWS.great,
        good: BEAT_JUDGE_WINDOWS.good
      };
    }
    const lengthBonus = Math.min((note.length || 0) * 0.2, 0.08);
    switch (note.type) {
      case "hold":
        return {
          perfect: 0.07 + lengthBonus,
          great: 0.12 + lengthBonus,
          good: 0.18 + lengthBonus
        };
      case "slide":
        return {
          perfect: 0.04 + lengthBonus,
          great: 0.08 + lengthBonus,
          good: 0.12 + lengthBonus
        };
      case "ex_tap":
        return {
          perfect: 0.055 + lengthBonus,
          great: 0.11 + lengthBonus,
          good: 0.16 + lengthBonus
        };
      default:
        return {
          perfect: 0.05 + lengthBonus,
          great: 0.1 + lengthBonus,
          good: 0.15 + lengthBonus
        };
    }
  };

  const judgeLane = (lane, inputTime) => {
    let closestIndex = -1;
    let closestDiff = Number.POSITIVE_INFINITY;

    for (let i = 0; i < notesRef.current.length; i += 1) {
      const note = notesRef.current[i];
      if (note.lane !== lane || processedRef.current.has(i) || isHoldingIndex(i)) {
        continue;
      }
      const diff = Math.abs(inputTime - note.time);
      const windows = getNoteWindows(note);
      if (diff <= windows.good && diff < closestDiff) {
        closestDiff = diff;
        closestIndex = i;
      }
      if (note.time > inputTime + MAX_INPUT_WINDOW) {
        break;
      }
    }

    if (closestIndex === -1) {
      return;
    }

    const targetNote = notesRef.current[closestIndex];
    const targetWindows = getNoteWindows(targetNote);
    let judgement = "good";
    if (closestDiff <= targetWindows.perfect) {
      judgement = "perfect";
    } else if (closestDiff <= targetWindows.great) {
      judgement = "great";
    }

    if ((targetNote.type === "hold" || targetNote.type === "slide") && targetNote.length > 0) {
      startHold(lane, closestIndex, targetNote, judgement);
      return;
    }

    processedRef.current.add(closestIndex);
    applyJudgement(judgement, lane, targetNote.type);
  };

  const judgeBeat = (inputTime) => {
    let closestIndex = -1;
    let closestDiff = Number.POSITIVE_INFINITY;

    for (let i = 0; i < notesRef.current.length; i += 1) {
      const note = notesRef.current[i];
      if (processedRef.current.has(i)) {
        continue;
      }
      const diff = Math.abs(inputTime - note.time);
      const windows = getNoteWindows(note);
      if (diff <= windows.good && diff < closestDiff) {
        closestDiff = diff;
        closestIndex = i;
      }
      if (note.time > inputTime + MAX_INPUT_WINDOW) {
        break;
      }
    }

    if (closestIndex === -1) {
      return;
    }

    const targetNote = notesRef.current[closestIndex];
    const targetWindows = getNoteWindows(targetNote);
    let judgement = "good";
    if (closestDiff <= targetWindows.perfect) {
      judgement = "perfect";
    } else if (closestDiff <= targetWindows.great) {
      judgement = "great";
    }

    processedRef.current.add(closestIndex);
    applyJudgement(judgement, 0, targetNote.type);
  };

  const processMisses = () => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }
    let hasMiss = false;
    let hasTick = false;
    for (let i = 0; i < notesRef.current.length; i += 1) {
      if (processedRef.current.has(i)) {
        continue;
      }
      const note = notesRef.current[i];
      if (note.length > 0 && isHoldingIndex(i)) {
        continue;
      }
      const missWindow = isBeatMode ? BEAT_JUDGE_WINDOWS.miss : JUDGE_WINDOWS.miss;
      if (audio.currentTime > note.time + missWindow) {
        processedRef.current.add(i);
        judgementRef.current.miss += 1;
        comboRef.current = 0;
        hasMiss = true;
      }
    }
    for (let lane = 0; lane < holdingRef.current.length; lane += 1) {
      const holding = holdingRef.current[lane];
      if (!holding) {
        continue;
      }
      if (holding.type === "slide" && pressedRef.current[lane]) {
        while (audio.currentTime >= holding.nextTick) {
          addScore(SLIDE_TICK_SCORE);
          holding.nextTick += SLIDE_TICK_INTERVAL;
          hasTick = true;
        }
      }
      if (audio.currentTime >= holding.endTime) {
        processedRef.current.add(holding.index);
        if (holding.type === "slide") {
          if (pressedRef.current[lane]) {
            applyJudgement(holding.judgement, lane, holding.type, SLIDE_END_BONUS);
          } else {
            applyJudgement("miss", lane, holding.type);
          }
        } else {
          applyJudgement(holding.judgement, lane, holding.type, HOLD_END_BONUS);
        }
        holdingRef.current[lane] = null;
      }
    }
    if (hasMiss) {
      setLastJudgementText("MISS");
      setLastJudgementType("miss");
      setEventPulse(null);
      if (eventTimerRef.current) {
        clearTimeout(eventTimerRef.current);
      }
      if (judgementTimerRef.current) {
        clearTimeout(judgementTimerRef.current);
      }
      judgementTimerRef.current = setTimeout(() => {
        setLastJudgementText("");
        setLastJudgementType("none");
      }, 700);
      setMissFlash(true);
      if (missTimerRef.current) {
        clearTimeout(missTimerRef.current);
      }
      missTimerRef.current = setTimeout(() => setMissFlash(false), 160);
      syncState();
    }
    if (hasTick) {
      syncState();
    }
  };

  const finishGame = () => {
    if (isFinished) {
      return;
    }
    setIsFinished(true);
    setIsPlaying(false);
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
    }

    const totalNotes = notesRef.current.length || 1;
    const totalScore = totalNotes * SCORE_VALUES.perfect;
    const finalAccuracy = (scoreRef.current / totalScore) * 100;
    const result = {
      score: scoreRef.current,
      accuracy: Number.isFinite(finalAccuracy) ? finalAccuracy : 0,
      maxCombo: maxComboRef.current,
      perfect: judgementRef.current.perfect,
      great: judgementRef.current.great,
      good: judgementRef.current.good,
      miss: judgementRef.current.miss
    };
    onFinish(result);
  };

  const checkForFinish = () => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }
    if (audio.ended) {
      finishGame();
      return;
    }
    const totalNotes = notesRef.current.length;
    if (
      processedRef.current.size >= totalNotes &&
      totalNotes > 0 &&
      audio.currentTime >= duration - 0.05
    ) {
      finishGame();
    }
  };

  const handleStart = async () => {
    const audio = audioRef.current;
    if (!audio || !isReady) {
      return;
    }
    audio.currentTime = 0;
    processedRef.current = new Set();
    laneFlashRef.current = new Array(lanes).fill(-1);
    hitRingRef.current = [];
    holdingRef.current = new Array(lanes).fill(null);
    pressedRef.current = new Array(lanes).fill(false);
    scoreRef.current = 0;
    comboRef.current = 0;
    maxComboRef.current = 0;
    judgementRef.current = { perfect: 0, great: 0, good: 0, miss: 0 };
    setLastJudgementText("");
    setLastJudgementType("none");
    setEventPulse(null);
    setComboPulse(null);
    setMissFlash(false);
    syncState();
    setIsFinished(false);
    setIsPlaying(true);
    try {
      await audio.play();
    } catch (err) {
      setIsPlaying(false);
    }
  };

  const handleBack = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
    }
    onBack();
  };

  const drawFrame = () => {
    const canvas = canvasRef.current;
    const audio = audioRef.current;
    if (!canvas || !audio) {
      return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }
    if (isBeatMode) {
      drawBeatFrame(ctx, canvas, audio);
      return;
    }

    const width = canvas.width;
    const height = canvas.height;
    const judgeLineY = height - 100;
    const laneWidth = width / lanes;
    const noteWidth = laneWidth * 0.75;
    const now = audio.currentTime || 0;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#0b1226";
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
    for (let i = 1; i < lanes; i += 1) {
      ctx.beginPath();
      ctx.moveTo(i * laneWidth, 0);
      ctx.lineTo(i * laneWidth, height);
      ctx.stroke();
    }

    for (let i = 0; i < lanes; i += 1) {
      const flashTime = laneFlashRef.current[i];
      if (flashTime < 0) {
        continue;
      }
      const delta = now - flashTime;
      if (delta < HIT_FLASH_DURATION) {
        const alpha = 0.28 * (1 - delta / HIT_FLASH_DURATION);
        ctx.fillStyle = `rgba(56, 189, 248, ${alpha})`;
        ctx.fillRect(i * laneWidth, 0, laneWidth, height);
      }
    }

    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, judgeLineY);
    ctx.lineTo(width, judgeLineY);
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "14px Space Grotesk";
    ctx.textAlign = "center";
    keyLabels.forEach((label, index) => {
      ctx.fillText(label, index * laneWidth + laneWidth / 2, judgeLineY + 32);
    });

    const noteColors = {
      tap: "#fb7185",
      ex_tap: "#f59e0b",
      hold: "#a855f7",
      slide: "#22d3ee"
    };
    ctx.textAlign = "center";
    for (let i = 0; i < notesRef.current.length; i += 1) {
      if (processedRef.current.has(i)) {
        continue;
      }
      const note = notesRef.current[i];
      const timeUntilHit = note.time - now;
      const y = judgeLineY - timeUntilHit * PIXELS_PER_SECOND;
      if (y < -50 || y > height + 50) {
        continue;
      }
      const x = note.lane * laneWidth + (laneWidth - noteWidth) / 2;
      ctx.fillStyle = noteColors[note.type] || noteColors.tap;
      let heightScale = 1;
      if (note.type === "ex_tap") {
        heightScale = 1.3;
      } else if (note.type === "slide") {
        heightScale = 1.1;
      }
      const baseHeight = NOTE_HEIGHT * heightScale;
      const lengthSeconds = Math.max(note.length || 0, 0);
      const isHolding = isHoldingIndex(i);
      if (lengthSeconds > 0) {
        const timeUntilEnd = note.time + lengthSeconds - now;
        const endY = judgeLineY - timeUntilEnd * PIXELS_PER_SECOND;
        const topY = Math.min(y, endY);
        let bottomY = Math.max(y, endY);
        if (isHolding) {
          bottomY = Math.min(bottomY, judgeLineY);
        }
        const heightValue = bottomY - topY + baseHeight * 0.2;
        if (heightValue > 0) {
          ctx.fillRect(x, topY, noteWidth, heightValue);
        }
      } else {
        ctx.fillRect(x, y - baseHeight / 2, noteWidth, baseHeight);
      }

      if (note.type === "slide") {
        ctx.fillStyle = "rgba(34, 211, 238, 0.6)";
        const capY = lengthSeconds > 0 ? Math.min(y, judgeLineY) - 10 : y - baseHeight / 2 - 10;
        ctx.fillRect(x + noteWidth * 0.4, capY, noteWidth * 0.2, 10);
      }
    }

    const nowMs = performance.now();
    hitRingRef.current = hitRingRef.current.filter((hit) => nowMs - hit.time < 1000);
    hitRingRef.current.forEach((hit) => {
      const delta = (nowMs - hit.time) / 1000;
      if (delta > HIT_RING_DURATION) {
        return;
      }
      const progress = delta / HIT_RING_DURATION;
      const alpha = 0.6 * (1 - progress);
      const radius = 20 + progress * 26;
      const centerX = hit.lane * laneWidth + laneWidth / 2;
      ctx.strokeStyle = `rgba(56, 189, 248, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(centerX, judgeLineY, radius, 0, Math.PI * 2);
      ctx.stroke();
    });

    ctx.fillStyle = "rgba(229, 231, 235, 0.9)";
    ctx.font = "16px Space Grotesk";
    ctx.textAlign = "left";
    ctx.fillText(`Combo: ${comboRef.current}`, 20, 30);
  };

  const drawBeatFrame = (ctx, canvas, audio) => {
    const width = canvas.width;
    const height = canvas.height;
    const now = audio.currentTime || 0;
    const notes = notesRef.current;
    const nextIndex = notes.findIndex((_, index) => !processedRef.current.has(index));
    const laneY = height * 0.5;
    const laneStart = Math.max(42, width * 0.12);
    const hitX = Math.min(width - 58, width * 0.82);
    const pixelsPerSecond = (hitX - laneStart) / BEAT_PREVIEW_SECONDS;
    const ballRadius = 18;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#060913";
    ctx.fillRect(0, 0, width, height);

    const glow = ctx.createRadialGradient(hitX, laneY, 8, hitX, laneY, 72);
    glow.addColorStop(0, "rgba(56, 189, 248, 0.18)");
    glow.addColorStop(0.42, "rgba(56, 189, 248, 0.08)");
    glow.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(hitX - 90, laneY - 90, 180, 180);

    ctx.strokeStyle = "rgba(148, 163, 184, 0.22)";
    ctx.lineWidth = 7;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(laneStart, laneY);
    ctx.lineTo(hitX, laneY);
    ctx.stroke();

    ctx.strokeStyle = "rgba(125, 211, 252, 0.58)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(hitX, laneY - 54);
    ctx.lineTo(hitX, laneY + 54);
    ctx.stroke();

    ctx.fillStyle = "rgba(56, 189, 248, 0.08)";
    ctx.beginPath();
    ctx.arc(hitX, laneY, 24, 0, Math.PI * 2);
    ctx.fill();

    for (let i = 0; i < notes.length; i += 1) {
      if (processedRef.current.has(i)) {
        continue;
      }
      const note = notes[i];
      const timeUntilHit = note.time - now;
      const x = hitX - timeUntilHit * pixelsPerSecond;
      if (x < laneStart - ballRadius * 2 || x > hitX + ballRadius * 2) {
        continue;
      }
      const isNext = i === nextIndex;
      const radius = isNext ? ballRadius : ballRadius * 0.72;
      const alpha = isNext ? 1 : 0.72;
      ctx.fillStyle = isNext ? "#38bdf8" : `rgba(147, 197, 253, ${alpha})`;
      ctx.strokeStyle = isNext ? "#e0f2fe" : "rgba(191, 219, 254, 0.55)";
      ctx.lineWidth = isNext ? 3 : 2;
      ctx.beginPath();
      ctx.arc(x, laneY, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    const flashTime = laneFlashRef.current[0];
    if (flashTime >= 0 && now - flashTime < HIT_FLASH_DURATION) {
      const alpha = 0.08 * (1 - (now - flashTime) / HIT_FLASH_DURATION);
      ctx.fillStyle = `rgba(125, 211, 252, ${alpha})`;
      ctx.fillRect(hitX - 70, laneY - 70, 140, 140);
    }

    const nowMs = performance.now();
    hitRingRef.current = hitRingRef.current.filter((hit) => nowMs - hit.time < 1000);
    hitRingRef.current.forEach((hit) => {
      const delta = (nowMs - hit.time) / 1000;
      if (delta > HIT_RING_DURATION) {
        return;
      }
      const ringProgress = delta / HIT_RING_DURATION;
      const alpha = 0.32 * (1 - ringProgress);
      const color = hit.judgement === "miss" ? "251, 113, 133" : "125, 211, 252";
      ctx.strokeStyle = `rgba(${color}, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(hitX, laneY, 18 + ringProgress * 46, 0, Math.PI * 2);
      ctx.stroke();
    });

    ctx.fillStyle = "#7cff8c";
    ctx.font = "18px Space Grotesk";
    ctx.textAlign = "center";
    if (lastJudgementText && lastJudgementType !== "miss") {
      ctx.fillText(lastJudgementText, hitX, laneY - 70);
    }
    ctx.fillStyle = "rgba(229, 231, 235, 0.88)";
    ctx.font = "14px Space Grotesk";
    ctx.fillText("SPACE / ENTER / D F J K", width / 2, height - 38);
    ctx.textAlign = "left";
    ctx.fillText(`Combo: ${comboRef.current}`, 20, 30);
  };

  return (
    <div className="game-screen">
      <div className="game-topbar">
        <div>
          <h2>{fileId || "Rhythm Game"}</h2>
          <span className="muted">
            Mode: {isBeatMode ? "Beat Only" : "Lane Keys"} | Difficulty: {chart?.difficulty || "normal"}
          </span>
        </div>
        <div className="game-hud">
          <div>
            <strong>Score</strong>
            <span>{score}</span>
          </div>
          <div>
            <strong>Combo</strong>
            <span>{combo}</span>
          </div>
          <div>
            <strong>Accuracy</strong>
            <span>{accuracy.toFixed(2)}%</span>
          </div>
        </div>
        <button className="ghost" onClick={handleBack}>
          Back
        </button>
      </div>

      <div className={`game-canvas-wrap ${missFlash ? "miss-flash" : ""}`}>
        <canvas
          ref={canvasRef}
          className="game-canvas"
          onClick={() => {
            if (!isPlaying || !isBeatMode || !audioRef.current) {
              return;
            }
            laneFlashRef.current[0] = audioRef.current.currentTime;
            judgeBeat(audioRef.current.currentTime);
          }}
        />
        {eventPulse && null}
        {exTapPulse && <div key={exTapPulse.id} className="ex-tap-flash" />}
        {comboPulse && (
          <div key={comboPulse.id} className="combo-pop">COMBO {comboPulse.value}</div>
        )}
        {lastJudgementText && (
          <div className={`judgement-banner ${lastJudgementType}`}>
            {lastJudgementText}
          </div>
        )}
      </div>

      <div className="game-bottom">
        {!isPlaying && !isFinished && (
          <button className="primary" onClick={handleStart} disabled={!isReady}>
            Start
          </button>
        )}
        <label className="volume-control">
          <span>Volume</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(event) => setVolume(Number(event.target.value))}
          />
          <strong>{Math.round(volume * 100)}%</strong>
        </label>
        <div className="game-judgements">
          <span className="judgement-perfect">Perfect: {judgementCounts.perfect}</span>
          <span className="judgement-great">Great: {judgementCounts.great}</span>
          <span className="judgement-good">Good: {judgementCounts.good}</span>
          <span className="judgement-miss">Miss: {judgementCounts.miss}</span>
        </div>
      </div>

      <audio
        ref={audioRef}
        src={audioUrl}
        preload="auto"
        onLoadedMetadata={() => setIsReady(true)}
        onEnded={finishGame}
      />
    </div>
  );
}

export default GamePlayer;
