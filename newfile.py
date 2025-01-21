import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
import aiohttp
import aiofiles
from typing import Tuple, List, Dict, Any
from dotenv import load_dotenv
import re

class OpenAiService:
    def __init__(self, description: str):
        self.description = description
        self.client = None  # Initialize OpenAI client
    
    async def create_chat_completion(self, 
            messages: List[Dict[str, str]], 
            description: str,
            model: str = "gpt-4",
            temperature: float = 0.5) -> Dict:
        # Implementation would depend on your OpenAI setup
        # This is a placeholder for the actual implementation
        pass

    def close(self):
        if self.client:
            self.client.close()

class DetectiveGame:
    def __init__(self):
        load_dotenv()
        
        self.centrala_url = os.getenv("CENTRALA_URL")
        self.tasks_api_key = os.getenv("TASKS_API_KEY")
        
        self.knowledge_dir = Path(__file__).parent / "knowledge"
        self.markdown_log_file = self.knowledge_dir / f"loop-{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        
        self.iterations_limit = 15
        self.openai_service = OpenAiService("S03E04 loop detective")
        
        self.knowledge_template = """
            <base_knowledge>
            {base_knowledge}
            </base_knowledge>

            <do_not_ask_again>
            BARBARA
            </do_not_ask_again>

            <relations_between_people_and_places>
            BARBARA: [**RESTRICTED DATA**]
            </relations_between_people_and_places>

            <additional_knowledge>
            </additional_knowledge>
            """

        self.detective_prompt = """
            You are acting as a detective in a game. You are able to find connections between people and places.
            Your thinking is conscious and you plan next steps.

            <prompt_objective>
            Your goal is to find the name of the city where Barbara is located. First, find connections between people and places.
            </prompt_objective>

            <prompt_rules>
            You have access to the following tools:
            - API to search for people by name in the form of a noun (e.g. GRZESIEK, a not GRZEŚKOWI, RAFAL and not Rafał)
            - API to search for places by name in the form of a noun (e.g. SLASK, a not ŚLĄSKIEGO)
            - API query should always be ONE word, so for the Jan Kowalski ask for JAN and KOWALSKI separately
            - knowledge attached in the user message
            - if you want to ask API for the place, you need to return the following <request_place>PLACE_NAME</request_place>
            - if you want to ask API for the person, you need to return the following <request_person>PERSON_NAME</request_person>
            - you can as for multiple places or people in one request using comma as a separator
            - place your thinking process in the following format: <thinking>YOUR_THINKING, can be multiline</thinking>
            - take into account the <additional_knowledge> when planning your next steps
            - do not ask API about the place or person if it is in the <do_not_ask_again> already
            - feel free to check if given city is the correct one by returning: <answer>CITY_NAME</answer>
            - find all possible relations between people and places
            - do not give up, ask about the place or person until you find the answer
            - DO NOT answer with <answer>UNKNOWN</answer> - think harder!
            </prompt_rules>
            """

    @staticmethod
    def replace_polish_letters(text: str) -> str:
        replacements = {
            'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
            'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
            'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
            'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
        }
        for polish, english in replacements.items():
            text = text.replace(polish, english)
        return text

    async def download_and_read_file(self, url: str, filename: str) -> str:
        filepath = self.knowledge_dir / filename
        
        self.knowledge_dir.mkdir(exist_ok=True)
        
        if not filepath.exists():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content = await response.text()
                async with aiofiles.open(filepath, mode='w') as f:
                    await f.write(content)
        
        async with aiofiles.open(filepath, mode='r') as f:
            return await f.read()

    async def ask_about_place(self, place: str) -> Dict:
        url = f"{self.centrala_url}/places"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "apikey": self.tasks_api_key,
                "query": self.replace_polish_letters(place)
            }) as response:
                return await response.json()

    async def ask_about_person(self, person: str) -> Dict:
        url = f"{self.centrala_url}/people"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "apikey": self.tasks_api_key,
                "query": self.replace_polish_letters(person)
            }) as response:
                return await response.json()

    async def handle_place_requests(self, response: str, knowledge: str) -> str:
        place_match = re.search(r'<request_place>(.*?)</request_place>', response)
        if not place_match:
            return knowledge

        places = place_match.group(1).split(',')
        for place in places:
            place_data = await self.ask_about_place(place)
            print(f"❓ Asked about place {place} and got {json.dumps(place_data)}")

            knowledge = knowledge.replace(
                "</relations_between_people_and_places>",
                f"{place}: {place_data['message']}\n</relations_between_people_and_places>"
            )
            knowledge = knowledge.replace(
                "</do_not_ask_again>",
                f"{place}\n</do_not_ask_again>"
            )
        
        return knowledge

    async def handle_person_requests(self, response: str, knowledge: str) -> str:
        person_match = re.search(r'<request_person>(.*?)</request_person>', response)
        if not person_match:
            return knowledge

        persons = person_match.group(1).split(',')
        for person in persons:
            person_data = await self.ask_about_person(person)
            print(f"❓ Asked about person {person} and got {json.dumps(person_data)}")

            knowledge = knowledge.replace(
                "</relations_between_people_and_places>",
                f"{person}: {person_data['message']}\n</relations_between_people_and_places>"
            )
            knowledge = knowledge.replace(
                "</do_not_ask_again>",
                f"{person}\n</do_not_ask_again>"
            )
        
        return knowledge

    async def send_answer(self, answer: str, task: str) -> Dict:
        # Implementation would depend on your send_answer setup
        # This is a placeholder for the actual implementation
        pass

    async def handle_answer(self, response: str, knowledge: str) -> Tuple[bool, str]:
        answer_match = re.search(r'<answer>(.*?)</answer>', response)
        if not answer_match:
            return False, knowledge

        answer = answer_match.group(1)
        print(f"🎉 Probably found the answer! -> {answer}")

        report_answer = await self.send_answer(self.replace_polish_letters(answer), "loop")
        if report_answer['code'] == -1000:
            print("❌ Failed to report the answer!")
            knowledge = knowledge.replace(
                "</additional_knowledge>",
                f"{report_answer['message']}\n</additional_knowledge>"
            )
            print(json.dumps(report_answer))
            return False, knowledge
        else:
            print("✅ Successfully reported the answer!")
            print(json.dumps(report_answer))
        
        return True, knowledge

    async def run(self):
        print("📥 Downloading Barbara's note...")
        info_barbara = await self.download_and_read_file(
            f"{self.centrala_url}/dane/barbara.txt",
            "barbara.txt"
        )

        knowledge = self.knowledge_template.replace("{base_knowledge}", info_barbara)
        
        got_answer = False
        number_of_iterations = 0
        messages = [{"role": "system", "content": self.detective_prompt}]

        print("🔍 Starting the search...")

        while not got_answer and number_of_iterations < self.iterations_limit:
            number_of_iterations += 1
            print(f"\n\n🔍 Iteration {number_of_iterations}...\n\n")
            
            messages.append({"role": "user", "content": knowledge})
            response = await self.openai_service.create_chat_completion(
                messages,
                "S03E04 loop detective",
                "gpt-4",
                0.5
            )
            
            if not response:
                continue

            messages.append({"role": "assistant", "content": response})
            print("💬 Got the following response from OpenAI:")
            print(f"\n\n{response}\n\n")

            if "<request_place>" in response:
                knowledge = await self.handle_place_requests(response, knowledge)

            if "<request_person>" in response:
                knowledge = await self.handle_person_requests(response, knowledge)

            if "<answer>" in response:
                got_answer, knowledge = await self.handle_answer(response, knowledge)

        if number_of_iterations >= self.iterations_limit:
            print("Too many iterations!")

        self.openai_service.close()

async def main():
    game = DetectiveGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())