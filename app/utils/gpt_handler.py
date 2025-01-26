import json
from openai import AsyncOpenAI
from app.config import settings


async def generate_keywords_and_category(video_data_list: list[dict]) -> dict:
    """
    동영상 데이터에서 카테고리와 키워드를 추출하는 함수.
    최대 50개의 동영상 데이터를 처리하며, OpenAI API를 이용해 분석을 수행함.

    Args:
        video_data_list (list[dict]): 동영상 메타데이터 리스트 (최대 50개).

    Returns:
        dict: 카테고리 비율 및 키워드가 포함된 JSON 데이터.
    """
    # 최대 50개의 동영상 데이터만 처리
    if len(video_data_list) > 50:
        video_data_list = video_data_list[:50]

    # 프롬프트 생성
    prompt = f"""
    You are an AI expert specializing in video content analysis. 
    Your task is to analyze the provided video dataset and generate meaningful, diverse insights. 
    Ensure that exactly **4 diverse categories** and their **balanced distribution ratios** are created, even if the dataset is heavily focused on a single topic.
    
    ### Objectives:
    1. **Generate 4 distinct categories**:
       - Always create 4 categories, regardless of dataset diversity.
       - Categories must reflect unique themes derived from the dataset.
       - If necessary, infer broad but meaningful topics to diversify categories (e.g., "음료 트렌드," "문화 및 역사," "소비자 리뷰," "트렌드 분석").
    
    2. **Provide 3 meaningful, generalized keywords** for each category:
       - Use **generalized terms** to summarize each category’s main idea.
       - Avoid overly specific or dataset-dependent terms (e.g., "테슬라 맥주" 대신 "고급 주류" 사용).
    
    3. **Calculate a balanced category distribution ratio**:
       - Distribute videos across all categories to ensure a balanced ratio.
       - Ensure the sum of all ratios equals 100%.
       - If the dataset heavily favors one theme, split it into **subcategories** to distribute videos evenly.
    
    4. **Prevent empty categories**:
       - All 4 categories must contain relevant videos or inferred topics.
       - If there’s no data for a category, infer a general category based on trends or related fields.
       
    5. **generate  board_name**
       - Generate board names based on the created keywords and categories.
       - The names are created by mixing adjectives and nouns.
       - The board name must always be a single, unique name.

    ### Output Format:
    Respond strictly in JSON format:
    ```json
    {{
        "category_ratio": [percentage1, percentage2, percentage3, percentage4],
        "keywords": {{
            "Category1": ["Keyword1", "Keyword2", "Keyword3"],
            "Category2": ["Keyword1", "Keyword2", "Keyword3"],
            "Category3": ["Keyword1", "Keyword2", "Keyword3"],
            "Category4": ["Keyword1", "Keyword2", "Keyword3"]
        }},
        "board_name": [board_name]
    }}
    
    ### Important Notes:
    - Categories must be meaningful and specific to the dataset themes.
    - Categories should be specific to the dataset.
    - Avoid placeholder names like "키워드1" or "카테고리1".
    - If a video overlaps multiple categories, assign it to the most relevant one.
    - Return exactly **4 categories** and **3 keywords per category**. No more, no less.
    - If the data is insufficient to generate meaningful categories, generate general topics based on the available data.
    - If a category contains no videos, ensure it is not included in the output ratio (adjust percentages accordingly).
    - Analyze data holistically, considering localizedTitle, localizedDescription, and tags as a combined context.
    - Ensure categories are balanced and diverse:
	    - Avoid overly specific categories like “칵테일 레시피” unless explicitly dominant in the dataset.
	- Focus on creating broader themes that encapsulate multiple related videos, such as “주류 문화” instead of “셀럽 술.”
	    - Adjust category ratios based on actual video content distribution.
	- Categories and keywords should be:
	    - Derived dynamically from the dataset.
	    - Relevant to themes inferred from localizedTitle, localizedDescription, and tags.
	    - Contextually generalized (e.g., use “고급 주류” instead of specific brand names like “테슬라 맥주”).
	- Example adjustments:
	    - If 70% of videos are related to alcohol, diversify categories into sub-themes like “음료 트렌드,” “셀럽 문화,” and “고급 주류 리뷰.”
	    - Ensure no category has a disproportionate share unless justified by dataset dominance.
    - Ensure no category or keywords are left empty.
    - Categories and keywords must align dynamically with dataset themes.
	- If the dataset is repetitive, infer nuanced themes to maximize diversity.
	- Verify that no placeholder names (e.g., “Keyword1” or “Category1”) appear in the output.
	- You must use KOREAN.


    ### Dataset: Below is the dataset you need to analyze:
    {json.dumps(video_data_list, ensure_ascii=False, indent=2)}
    
    ### Key Notes for Analysis:
    1.	Categories and keywords should generalize themes, especially for topics like alcohol or beverages. For instance:
	    - Replace specific product names (“로얄살루트”) with general terms like “위스키” or “주류.”
	    - Replace celebrity-specific keywords with broader themes like “셀럽 트렌드” or “주류 문화.”
	    - Avoid dataset-specific terms unless they are critical to the category.
	2.	Categories should be diverse and cover as many unique topics as possible within the dataset.
	3.	If the dataset contains overlapping content, make categories mutually exclusive to maximize diversity.
	4.	Analyze holistically across all metadata fields, including localizedTitle, localizedDescription, and tags.
	
	### Additional Notes:
    - If a video does not clearly fit into one of the 4 categories, infer the most appropriate category based on context.
	- If necessary, refine overlapping themes into broader but still meaningful categories.
    - Ensure no placeholders like “Keyword1” or “Category1” appear in the output.
	- Always verify that categories and keywords dynamically align with the dataset’s diversity and themes.
	- If the dataset is highly repetitive, extract nuanced themes from metadata to create broader categories.
    """

    # OpenAI API 클라이언트 생성
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        # OpenAI API 호출
        response = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        # 응답 데이터 로깅
        response_content = response.choices[0].message.content.strip()
        print(f"GPT 응답 데이터: {response_content}")  # 디버깅용 로그

        # JSON 시작 위치 확인 및 추출
        json_start = response_content.find("{")
        json_end = response_content.rfind("}")
        if json_start == -1 or json_end == -1:
            raise ValueError("JSON 형식의 응답을 찾을 수 없습니다.")

        # JSON 부분만 파싱
        json_string = response_content[json_start:json_end + 1]
        output_data = json.loads(json_string)

        # 카테고리와 키워드 검증
        if (
            "category_ratio" not in output_data
            or "keywords" not in output_data
            or len(output_data["category_ratio"]) != 4
            or len(output_data["keywords"]) != 4
        ):
            raise ValueError("응답 데이터 형식이 올바르지 않습니다.")

        return output_data

    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류 발생: {str(e)}")  # 디버깅용 로그
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}. 응답 데이터: {response_content}")
    except Exception as e:
        print(f"GPT 요청 실패: {str(e)}")  # 디버깅용 로그
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")


