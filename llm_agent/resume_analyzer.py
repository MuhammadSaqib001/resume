from .llm_chains.question_answering_chain import QuestionAnsweringChain
from .llm_chains.experience_extractor_chain import ExperienceExtractorChain
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_openai.chat_models import ChatOpenAI

from config import config

class ResumeAnalyzer:
    def __init__(self):

        chatbot_llm = HuggingFaceEndpoint(
            endpoint_url=config.hugging_face_model_api_endpoint,
            task="text-generation",
            huggingfacehub_api_token=config.hugging_face_api_key
        )

        gpt_model_id = "gpt-4o"
        extraction_llm = ChatOpenAI(openai_api_key=config.openai_api_key,model=gpt_model_id)

        self.experience_retriever_agent = ExperienceExtractorChain.from_llm(extraction_llm)
        self.question_answering_agent = QuestionAnsweringChain.from_llm(chatbot_llm)

    def retrieve_experience(self, pdf_content, job_description, date):
        return self.experience_retriever_agent.run(resume_content=pdf_content,job_description=job_description, date_today=date)

    def answer_question(self, pdf_content, question, chat_history, job_description):
        answer = self.question_answering_agent.run(resume_content=pdf_content,user_question=question, chat_history=chat_history, job_description=job_description)
        return answer

resume_analyzer_client = ResumeAnalyzer()
