import json
import random
import csv
import itertools

# Intent categories
INTENTS = ["market", "disease", "weather", "advice", "subsidy"]

# Vocabulary and misspellings
CROPS = ["wheat", "wheet", "gehu", "gehun", "kanak", "rice", "rise", "dhan", "chawal", 
         "corn", "makka", "cotton", "kapas", "sugarcane", "ganna", "mustard", "sarso", 
         "potato", "aloo", "onion", "pyaz", "tomato", "tamatar", "soybean", "soyabean"]

MARKET_TERMS = ["price", "pryce", "rate", "ret", "bhav", "baav", "paise", "prise", "mkt", "market", "mandi", "markit"]
TODAY_TERMS = ["today", "2day", "td", "todday", "aaj", "now"]

WEATHER_TERMS = ["weather", "wether", "mosam", "mausam", "wedder", "rain", "barish", "baarish", "temp", "dhoop", "heat"]
TOMORROW_TERMS = ["tomorrow", "tmrw", "kal", "tomorow", "2moro", "next day"]

DISEASE_TERMS = ["disease", "sick", "bimari", "keeda", "pest", "bugs", "yellowing", "spots", "dying", "sukha", "dry"]
PARTS = ["leaves", "pattiyan", "root", "jad", "stem", "tana", "crop", "fasal"]

ADVICE_TERMS = ["fertilizer", "khad", "urea", "dap", "water", "pani", "seeds", "beej", "plant", "boi", "grow", "ugana"]

SUBSIDY_TERMS = ["subsidy", "sabsidi", "scheme", "schem", "yojana", "loan", "karz", "govt", "sarkar", "pm kisan", "bank"]

# Sentence Templates
TEMPLATES = {
    "market": [
        "what is the {market} of {crop} {today}?",
        "{market} {market} for {crop}??",
        "{crop} {market}",
        "where to sell {crop} for good {market}",
        "current {crop} {market} {market}",
        "{crop} ka {market} kya hai {today}?",
        "sell {crop} {today} {market}",
        "tell me {crop} {market}",
        "is {market} up for {crop} {today}?"
    ],
    "disease": [
        "my {crop} {parts} are turning yellow",
        "{disease} attack on {crop}",
        "{disease} {crop} help",
        "bugs in {crop}",
        "{crop} is dying what to do",
        "spots on {crop} {parts}",
        "white powder on {crop}",
        "{crop} me {disease} lag gaya",
        "how to save {crop} from {disease}",
        "medicine for {crop} {disease}"
    ],
    "weather": [
        "will it {weather} {tomorrow}?",
        "{weather} forecast for punjab",
        "is {weather} coming?",
        "{weather} {tomorrow}",
        "too much {weather} for {crop}",
        "kya {tomorrow} {weather} hogi?",
        "how is the {weather} {today}?",
        "any chance of {weather} {tomorrow}?",
        "{weather} alert needed"
    ],
    "advice": [
        "what {advice} for {crop}?",
        "when to {advice} {crop}?",
        "how much {advice} for {crop}?",
        "best {advice} for {crop}",
        "intercropping with {crop}",
        "{crop} ke liye kaun sa {advice} acha hai?",
        "need help with {crop} {advice}",
        "should i give {advice} to {crop} {today}?",
        "right time for {crop} {advice}"
    ],
    "subsidy": [
        "{subsidy} for tractor",
        "how to apply for {subsidy}",
        "govt {subsidy} for {crop}",
        "{subsidy} status",
        "kisan credit card {subsidy}",
        "{subsidy} form kaha milega",
        "need {subsidy} for farming",
        "is there any {subsidy} for {crop} farmers?",
        "PM {subsidy} details"
    ]
}

def generate_sentence(intent):
    template = random.choice(TEMPLATES[intent])
    
    # Fill in the blanks with random vocabulary
    sentence = template.format(
        market=random.choice(MARKET_TERMS),
        crop=random.choice(CROPS),
        today=random.choice(TODAY_TERMS),
        weather=random.choice(WEATHER_TERMS),
        tomorrow=random.choice(TOMORROW_TERMS),
        disease=random.choice(DISEASE_TERMS),
        parts=random.choice(PARTS),
        advice=random.choice(ADVICE_TERMS),
        subsidy=random.choice(SUBSIDY_TERMS)
    )
    
    # Sometimes randomly drop characters, flip cases, or remove spaces to simulate bad typing
    if random.random() < 0.2:
        sentence = sentence.replace(" ", "", 1)
    if random.random() < 0.1:
        sentence = sentence.upper()
    if random.random() < 0.3:
        sentence = sentence.replace("?", "")
    
    return sentence.strip()

def build_dataset(num_samples=10000):
    data = []
    
    for _ in range(num_samples):
        intent = random.choice(INTENTS)
        text = generate_sentence(intent)
        data.append({"text": text, "intent": intent})
        
    return data

if __name__ == "__main__":
    dataset = build_dataset(15000)
    
    # Save as JSON
    json_data = {
        "text": [item["text"] for item in dataset],
        "intent": [item["intent"] for item in dataset]
    }
    
    with open("farmers_dataset.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
        
    print(f"✅ Generated farmers_dataset.json with {len(dataset)} records.")
    
    # Save as standard JSON Lines
    with open("farmers_dataset.jsonl", "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"✅ Generated farmers_dataset.jsonl with {len(dataset)} records.")

    # Save as CSV
    with open("farmers_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "intent"])
        for item in dataset:
            writer.writerow([item["text"], item["intent"]])
            
    print(f"✅ Generated farmers_dataset.csv with {len(dataset)} records.")
