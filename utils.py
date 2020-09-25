def get_genres(form):
    new_list=[]
    for i in form:
        if i[0] == 'genres':
            new_list.append(i[1])
            
    return new_list



# def get_genres(some_list):
#     result = {}
#     for k in some_list:
#         result.setdefault(k, []).append(some_list[k])

#     return result    