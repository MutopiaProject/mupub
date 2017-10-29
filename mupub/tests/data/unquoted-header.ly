% test note: unquoted declarations (subtitle,mytagline) should survive parsing.
\header {
 title = "Danzas Españolas No. 2, Oriental"
 subtitle = \markup { \smaller "Arranged for Guitar Duo" }
 composer = "Enrique Granados" % d.1916
 arranger = "Arr: Dennis Burns"
 style = "Romantic"
 date = "1890"
 source = "Barcelona: Casa Dostesio, n.d. (IMSLP01200)"
 mytagline = ##f

 %            o_
 %       (\___\/_____/)
 %  ~ ~ ~ ~ ~ / ~ ~ ~ ~ ~ ~ ~
 maintainer = "Jeffrey Olson & Dennis Burns"
 maintainerEmail = "gmail's jjocanoe & boldersounds.com's dennis"
 license = "Creative Commons Attribution-ShareAlike 4.0"

 mutopiacomposer = "GranadosE"
 mutopiatitle = "Danzas Españolas No. 2, Oriental"
 mutopiaopus = "Op. 37"
 mutopiadate = "1890"
 mutopiasource = "Barcelona: Casa Dostesio, n.d."
 mutopiainstrument = "2 Guitars"

 footer = "Mutopia-2017/10/01-submittal"
 copyright = \markup {\override #'(font-name . "DejaVu Sans, Bold") \override #'(baseline-skip . 0) \right-column {\with-url #"http://www.MutopiaProject.org" {\abs-fontsize #9  "Mutopia " \concat {\abs-fontsize #12 \with-color #white \char ##x01C0 \abs-fontsize #9 "Project "}}}\override #'(font-name . "DejaVu Sans, Bold") \override #'(baseline-skip . 0 ) \center-column {\abs-fontsize #11.9 \with-color #grey \bold {\char ##x01C0 \char ##x01C0 }}\override #'(font-name . "DejaVu Sans,sans-serif") \override #'(baseline-skip . 0) \column { \abs-fontsize #8 \concat {"Typeset using " \with-url #"http://www.lilypond.org" "LilyPond " \char ##x00A9 " 2017 " "by " \maintainer " " \char ##x2014 " " \footer}\concat {\concat {\abs-fontsize #8 { \with-url #"http://creativecommons.org/licenses/by-sa/4.0/" "Creative Commons Attribution ShareAlike 4.0 International License "\char ##x2014 " free to distribute, modify, and perform" }}\abs-fontsize #13 \with-color #white \char ##x01C0 }}}
 tagline = ##f
}