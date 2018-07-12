"""
Module to reduce the number of unique chords by accorpating identical chords expressed in different ways, or similar
chords (stemming)
"""

import re

not_recon = []

# A regular expression for a chord
chord_regexp = "^([A-H]|[ACDFG]#|[ABDEGH]b)(major|Major|m|-|min|minor|Min)?([5679]|11)?" \
               "(sus|sus7|Sus|add9|dim|Maj7|maj7|maj9|Maj9|aug|Aug)?$"


def standardize_chord(ch, verbose=False):
    
    # This function recognizes the chords and perform some stemming to
    # reduce the number of unique chords we need to process
    
    # Remove parenthesis (sometimes A7 is written A(7), for example)
    nch = ch.replace("(", "").replace(")", "")

    # A slash cord needs to be split in two on the slash.
    # For example A/B ("A on B") can be split in two, the two
    # chords recognized, and then re-merged
    chords = nch.split("/")
        
    new_chords = []

    for this_ch in chords:

        # Manual tricks:
        # The first letter should be upper case
        # so c# -> C#
        lc = list(this_ch)
        lc[0] = lc[0].upper()
        this_ch = "".join(lc)

        # The # or b must go second, so that Am# becomes A#m
        for alter in ['#', 'b']:

            lc = list(this_ch)

            if alter in lc:

                idx = lc.index(alter)

                lc.insert(1, alter)
                lc.pop(idx + 1)
                this_ch = "".join(lc)
                
        # Remove the 2, so A2 becomes A, Asus42 -> Asus4
        # and so on
        this_ch = this_ch.replace("2", "")
        # Remove 13, so A13 becomes A
        this_ch = this_ch.replace("13", "")
        # Same for 3
        this_ch = this_ch.replace("3", "")

        # "sus4" -> "sus", "sus42" -> "sus"
        this_ch = re.sub("(sus4|sus42|sus)", "sus", this_ch)
        
        this_ch = this_ch.replace("7+", "maj7")
        # 7M -> maj7
        this_ch = this_ch.replace("7M", "maj7")
        # D+ -> Daug
        this_ch = re.sub("^([A-H])\+$", '\g<1>aug', this_ch)
        # D4 -> D
        this_ch = re.sub("^([A-H]([#|b])?)4$", '\g<1>', this_ch)
        # G7-9 -> G7
        this_ch = this_ch.replace('7-9', '7')
        # G79 -> G7
        this_ch = this_ch.replace('79', '7')
        # G7-5 -> G7
        this_ch = this_ch.replace('7-5', '7')
        # G75 -> G7
        this_ch = this_ch.replace('75', '7')
        # Fm13 -> Fm
        this_ch = this_ch.replace("m13", "m")
        # dim7 -> dim
        this_ch = this_ch.replace("dim7", "dim")
        # B# -> C (B sharp IS C, even though depending on the key
        # it migth be more appropriate to write it as B#)
        this_ch = this_ch.replace("B#", "C")
        this_ch = this_ch.replace("H#", "C")
        this_ch = this_ch.replace("Cb", "B")
        # Db -> C#
        this_ch = this_ch.replace("Db", "C#")
        # D# -> Eb
        this_ch = this_ch.replace("D#", "Eb")
        # Same for E# -> F and Fb -> E
        this_ch = this_ch.replace("E#", "F")
        this_ch = this_ch.replace("Fb", "E")
        # Gb -> F#
        this_ch = this_ch.replace("Gb", "F#")
        # Ab -> G#
        this_ch = this_ch.replace("Ab", "G#")
        # A# -> Bb
        this_ch = this_ch.replace("A#", "Bb") 
        
        # If there is maj, but not for example maj7, then remove it
        # so Fmaj -> F, but Fmaj7 -> Fmaj7
        this_ch = re.sub("^([A-H]|[ACDFG]#|[ABDEGH]b)maj$", "\g<1>", this_ch)
        
        # Same for M, so FM -> F but FM7 -> FM7
        this_ch = re.sub("^([A-H]|[ACDFG]#|[ABDEGH]b)M$", "\g<1>", this_ch)
        # FM7 -> Fmaj7
        this_ch = re.sub("^([A-H]|[ACDFG]#|[ABDEGH]b)M7$", "\g<1>maj7", this_ch)
        
        # B7# -> C7
        this_ch = re.sub("^B([0-9]?)#", 'C\g<1>', this_ch)
        # A7m -> Am7
        this_ch = re.sub("^([A-H])([0-9]*)?m", "\g<1>m\g<2>", this_ch)

        # Bb7m -> Bbm7
        this_ch = re.sub("([0-9])m", "m\g<1>", this_ch)
                
        tokens = re.match(chord_regexp, this_ch)
                
        if tokens is None:

            if this_ch not in not_recon:

                if verbose:
                    
                    print("%s not recognized" % ch)

                not_recon.append(this_ch)

            return None

        else:

            root, major_or_minor, qualif, susp = tokens.groups()

            # In some countries in Europe, B is called H
            if 'H' in root:

                root = root.replace("H", 'B')

            if major_or_minor in ['major', 'Major'] or major_or_minor is None:

                major_or_minor = ''

            elif major_or_minor.lower() in ['m', '-', 'min']:

                major_or_minor = 'm'

            if qualif is None:

                qualif = ''

            else:

                # Of the various 5/6/7/9/11 let's keep just the seventh
                if qualif != '7':

                    qualif = ''

            if susp is None:

                susp = ''

            new_ch = root + major_or_minor + qualif + susp.lower()

            new_chords.append(new_ch)

    return "/".join(new_chords)


