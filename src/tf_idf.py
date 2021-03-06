import ast
import math
"""

This function will convert tf scores in the index 'merge3.txt' to tf-idf scores.

Writes to 'final_index.txt'

"""

def calculate_tf_idf(tf: int, N: int, df: int):
    ''' 
    df = len of postings 
    '''
    result = (1 + math.log10(tf)) * (math.log10(N/df))
    return result

def compute_tf_idf(N: int):
    temp_index = open('index/temp_index.txt','w')
    with open('merges/merge3.txt','r') as merge3:
        curr_region = '0'
        print('Computing tf-idfs for tokens starting with: {}'.format(curr_region))
        while True:
            try:
                new_postings = {}
                line = ast.literal_eval(merge3.readline())
                token = line[0]
                
                # Print current progress of what region of tokens are getting their posting lists changed
                if curr_region != str(token[0]):
                    curr_region = str(token[0])
                    print('Computing tf-idfs for tokens starting with: {}'.format(curr_region))

                postings = dict(line[1]) # dict
                for doc, tf in postings.items():
                    df = len(postings)
                    new_postings[doc] = calculate_tf_idf(tf, N, df)
                new_tuple = (token, new_postings)
                temp_index.write(str(new_tuple)+'\n')
            except SyntaxError:
                break


# if __name__ == '__main__':
#     print('Computing tf-idf scores in index...')
#     compute_tf_idf(55393)
#     print('Done.')