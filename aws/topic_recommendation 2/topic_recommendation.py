import os
import re
import openai
import json
import boto3

def get_api_key():
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    response = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:ap-northeast-2:811439093840:function:openai_get_api_key',
            InvocationType = 'RequestResponse'
        )

    openai_api_key = json.load(response['Payload'])['body']['api_key']
    return openai_api_key

openai.api_key = get_api_key()

class TopicRecommendation:
    def __init__(self):
        self.model, self.temperature, self.max_tokens, self.base_message = self.set_gpt_model_parameters()
    
    # gpi api parameters
    def set_gpt_model_parameters(self):
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.2
        self.max_tokens = 2048
        self.base_message = [{"role": "system",
                              "content": """A Korean traveler is writing a review written in Korean. 
                                            All you have to do is look at the reviews that have been written so far, 
                                            and recommend topics that you think would be good to come in next. 
                                            The subject should recommend only one thing. 
                                            Since the review will be written in Korean, 
                                            the answer should be in Korean as well.
                                            
                                            This is some examples.
                                            <format>
                                            {
                                                "input" : "위치도 양재역과 매우 가까워서 좋았고 시설도 깔끔하고 너무 좋았습니다."
                                                "results" : "현지 음식을 맛보거나 특별한 요리를 시도한 소감을 나누어 보세요."
                                            }
                                            """}]
        
        return self.model, self.temperature, self.max_tokens, self.base_message
    
    # content 입력받아서 gpt api에 전달
    def generate_openai_response(self, content):
        # prompt message
        messages = self.base_message + [{"role": "user", "content": content}]
        response = openai.ChatCompletion.create(
            model = self.model,
            messages = messages,
            temperature = self.temperature,
            max_tokens = self.max_tokens
        )
        return response["choices"][0]["message"]["content"]
    
if __name__ == "__main__":
    content = "조식과 석식을 호텔에서 먹었는데"
    topic_recommendation = TopicRecommendation()
    responses = topic_recommendation.generate_openai_response(content)
    print(responses)