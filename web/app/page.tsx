"use client";

import { useEffect, useMemo, useState, type ChangeEvent } from "react";

type Move = {
  name: string;
  pose: string;
};

const moves: Move[] = [
  { name: "Groove", pose: "groove" },
  { name: "Shuffle", pose: "shuffle" },
  { name: "Spin", pose: "spin" },
  { name: "Bounce", pose: "bounce" },
  { name: "Freestyle", pose: "freestyle" },
];

function WingMark() {
  return (
    <span className="wing-mark" aria-hidden="true">
      <i /><i /><i /><i />
    </span>
  );
}

function Sparkle({ small = false }: { small?: boolean }) {
  return <span className={small ? "sparkle sparkle--small" : "sparkle"} aria-hidden="true">✦</span>;
}

function Dancer({
  pose = "hero",
  colorful = false,
}: {
  pose?: string;
  colorful?: boolean;
}) {
  return (
    <div className={`dancer dancer--${pose} ${colorful ? "dancer--colorful" : "dancer--holographic"}`} aria-hidden="true">
      <span className="dancer__glow" />
      <span className="dancer__head" />
      <span className="dancer__neck" />
      <span className="dancer__body" />
      <span className="dancer__arm dancer__arm--left"><i /></span>
      <span className="dancer__arm dancer__arm--right"><i /></span>
      <span className="dancer__leg dancer__leg--left"><i /></span>
      <span className="dancer__leg dancer__leg--right"><i /></span>
    </div>
  );
}

function Waveform({ playing }: { playing: boolean }) {
  const bars = [18, 38, 62, 32, 72, 51, 84, 44, 67, 35, 78, 55, 91, 48, 69, 37, 82, 58, 73, 30, 64, 42, 76, 52, 88, 39, 71, 47, 80, 33, 59, 26];
  return (
    <span className={`waveform${playing ? " is-playing" : ""}`} aria-hidden="true">
      {bars.map((height, index) => <i key={index} style={{ height: `${height}%`, animationDelay: `${index * -34}ms` }} />)}
    </span>
  );
}

function StageLights() {
  return (
    <div className="stage-lights" aria-hidden="true">
      <span className="beam beam--one" /><span className="beam beam--two" />
      <span className="beam beam--three" /><span className="beam beam--four" />
      <span className="tower tower--left"><i /><i /><i /><i /></span>
      <span className="tower tower--right"><i /><i /><i /><i /></span>
      <span className="equalizer equalizer--left">{Array.from({ length: 18 }, (_, index) => <i key={index} />)}</span>
      <span className="equalizer equalizer--right">{Array.from({ length: 18 }, (_, index) => <i key={index} />)}</span>
    </div>
  );
}

function fileName(event: ChangeEvent<HTMLInputElement>, fallback: string) {
  return event.target.files?.[0]?.name ?? fallback;
}

