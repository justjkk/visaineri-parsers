# -*- coding: utf-8 -*-
from pyparsing import Word, Literal, ParseException, Combine, OneOrMore, Group, StringEnd, White, NotAny, Suppress, FollowedBy, Optional, ZeroOrMore

def u(utf8_str):
   """
   Shorthand for decoding utf-8 string literal to unicode
   """
   return utf8_str.decode('utf-8')

uyir_kuril = u("அஇஉஎஒ") # உயிர்குறில்

uyir_nedil = u("ஆஈஊஏஐஓஔ") # உயிர்நெடில்

uyir = uyir_kuril + uyir_nedil # உயிர்

combining_kuril = u("்ிுெொ") # புணரும் குறில் ( புணரும் அகரத்திற்கு பதில் ஒற்று )

combining_nedil = u("ாீூோோௌை") # புணரும் நெடில்

combining_uyir = combining_kuril + combining_nedil # புணரும் உயிர்

virama = u("்") # புள்ளி

mei = u("கஙசஞடணதநபமயரலவழளறன") # மெய்யெழுத்து (புள்ளி இல்லாமல் மெய்யாய் கொள்ளப்பட்டுள்ளது)

vallina_mei = u("கசடதபற")

aaytham = u("ஃ")

space = White() | StringEnd()

def swap_agaram(strg):
   """
   Rationale:
     Because the unicode defines codepoints for vowels ( separate as well as
   combined ) and consonants ( defaulted with the vowel அ ). This complicates
   the parsing process as we deal with உயிர் எழுத்துக்கள் and மெய் எழுத்துக்கள். So,
   using this function will replace \u0b95(க) with \u0b95(க)\u0bcd(்)=க் and
   \u0b95\u0bcd(க்) with \u0b95(க). Then, the codepoint of virama is borrowed
   as the codepoint of combined அ and the codepoint of consonant is treated
   as the codepoint of the மெய் எழுத்து.

   >>> swap_agaram(u("கல்வி")) == u("க்லவி")
   True

   This function is self-inverse.
   >>> swap_agaram(swap_agaram(u("கல்வி"))) == u("கல்வி")
   True

   """
   def process_form1(tokens):
      return [tokens[0][0] + virama]

   def process_form2(tokens):
      return [tokens[0][0]]

   form1 = Group(Word(mei, exact=1) + NotAny(Word(combining_uyir, exact=1))).setParseAction(process_form1)
   form2 = Group(Word(mei, exact=1) + virama).setParseAction(process_form2)
   swapped_strg = (form1 | form2).transformString(strg)
   return swapped_strg

def token_swap_agaram(tokens):
   for t in tokens:
      t[0] = swap_agaram(t[0]).encode('utf-8')

### எழுத்து ###
# உயிரெழுத்து
thani_kuril_uyir_ezhuttu = Word(uyir_kuril, exact=1) # தனிக்குறில் உயிரெழுத்து
thani_nedil_uyir_ezhuttu = Word(uyir_nedil, exact=1) # தனிநெடில் உயிரெழுத்து
thani_uyir_ezhuttu = Word(uyir, exact=1) # தனி உயிரெழுத்து
combining_uyir_ezhuttu = Word(combining_uyir, exact=1) # புணரும் உயிரெழுத்து
# மெய்யெழுத்து
mei_ezhuttu = Word(mei, exact=1)
vallina_mei_ezhuttu = Word(vallina_mei, exact=1)
# ஆயுதம்
aaytha_ezhuttu = Word(aaytham, exact=1)
# உயிர்மெய் எழுத்து
kuril_uyir_mei_ezhuttu = Combine(mei_ezhuttu + Word(combining_kuril, exact=1))
nedil_uyir_mei_ezhuttu = Combine(mei_ezhuttu + Word(combining_nedil, exact=1))
uyir_mei_ezhuttu = Combine(mei_ezhuttu + combining_uyir_ezhuttu)
vallina_ugaram = Group(Combine(vallina_mei_ezhuttu + Word(u("ு"), exact=1)) + ZeroOrMore('#'))("வல்லின உகரம்")
vallina_ugaram.setParseAction(token_swap_agaram)

### அசை ###
# நேரசை
thani_kuril_ezhuttu = kuril_uyir_mei_ezhuttu | thani_kuril_uyir_ezhuttu # தனிக்குறில்
thani_nedil_ezhuttu = nedil_uyir_mei_ezhuttu | thani_nedil_uyir_ezhuttu # தனிநெடில்
kuril_otru = Combine(thani_kuril_ezhuttu + OneOrMore(mei_ezhuttu + NotAny(combining_uyir_ezhuttu))) # குறிலொற்று
nedil_otru = Combine(thani_nedil_ezhuttu + OneOrMore(mei_ezhuttu + NotAny(combining_uyir_ezhuttu))) # நெடிலொற்று
ner_asai = Group((nedil_otru | kuril_otru | thani_nedil_ezhuttu | (thani_kuril_ezhuttu + FollowedBy(space))) + ZeroOrMore('#'))("நேரசை") # hack: ZeroOrMore forces asai to become a pyparsing.Group rather than just a string
ner_asai.setParseAction(token_swap_agaram)

