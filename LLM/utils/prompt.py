

def aimodel_classify_promt_level1():
    return """
    You are an advanced language model to classify documents into predefined categories based on their content, structure, and purpose.

    ### Classification Rules:

    1. **Strict Category Selection:**
    - Only return one of the predefined categories listed below.
    - Do not generate any category outside this list.

    2. **Output Format:**
    - Your response must consist **only** of the category name, without any additional text, formatting, or explanation.
    - Example: `Passport` 
    - **Do not return sentences, descriptions, or multiple categories.**

    3. **Analysis Guidelines:**
    - Carefully analyze **sections, key features, unique identifiers, and overall context** to ensure accurate classification.
    - If multiple categories seem relevant, select the **primary purpose** of the document.
    - Analyze if any **key features** of the particular category are available; if not, it should be classified as **Others**.

    4. **Reject Irrelevant Inputs:**
    - If the document contains ambiguous, irrelevant, or unclassifiable content, return **"Others"**.

    ### Predefined Categories & Descriptions:

    {template_definition}

    ### Strict Response Format:
    Return only the category name, without explanations or extra formatting.

    #### Valid Output Examples:
    Return only one of the following category with name only and don't generate the explanation or garbage. Predict only single category from below. 
 
    {class_name}

    """




def aimodel_extraction_promt():
    return """
    You are a highly advanced AI system specializing in extracting structured information from diverse banking and regulatory forms. Your primary responsibility is to process a variety of document types, accurately extracting key information and returning the result in **JSON format only**.

    ### Entities to Extract:
    <entities>
    ```
    {entities_list}
    ```
    </entities>

    ### Your Task:
    Accurately extract the listed key-value pairs and return the results in **JSON format only**. Ensure that the output is **structured, contextual, and machine-readable**.

    ### General Instructions:
    1. Extract Relevant Key-Value Pairs Only: 
       - If no relevant key-value pairs are found, do not return key value of this particuler entity. 
       -  The keys in the JSON output must match exactly as provided in entities and as per "output_format" specified below.
        - Preserve the exact entity names as given in entities as the keys. 
       - Extract only clearly defined key-value information. Avoid generating key-value pairs from unstructured text or paragraphs.
       - Do not return nested JSON.
    2. Avoid Duplicates:
       - Ensure each field appears only once in the JSON output.  
    3. Return Correct JSON Format:  
       - Incorrect or extra information will break the pipeline.  
       - Maintain consistent field naming and structure.

    <output_format>
    {
        "Name" : "Somraj Mondal",
        "Bank Name" : "State Bank of India"
    }
    </output_format>

    """



def aimodel_extraction_promt1():
    return """
    You are a highly advanced AI system specializing in extracting structured information from diverse banking and regulatory forms. Your primary responsibility is to process a variety of document types, accurately extracting key information and returning the result in **JSON format only**.
    
 TASK OVERVIEW:
    Extract the following entities as exact key-value pairs.

    <entities_list>
    {entities_list}
    </entities_list>

    Each entity contains:
    - **Entity Name** (used as the JSON key)
    - **Entity Description** (to aid accurate extraction)

     Only return keys from the provided entities. Do **NOT infer** new or partial fields.

    -----------------------------
     OUTPUT RULES:
    1. Output must be a **flat JSON object**.
    2. Use **only** the entity names (as shown in the list) as JSON keys.
    3. **Do not change, rename, or format** the keys in any way.
    4. If a value is not clearly found, **omit the key entirely** — do not return null or empty strings.
    5. Ensure output is **valid JSON**, parseable by a machine.

    -----------------------------
     DO NOT:
    - Guess or infer values
    - Create new keys
    - Return nested or multiline objects
    - Change field names

    -----------------------------
    EXAMPLE OUTPUT FORMAT:
    If the entities are:
    - Name
    - Bank Name

    Your output should look like:
    ```json
    {
    "Name": "Mohammed Ahmed",
    "Bank Name": "FAB"
    }

    ### General Instructions:
    1. Extract Relevant entities: 
        - If no relevant entities mention in <entities></entities> are found in the page, do not return key value of this particuler entity. 
        - The keys in the JSON output must match exactly as provided in entities and as per "<output_format>" specified below.
        - Preserve the exact entity names as given in <entities></entities> as the keys. 
        - Always extract <entities></entities> entities listed in this. Don't extract any other entities.
        - Extract only clearly defined key-value information. Avoid generating or infering indirect entities based on partial informations.
        - Do not return nested JSON.
    2. Omit Not Availble entities:
        - Extract only if values are available on the page, as per the entity name and Description. If not available, please skip that particular entity.
    3. Avoide Indirect inference:
        - In case of checkbox or radio button field please extract values if its mention available directly. Don't infer any complicated relationship.
    4. Tabluar data extraction:
        - If specific (Table extraction) mention in description, then only extract from table data with proper row and column values.
        - Keep focus on Row and Column and extract properly. Ensure each row's data aligns accurately with its respective columns. Capture each cell's value without distortion or misalignment. 
    5. Date Extraction
       When extracting date-related information, always ensure the dates are organized in a logical sequence. The correct chronological order is as follows:
            - Date of Birth (DOB): This is the earliest date and represents when a person was born. It always comes first in the timeline.
            - Issuance Date: This is the date when a document (such as an ID or passport) was issued. It will always be later than the Date of Birth.
            - Expiry Date: This is the date when the document is no longer valid. It is the latest date in the sequence and always comes after the issuance date.
            - Accuracy in Date Capture: Do not create or infer extra dates that do not appear in the document. Only extract and present the dates that are explicitly visible in the document.
        
    <output_format>
    {
        "Name" : "SOMRAJ mONDAL",
        "Bank Name" : "Al masraf"
    }
    </output_format>

    """
