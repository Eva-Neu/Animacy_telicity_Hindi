import sys 
import os 
import re 


# This script extracts the following items from the Hindi treebank:
    # - Non-DOM-marked k2 arguments (strong predictor for inanimacy)
    # - Ergative-marked k1 arguments (strong predictor for animacy)
    # - Verbs with only a k1 argument (intransitives)

# The treebank is available here: https://ltrc.iiit.ac.in/hutb_release/
# The HDTB folder needs to be stored in same directory as this file. 


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

########################## NOUNS ###############################################################

# Find non-DOM k2 NPs, return dict (key: NP, value: identifying info)
def nondomfinder(dict):
    nondoms = {}

    for key in dict:
        findings = re.finditer(r'\(\((?:\s*NP[^\)]*drel=\'k2:[^\)]*,d,[^\)]*\')(?:[^\)]*)\)\)', key)
        for finding in findings:
            if 'PSP' not in finding.group(0):

                # Confound: check that the verb is not a passive (k2 arguments which otherwise would be DOM
                # often are not when promoted to subject under passivization)

                # Find the VP label of the k2 argument (VGF, VGF2...?) and find the line with Voice info for this VP           
                vplabel = re.search(r"(?<=drel='k2:)[^']+?(?=')", finding.group(0)) 
                voiceinfo = re.search(r"<fs[^\>]*name='" + re.escape(vplabel.group(0)) + r"'[^\>]*>", key)

                # Check if voicetype is passive; if not, add k2 argument to dict
                if "voicetype='passive'" not in voiceinfo.group(0): 
                    nondoms[finding.group(0)] = dict[key]
        
    return nondoms

# Find ergative NPs, return dict (key: NP, value: identifying info)
def ergfinder(dict):
    ergs = {}

    for key in dict:
        findings = re.finditer(r'\(\((?:\s*NP[^\)]*af=\'ने,psp[^\)]*)\)\)', key)
        for finding in findings: 
            ergs[finding.group(0)] = dict[key]

    return ergs 

# Extract nouns out of NPs, return dict (key: noun, value: identifying info)
def nounextracter(dict):
    nouns = {}

    for key in dict: 
        noun = re.search(r"NN[CP]?[^\.]*?<fs[^\.]*name='([^']+)'", key)
        if noun: 
            nouns[noun.group(1)] = dict[key]

    return nouns 

############################## VERBS #########################################################

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

# Find intransitive verbs, return dict (key: verb, value: identifying info)      
def intranfinder(dict):
    intrans = {}

    # Confound: verbs with a POF (complex predicates) are wrongly treated as intransitives 
    # since the treebank doesn't consider POFs arguments (very roughly, they are incorporated).

    # Check for each VGF if it has a POF; if yes, discard the label
    def pofchecker(k, ls):
        for l in ls: 
            pofvps = []
            pof = re.search(r"'pof:" + re.escape(l) + r"'", k)
            if pof:
                pofvps.append(l)
            ls = [item for item in ls if item not in pofvps]

        return ls  
    
    # For each VP, find all arguments associated with it 
    # and store them with their drel specifications
    def argcounter(k, vps):
        args = {}
        nps = re.findall(r"drel='k\w+:", k)
        
        for j in range(len(vps)):
            drels = []

            for np in nps:
                if np + str(vps[j]) + "'" in k:
                    drels.append(np)

            # If both verbs have a k1 arg, it will be listed twice for each,
            # hence we need to remove the duplicates      
            drels2 = list(set(drels)) 

            args[vps[j]] = drels2

        return args    
            
    for key in dict:

        # We first check VGF, then VGF2, then VGF3, etc. (There might be sentences 
        # without VGF but it wouldn't matter beause of how argcounter works.) 
        vplist_init = ['VGF']
        index = 2

        vplist_complete = vpcounter(key, vplist_init, index)[1] # list of VP labels for a single sent
        vplist_nopof = pofchecker(key, vplist_complete) # same list of VP labels but filtered for POF 
        vpsplusargs = argcounter(key, vplist_nopof) # dict of VP labels with arguments (key: VP label, value: args of VP)

        # Find VPs with only one k1 argument, then find corresponding verb
        # and store it in intrans dict with identifying info
        for vp in vpsplusargs:
            if len(vpsplusargs[vp]) == 1 and "drel='k1:" in vpsplusargs[vp]: 
                intrans[verbextractor(key, vp)] = dict[key]  

    return intrans


###################### MAIN ##################################################################

def loop_directory(directory: str):

    if len(sys.argv) != 1:
        print("I don't take any additional arguments.")

    else: 
        # Loop through folders and files 
        for path, folders, files in os.walk(directory):
            for file in files:
                file_directory = os.path.join(path, file)
                sents = readfunction(file_directory)

                # Find non-DOM and ergative nouns and intransitive verbs
                nondoms = nondomfinder(sents)
                nondomnouns = nounextracter(nondoms)
                ergs = ergfinder(sents)
                ergnouns = nounextracter(ergs)
                intrans = intranfinder(sents)

                ############## Store results 
                # All lists are stored twice, with and without identifying info. 
                
                # Open output files 
                # With identifying info 
                nondomNs_info = open("nondomNs_info.txt", "a")
                ergNs_info = open("ergNs_info.txt", "a")
                intranVs_info = open("intranVs_info.txt", "a")

                # Items only 
                nondomNs = open("nondomNs.txt", "a")
                ergNs = open("ergNs.txt", "a")
                intranVs = open("intranVs.txt", "a")

                # # Append to output files
                # # Non-DOM nouns  
                for key in nondomnouns:
                    nondomNs_info.write(str(key) + '\n' + str(nondomnouns[key]) + '\n\n')
                    nondomNs.write(str(key) + '\n')
      
                # # Ergative nouns 
                for key in ergnouns:
                    ergNs_info.write(str(key) + '\n' + str(ergnouns[key]) + '\n\n')
                    ergNs.write(str(key) + '\n')

                # Verbs 
                for key in intrans:
                    intranVs_info.write(str(key) + '\n' + str(intrans[key]) + '\n\n')
                    intranVs.write(str(key) + '\n')

                # Close output files 
                nondomNs_info.close()  
                ergNs_info.close() 
                intranVs_info.close()

                nondomNs.close()  
                ergNs.close() 
                intranVs.close()

if __name__ == "__main__":
    loop_directory('./HDTB/InterChunk/SSF/utf')

# NB: data will be appended to the files. To re-run, delete previous files.