# நிரையசை
kuril_inai = Combine(thani_kuril_ezhuttu + thani_kuril_ezhuttu) # குறிலினை
kuril_nedil = Combine(thani_kuril_ezhuttu + thani_nedil_ezhuttu) # குறில் நெடில்
kuril_inai_otru = Combine(kuril_inai + OneOrMore(mei_ezhuttu + NotAny(combining_uyir_ezhuttu))) # குறிலினை ஒற்று
kuril_nedil_otru = Combine(kuril_nedil + OneOrMore(mei_ezhuttu + NotAny(combining_uyir_ezhuttu))) # குறில் நெடில் ஒற்று
nirai_asai = Group((kuril_nedil_otru | kuril_inai_otru | kuril_nedil | kuril_inai) + ZeroOrMore('#'))("நிரையசை") # hack: ZeroOrMore forces asai to become a pyparsing.Group rather than just a string
nirai_asai.setParseAction(token_swap_agaram)
#asai = (nirai_asai | ner_asai)("அசை")

### சீர் ###
## ஈரசைச்சீர்
# மாச்சீர்
te_maa = Group(ner_asai + ner_asai)("தேமா")
puli_maa = Group(nirai_asai + ner_asai)("புளிமா")
maa_cheer = ((puli_maa | te_maa) + FollowedBy(space))#("மாச்சீர்")
# விளச்சீர்
koo_vilam = Group(ner_asai + nirai_asai)("கூவிளம்")
karu_vilam = Group(nirai_asai + nirai_asai)("கருவிளம்")
vilam_cheer = ((karu_vilam | koo_vilam) + FollowedBy(space))#("விளச்சீர்")
eerasai_cheer = ((karu_vilam | puli_maa | koo_vilam | te_maa) + FollowedBy(space))#("ஈரசைச்சீர்")
#eerasai_cheer = (vilam_cheer | maa_cheer)("ஈரசைச்சீர்") #NOTE: Results in false grammar

## மூவசைச்சீர்
# காய்ச்சீர்
te_maa_kai = Group(ner_asai + ner_asai + ner_asai)("தேமாங்காய்")
puli_maa_kai = Group(nirai_asai + ner_asai + ner_asai)("புளிமாங்காய்")
karu_vilam_kai = Group(nirai_asai + nirai_asai + ner_asai)("கருவிளங்காய்")
koo_vilam_kai = Group(ner_asai + nirai_asai + ner_asai)("கூவிளங்காய்")
kai_cheer = ((karu_vilam_kai | puli_maa_kai | koo_vilam_kai |  te_maa_kai) + FollowedBy(space))#("காய்ச்சீர்")
# கனிச்சீர்
te_maa_kani = Group(ner_asai + ner_asai + nirai_asai)("தேமாங்கனி")
puli_maa_kani = Group(nirai_asai + ner_asai + nirai_asai)("புளிமாங்கனி")
karu_vilam_kani = Group(nirai_asai + nirai_asai + nirai_asai)("கருவிளங்கனி")
koo_vilam_kani = Group(ner_asai + nirai_asai + nirai_asai)("கூவிளங்கனி")
kani_cheer = ((karu_vilam_kani | puli_maa_kani | koo_vilam_kani | te_maa_kani) + FollowedBy(space))#("கனிச்சீர்")
moovasai_cheer = ((karu_vilam_kani | karu_vilam_kai | puli_maa_kani | puli_maa_kai | koo_vilam_kani | koo_vilam_kai | te_maa_kani | te_maa_kai) + FollowedBy(space))#("மூவசைச்சீர்")

