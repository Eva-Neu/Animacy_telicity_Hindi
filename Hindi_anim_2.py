import sys 
import os 
import re 


# This script takes three lists:
#   - intransitive verbs 
#   - ergative-marked/animate nouns 
#   - non-DOM-marked/inanimate nouns 
#   (all based on Hindi_anim_1.py but edited manually)

# We then calculate for each intransitive the likelihood of it taking an animate or 
# inanimate argument, based on the Hindi-Urdu treebank (https://ltrc.iiit.ac.in/hutb_release/).


##################### PREP ####################################################################

# Read input files and convert into dictionary. Each sentence is a key,
# with identifying info (input file and sent ID) as its value.
def readfunction(x):
    sentdict = {}
    filename = os.path.splitext(x)[0]

    with open(x, encoding="utf8", errors='ignore') as f:
        postfile = f.read()
    sentlist = postfile.split('</Sentence>')
    sentlist = sentlist[:-1] # (The last item is empty because of splitting)

    for sent in sentlist: 
        preID = re.search(r"id='[\d]+'", sent)
        if preID: 
            ID = preID.group(0)
        sentdict[sent] = {filename : ID} 

    return sentdict

# Read input lists
def simple_readfunction(y):

    prefile = open(y)
    postfile = prefile.read()
    ls = postfile.split('\n')

    return ls 


############# AUXILIARY FUNCTIONS FROM HINDI_ANIM_1 FILE ############################################

# Find all VP labels in the sentence (VGF, VGF2...)
def vpcounter(k, ls, i):
        
    if 'VGF' + str(i) in k:
        ls.append('VGF' + str(i))
        i += 1
        vpcounter(k, ls, i)

    return k, ls, i

# Extract verbs out of VPs
def verbextractor(key, label):

    # First, find VPs
    verbcontext = re.search(r'\(\(.*?name=\'' + re.escape(label) + r'\'[^()]*\)\)', key)

    # In the VP, then find root
    if verbcontext:
        verb = re.search(fr"VM.*af='([^,]+)", verbcontext.group())

        if verb: 
            return verb.group(1)


###################### ANIMACY CALCULATOR ###################################################

# For each verb, count how many times it takes an erg or non-dom subject 
def counter(dict, vls, els, ndls, edict, nddict):

    # For each sent, find subject of each verb (verb type, not token), return as dict {verb: [subject1, subject2, ...]}
    def find_subs(file):

        verbs_with_subs = {}
        for sent in file:

            # Find all VP labels and k1 NPs in the sent 
            vplist_init = ['VGF']
            index = 2
            vps = vpcounter(sent, vplist_init, index)[1]
            subject_nps = re.findall(r'\(\((?:\s*NP[^\)]*drel=\'k1:[^\)]*,[^\)]*\')(?:[^\)]*)\)\)', sent)

            # Match VP labels and k1 NPs
            for np in subject_nps:
                for vp in vps:
                    if str(vp + "'") in np:

                        # Extract nouns and verbs from NPs and VPs
                        noun = re.search(r"(?:NN[CP]?|PRP|WC)[^\.]*?<fs[^\.]*name='([^']+)'", np)
                        if noun:
                            verb = verbextractor(sent, vp)

                            # Store nouns and verbs in dict  
                            if verb in verbs_with_subs.keys():
                                verbs_with_subs[verb].append(noun.group(1))
                            else: 
                                verbs_with_subs[verb] = [noun.group(1)]
                    
        return verbs_with_subs
    
    # For each verb type, count how often subject is in erg or non-dom list, respectively
    def check_subs(vwiths, ls1, ls2, ls3, dict1, dict2):


        # Loop through verbs and count how often subject is erg or non-DOM
        for verb in vwiths.keys(): # For each verb in the corpus
            if verb != None: # which isn't empty,
                if verb in ls1: # check if it is in our intransitive list.
                    for val in vwiths[verb]: # Then check for each of the subjects it takes
                        if val in ls2: # if it is in the ergative list
                            dict1[verb] += 1
                        elif val in ls3: # or the non-DOM list 
                            dict2[verb] += 1
                            # and add a count to the erg or non-DOM dict, respectively.

        return edict, nddict
    
    vsubdict = find_subs(dict)
    numbers = check_subs(vsubdict, vls, els, ndls, edict, nddict)

    return numbers 

###################### MAIN ##################################################################

def loop_directory(directory: str):

    erg_dict = {}
    nondom_dict = {}

    for verb in verblist: 
        erg_dict[verb] = 0
        nondom_dict[verb] = 0

    for path, folders, files in os.walk(directory):
            for file in files:
                file_directory = os.path.join(path, file)
                sents = readfunction(file_directory)

                # Calculate numbers 
                erg_subs, nondom_subs = counter(sents, verblist, erglist, nondomlist, erg_dict, nondom_dict)
                
    # Calculate percentage of verb tokens taking an erg subject 
    percentages = {}
    for key in verblist: 
        if nondom_subs[key] == 0:
            if erg_subs[key] == 0:
                percentages[key] = 'NA' # if none of the subjects of the verb appears in either list 
            else: percentages[key] = 1 # if the subjects are only on erglist 
        else:
            percentages[key] = erg_subs[key]/(nondom_subs[key]+erg_subs[key])

    # Save to output file
    output = open('anim_percents.txt', 'w')
    for key in percentages:
        output.write(str(key) + str('\t') + str(percentages[key]) + str('\t') + str(erg_dict[key] + nondom_dict[key]) + str('\n'))
    output.close()

if __name__ == "__main__":

    verblist = simple_readfunction(sys.argv[1])
    erglist = simple_readfunction(sys.argv[2])
    nondomlist = simple_readfunction(sys.argv[3])

    loop_directory('./HDTB/InterChunk/SSF/utf')