async def regenerate_keywords_for_specific_category(
    category_name: str, current_keywords: dict, video_data_list: list[dict]
) -> dict:
    """
    특정 카테고리의 키워드를 재생성합니다. 카테고리명은 유지하고 키워드만 변경됩니다.

    Args:
        category_name (str): 수정할 카테고리 이름.
        current_keywords (dict): 현재 보드의 키워드 데이터.
        video_data_list (list[dict]): 동영상 메타데이터 리스트.

    Returns:
        dict: 변경된 키워드를 포함한 전체 카테고리 데이터.
    """
    # 프롬프트 생성
    prompt = f"""
    You are an AI specializing in video content analysis. Your task is to update the keywords for a specific category 
    based on the provided video dataset. The current category and its keywords are:

    Category: {category_name}
    Current Keywords: {current_keywords}

    ### Objectives:
    1. Generate **3 new keywords** for the provided category based on the dataset.
    2. Avoid duplicating the current keywords. Ensure all keywords are unique.
    3. Analyze the dataset to infer new insights and generate diverse, meaningful keywords.
    4. Keywords should be contextually relevant and derived from the dataset’s `tags`, `localizedTitle`, and `localizedDescription`.

    ### Dataset:
    Below is the dataset you need to analyze:
    {json.dumps(video_data_list, ensure_ascii=False, indent=2)}

    ### Output Format:
    Respond strictly in JSON format:
    ```json
    {{
        "new_keywords": ["Keyword1", "Keyword2", "Keyword3"]
    }}
    ```

    ### Notes:
    - New keywords must be in **Korean**.
    - Keywords should reflect the main themes or insights derived from the dataset.
    - Avoid overly specific or repetitive terms.
    - Ensure the output contains exactly 3 keywords.
    """

    try:
        # OpenAI API 클라이언트 생성
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # GPT 호출
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )

        # 응답 데이터 파싱
        response_content = response.choices[0].message.content.strip()
        json_start = response_content.find("{")
        json_end = response_content.rfind("}")
        if json_start == -1 or json_end == -1:
            raise ValueError("JSON 형식의 응답을 찾을 수 없습니다.")

        # JSON 데이터 파싱
        json_string = response_content[json_start:json_end + 1]
        output_data = json.loads(json_string)

        # 새 키워드 추출
        new_keywords = output_data.get("new_keywords", [])
        if not new_keywords or len(new_keywords) != 3:
            raise ValueError("생성된 키워드 데이터가 올바르지 않습니다.")

        print(f"[DEBUG]: new keywords: {new_keywords}")
        return {
            "category_name": category_name,
            "new_keywords": new_keywords,
        }

    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류 발생: {str(e)}")
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        print(f"GPT 요청 실패: {str(e)}")
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")


