from numpy import diagonal


def min_length_of_lists(list1, list2):
    if len(list1) > len(list2): return len(list2)
    else: return len(list1)

def differences_between_frames(frame1, frame2):
    difference_number = 0
    for idx in range(min_length_of_lists(frame1, frame2)):
        if frame1[idx].lower() != frame2[idx].lower():
            difference_number += 1
    return difference_number

def max_length_of_lists(list1, list2):
    if len(list1) > len(list2): return list1
    else: return list2

def diagonal_score(char1, char2):
    if char1 == char2:
        return 500
    else:
        return -500

def global_alignment(frame1, frame2, mismatching_character_score):
    string_frame1 = ''.join(frame1)
    string_frame2 = ''.join(frame2)

    Scoring = [[0 for repeat_j in range(len(string_frame2)+1)] for repeat_i in range(len(string_frame1)+1)]
    backtrack = [[0 for repeat_j in range(len(string_frame2)+1)] for repeat_i in range(len(string_frame1)+1)]

    for idx in range(1, len(string_frame1)+1):
        Scoring[idx][0] = idx*mismatching_character_score
    for idx in range(1, len(string_frame2)+1):
        Scoring[0][idx] = idx*mismatching_character_score
    
    for i in range(1, len(string_frame1)+1):
        for j in range(1, len(string_frame2)+1):
            scores = [Scoring[i-1][j] + mismatching_character_score, Scoring[i][j-1] + mismatching_character_score, Scoring[i-1][j-1] + diagonal_score(string_frame1[i-1], string_frame2[j-1])]
            Scoring[i][j] = max(scores)
            
            backtrack[i][j] = scores.index(Scoring[i][j])
    
    insert_indel = lambda word, i: word[:i] + '-' + word[i:]

    aligned_string_frame1, aligned_string_frame2 = string_frame1, string_frame2
    i,j = len(string_frame1), len(string_frame2)
    max_score = str(Scoring[i][j])

    while i*j != 0:
        if backtrack[i][j] == 0:
            i -= 1
            aligned_string_frame2 = insert_indel(aligned_string_frame2, j)
        elif backtrack[i][j] == 1:
            j -= 1
            aligned_string_frame1 = insert_indel(aligned_string_frame1, i)
        else:
            i -= 1
            j -= 1
    
    for _ in range(i):
        aligned_string_frame2 = insert_indel(aligned_string_frame2, 0)
    for _ in range(j):
        aligned_string_frame1 = insert_indel(aligned_string_frame1, 0)
    
    return max_score, aligned_string_frame1, aligned_string_frame2