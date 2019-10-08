from sqlalchemy import (String, Unicode, Integer, Boolean, Index,
                        ForeignKey, ForeignKeyConstraint, UniqueConstraint)

dicref_text = """
nelson_c - "Modern Reader's Japanese-English Character Dictionary",  
	edited by Andrew Nelson (now published as the "Classic" 
	Nelson).
nelson_n - "The New Nelson Japanese-English Character Dictionary", 
	edited by John Haig.
halpern_njecd - "New Japanese-English Character Dictionary", 
	edited by Jack Halpern.
halpern_kkd - "Kodansha Kanji Dictionary", (2nd Ed. of the NJECD)
	edited by Jack Halpern.
halpern_kkld - "Kanji Learners Dictionary" (Kodansha) edited by 
	Jack Halpern.
halpern_kkld_2ed - "Kanji Learners Dictionary" (Kodansha), 2nd edition
  (2013) edited by Jack Halpern.
heisig - "Remembering The  Kanji"  by  James Heisig.
heisig6 - "Remembering The  Kanji, Sixth Ed."  by  James Heisig.
gakken - "A  New Dictionary of Kanji Usage" (Gakken)
oneill_names - "Japanese Names", by P.G. O'Neill. 
oneill_kk - "Essential Kanji" by P.G. O'Neill.
moro - "Daikanwajiten" compiled by Morohashi. For some kanji two
	additional attributes are used: m_vol:  the volume of the
	dictionary in which the kanji is found, and m_page: the page
	number in the volume.
moro_vol - Volume of the dictionary in which the kanji is found.
moro_page - Page number in the volume.
henshall - "A Guide To Remembering Japanese Characters" by
	Kenneth G.  Henshall.
sh_kk - "Kanji and Kana" by Spahn and Hadamitzky.
sh_kk2 - "Kanji and Kana" by Spahn and Hadamitzky (2011 edition).
sakade - "A Guide To Reading and Writing Japanese" edited by
	Florence Sakade.
jf_cards - Japanese Kanji Flashcards, by Max Hodges and
      Tomoko Okazaki. (Series 1)
henshall3 - "A Guide To Reading and Writing Japanese" 3rd
      edition, edited by Henshall, Seeley and De Groot.
tutt_cards - Tuttle Kanji Cards, compiled by Alexander Kask.
crowley - "The Kanji Way to Japanese Language Power" by
	Dale Crowley.
kanji_in_context - "Kanji in Context" by Nishiguchi and Kono.
busy_people_volume - "Japanese For Busy People" vols I-III, published
      by the AJLT. The codes are the volume.chapter.
busy_people_chapter - See busy_people_volume.
kodansha_compact - the "Kodansha Compact Kanji Guide".
maniette - codes from Yves Maniette's "Les Kanjis dans la tete" French adaptation of Heisig.
"""

def extract_keys(text):
    return [line.split(' - ')[0]
            for line in text.replace('\t',' '*4).split('\n')
            if line and not line.startswith(' ')]

dicref_keys = extract_keys(dicref_text)

