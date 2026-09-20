#!/usr/bin/env python3
# Stage 23 — the door opens onto the shop itself.
#
# Behind the hero: their own footage, muted, looping, starting the moment the
# age gate is answered. Until that file is dropped in, the same slot runs a
# slow push across their storefront photograph, so the shape of the screen is
# the finished one either way and the video is a one-line swap.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:100])
    s = s.replace(a, b)
    print('  ok:', a[:62].replace('\n', ' '))

# ---------------------------------------------------------------- the slot
rep("""const STORE_CONTENT = {""",
"""/* =========================================================================
   THE HERO FILM

   What plays behind the logo when the door opens. HERO_FILM is their own
   footage as a muted, looping, inline mp4 data URI; the moment it is set the
   hero plays it and the still below is only the poster.

   Until then the same slot runs a slow push across the storefront photograph,
   which is real and is theirs, so the screen is composed either way.

   Muted and playsinline are not optional: every mobile browser refuses to
   autoplay anything else, and this must start by itself or it is not a
   background. */
const HERO_FILM = '';                 /* data:video/mp4;base64,... */
const HERO_FILM_POSTER = FRONT_PHOTO; /* first frame, and the reduced-motion still */

const STORE_CONTENT = {""")

# ---------------------------------------------------------------- markup
rep("""function skyHeroHTML(){
  return `<div class="skyhero">
    ${skyHTML('hero')}""",
"""function heroFilmHTML(){
  /* Under reduced motion nothing moves: the still is the background. */
  const still = `<div class="herofilm still" aria-hidden="true"
      style="background-image:url('${HERO_FILM_POSTER}')"></div>`;
  if(!HERO_FILM) return still + `<div class="heroscrim" aria-hidden="true"></div>`;
  return `<div class="herofilm" aria-hidden="true">
      <video id="heroFilm" muted loop playsinline preload="auto" tabindex="-1"
        poster="${HERO_FILM_POSTER}" disablepictureinpicture>
        <source src="${HERO_FILM}" type="video/mp4">
      </video>
    </div>
    <div class="heroscrim" aria-hidden="true"></div>`;
}

/* The film starts when the door is answered, not before: nobody should hear
   about a shop they have not been let into yet, and a video decoding behind a
   full screen gate is a battery bill with no picture. */
function heroFilmPlay(){
  const v = document.getElementById('heroFilm');
  if(!v) return;
  if(window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches){
    v.removeAttribute('autoplay'); v.pause(); return;
  }
  const go = () => v.play().catch(()=>{ /* a refusal just leaves the poster */ });
  v.readyState >= 2 ? go() : v.addEventListener('loadeddata', go, {once:true});
}
document.addEventListener('sp:gateopen', heroFilmPlay);

function skyHeroHTML(){
  return `<div class="skyhero">
    ${skyHTML('hero')}
    ${heroFilmHTML()}""")

# ---------------------------------------------------------------- style
rep(""".skyhero .sky{z-index:0}""",
""".skyhero .sky{z-index:0}
/* ---- the film ----
   It sits under everything, covers the band whatever the shape of the phone,
   and is dimmed and warmed toward the plum so white copy stays readable on
   top of a moving picture. The scrim is a separate layer rather than a filter
   on the video, because a filter on a playing video is a repaint of every
   pixel every frame and this has to be free. */
.skyhero .herofilm{position:absolute;inset:0;z-index:1;overflow:hidden}
.skyhero .herofilm video{width:100%;height:100%;object-fit:cover;display:block;
  filter:saturate(1.06)}
.skyhero .herofilm.still{background-size:cover;background-position:50% 42%;
  animation:heroPush 26s ease-in-out infinite alternate}
@keyframes heroPush{from{transform:scale(1.02) translate3d(0,0,0)}
  to{transform:scale(1.16) translate3d(0,-2%,0)}}
/* The band is the shop's light, not a grey wash: plum at the edges, clear in
   the middle, and heaviest at the bottom where the buttons sit. */
.skyhero .heroscrim{position:absolute;inset:0;z-index:2;pointer-events:none;
  background:
    radial-gradient(120% 80% at 50% 18%, rgba(16,10,24,0) 0%, rgba(16,10,24,.34) 52%, rgba(16,10,24,.72) 100%),
    linear-gradient(to bottom, rgba(16,10,24,.62) 0%, rgba(16,10,24,.30) 26%, rgba(16,10,24,.66) 68%, rgba(16,10,24,.94) 100%)}
@media (prefers-reduced-motion:reduce){
  .skyhero .herofilm.still{animation:none;transform:scale(1.06)}
}""")

# the mark and the copy have to sit above the film
rep(""".skyhero .hero-in{position:relative;z-index:3;height:100%;display:flex;flex-direction:column;""",
    """.skyhero .hero-in{position:relative;z-index:4;height:100%;display:flex;flex-direction:column;""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
