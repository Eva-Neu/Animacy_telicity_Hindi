import sys 
import os 
import re 


# This script calculates the rate at which different intransitive verbs combine with different light verbs,
# based on the Hindi-Urdu treebank (https://ltrc.iiit.ac.in/hutb_release/). 

# Focus is on the light verbs 'आ' ('come') and 'जा' ('go') as well as 'दे' ('give') and 'ले' ('take'). 
# For each verb, we calculate how often it appears with a light verb from the two groups. 


##################### PREP ####################################################################

# Read input files and convert into dictionary. Each sentence is a key,
# with identifying info (input file and sent ID) as its value.
def readfunction(x):
    sentdict = {}
    filename = os.path.splitext(x)[0]

    with open(x, encoding="utf8", errors='ignore') as f:
        postfile = f.read()
    sentlist = postfile.split('</Sentence>')
    sentlist = sentlist[:-1] # The last item is empty because of splitting

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

############################## LIGHT VERBS #########################################################        

light_verbs = ['आ', 'बैठ', 'चल', 'छोड़', 'डाल', 'दे', 'जा', 'ले', 'मार', 'पड़़']

'''

A आ come
bET बैठ sit
cal  चल walk
Cod  छोड़ leave.behind
dAl डाल put
de दे give
jA जा go
le ले take
mAr मार hit
pad पड़़ fall

'''

def get_light_verbs(sent):

    # Find all VPs
    vps = []
    matches = re.findall('\(\((?:\t)VG(?:|N)F[^\)]+\)\)', sent)
    for match in matches:
        vps.append(match)

    # Find only those which contain a bare root and a light verb 
    # Return list of tuples (VP, light verb)
    light_vps = []
    for vp in vps:
        good_vps = re.search(r"v,any,any,any,,0,0'[^\n]*\n[^\n]*(?:आ|बैठ|चल|छोड़|डाल|दे|जा|ले|मार|पड़़)", vp)
        if good_vps:
                for lv in light_verbs:
                    if lv in vp:
                        light_vps.append((vp, lv))

    # Extract the verb root and return list of tuples (root, light verb)
    light_vs = []
    for t1, t2 in light_vps:
        verb = re.search(r"v,any,any,any,,0,0'.*name='([^']+)'", t1)
        if verb:
            if verb.group(1) != t2:
                light_vs.append((verb.group(1), t2))

    return light_vs 


###################### MAIN ##################################################################

def loop_directory(directory: str):

    if len(sys.argv) != 2:
        print("I need a list with intransitive verbs.")

    else: 
        # Loop through folders and files  
        lights = {}
        for path, folders, files in os.walk(directory):
            for file in files:
                file_directory = os.path.join(path, file)
                sents = readfunction(file_directory)

                # Find pairs of verbs and light verbs and how often they occur 
                for sent in sents:
                    outputs = get_light_verbs(sent)
                    for output in outputs:
                        if output != [] and output[0] in intrans:
                            if output in list(lights.keys()):
                                lights[output] += 1
                            else:
                                lights[output] = 1
        
        # Rearrange results vol. I: for each verb, list how many times each light verb occurs 
        counts = {}
        for key in lights:
            if key[0] in counts.keys():
                counts[key[0]].append((key[1], lights[key]))
            else:
                counts[key[0]] = [(key[1], lights[key])]

        # Rearrange results vol. II: for each verb, compute percentage of come/go and give/take light verbs 
        percents = {}
        for verb in counts:
            come_go = 0
            give_take = 0
            for k, v in counts[verb]:
                if k == 'आ' or k == 'जा':
                    come_go += v 
                elif k == 'दे' or k == 'ले':
                    give_take += v 
            
            percents[verb] = (come_go, give_take)
                
        # Save results to output file 
        output_counts = open('tel_counts', 'w')
        for key in counts:
            output_counts.write(str(key) + '\t')
            for item in counts[key]:
                output_counts.write(str(item) + '\t')
            output_counts.write('\n')
        output_counts.close()

        output_percents = open('tel_percents', 'w')
        for key in percents:
            output_percents.write(str(key) + ('\t') + str(percents[key][0]) + '\t' + str(percents[key][1]) + '\t' + str(percents[key][0] + percents[key][1]) + '\n')
        output_percents.close()

if __name__ == "__main__":
    intrans = simple_readfunction(sys.argv[1])
    loop_directory('./HDTB/InterChunk/SSF/utf')
