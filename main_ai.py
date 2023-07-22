import os
import openai
import json 
from dotenv import load_dotenv

class PumpDataProcessor:
    def __init__(self):
        self.info_save_folder = os.getenv("DEFAULT_FILE_FOLDER")
        self.sample_data_keys = [
            'name', 'Maximum temperature', 'Maximum temperature (with flush)', 'Maximum suction pressure',
            'Maximum head', 'Maximum speed', 'Maximum flow', 'Maximum horsepower', 'Rotor',
            'Rotor cover', 'Manifold', 'Endbell', 'Pick-up tube*', 'Shaft'
        ]
        self.sample_data_value=[
            'Roto-Jet API-R11', '180F, 82C', '250F 121C', '200PSI 14BAR',
            '1500Ft', '150GPM 34m3/hr', '75HP 55KW', '380Ibs. 159kg', '316 St. Steel',
            '316 St. Steel', '316 St. Steel', 'Ductile Iron', '17-4 PH', 'AISI 4140'
        ]
    def get_pump_info(self, pump_data):
        try:
            prompt = f"{pump_data}This is dog description. Give me {', '.join(self.sample_data_keys)}. Provide the response in JSON format, with keys in lowercase without spaces or symbols."
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=prompt,
                max_tokens=500,
                temperature=0.8,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                n=1
            )
            return json.loads(response.choices[0].text.strip())
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {"":""}
    def process_unique_keys(self):
        while True:
            pdf_files = [file for file in os.listdir(self.info_save_folder) if file.endswith(".pdf")]
            if not pdf_files.count:
                break
            for pdf_file in pdf_files:
                folder_name = os.path.splitext(pdf_file)[0]
                pdf_folder_path = os.path.join(self.info_save_folder, folder_name)
                text_file_path = os.path.join(pdf_folder_path, folder_name+".txt")
                json_file_path = os.path.join(pdf_folder_path, "json.txt")
                with open(text_file_path, "r") as text_file:
                    pump_data=text_file.read()
                    pump_info=self.get_pump_info(pump_data)
                    print(pump_info)
                    with open(json_file_path, "w") as json_file:
                        json_file.write(str(pump_info))
                
            


if __name__ == "__main__":
    load_dotenv()
    openai.api_key=os.getenv("OPENAI_API_KEY")
    processor = PumpDataProcessor()
    processor.process_unique_keys()