export default function Home() {
  const [selectedMoves, setSelectedMoves] = useState(() => new Set(["Groove", "Spin", "Bounce"]));
  const [previewing, setPreviewing] = useState(false);
  const [songPlaying, setSongPlaying] = useState(false);
  const [carouselOffset, setCarouselOffset] = useState(0);
  const [heroesOpen, setHeroesOpen] = useState(false);
  const [song, setSong] = useState("I Will Be Here (Wolfgang Gartner Remix)");
  const [drawing, setDrawing] = useState("woman-1.png");
  const [created, setCreated] = useState(false);

  const selectedCount = selectedMoves.size;
  const moveSummary = useMemo(() => [...selectedMoves].join(", "), [selectedMoves]);
  const orderedMoves = useMemo(
    () => [...moves.slice(carouselOffset), ...moves.slice(0, carouselOffset)],
    [carouselOffset],
  );
  const selectedPose = moves.find((move) => selectedMoves.has(move.name))?.pose ?? "hero";

  useEffect(() => {
    if (!heroesOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setHeroesOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [heroesOpen]);

  function toggleMove(name: string) {
    setSelectedMoves((current) => {
      const next = new Set(current);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
    setCreated(false);
  }

  function createDance() {
    if (!selectedCount) return;
    setCreated(true);
    setPreviewing(true);
    window.setTimeout(() => setCreated(false), 3200);
  }

  function rotateMoves(direction: -1 | 1) {
    setCarouselOffset((current) => (current + direction + moves.length) % moves.length);
  }

  return (
    <main className="site-frame">
      <div className="ambient ambient--mint" aria-hidden="true" />
      <div className="ambient ambient--violet" aria-hidden="true" />

      <section className="app-shell" aria-label="Dancing Angels AI dance creator">
        <nav className="topbar">
          <a className="brand" href="#stage" aria-label="Dancing Angels AI home">
            <WingMark />
            <span>Dancing Angels <strong>AI</strong></span>
          </a>
          <div className="topbar__actions">
            <button className="heroes-button" type="button" onClick={() => setHeroesOpen(true)} aria-expanded={heroesOpen}><span aria-hidden="true">♙</span> My Heroes</button>
            <button className="gold-button gold-button--small" type="button" onClick={() => document.querySelector("#creator")?.scrollIntoView({ behavior: "smooth" })}>
              <Sparkle small /> Create
            </button>
          </div>
        </nav>

        <section className={`stage${previewing ? " is-previewing" : ""}`} id="stage">
          <StageLights />
          <div className="skills-badge"><span>★</span> {selectedCount} skill{selectedCount === 1 ? "" : "s"} equipped</div>
          <div className="hero-dancer"><Dancer pose={previewing ? selectedPose : "hero"} /></div>
          <div className="stage-platform"><i /><b /></div>
          <button className="preview-button" type="button" onClick={() => setPreviewing((value) => !value)} aria-pressed={previewing} disabled={!selectedCount}>
            <span>{previewing ? "Ⅱ" : "▶"}</span>{previewing ? "Pause preview" : "Preview dance"}
          </button>
        </section>

        <section className="moves-section" aria-labelledby="moves-heading">
          <header className="section-title">
            <span className="section-icon" aria-hidden="true">⌁</span>
            <div><h1 id="moves-heading">Choose your hero&apos;s moves</h1><p>{selectedCount ? moveSummary : "Pick at least one move"}</p></div>
          </header>

          <div className="moves-rail">
            <button className="rail-arrow" type="button" aria-label="Rotate moves backward" onClick={() => rotateMoves(-1)}>‹</button>
            <div className="move-grid">
              {orderedMoves.map((move) => {
                const selected = selectedMoves.has(move.name);
                return (
                  <button
                    className={`move-card${selected ? " is-selected" : ""}`}
                    type="button"
                    key={move.name}
                    onClick={() => toggleMove(move.name)}
                    aria-pressed={selected}
                  >
                    <span className="move-card__check">{selected ? "✓" : "+"}</span>
                    <span className="move-card__figure"><Dancer pose={move.pose} /></span>
                    <strong>{move.name}</strong>
                  </button>
                );
              })}
            </div>
            <button className="rail-arrow" type="button" aria-label="Rotate moves forward" onClick={() => rotateMoves(1)}>›</button>
          </div>
          <p className="sr-only" aria-live="polite">{orderedMoves[0].name} is first in the move carousel.</p>
        </section>

        <section className="creator" id="creator" aria-label="Three-step dance creator">
          <article className="creator-step song-step">
            <header><span className="step-number">1</span><h2>Add a song</h2></header>
            <div className="track-card">
              <span className="music-tile" aria-hidden="true">♫</span>
              <span className="track-copy"><strong>{song}</strong><small>Tiësto &amp; Sneaky Sound System</small></span>
              <label className="change-button">Change<input type="file" accept="audio/*" onChange={(event) => setSong(fileName(event, song))} /></label>
              <button className="round-play" type="button" aria-label={songPlaying ? "Pause song" : "Play song"} aria-pressed={songPlaying} onClick={() => setSongPlaying((value) => !value)}>{songPlaying ? "Ⅱ" : "▶"}</button>
              <Waveform playing={songPlaying} />
              <time>{songPlaying ? "0:24" : "2:48"}</time>
            </div>
            <label className="upload-zone">
              <span className="upload-symbol">↥</span>
              <span><strong>Upload your song</strong><small>MP3, WAV, M4A up to 50MB</small></span>
              <input type="file" accept="audio/*" onChange={(event) => setSong(fileName(event, song))} />
            </label>
          </article>

          <span className="flow-arrow" aria-hidden="true">⟶</span>

          <article className="creator-step character-step">
            <header><span className="step-number">2</span><h2>Add your character</h2></header>
            <label className="drawing-card">
              <span className="drawing-paper"><span className="drawing-art"><img src="/woman-1.png" alt="Uploaded woman-1 character drawing" /></span></span>
              <span className="drawing-upload"><span>↥</span> {drawing}</span>
              <input type="file" accept="image/png,image/jpeg" onChange={(event) => setDrawing(fileName(event, drawing))} />
            </label>
            <div className="transformation-arrow" aria-hidden="true"><span>→</span><Sparkle small /></div>
            <div className="character-preview"><Dancer pose="groove" /><Sparkle /><Sparkle small /></div>
          </article>

          <span className="flow-arrow" aria-hidden="true">⟶</span>

          <article className="creator-step result-step">
            <header><span className="step-number">3</span><h2>Dance on beat</h2></header>
            <div className={`result-stage${previewing ? " is-previewing" : ""}`}>
              <StageLights />
              <Dancer pose="groove" />
              <span className="result-floor" />
            </div>
            <button className="gold-button create-dance-button" type="button" onClick={createDance} disabled={!selectedCount}>
              <Sparkle /> {created ? "Your hero is alive!" : selectedCount ? "Bring my hero to life" : "Choose a move first"}
            </button>
          </article>
        </section>
      </section>

      {heroesOpen && (
        <div className="heroes-scrim" onMouseDown={() => setHeroesOpen(false)}>
          <aside className="heroes-panel" role="dialog" aria-modal="true" aria-labelledby="heroes-title" onMouseDown={(event) => event.stopPropagation()}>
            <header><div><span className="panel-kicker">Current mock hero</span><h2 id="heroes-title">Your stage setup</h2></div><button type="button" onClick={() => setHeroesOpen(false)} aria-label="Close My Heroes" autoFocus>×</button></header>
            <div className="hero-summary-stage"><Dancer pose={selectedPose} /><span /></div>
            <dl>
              <div><dt>Moves</dt><dd>{selectedCount ? moveSummary : "None selected"}</dd></div>
              <div><dt>Song</dt><dd>{song}</dd></div>
              <div><dt>Character</dt><dd>{drawing}</dd></div>
            </dl>
            <button className="gold-button panel-action" type="button" disabled={!selectedCount} onClick={() => { setHeroesOpen(false); createDance(); }}>Preview this hero</button>
          </aside>
        </div>
      )}

      <div className={`creator-toast${created ? " is-visible" : ""}`} role="status" aria-live="polite"><Sparkle small /> Mock dance ready — previewing your selected moves.</div>

      <footer className="site-footer">
        <span><i /> Blueprint Grid</span><span><i /> Holographic Polymer</span><span><i /> Golden Beat</span>
        <p>Roadmap V4 · Step 7 complete</p>
      </footer>
    </main>
  );
}
