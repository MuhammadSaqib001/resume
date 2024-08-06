from typing import Any, Coroutine, Dict
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


class ExperienceExtractorChain(LLMChain):
    def parse_output(self, output: str) -> Dict[str, Any]:
        try:
            relevant_job_experience = output.split('<relevant_job_experience>')[1].split('</relevant_job_experience>')[0].strip()
            total_job_experience = output.split('<total_job_experience>')[1].split('</total_job_experience>')[0].strip()
            return [total_job_experience,relevant_job_experience]
        except Exception:
                return ['N/A','N/A']

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
            """Given a candidate's resume content and description specific to a job role , your task is to extract and output two things 
            based on the work experience (rounded to nearest half year) mentioned by the candidate in the resume.
            
            1. Total Job Experience of the candidate rounded to nearest half year.
            **[IMPORTANT] Projects and education listed by candidate aren't considered in work experience . Just jobs listed under Work/Work Experience section are considered.**

            2. Relevant Job Experience of the candidate (candidate's experience tenure that completely matches with the given job description) rounded to nearest half year.
            Output N/A if there is no experience of the candidate matching with the job role mentioned.

            **Analyze and think within <analysis> tag before generating output.**

            Output Format :-
            [IMPORTANT] Please output the Total Job Experience duration within <total_job_experience> tag and Relevant Job Experience duration within <relevant_job_experience> tag.
            [IMPORTANT] Just output the duration numbers as instructed within the respective tags ; no explanation needed.        
            """
        )

        human_prompt = (
            """
            Given the inputs as follows
            --
            <job_description>
            {job_description}
            </job_description>
            --
            <date_today>
            {date_today}
            </date_today>
            --
            <resume_content>
            {resume_content}
            </resume_content>



            <instructions>
            1. Please output N/A in both total and relevant work experience if the document content contains no job description.
            2. **Always output experience rounded to nearest half year like `3 years 11 months` is rounded to `4 years` or `3 years 1 month` is rounded `3 years`.**
            </instructions>
            """
        )

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_prompt)
        prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        return cls(prompt=prompt, llm=llm, verbose=verbose)