## நாலசைச்சீர்
# பூச்சீர்
te_maa_than_poo = Group(ner_asai + ner_asai + ner_asai + ner_asai)("தேமாந்தண்பூ")
puli_maa_than_poo = Group(nirai_asai + ner_asai + ner_asai + ner_asai)("புளிமாந்தண்பூ")
karu_vilam_than_poo = Group(nirai_asai + nirai_asai + ner_asai + ner_asai)("கருவிளந்தண்பூ")
koo_vilam_than_poo = Group(ner_asai + nirai_asai + ner_asai + ner_asai)("கூவிளந்தண்பூ")
te_maa_narum_poo = Group(ner_asai + ner_asai + nirai_asai + ner_asai)("தேமாநறும்பூ")
puli_maa_narum_poo = Group(nirai_asai + ner_asai + nirai_asai + ner_asai)("புளிமாநறும்பூ")
karu_vilam_narum_poo = Group(nirai_asai + nirai_asai + nirai_asai + ner_asai)("கருவிளநறும்பூ")
koo_vilam_narum_poo = Group(ner_asai + nirai_asai + nirai_asai + ner_asai)("கூவிளநறும்பூ")
poo_cheer = ((karu_vilam_narum_poo | karu_vilam_than_poo | puli_maa_narum_poo | puli_maa_than_poo | koo_vilam_narum_poo | koo_vilam_than_poo | te_maa_narum_poo | te_maa_than_poo) + FollowedBy(space))#("பூச்சீர்")
# நிழற்சீர்
te_maa_than_nizhal = Group(ner_asai + ner_asai + ner_asai + nirai_asai)("தேமாந்தண்ணிழல்")
puli_maa_than_nizhal = Group(nirai_asai + ner_asai + ner_asai + nirai_asai)("புளிமாந்தண்ணிழல்")
karu_vilam_than_nizhal = Group(nirai_asai + nirai_asai + ner_asai + nirai_asai)("கருவிளந்தண்ணிழல்")
koo_vilam_than_nizhal = Group(ner_asai + nirai_asai + ner_asai + nirai_asai)("கூவிளந்தண்ணிழல்")
te_maa_narum_nizhal = Group(ner_asai + ner_asai + nirai_asai + nirai_asai)("தேமாநறுநிழல்")
puli_maa_narum_nizhal = Group(nirai_asai + ner_asai + nirai_asai + nirai_asai)("புளிமாநறுநிழல்")
karu_vilam_narum_nizhal = Group(nirai_asai + nirai_asai + nirai_asai + nirai_asai)("கருவிளநறுநிழல்")
koo_vilam_narum_nizhal = Group(ner_asai + nirai_asai + nirai_asai + nirai_asai)("கூவிளநறுநிழல்")
nizhal_cheer = ((karu_vilam_narum_nizhal | karu_vilam_than_nizhal | puli_maa_narum_nizhal | puli_maa_than_nizhal | koo_vilam_narum_nizhal | koo_vilam_than_nizhal | te_maa_narum_nizhal | te_maa_than_nizhal) + FollowedBy(space))#("நிழற்சீர்")
naalasai_cheer = ((karu_vilam_narum_nizhal | karu_vilam_narum_poo | karu_vilam_than_nizhal | karu_vilam_than_poo | puli_maa_narum_nizhal | puli_maa_narum_poo | puli_maa_than_nizhal |
puli_maa_than_poo | koo_vilam_narum_nizhal | koo_vilam_narum_poo | koo_vilam_than_nizhal | koo_vilam_than_poo | te_maa_narum_nizhal | te_maa_narum_poo | te_maa_than_nizhal | te_maa_than_poo) + FollowedBy(space))#("நாலசைச்சீர்")

## ஈற்றுச்சீர்
naal = Group(ner_asai + StringEnd())("நாள்")
malar = Group(nirai_asai + StringEnd())("மலர்")
kaasu = Group(ner_asai + vallina_ugaram + StringEnd())("காசு")
pirappu = Group(nirai_asai + vallina_ugaram + StringEnd())("பிறப்பு")
eetru_cheer = (pirappu | kaasu | malar | naal)#("ஈற்றுச்சீர்")

cheer = ((eetru_cheer | eerasai_cheer | moovasai_cheer | naalasai_cheer ) + Optional(Suppress(".,!-_?")))#("சீர்")

# அடி
adi = Group(OneOrMore(cheer + Suppress(Optional(White(" \t")))) + Suppress(Optional(White("\n"))))("அடி")

def generateXML(parse_results):
   from xml.dom.minidom import getDOMImplementation
   impl = getDOMImplementation()
   doc = impl.createDocument(None, "பா", None)
   top_element = doc.documentElement
   for adi in parse_results:
      n_adi = doc.createElement("அடி")
      for cheer in adi:
         n_cheer = doc.createElement("சீர்")
         for asai in cheer:
            n_asai = doc.createElement("அசை")
            a_asai_type = doc.createAttribute("வகை")
            a_asai_type.value = asai.getName()
            n_asai.setAttributeNode(a_asai_type)
            a_porul = doc.createAttribute("பொருள்")
            a_porul.value = ''.join(asai)
            n_asai.setAttributeNode(a_porul)
            n_cheer.appendChild(n_asai)
         a_cheer_type = doc.createAttribute("வகை")
         a_cheer_type.value = cheer.getName()
         n_cheer.setAttributeNode(a_cheer_type)
         n_adi.appendChild(n_cheer)
      top_element.appendChild(n_adi)
   return top_element.toprettyxml()

def analyzeVerse(instr):
   swp = swap_agaram(unicode(instr))
   parse_syntax = OneOrMore(adi).leaveWhitespace()
   try:
      result = parse_syntax.parseString(swp, parseAll=True)
      return generateXML(result)
   except Exception,e:
      return None

if __name__ == "__main__":
   str1 = u("தோடுடைய செவியன் விடையேறியோர் தூவெண் மதிசூடிக்\n" +
          "காடுடைய சுடலைப் பொடிபூசியென் னுள்ளங் கவர்கள்வன்\n" +
          "ஏடுடைய மலரான் முனைநாட்பணிந் தேத்த வருள்செய்த\n" +
          "பீடுடைய பிரமா புரமேவிய பெம்மா னிவனன்றே")
   str2 = u("அகர முதல எழுத்தெல்லாம் ஆதி\n" +
          "பகவன் முதற்றே உலகு")
   print analyzeVerse(str1)
   with open("sample.xml","w") as f:
      f.write(analyzeVerse(str2))
