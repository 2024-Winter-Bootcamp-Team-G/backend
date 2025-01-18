import json
from openai import AsyncOpenAI
from app.config import settings


async def generate_keywords_and_category(video_data_list: list[dict]) -> dict:
    # 여러 video_id의 데이터를 선택해 프롬프트로 전달
    prompt = f"""
    Below is a variety of videos selected. The use of each field is as follows::
    1. tags and category ID (cate) and category ID (cate) is used when extract categories.
    2. Title (localized Title) and description (localizedDes) is used when extracting keywords.

    Analysis of data:
    - Generate the name of each category and 3 related keywords in Korean.
    - Calculates the ratio of each category based on all data.

    동영상 데이터:
    {json.dumps(video_data_list, ensure_ascii=False, indent=2)}

    출력 형식:
    {{
      "category_ratio": [25, 25, 30, 20],
      "keywords": {{
          "category1": ["키워드1", "키워드2", "키워드3"],
          "category2": ["키워드1", "키워드2", "키워드3"],
          "category3": ["키워드1", "키워드2", "키워드3"],
          "category4": ["키워드1", "키워드2", "키워드3"]
      }}
    }}
    """
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")


async def match_board_ratio(board_sum_list: list):
    # 여러 video_id의 데이터를 선택해 프롬프트로 전달
    prompt = f"""
    #Instruction
    You are a YouTube Algorithm Expert. Your role is to analyze the keywords provided in two datasets, calculate the 
    similarity rate between the two datasets, and provide an analysis.
    
    #Constraints
    1.Each dataset contains exactly 12 keywords, with a total of 24 keywords provided.
    2.The calculation method must use cosine similarity.
    3.Calculation steps:
      a. Assess the similarity of the keywords and assign weight values based on the criteria.
      b. Apply the weight values to calculate the cosine similarity.
      c. Convert the resulting cosine similarity calculation into a percentage and include this value in the final JSON
         output.
    4.Similarity criteria and weights:
     Exact Match: Identical keywords
      -Weight 0.25
     Semantic Similarity: Keywords belonging to the same category
      -Weight 0.23
     Hierarchical Relationship: One keyword is a sub-concept of another keyword
      -Weight 0.2
     Industry Relationship: Keywords from the same industry or field
      -Weight 0.2
     Functional Similarity: Keywords with similar purposes or functions
     -Weight 0.1
     Synonym Relationship: Keywords with the same meaning but different words
      -Weight 0.1
     Technological Relation: Keywords closely related in terms of technology
      -Weight 0.1
     The similarity score will account for the semantic relationships between keywords, trend relevance, search
     frequency, and other factors.
    
    #Notes
    Carefully analyze the keywords provided and evaluate their similarity based on the given criteria.
    Ensure that the result is presented in the specified JSON format.

    

    키워드 데이터:
    {json.dumps(board_sum_list, ensure_ascii=False, indent=2)}

    출력 형식:
    {{
        "result": {{
            "user1_keywords": [keywords1, keywords2, keywords3, keywords4] ,
            "user2_keywords": [keywords2, keywords5, keywords6, keywords4] ,
            "match_keywords": [keywords2, keywords4],
            "total_match_rate":[25.6]
    }}
    """
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")
