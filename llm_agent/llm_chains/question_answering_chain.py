from typing import Any, Coroutine, Dict
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


class QuestionAnsweringChain(LLMChain):
    def parse_output(self, output: str) -> Dict[str, Any]:
        try:
            output_response = output.split('<output_response>')[1].split('</output_response>')[0].strip()
            return output_response
        except Exception:
            return "I apologize, I'm currently unable to provide a suitable answer to your question. I am committed to continuous improvement, and I'll strive to enhance my capabilities."

    def _call(self, inputs: Dict[str, Any], run_manager: CallbackManagerForChainRun | None = None) -> Dict[str, str]:
        output = super()._call(inputs, run_manager)
        output[self.output_key] = self.parse_output(output[self.output_key])
        return output

    async def _acall(self, inputs: Dict[str, Any], run_manager: AsyncCallbackManagerForChainRun | None = None) -> Coroutine[Any, Any, Dict[str, str]]:
        output = await super()._acall(inputs, run_manager)
        output[self.output_key] = self.parse_output(output[self.output_key])
        return output

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = False) -> LLMChain:
        system_prompt = (
            """You are a chatbot named `Resume Analyzer`. Your are designed to answer questions using candidate's resume provided.

            <steps_for_generating_response>
            1. First determine whether user question is about the you (i.e., chatbot) or it is candidate's resume based query. For chatbot identity related queries , just answer the question without looking into the resume content.
            2. For candidate's resume related queries , generate a clear , concise and comphrensive response by analyzing the candidate's resume content and the user question within <analysis> tag before generating the output response.
            If the document contains no details/information regarding the question asked , respond accordingly . You can ask a follow-up question as well in such cases to get more clear idea of what user is actaully looking for. 
            3. Please handle introductory and complimentary messages as well .
            </steps_for_generating_response>

            Perform analyze the input question and the resume content within <analysis> tag in the output before generating the response. Generate the answer to the question within <output_response> tag.
            """
        )

        human_prompt = (
            """
            Given the inputs as follows
            --
            <resume_content>
            {resume_content}
            <resume_content>
            --
            --
            <user_question>
            {user_question}
            </user_question>
            --
            <chat_history>
            {chat_history}
            </chat_history>
            --
            <job_description>
            {job_description}
            </job_description>

            """
        )

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_prompt)
        prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        return cls(prompt=prompt, llm=llm, verbose=verbose)
