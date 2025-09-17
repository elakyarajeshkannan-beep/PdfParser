import pdfplumber
import re
import json 
import datetime

class FileParser:

    def __init__(self , file_name):
        self.file_name = file_name
        self.toc_json_path = "dummy.json"
        self.output_json = "extracted_content.json"
        self.toc_json={}

    def toc_extraction(self , start_in , end_in):
        text = []
        with pdfplumber.open(self.file_name) as pdf:
            for j in range(start_in , end_in):
                    page = pdf.pages[j].extract_text()
                    text.append(page.split("\n"))

        modified_text = [item for sublist in text for item in sublist]
        # print(modified_text)
        dummy = {}
        title = r"^(.*?)\s*\.{2,}"
        page_no = r"(\d+)\s*$"
        for t in modified_text:
            extract = re.search(title , t)
            pg = re.search(page_no , t)
            if extract is None:
                dummy[t] = "null"
            else:
                dummy[extract.group(1)] = pg.group(1)
        self.toc_json=dummy
        with open("dummy.json" , 'w') as file:
            json.dump(dummy , file , indent = 4)

    def content_extraction(self):
       
        #Declare two variables

        seen = set()
        page = set()
        result = {}
        global pastline
        with pdfplumber.open(self.file_name) as live:
            for k,v in self.toc_json.items():
                # print(k)
                # print(self.toc_json.get(k) == "null")
                if v == "null":
                    continue

                page_num = v

                if page_num in page:
                    continue


                page.add(page_num)

                entire_text = live.pages[int(self.toc_json.get(k)) - 1].extract_text()
                pastline = ""
                # print(entire_text)
                for line in entire_text.split("\n"):
                    # print(line)
                        if re.search(r"^(\d+\.)+", line):
                            pastline = line
                            # print(pastline)
                            seen.add(line)
                new_topics = sorted(list(seen))
                # Start timing before content extraction
                st_time = datetime.datetime.now()
                print("Content Extraction Start Time:", st_time)
                for i , topic in enumerate(new_topics):
                    ##change it to regex and calculte the time complexility
                    start_index = entire_text.find(topic)
                    if start_index == -1:
                        #   print("No start indexx.........")
                        continue
                    
                    if i+1 < len(new_topics):
                        next_topics = new_topics[i+1]
                        end_index = entire_text.find(next_topics)

                    else:
                        end_index = len(entire_text)
                    content_start = start_index + len(topic)
                    content = entire_text[content_start:end_index].strip()


                    result[topic] = content
                end_time=datetime.datetime.now()
                print("Content Extraction End Time:", end_time)
                print("Content Extraction Duration:", end_time - st_time)

        # json_op = json.dumps(result , indent = 4)

        with open("extracted_content.json" , "w") as jsonp:
            json.dump(result ,jsonp, indent = 4)
    def contentExtraction_regex(self):
        try:
            with open("dummy.json", 'r') as f:
                file1 = json.load(f)
        except FileNotFoundError:
            print("Error: 'dummy.json' not found. Please create the file.")
            return

        seen = set()
        page = set()
        result1 = {}
        all_text = {}  # Dictionary to store text from each page

        # First pass: collect all text and topics
        with pdfplumber.open("pfizer.pdf") as live:
            for k, v in file1.items():
                if v == "null":
                    continue
                
                page_num = int(v)
                if page_num in page:
                    continue

                page.add(page_num)
                page_text = live.pages[page_num - 1].extract_text()
                all_text[page_num] = page_text

                # Collect topics from this page
                for line in page_text.split("\n"):
                    if re.search(r"^(\d+\.)+", line):
                        seen.add(line.strip())

        # Sort topics to maintain order
        topics = sorted(list(seen))
        
        # Combine all text in page order
        combined_text = ""
        for page_num in sorted(all_text.keys()):
            combined_text += all_text[page_num] + "\n"

        # Extract content between each pair of topics
        st_time = datetime.datetime.now()
        print("Regex Extraction Start Time:", st_time)
        for i in range(len(topics)):
            if i + 1 < len(topics):
                current_topic = topics[i]
                next_topic = topics[i + 1]
                
                # Escape special characters in topics
                current_topic_escaped = re.escape(current_topic)
                next_topic_escaped = re.escape(next_topic)
                
                # Create pattern to match content between topics
                pattern = f"(?<={current_topic_escaped})(.*?)(?={next_topic_escaped})"
                
                match = re.search(pattern, combined_text, re.DOTALL)
                if match:
                    # Store the extracted content, removing leading/trailing whitespace
                    content = match.group(1).strip()
                    result1[current_topic] = content
                else:
                    result1[current_topic] = ""  # No content found between these topics
        end_time = datetime.datetime.now()
        print("Regex Extraction End Time:", end_time)
        print("Regex Extraction Duration:", end_time - st_time)
        # Save the results
        with open("newdummy.json", 'w', encoding='utf-8') as file:
            json.dump(result1, file, indent=4, ensure_ascii=False)   
        
if __name__== '__main__':
    fp = FileParser("pfizer.pdf")
    fp.toc_extraction(27 ,33)
    fp.content_extraction()
    fp.contentExtraction_regex()
#2025-09-11 15:38:34.398593
#2025-09-11 15:38:28.506600