# Clean up corpus. 
def stem(chord_sequence):
    """
    Recognizes and standardize the chords contained in the sequence given as input

    :param chord_sequence: string containing a sequence of chords
    :return: a string where each chord is replaced by its standardized version
    """

    # Transform the string to a list of chords
    chord_sequence = chord_sequence.replace("  ", " ").strip()
    input_list = chord_sequence.split()
    
    # Standardize chords, i.e., transform equivalent chords so that
    # they will be recognized as the same chord. I will also simplify
    # them to reduce the total number of chords we need to consider
    cleaned = []
    
    for i, chord in enumerate(input_list):
        
        standardized = standardize_chord(chord)
        
        if standardized == '':
            
            raise RuntimeError("Failed to process chord %s" % chord)
        
        if standardized is None:
            return None
        
        if i > 0 and standardized == cleaned[-1]:
            
            # This chord is the same as the previous, we skip it
            # so the final sequence will have subsequent chords
            # removed
            continue
        
        else:
        
            cleaned.append(standardized)
    
    return " ".join(cleaned)


def test():

    tests = ['F#sus7', 'A2', 'am#', 'a#m', 'am#', 
               'abm', 'amb', 'Asus42', 'asus42', 
               'A3', 'A13', 'f7+', 'FM', 'F7M',
               'D+', 'Daug', 'D4', 'G7-9', 'G79', 'G7', 'G7-5', 'G75',
               'Fm13', 'Fm', 'Fdim7', 'Cdim', 
               'B#', 'C', 'Cb', 'Fb', 'E#', 'FM7', 
               'B7#', 'Cb7', 'Fb7', 'E#7',
               'a7m', 'C/B', 'A/B#', 'C79',
               'Ab79', 'D#m75', 'DMin', 'Fmaj79',
               'A#', 'Bb',
               'C#', 'Db', 'D#', 'Eb', 
               'E#', 'F', 'F#', 'Gb', 'G#', 
               'Ab', 'A#', 'Bb',
               'A#m', 'Bbm',
               'C#m', 'Dbm', 'D#m', 'Ebm', 
               'E#m', 'Fm', 'F#m', 'Gbm', 'G#m', 
               'Abm', 'A#m', 'Bbm', 'H', 'Hb7',
               'E#m7', 'Ama7', 'H#', 'Bb7m', 'Bbm7', 'H#m7', "Bsus2"]
    
    for ch in tests:
        
        print("%10s -> %10s" % (ch, standardize_chord(ch)))
    
    stem(" ".join(tests))
