from test_app import db, Courses, RecommendationTable, RecommendationScoreTable
import pandas as pd
import numpy as np
from rake_nltk import Rake
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

db.create_all()

all_courses=Courses.query.all()
rows={}
for course in all_courses:
    course_categories=[]
    for category in course.categories:
        course_categories.append(category.name.lower().replace(' ',''))
    author=course.author.name.lower().replace(' ','')
    author=author.replace('.','')
    course_id=course.id
    course_title=course.title.lower()
    course_subtitle=course.subtitle.lower()
    course_data=[author,course_title,course_subtitle,*course_categories]
    course_data=' '.join(course_data)
    rows[course_id]=course_data
# print(rows)

# Apply rake
final_data={}
r=Rake()
for key,val in rows.items():
    r.extract_keywords_from_text(val)
    key_words_dict_scores = r.get_word_degrees()
    # filtered_keys=list(key_words_dict_scores.keys())
    filtered_keys=r.get_ranked_phrases()
    final_data[key]=' '.join(filtered_keys)
# print(final_data)

# Convert final_data into dataFrame
df=pd.DataFrame(final_data.items())
df.columns=['course_id','bow']
course_ids=np.array(list(df['course_id']))
print(course_ids)

count = CountVectorizer()
count_matrix = count.fit_transform(df['bow'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)
print(cosine_sim.shape)

# Test the recommender system
test=np.sort(cosine_sim[0])
idx_test=np.argsort(cosine_sim[0])
print(test,idx_test,idx_test[-6:-1][::-1],course_ids[0],course_ids[90])

## Loop over cosine similarity score and feed data into recommendation table
for idx,cs_data in enumerate(cosine_sim):
    sorted_data=np.sort(cs_data)
    sorted_idx=np.argsort(cs_data)
    print(sorted_data[-6:-1],sorted_idx[-6:-1])
    filtered_idx=sorted_idx[-6:-1][::-1]
    filtered_data=sorted_data[-6:-1][::-1]
    data_score={}
    data_score['course_id']=int(course_ids[idx])
    data_score['recom_score_id1']=filtered_data[0]
    data_score['recom_score_id2']=filtered_data[1]
    data_score['recom_score_id3']=filtered_data[2]
    data_score['recom_score_id4']=filtered_data[3]
    data_score['recom_score_id5']=filtered_data[4]
    data_score_to_db=RecommendationScoreTable(**data_score)
    db.session.add(data_score_to_db)
    # db.session.commit()
    selected_course_ids=course_ids[filtered_idx]
    print(idx,course_ids[idx],selected_course_ids)
    data={}
    data['course_id']=int(course_ids[idx])
    data['recom_course_id1']=int(selected_course_ids[0])
    data['recom_course_id2']=int(selected_course_ids[1])
    data['recom_course_id3']=int(selected_course_ids[2])
    data['recom_course_id4']=int(selected_course_ids[3])
    data['recom_course_id5']=int(selected_course_ids[4])
    data_to_db=RecommendationTable(**data)
    db.session.add(data_to_db)
    db.session.commit()
    print('Data inserted successfully')