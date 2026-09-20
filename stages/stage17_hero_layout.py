#!/usr/bin/env python3
# Stage 17 — a hero slide that composes two or three products as a fan instead
# of stacking them on top of each other, and copy that fits the column it is in.
import io
P = '/root/work/smokers-paradise-demo/build/index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, 'count %d for: %s' % (s.count(a), a[:100])
    s = s.replace(a, b)
    print('  ok:', a[:64].replace('\n', ' '))

# ---- the fan -------------------------------------------------------------
# One plate fills the stage. Two or three step down and across it, each one
# narrower than the last, so all of them are actually visible.
rep("""      const OFF3=['40%','58%','76%'], TOP3=['42%','56%','70%'];
      const off = n.length>2 ? OFF3[i] : (n.length>1 ? (i===0?'46%':'72%') : '50%');
      const top = n.length>2 ? TOP3[i] : (n.length>1 ? (i===0?'45%':'66%') : '50%');""",
"""      const FAN = {
        1:{off:['50%'],              top:['50%'],              w:'88%', h:'70%'},
        2:{off:['40%','70%'],        top:['42%','62%'],        w:'62%', h:'54%'},
        3:{off:['31%','52%','73%'],  top:['38%','53%','68%'],  w:'50%', h:'44%'}
      }[Math.min(n.length,3)];
      const off = FAN.off[i] || '50%', top = FAN.top[i] || '50%';""")

rep("""      return `<span class="pz flat"
        style="left:${off};top:${top};z-index:${x.z||1};
               transform:translate(-50%,-50%) rotate(${x.tilt||0}deg) scale(${x.scale||1})">""",
"""      return `<span class="pz flat"
        style="left:${off};top:${top};z-index:${x.z||1};width:${FAN.w};height:${FAN.h};
               transform:translate(-50%,-50%) rotate(${x.tilt||0}deg) scale(${x.scale||1})">""")

# the stage needs a little more room once three plates fan across it
rep(""".slide .txt{position:absolute;left:0;top:0;bottom:0;width:56%;padding:22px 10px 34px 20px;""",
    """.slide .txt{position:absolute;left:0;top:0;bottom:0;width:54%;padding:20px 8px 32px 20px;""")
rep(""".slide .stage{position:absolute;right:0;top:0;bottom:0;width:44%;z-index:2}""",
    """.slide .stage{position:absolute;right:0;top:0;bottom:0;width:46%;z-index:2}""")

# a fanned plate carries a thin rim so two white cards read as two cards
rep(""".slide .stage .pz.flat img{filter:none;border-radius:7px}""",
    """.slide .stage .pz.flat img{filter:none;border-radius:7px}
/* Fanned plates overlap, so each needs an edge of its own or three white
   cards read as one white shape. */
.slide .stage .pz.flat{outline:1px solid rgba(0,0,0,.10);outline-offset:-1px}""")

# ---- copy that fits ------------------------------------------------------
# The sub line is clamped to three lines in a 21-character column, so anything
# over about ninety characters was being cut mid-word with an ellipsis.
rep("""    sub:'Extra-strength mushroom chocolate in five flavors. Peanut butter, fruity cereal, chocolate crunch, cookies and cream, chocolate milk.',""",
    """    sub:'Extra strength, five flavors. Peanut butter, fruity cereal, chocolate crunch and more.',""")
rep("""    sub:'Or 3 for $12. Crystal Cube, Golden Berry, Rocket Freeze, Blue Razz Dragonfruit, Cool Mint Ice.',""",
    """    sub:'Or 3 for $12. Crystal Cube, Golden Berry, Rocket Freeze, Cool Mint Ice.',""")
rep("""    sub:'Hawaiian Punch, Juicy Peach Ice, Strawberry Watermelon, Pineapple Coconut, Polar Mint and more.',""",
    """    sub:'Hawaiian Punch, Juicy Peach Ice, Strawberry Watermelon, Polar Mint and more.',""")
rep("""    sub:'Thank you, Nogales. You put us here, and the shelf will keep earning it.',""",
    """    sub:'Thank you, Nogales. You put us here and the shelf will keep earning it.',""")

# headline that wraps to three lines pushes the sub into the fine print
rep("""    headline:'Lost Mary NERA, new flavors',""",
    """    headline:'Lost Mary, new flavors',""")
rep("""    headline:'Voted Best Smoke Shop 2026',""",
    """    headline:'Best Smoke Shop 2026',""")

# the arrows sit on the copy at 50%; move them clear of the headline
rep(""".promoc .arw{position:absolute;top:50%;transform:translateY(-50%);width:31px;height:31px;border-radius:99px;z-index:6;""",
    """.promoc .arw{position:absolute;top:auto;bottom:9px;transform:none;width:31px;height:31px;border-radius:99px;z-index:6;""")

# the award slide is a photograph, not a packshot: let it fill its plate
rep("""    return `<div class="stage"><span class="pz flat photo"
      style="left:50%;top:50%;transform:translate(-50%,-50%) rotate(-2deg)">""",
"""    return `<div class="stage"><span class="pz flat photo"
      style="left:50%;top:50%;width:90%;height:76%;transform:translate(-50%,-50%) rotate(-2deg)">""")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n%d -> %d bytes' % (n0, len(s)))
