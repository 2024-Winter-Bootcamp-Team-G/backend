import json
from openai import OpenAI, AsyncOpenAI
from app.config import settings


def generate_keywords_and_category(video_data_list: list[dict]) -> dict:
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

    # OpenAI API 클라이언트 생성 (동기 방식)
    client = OpenAI(api_key=settings.openai_api_key)

    try:
        # OpenAI API 호출 (동기 방식)
        response = client.chat.completions.create(
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


async def match_board_ratio(board1_keywords: dict, board2_keywords: dict) -> dict:
    """
    두 사용자의 보드 데이터를 비교하여 카테고리 재분류, 카테고리 비율 계산, 그리고 유사도 계산을 수행.

    Args:
        board1_keywords (dict): 유저 1의 보드 키워드 데이터.
        board2_keywords (dict): 유저 2의 보드 키워드 데이터.

    Returns:
        dict: 유저 1/2의 여집합 키워드, 새로 분류된 카테고리, 카테고리 비율, 유사도 결과를 포함한 JSON 데이터.
    """
    # 프롬프트 생성
    prompt = f"""
    You are an AI specializing in semantic analysis and interest comparison between users. 
    Your task is to analyze two users' keyword datasets, identify similarities and differences, 
    and categorize their interests into broad, fun, and casual categories to make the comparison engaging.

    # Objectives:
    1. **Keyword Analysis**:
        - Identify shared keywords (`match_keywords`) between the two datasets.
        - Exclude `match_keywords` from each user's unique keyword list (`user1_keywords`, `user2_keywords`).
        - Ensure `user1_keywords` and `user2_keywords` only contain keywords that do not overlap (completely unique to each user).
    2. **Category Generation**:
        - Create **8 broad, fun, and engaging categories**.
        - Write categories in **Korean** to make the output locally relevant and relatable.
        - Categories should be broad yet meaningful and avoid technical or overly specific themes.
        - **Do not include the keywords within the categories** in the output. Only provide category names as an array.
    3. **Category Ratios**:
        - Calculate the percentage distribution of keywords across the 8 categories for each user.
        - Ratios must sum up to 100% for each user and be rounded to **two decimal places**.
        - Adjust ratios to ensure a balanced and visually engaging comparison.
    4. **Similarity Score**:
        - Calculate an overall similarity score using **cosine similarity** between the two users' categories.
        - Dynamically adjust the score to ensure it remains engaging but realistic (e.g., avoid very low or very high scores).
        - Present the similarity score in **percentage format with two decimal places**.

    # Input Data:
    - User 1 Keywords: A list of keywords associated with User 1's interests.
    {json.dumps(board1_keywords, ensure_ascii=False, indent=2)}

    - User 2 Keywords: A list of keywords associated with User 2's interests.
    {json.dumps(board2_keywords, ensure_ascii=False, indent=2)}

    # Output Format:
    Respond **only** in the following JSON format:
    ```json
    {{
        "user1_keywords": ["UniqueKeyword1", "UniqueKeyword2", ..., "UniqueKeywordN"],
        "user2_keywords": ["UniqueKeyword1", "UniqueKeyword2", ..., "UniqueKeywordN"],
        "match_keywords": ["MatchingKeyword1", "MatchingKeyword2", ..., "MatchingKeywordN"],
        "new_categories": ["Category1", "Category2", ..., "Category8""],
        "user1_category_ratio": [Percentage1, Percentage2, ..., Percentage8],
        "user2_category_ratio": [Percentage1, Percentage2, ..., Percentage8],
        "similarity_score": "Final similarity score in percentage (e.g., 78.45)"
    }}

    # Rules:
    1. Categories should be broad, engaging, and relatable, reflecting casual everyday interests (e.g., "엔터테인먼트," "라이프스타일").
    2. Use "match_keywords" to capture shared or semantically similar interests. Keywords that are loosely related or contextually overlapping should also be considered matches.
    3. Adjust the similarity score sensitivity to ensure it reflects casual overlaps. Ensure scores are not overly strict or too low (e.g., aim for a minimum of 50% if users share overlapping interests).
    4. Provide **only non-overlapping keywords** in "user1_keywords" and "user2_keywords." Exclude any keywords listed in "match_keywords" to ensure unique representation.
    5. Use **cosine similarity** for comparison but apply leniency to better account for casual and approximate similarities in user preferences.
    6. Exclude political, controversial, extreme, or negative terms. Replace them with neutral, inclusive, or positive alternatives to maintain a lighthearted and enjoyable tone.
    7. All categories must be written in **Korean** and must reflect localized, relatable interests to appeal to users.
    8. Broad categories should prioritize fun, inclusive, and casual themes. Examples include "여행과 모험" or "일상과 라이프스타일."
    9. Provide a fun, lighthearted comparison experience that fosters curiosity and engagement between users.

    # Additional Notes:
    - Categories must be **mutually exclusive** to avoid overlaps and maximize thematic diversity.
    - If two keywords have semantic similarities but differ in phrasing, treat them as "matching" and include them in "match_keywords."
    - Focus on creating a positive, engaging user experience that feels intuitive and exciting.
    - Ensure the final output is visually appealing by balancing category ratios dynamically and avoiding extreme dominance of any single category.
    - In cases where keywords are repetitive or heavily skewed towards a single topic, infer nuanced themes to maximize diversity across the categories.
    - Keep categories general enough to encompass multiple related topics but specific enough to reflect the uniqueness of the dataset.
    - Keywords and categories should feel dynamic and relevant, avoiding placeholders or overly generic terms like "카테고리1."
    - Adjust similarity score calculations dynamically to favor user engagement, ensuring that comparisons feel meaningful without being overly rigid.
    - Maintain consistency in formatting and ensure all JSON responses align perfectly with the defined structure.
    """

    # OpenAI API 호출
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )

        # 응답 데이터 로깅
        response_content = response.choices[0].message.content.strip()
        print(f"[DEBUG] GPT 응답 데이터: {response_content}")

        # JSON 시작과 끝 확인
        json_start = response_content.find("{")
        json_end = response_content.rfind("}")
        if json_start == -1 or json_end == -1:
            raise ValueError("JSON 형식의 응답을 찾을 수 없습니다.")

        # JSON 데이터 파싱
        json_string = response_content[json_start:json_end + 1]
        output_data = json.loads(json_string)

        # 필수 필드 검증
        required_keys = [
            "user1_keywords",
            "user2_keywords",
            "match_keywords",
            "new_categories",
            "user1_category_ratio",
            "user2_category_ratio",
            "similarity_score",
        ]
        for key in required_keys:
            if key not in output_data:
                raise ValueError(f"응답 데이터에 {key} 필드가 없습니다.")

        return output_data

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 오류: {str(e)}")
        raise RuntimeError(f"JSON 파싱 실패: {str(e)}")
    except Exception as e:
        print(f"[ERROR] GPT 요청 실패: {str(e)}")
        raise RuntimeError(f"GPT 요청 실패: {str(e)}")
