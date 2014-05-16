import json as pyjson
from datetime import datetime
import struct
import os
import argparse, textwrap

# 0: Input file path relative to dev folder
# 1: Output file path relative to include folder
# 2: Name of variable
values = [
    ('all_fluids.json','all_fluids_JSON.h','all_fluids_JSON'),
    ('mixtures/mixture_excess_term.json', 'mixture_excess_term_JSON.h', 'mixture_excess_term_JSON'),
    ('mixtures/mixture_reducing_parameters.json', 'mixture_reducing_parameters_JSON.h', 'mixture_reducing_parameters_JSON')
]

def TO_CPP(root_dir):
    def to_chunks(l, n):
        if n<1:
            n=1
        return [l[i:i+n] for i in range(0, len(l), n)]
    
    # Normalise path name
    root_dir = os.path.normpath(root_dir)
    
    # First we package up the JSON files
    import package_json
    package_json.package_json(root_dir)
    
    for infile,outfile,variable in values:
        
        json = open(os.path.join(root_dir,'dev',infile),'r').read()
        
        # convert each character to hex and add a terminating NULL character to end the 
        # string, join into a comma separated string
        h = [hex(struct.unpack("b",b)[0]) for b in json] + ['0x00']
        
        # Break up the file into lines of 16 hex characters
        chunks = to_chunks(h, 16)
        
        # Put the lines back together again
        # The chunks are joined together with commas, and then EOL are used to join the rest
        hex_string = ',\n'.join([', '.join(chunk) for chunk in chunks])
        
        # Generate the output string
        output  = '// File generated by the script dev/JSON_to_CPP.py on '+ str(datetime.now()) + '\n\n'
        output += '// JSON file encoded in binary form\n'
        output += 'const unsigned char '+variable+'_binary[] = {\n' + hex_string + '\n};'+'\n\n'
        output += '// Combined into a single std::string \n'
        output += 'std::string {v:s}({v:s}_binary, {v:s}_binary + sizeof({v:s}_binary)/sizeof({v:s}_binary[0]));'.format(v = variable)
        
        f = open(os.path.join(root_dir,'include',outfile), 'w')
        f.write(output)
        f.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description=textwrap.dedent("""CoolProp
      This program converts the JSON files from dev/fluid etc
      to header files. It is necessary to give this program the
      value for --path, this is the root directory where
      dev/ can be found.""")
    )
                       
    parser.add_argument('--path', required=False,
                        help='Location of the root folder',
                        default=None)
                        
    args = parser.parse_args()

    TO_CPP(args.path)