async def match_board_ratio(board_sum_list: list):
    # 두 board_id를 프롬프트에 전달
    prompt = f"""
    #Instruction
    You are a keyword similarity analysis expert. You need to receive the keyword lists of two users, 
    calculate the similarity, and provide an analysis of the results. Calculate the similarity based on
    cosine similarity while reflecting the given weights for the conditions to derive the final similarity score.
    
    #Analysis Method
    1.The input format is as follows: “keywords”: {{"category1":["keywords1",…..],"category2":[..]..}}.
    2.Ignore the outermost 'keywords' in the received JSON.
    3.Gather all keywords(keyword1, keyword2, and keyword3....) from within the 'category' to create the user1_keywords
      list. At this point, user1_keywords refers to the keywords of board1. Similarly, create the user2_keywords list.
    4.Gather only the categories from board1 to create the 'user 1's categories' list. 
      Similarly create the 'user 2's categories'. 
    5.Compare the keyword lists of the two users.
    6.Evaluate the similarity for each keyword pair according to the following criteria:
        -Exact match (Weight: 0.25)
        -Semantic similarity (Weight: 0.23)
        -Hierarchical relationship (Weight: 0.20)
        -Industrial relationship (Weight: 0.20)
        -Functional similarity (Weight: 0.10)
        -Synonymous relationship (Weight: 0.10)
        -Technical relevance (Weight: 0.10)
    7.Calculate similarity scores based on each criterion and apply the weights.
    8.Sum all the scores to derive the final similarity score.
    9.Collect the overlapping elements from both users' keyword lists to create match_keywords.

    #constraints
    "Exclude categories from calculations and outputs."
    "All calculation results must be rounded to the third decimal place."
    "Convert the calculation results to percentages."
    "Strictly apply the given criteria when assessing the similarity between keywords."
    "Avoid duplicate calculations, and evaluate each keyword pair only once."
    "Present the results in the specified JSON format."    
    
    #Notes
    "Consider the context and meaning of the keywords when determining similarity."
    "Evaluate relevance by reflecting industry and technological trends."
    "Maintain consistency and accuracy in the results."
    "In the input, the term "keywords" must be ignored."

    # Dataset: Below is the dataset you need to analyze:
    {json.dumps(board_sum_list, ensure_ascii=False, indent=2)}
    
    # Output Format:
    {{ 
        "result": 
        {{ 
            "user1_category": [user 1's categories],
            "user1_keywords": [user 1's keywords excluding matching keywords.],
            "user2_category": [user 2's categories],            
            "user2_keywords": [user 2's keywords excluding matching keywords.], 
            "match_keywords": [matching keywords], 
            "similarity_score": [Final similarity score] 
        }} 
    }}
    """

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")
