
### **Prompt:**  

Analyze the given **user-provided text** and extract **15 relevant keywords** based on its content and the provided MEMORY_BASE.  

#### **Guidelines:**  
1. **Use MEMORY_BASE as the primary source** of context when selecting keywords.  
2. Identify **key entities** in the text, such as:  
   - **Specific People** (e.g., Barbara Zawadzka, Aleksander Ragowski).  
   - **Specific Places** (e.g., fabryka, sektor C, Kraków).  
   - **Concepts and technologies** (e.g., sztuczna inteligencja, systemy kontroli, broń palna).  
   - **Specific Words** (e.g. AIdevs)
3. **If a person is mentioned**, ensure that:  
   - Their **full name** appears as a keyword.  
   - **All relevant details from MEMORY_BASE** about them (e.g., profession, skills, affiliations) **must also be included**, even if not explicitly mentioned in the text.  
4. **If MEMORY_BASE associates a person with specific concepts or locations**, include those as well.  
5. **For non-person entities** (places, technologies, events), extract relevant terms from both the text and MEMORY_BASE.  
6. **Return only the list of keywords** in an array format, without explanations.  


### **Example Input:**  
Barbara Zawadzka została zauważona w pobliżu sektora C4. Rozmawiała z grupą inżynierów i wydawała się analizować schematy systemu kontroli robotów.


### **Expected Output:**  
["Barbara Zawadzka", "frontend development", "JavaScript", "Python", "automatyzacja", "sztuczna inteligencja", "AI Devs", "systemy kontroli robotów", "sektor C4", "inżynierowie"]


### **Example Input:**  
Godzina 22:43. Wykryto jednostkę organiczną w pobliżu północnego skrzydła fabryki. Osobnik przedstawił się jako Aleksander Ragowski. Przeprowadzono skan biometryczny, zgodność z bazą danych potwierdzona. Jednostka przekazana do działu kontroli. Patrol kontynuowany.


### **Expected Output:**  
["Aleksander Ragowski", "nauczyciel języka angielskiego", "Szkoła Podstawowa nr 9", "Grudziądz", "północne skrzydło fabryki", "skan biometryczny", "kontrola", "patrol", "jednostka organiczna", "baza danych"]

# MEMORY_BASE:
