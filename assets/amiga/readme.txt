a great deal of effort was made to extract only the used tiles & cluts for a given context

Intro:

In the intro, we also have a transparency issue plus a color issue (too many colors)
So it was worth implementing something special so the title renders great.

- ripped backgroundless pics of big dudes in MAME (using pattern 6000 in 24A000
  so background was of uniform color: in mame debugger:
   fill $24A000,$200,$6000
   snap
- converted to 16 colors (from 23 colors), added magenta background
- fixed left dude fist as it seems that some pixels are missing (less noticeable on MAME/original gfx but defect exists)
- ripped tiles used by big dudes to NOT include them in graphics
- converted 2 dudes images into 2 big BOBs, with specific palette that will change
  before displaying them. So the "baddudes vs dragonninja" colors aren't taken into
  account in the 15 available colors
  
... Then threw this dual playfield thing away and went 64 colors with cookie cut => titke is now perfect!!

Game:

64 colors was the bare minimum. Tiles use 32 colors and BOBs use the other 32 colors, with no shared colors.
OSD is made of 64-wide AGA sprites with dynamic color change for great effect.


  